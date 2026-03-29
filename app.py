"""
智能文献分析系统 - 基于AI大模型
主界面：Streamlit应用
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import json
import streamlit as st
import pandas as pd
import numpy as np

from modules.data_collector import (
    search_arxiv, search_semantic_scholar, clean_and_standardize,
    save_papers, load_papers, get_paper_citations, get_paper_references,
)
from modules.info_extractor import (
    extract_keywords_tfidf, batch_extract_info_llm, build_knowledge_graph,
    build_author_collaboration_network, get_llm_client,
)
from modules.topic_analyzer import (
    topic_modeling_lda, topic_modeling_tfidf_kmeans,
    trend_analysis, identify_hot_topics,
)
from modules.recommender import (
    load_user_profile, save_user_profile, update_user_interests,
    mark_paper_read, mark_paper_liked, add_search_history,
    content_based_recommend, similar_paper_recommend,
)
from modules.visualizer import (
    plot_yearly_trend, plot_citation_trend, plot_topic_distribution,
    plot_topic_scatter, plot_keyword_bar, plot_author_stats,
    plot_collaboration_network, plot_keyword_trend_heatmap,
    plot_keyword_cloud_data,
)

# ============ 页面配置 ============
st.set_page_config(
    page_title="智能文献分析系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ 自定义样式 ============
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📚 智能文献分析系统</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:gray;">基于AI大模型的学术文献智能分析、知识挖掘与可视化平台</p>', unsafe_allow_html=True)

# ============ 初始化Session State ============
if "papers_df" not in st.session_state:
    st.session_state.papers_df = load_papers()
if "user_profile" not in st.session_state:
    st.session_state.user_profile = load_user_profile()
if "topic_result" not in st.session_state:
    st.session_state.topic_result = None


# ============ 侧边栏 ============
with st.sidebar:
    st.header("🔧 系统设置")

    # 数据源选择
    data_source = st.selectbox("数据源", ["arXiv", "Semantic Scholar", "Both"])

    # LLM状态
    llm_client = get_llm_client()
    if llm_client:
        st.success("✅ LLM已连接")
    else:
        st.warning("⚠️ LLM未配置 (使用TF-IDF替代)")
        st.caption("在.env文件中配置OPENAI_API_KEY")

    st.divider()

    # 用户画像
    st.header("👤 用户画像")
    profile = st.session_state.user_profile
    if profile["interests"]:
        st.write("**研究兴趣：**")
        st.write(", ".join(profile["interests"][:10]))
    if profile["read_papers"]:
        st.metric("已读论文", len(profile["read_papers"]))
    if profile["liked_papers"]:
        st.metric("收藏论文", len(profile["liked_papers"]))

    # 手动添加兴趣
    new_interest = st.text_input("添加研究兴趣关键词")
    if st.button("添加") and new_interest:
        update_user_interests(profile, [new_interest])
        st.session_state.user_profile = profile
        st.rerun()

    st.divider()
    # 数据统计
    if not st.session_state.papers_df.empty:
        st.header("📊 数据概览")
        df = st.session_state.papers_df
        st.metric("总文献数", len(df))
        if "year" in df.columns:
            valid_years = df["year"].dropna()
            if len(valid_years) > 0:
                st.metric("时间跨度", f"{int(valid_years.min())}-{int(valid_years.max())}")


# ============ 主页面标签页 ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 文献检索", "📊 主题与趋势", "🌐 知识图谱",
    "💡 智能推荐", "📋 文献管理"
])


# ============ Tab 1: 文献检索 ============
with tab1:
    st.header("🔍 文献数据收集与检索")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        query = st.text_input("输入搜索关键词", placeholder="e.g., large language model, transformer")
    with col2:
        max_results = st.number_input("最大结果数", 10, 200, 50, step=10)
    with col3:
        sort_option = st.selectbox("排序", ["relevance", "date"])

    if st.button("🚀 开始检索", type="primary", use_container_width=True):
        if query:
            with st.spinner("正在检索文献数据..."):
                papers = []
                if data_source in ["arXiv", "Both"]:
                    arxiv_papers = search_arxiv(query, max_results, sort_option)
                    papers.extend(arxiv_papers)
                    st.toast(f"从arXiv获取 {len(arxiv_papers)} 篇文献")

                if data_source in ["Semantic Scholar", "Both"]:
                    s2_papers = search_semantic_scholar(query, max_results)
                    papers.extend(s2_papers)
                    st.toast(f"从Semantic Scholar获取 {len(s2_papers)} 篇文献")

                if papers:
                    df = clean_and_standardize(papers)

                    # TF-IDF关键词提取
                    kw_dict = extract_keywords_tfidf(df)
                    for i, row in df.iterrows():
                        if row["title"] in kw_dict:
                            df.at[i, "keywords"] = kw_dict[row["title"]]

                    st.session_state.papers_df = df
                    save_papers(df)

                    # 更新用户画像
                    add_search_history(profile, query)
                    st.session_state.user_profile = profile

                    st.success(f"✅ 共获取并处理 {len(df)} 篇文献")
                else:
                    st.error("未找到相关文献，请调整搜索词")
        else:
            st.warning("请输入搜索关键词")

    # 展示检索结果
    df = st.session_state.papers_df
    if not df.empty:
        st.subheader(f"📄 文献列表 ({len(df)} 篇)")

        # 过滤选项
        col1, col2 = st.columns(2)
        with col1:
            if "year" in df.columns:
                years = sorted(df["year"].dropna().unique())
                if years:
                    year_range = st.slider("年份筛选",
                                           int(min(years)), int(max(years)),
                                           (int(min(years)), int(max(years))))
        with col2:
            title_filter = st.text_input("标题关键词过滤")

        # 应用过滤
        filtered_df = df.copy()
        if "year" in df.columns and years:
            filtered_df = filtered_df[
                (filtered_df["year"] >= year_range[0]) & (filtered_df["year"] <= year_range[1])
            ]
        if title_filter:
            filtered_df = filtered_df[
                filtered_df["title"].str.contains(title_filter, case=False, na=False)
            ]

        # 展示表格
        display_cols = ["title", "authors", "published", "source"]
        if "citation_count" in filtered_df.columns:
            display_cols.append("citation_count")

        st.dataframe(
            filtered_df[display_cols].reset_index(drop=True),
            use_container_width=True,
            height=400,
        )

        # 论文详情
        st.subheader("📖 论文详情")
        paper_titles = filtered_df["title"].tolist()
        selected_title = st.selectbox("选择论文查看详情", paper_titles)

        if selected_title:
            paper = filtered_df[filtered_df["title"] == selected_title].iloc[0]
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"### {paper['title']}")
                authors = paper["authors"]
                if isinstance(authors, list):
                    st.markdown(f"**作者：** {', '.join(authors)}")
                st.markdown(f"**发表日期：** {paper.get('published', 'N/A')}")
                st.markdown(f"**来源：** {paper.get('source', 'N/A')}")
                if paper.get("doi"):
                    st.markdown(f"**DOI：** {paper['doi']}")
                st.markdown("**摘要：**")
                st.markdown(paper.get("abstract", "无摘要"))
            with col2:
                if paper.get("citation_count"):
                    st.metric("引用次数", int(paper["citation_count"]))
                keywords = paper.get("keywords", [])
                if isinstance(keywords, list) and keywords:
                    st.markdown("**关键词：**")
                    for kw in keywords:
                        st.markdown(f"- {kw}")
                if paper.get("pdf_url"):
                    st.link_button("📄 查看原文", paper["pdf_url"])

                # 交互按钮
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("📖 标记已读"):
                        mark_paper_read(profile, selected_title)
                        st.toast("已标记为已读")
                with bcol2:
                    if st.button("❤️ 收藏"):
                        mark_paper_liked(profile, selected_title)
                        keywords = paper.get("keywords", [])
                        if isinstance(keywords, list):
                            update_user_interests(profile, keywords)
                        st.toast("已收藏")


# ============ Tab 2: 主题与趋势分析 ============
with tab2:
    st.header("📊 主题建模与趋势分析")

    df = st.session_state.papers_df
    if df.empty:
        st.info("请先在「文献检索」中搜索文献")
    else:
        # 趋势分析
        st.subheader("📈 发表趋势")
        trends = trend_analysis(df)
        if trends:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总论文数", trends["total_papers"])
            with col2:
                yr = trends.get("year_range", (0, 0))
                st.metric("时间范围", f"{yr[0]}-{yr[1]}")
            with col3:
                if trends.get("top_categories"):
                    st.metric("热门领域", trends["top_categories"][0][0])

            if trends.get("yearly_counts"):
                st.plotly_chart(plot_yearly_trend(trends["yearly_counts"]),
                               use_container_width=True)

            if trends.get("yearly_citations"):
                st.plotly_chart(plot_citation_trend(trends["yearly_citations"]),
                               use_container_width=True)

        st.divider()

        # 主题建模
        st.subheader("🎯 主题建模")
        col1, col2 = st.columns(2)
        with col1:
            method = st.selectbox("建模方法", ["LDA", "TF-IDF + KMeans"])
        with col2:
            n_topics = st.slider("主题数量", 2, 10, 5)

        if st.button("🔬 开始主题分析", type="primary"):
            with st.spinner("正在进行主题建模..."):
                if method == "LDA":
                    result = topic_modeling_lda(df, n_topics)
                else:
                    result = topic_modeling_tfidf_kmeans(df, n_topics)
                st.session_state.topic_result = result

        if st.session_state.topic_result:
            result = st.session_state.topic_result
            topics = result["topics"]

            # 主题关键词展示
            for topic_name, topic_data in topics.items():
                with st.expander(f"📌 {topic_name}: {', '.join(topic_data['top_words'][:5])}"):
                    words = topic_data["top_words"]
                    st.write(", ".join(words))

            # 主题分布图
            if "df" in result:
                st.plotly_chart(plot_topic_scatter(result["df"]),
                               use_container_width=True)

        st.divider()

        # 关键词分析
        st.subheader("🔑 关键词分析")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(plot_keyword_bar(df), use_container_width=True)
        with col2:
            if trends and trends.get("keyword_trends"):
                st.plotly_chart(plot_keyword_trend_heatmap(trends["keyword_trends"]),
                               use_container_width=True)

        # 热点识别
        st.subheader("🔥 热点识别")
        hot = identify_hot_topics(df)
        if hot:
            st.markdown(f"**分析周期：** {hot.get('period', 'N/A')}")
            if hot.get("hot_keywords"):
                st.markdown("**热门关键词：**")
                kw_text = " | ".join([f"**{k}** ({v})" for k, v in hot["hot_keywords"][:10]])
                st.markdown(kw_text)
            if hot.get("hot_papers"):
                st.markdown("**高引用论文：**")
                for p in hot["hot_papers"][:5]:
                    authors = p["authors"]
                    if isinstance(authors, list):
                        authors = ", ".join(authors[:3])
                    st.markdown(f"- 📄 **{p['title']}** | {authors} | 引用: {p.get('citation_count', 0)}")


# ============ Tab 3: 知识图谱 ============
with tab3:
    st.header("🌐 知识图谱与网络分析")

    df = st.session_state.papers_df
    if df.empty:
        st.info("请先在「文献检索」中搜索文献")
    else:
        graph_type = st.selectbox("选择网络类型", [
            "作者合作网络", "关键词共现网络", "论文-作者-关键词知识图谱"
        ])

        if st.button("🔗 生成网络图", type="primary"):
            with st.spinner("正在构建网络..."):
                if graph_type == "作者合作网络":
                    G = build_author_collaboration_network(df)
                    st.session_state.current_graph = G
                    st.session_state.graph_type = "collaboration"
                elif graph_type == "论文-作者-关键词知识图谱":
                    G = build_knowledge_graph(df)
                    st.session_state.current_graph = G
                    st.session_state.graph_type = "knowledge"
                else:
                    # 关键词共现网络
                    G = nx.Graph()
                    for _, row in df.iterrows():
                        kws = row.get("keywords", [])
                        if isinstance(kws, str):
                            kws = [k.strip() for k in kws.split(",")]
                        if isinstance(kws, list):
                            for i in range(len(kws)):
                                for j in range(i + 1, len(kws)):
                                    if kws[i] and kws[j]:
                                        if G.has_edge(kws[i], kws[j]):
                                            G[kws[i]][kws[j]]["weight"] += 1
                                        else:
                                            G.add_edge(kws[i], kws[j], weight=1)
                    st.session_state.current_graph = G
                    st.session_state.graph_type = "keyword"

        if "current_graph" in st.session_state:
            G = st.session_state.current_graph
            st.markdown(f"**节点数：** {G.number_of_nodes()} | **边数：** {G.number_of_edges()}")

            # 使用plotly绘制网络图
            if G.number_of_nodes() > 0:
                max_display = st.slider("最大显示节点数", 10, 200, 50)

                # 选择度数最高的节点
                if G.number_of_nodes() > max_display:
                    top_nodes = sorted(G.nodes, key=lambda n: G.degree(n), reverse=True)[:max_display]
                    subG = G.subgraph(top_nodes)
                else:
                    subG = G

                pos = nx.spring_layout(subG, seed=42, k=2/np.sqrt(max(subG.number_of_nodes(), 1)))

                # 边
                edge_x, edge_y = [], []
                for u, v in subG.edges():
                    x0, y0 = pos[u]
                    x1, y1 = pos[v]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])

                edge_trace = {
                    "x": edge_x, "y": edge_y,
                    "mode": "lines",
                    "line": {"width": 0.5, "color": "#888"},
                    "hoverinfo": "none",
                    "type": "scatter",
                }

                # 节点
                node_x = [pos[n][0] for n in subG.nodes()]
                node_y = [pos[n][1] for n in subG.nodes()]
                node_text = list(subG.nodes())
                node_size = [min(5 + subG.degree(n) * 2, 30) for n in subG.nodes()]

                # 节点颜色
                if st.session_state.get("graph_type") == "knowledge":
                    color_map = {"paper": "blue", "author": "red", "keyword": "green"}
                    node_color = [color_map.get(subG.nodes[n].get("type", ""), "gray") for n in subG.nodes()]
                else:
                    node_color = [subG.degree(n) for n in subG.nodes()]

                node_trace = {
                    "x": node_x, "y": node_y,
                    "mode": "markers+text",
                    "text": [n[:20] for n in node_text],
                    "textposition": "top center",
                    "textfont": {"size": 8},
                    "marker": {
                        "size": node_size,
                        "color": node_color,
                        "colorscale": "YlOrRd" if isinstance(node_color[0], (int, float)) else None,
                        "showscale": isinstance(node_color[0], (int, float)),
                        "line": {"width": 1, "color": "white"},
                    },
                    "hovertext": node_text,
                    "hoverinfo": "text",
                    "type": "scatter",
                }

                import plotly.graph_objects as go
                fig = go.Figure(data=[edge_trace, node_trace])
                fig.update_layout(
                    title=f"🌐 {graph_type}",
                    showlegend=False,
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=600,
                    template="plotly_white",
                )
                st.plotly_chart(fig, use_container_width=True)

                # 网络统计
                st.subheader("📊 网络统计")
                col1, col2, col3 = st.columns(3)
                with col1:
                    degrees = dict(subG.degree())
                    top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
                    st.markdown("**核心节点 (度中心性)：**")
                    for node, deg in top_nodes:
                        st.markdown(f"- {node[:30]}: {deg}")
                with col2:
                    st.metric("网络密度", f"{nx.density(subG):.4f}")
                    if not nx.is_directed(subG):
                        components = nx.number_connected_components(subG)
                        st.metric("连通分量数", components)
                with col3:
                    if subG.number_of_nodes() > 2:
                        try:
                            betweenness = nx.betweenness_centrality(subG)
                            top_between = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
                            st.markdown("**桥梁节点 (介数中心性)：**")
                            for node, bc in top_between:
                                st.markdown(f"- {node[:30]}: {bc:.3f}")
                        except Exception:
                            pass

        # 作者统计
        st.divider()
        st.subheader("👨‍🔬 作者统计")
        st.plotly_chart(plot_author_stats(df), use_container_width=True)


# ============ Tab 4: 智能推荐 ============
with tab4:
    st.header("💡 智能推荐与个性化服务")

    df = st.session_state.papers_df
    profile = st.session_state.user_profile

    if df.empty:
        st.info("请先在「文献检索」中搜索文献")
    else:
        st.subheader("🎯 个性化推荐")
        if profile.get("interests"):
            st.markdown(f"**当前研究兴趣：** {', '.join(profile['interests'][:10])}")

        if st.button("🔄 获取推荐", type="primary"):
            with st.spinner("正在生成推荐..."):
                recommended = content_based_recommend(df, profile, top_n=10)
                st.session_state.recommended_papers = recommended

        if "recommended_papers" in st.session_state:
            rec_df = st.session_state.recommended_papers
            for i, (_, paper) in enumerate(rec_df.iterrows()):
                with st.expander(f"📄 {i+1}. {paper['title']}" +
                                (f" (相关度: {paper.get('relevance_score', 0):.2f})" if "relevance_score" in paper else "")):
                    authors = paper["authors"]
                    if isinstance(authors, list):
                        st.markdown(f"**作者：** {', '.join(authors[:5])}")
                    st.markdown(f"**发表日期：** {paper.get('published', 'N/A')}")
                    st.markdown(f"**摘要：** {str(paper.get('abstract', ''))[:300]}...")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📖 标记已读", key=f"read_{i}"):
                            mark_paper_read(profile, paper["title"])
                            st.toast("已标记已读")
                    with col2:
                        if st.button("❤️ 收藏", key=f"like_{i}"):
                            mark_paper_liked(profile, paper["title"])
                            st.toast("已收藏")

        st.divider()

        # 相似论文推荐
        st.subheader("🔗 相似论文推荐")
        selected = st.selectbox("选择一篇论文，查找相似文献", df["title"].tolist(), key="sim_select")
        if st.button("查找相似论文"):
            with st.spinner("计算相似度..."):
                similar = similar_paper_recommend(df, selected, top_n=5)
                for _, paper in similar.iterrows():
                    st.markdown(f"- 📄 **{paper['title']}** (相似度: {paper.get('similarity', 0):.2f})")


# ============ Tab 5: 文献管理 ============
with tab5:
    st.header("📋 文献管理与报告")

    df = st.session_state.papers_df
    if df.empty:
        st.info("请先在「文献检索」中搜索文献")
    else:
        # LLM 分析
        st.subheader("🤖 AI智能分析")
        if st.button("生成文献综述报告", type="primary"):
            client = get_llm_client()
            if client:
                with st.spinner("AI正在生成文献综述报告..."):
                    # 取top10论文做综述
                    top_papers = df.head(10)
                    papers_text = ""
                    for _, p in top_papers.iterrows():
                        papers_text += f"\n标题: {p['title']}\n摘要: {str(p.get('abstract', ''))[:300]}\n"

                    try:
                        resp = client.chat.completions.create(
                            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
                            messages=[
                                {"role": "system", "content": "你是一个学术文献综述专家。请根据以下论文信息，生成一份简要的文献综述报告，包括：1)研究领域概述 2)主要研究方向和趋势 3)关键发现和贡献 4)未来研究方向建议。使用中文，保持学术风格。"},
                                {"role": "user", "content": papers_text},
                            ],
                            temperature=0.3,
                            max_tokens=2000,
                        )
                        report = resp.choices[0].message.content
                        st.markdown(report)
                    except Exception as e:
                        st.error(f"AI分析出错: {e}")
            else:
                st.warning("请配置LLM API密钥以使用AI分析功能")

        st.divider()

        # 数据导出
        st.subheader("📥 数据导出")
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("下载CSV", csv, "papers.csv", "text/csv")
        with col2:
            json_data = df.to_json(orient="records", force_ascii=False, indent=2)
            st.download_button("下载JSON", json_data, "papers.json", "application/json")

        st.divider()

        # 文献标注
        st.subheader("🏷️ 文献标注")
        selected_paper = st.selectbox("选择论文", df["title"].tolist(), key="annotate_select")
        annotation = st.text_area("添加笔记/标注", placeholder="在此输入您对这篇论文的笔记...")
        if st.button("💾 保存标注"):
            # 存储到本地
            notes_path = os.path.join(os.path.dirname(__file__), "data", "notes.json")
            notes = {}
            if os.path.exists(notes_path):
                with open(notes_path, "r", encoding="utf-8") as f:
                    notes = json.load(f)
            notes[selected_paper] = annotation
            with open(notes_path, "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            st.success("标注已保存")

        # 展示已有标注
        notes_path = os.path.join(os.path.dirname(__file__), "data", "notes.json")
        if os.path.exists(notes_path):
            with open(notes_path, "r", encoding="utf-8") as f:
                notes = json.load(f)
            if notes:
                st.subheader("📝 已有标注")
                for title, note in notes.items():
                    with st.expander(f"📄 {title[:60]}..."):
                        st.write(note)


# ============ 页脚 ============
st.divider()
st.markdown("""
<p style="text-align:center;color:gray;font-size:0.8rem;">
    智能文献分析系统 v1.0 | 基于AI大模型 | 数据来源: arXiv & Semantic Scholar
</p>
""", unsafe_allow_html=True)
