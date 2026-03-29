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
import networkx as nx
import plotly.graph_objects as go

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
from config import MODEL_NAME

# ============ 页面配置 ============
st.set_page_config(
    page_title="ScholarMind - 智能文献分析系统",
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
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 16px; border-radius: 8px; }
    .paper-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        background: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📚 ScholarMind 智能文献分析系统</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:gray;">基于AI大模型的学术文献智能分析、知识挖掘与可视化平台</p>', unsafe_allow_html=True)

# ============ Helper ============
NOTES_PATH = os.path.join(os.path.dirname(__file__), "data", "notes.json")


def load_notes() -> dict:
    if os.path.exists(NOTES_PATH):
        try:
            with open(NOTES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_notes(notes: dict):
    os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
    with open(NOTES_PATH, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def format_date(d):
    """格式化日期显示"""
    if pd.isna(d):
        return "N/A"
    try:
        return pd.Timestamp(d).strftime("%Y-%m-%d")
    except Exception:
        return str(d)


def generate_bibtex(df: pd.DataFrame) -> str:
    """生成BibTeX格式"""
    entries = []
    for i, row in df.iterrows():
        authors = row.get("authors", [])
        if isinstance(authors, list):
            author_str = " and ".join(authors)
        else:
            author_str = str(authors)
        title = row.get("title", "")
        year = row.get("year", "")
        doi = row.get("doi", "")
        # 生成cite key
        first_author = authors[0].split()[-1] if isinstance(authors, list) and authors else "unknown"
        key = f"{first_author}{int(year) if pd.notna(year) else 'xxxx'}_{i}"
        entry = f"""@article{{{key},
  title = {{{title}}},
  author = {{{author_str}}},
  year = {{{int(year) if pd.notna(year) else ''}}},
  doi = {{{doi}}},
}}"""
        entries.append(entry)
    return "\n\n".join(entries)


# ============ 初始化Session State ============
if "papers_df" not in st.session_state:
    st.session_state.papers_df = load_papers()
if "user_profile" not in st.session_state:
    st.session_state.user_profile = load_user_profile()
if "topic_result" not in st.session_state:
    st.session_state.topic_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ============ 侧边栏 ============
with st.sidebar:
    st.header("🔧 系统设置")
    data_source = st.selectbox("数据源", ["arXiv", "Semantic Scholar", "Both"])

    llm_client = get_llm_client()
    if llm_client:
        st.success("✅ LLM已连接")
    else:
        st.warning("⚠️ LLM未配置 (TF-IDF替代)")
        st.caption("在.env中配置OPENAI_API_KEY")

    st.divider()
    st.header("👤 用户画像")
    profile = st.session_state.user_profile
    if profile["interests"]:
        st.write("**研究兴趣：**")
        st.write(", ".join(profile["interests"][:10]))

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("已读", len(profile.get("read_papers", [])))
    with col_s2:
        st.metric("收藏", len(profile.get("liked_papers", [])))

    new_interest = st.text_input("添加研究兴趣")
    if st.button("添加") and new_interest:
        update_user_interests(profile, [new_interest])
        st.session_state.user_profile = profile
        st.rerun()

    st.divider()
    if not st.session_state.papers_df.empty:
        st.header("📊 数据概览")
        df_sidebar = st.session_state.papers_df
        st.metric("总文献数", len(df_sidebar))
        if "year" in df_sidebar.columns:
            valid_years = df_sidebar["year"].dropna()
            if len(valid_years) > 0:
                st.metric("时间跨度", f"{int(valid_years.min())}-{int(valid_years.max())}")
        if "citation_count" in df_sidebar.columns:
            st.metric("总引用", int(df_sidebar["citation_count"].sum()))

# ============ 主页面标签页 ============
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 文献检索", "📊 主题与趋势", "🌐 知识图谱",
    "💡 智能推荐", "🤖 AI助手", "📋 文献管理"
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

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        search_clicked = st.button("🚀 开始检索", type="primary", use_container_width=True)
    with col_btn2:
        use_llm_extract = st.checkbox("使用LLM增强提取", value=False,
                                       help="使用大模型提取关键词、研究方法等（需配置API）")

    if search_clicked:
        if query:
            with st.spinner("正在检索文献数据..."):
                papers = []
                errors = []
                if data_source in ["arXiv", "Both"]:
                    arxiv_papers = search_arxiv(query, max_results, sort_option)
                    if arxiv_papers:
                        papers.extend(arxiv_papers)
                        st.toast(f"arXiv: {len(arxiv_papers)} 篇")
                    else:
                        errors.append("arXiv检索失败或无结果")

                if data_source in ["Semantic Scholar", "Both"]:
                    s2_papers = search_semantic_scholar(query, max_results)
                    if s2_papers:
                        papers.extend(s2_papers)
                        st.toast(f"Semantic Scholar: {len(s2_papers)} 篇")
                    else:
                        errors.append("Semantic Scholar检索失败或无结果")

                if errors:
                    for err in errors:
                        st.warning(err)

                if papers:
                    df = clean_and_standardize(papers)

                    # 关键词提取
                    try:
                        if use_llm_extract and llm_client:
                            with st.spinner("LLM正在提取关键信息..."):
                                paper_dicts = df.to_dict("records")
                                enriched = batch_extract_info_llm(paper_dicts)
                                df = pd.DataFrame(enriched)
                                df["published"] = pd.to_datetime(df["published"], errors="coerce")
                                df["year"] = df["published"].dt.year
                        else:
                            kw_dict = extract_keywords_tfidf(df)
                            for i, row in df.iterrows():
                                if row["title"] in kw_dict:
                                    df.at[i, "keywords"] = kw_dict[row["title"]]
                    except Exception as e:
                        st.warning(f"关键词提取出错: {e}，使用原始关键词")

                    st.session_state.papers_df = df
                    st.session_state.topic_result = None  # 清除旧主题
                    save_papers(df)
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
        years = []
        year_range = None
        with col1:
            if "year" in df.columns:
                years = sorted(df["year"].dropna().unique())
                if len(years) >= 2:
                    year_range = st.slider("年份筛选",
                                           int(min(years)), int(max(years)),
                                           (int(min(years)), int(max(years))))
                elif len(years) == 1:
                    st.info(f"全部为 {int(years[0])} 年")
        with col2:
            title_filter = st.text_input("标题关键词过滤")

        filtered_df = df.copy()
        if year_range and len(years) >= 2:
            filtered_df = filtered_df[
                (filtered_df["year"] >= year_range[0]) & (filtered_df["year"] <= year_range[1])
            ]
        if title_filter:
            filtered_df = filtered_df[
                filtered_df["title"].str.contains(title_filter, case=False, na=False)
            ]

        # 展示表格
        display_cols = ["title", "authors", "published", "source", "citation_count"]
        available_cols = [c for c in display_cols if c in filtered_df.columns]
        show_df = filtered_df[available_cols].copy()
        if "published" in show_df.columns:
            show_df["published"] = show_df["published"].apply(format_date)

        st.dataframe(show_df.reset_index(drop=True), use_container_width=True, height=400)

        # 论文详情
        st.subheader("📖 论文详情")
        paper_titles = filtered_df["title"].tolist()
        selected_title = st.selectbox("选择论文查看详情", paper_titles)

        if selected_title:
            paper = filtered_df[filtered_df["title"] == selected_title].iloc[0]
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"### {paper['title']}")
                authors = paper.get("authors", [])
                if isinstance(authors, list):
                    st.markdown(f"**作者：** {', '.join(authors)}")
                st.markdown(f"**发表日期：** {format_date(paper.get('published'))}")
                st.markdown(f"**来源：** {paper.get('source', 'N/A')}")
                if paper.get("doi"):
                    st.markdown(f"**DOI：** {paper['doi']}")
                if paper.get("main_contribution"):
                    st.markdown(f"**核心贡献：** {paper['main_contribution']}")
                if paper.get("research_method"):
                    st.markdown(f"**研究方法：** {paper['research_method']}")
                if paper.get("research_field"):
                    st.markdown(f"**研究领域：** {paper['research_field']}")
                st.markdown("**摘要：**")
                st.markdown(paper.get("abstract", "无摘要"))

            with col2:
                st.metric("引用次数", int(paper.get("citation_count", 0)))
                keywords = paper.get("keywords", [])
                if isinstance(keywords, list) and keywords:
                    st.markdown("**关键词：**")
                    for kw in keywords[:8]:
                        st.markdown(f"` {kw} `")
                if paper.get("pdf_url"):
                    st.link_button("📄 查看原文", paper["pdf_url"])

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("📖 标记已读", key="detail_read"):
                        mark_paper_read(profile, selected_title)
                        st.toast("已标记为已读")
                        st.rerun()
                with bcol2:
                    if st.button("❤️ 收藏", key="detail_like"):
                        mark_paper_liked(profile, selected_title)
                        kws = paper.get("keywords", [])
                        if isinstance(kws, list):
                            update_user_interests(profile, kws)
                        st.toast("已收藏")
                        st.rerun()

            # ===== 引用/参考文献探索 =====
            st.divider()
            st.subheader("🔗 引用关系探索")
            ref_col1, ref_col2 = st.columns(2)

            with ref_col1:
                if st.button("📥 查看引用该论文的文献 (Citations)", use_container_width=True):
                    with st.spinner("正在获取引用数据..."):
                        paper_id = paper.get("id", "")
                        citations = get_paper_citations(paper_id)
                        if citations:
                            st.session_state.current_citations = citations
                            st.toast(f"找到 {len(citations)} 篇引用文献")
                        else:
                            st.info("未找到引用信息（可能需要Semantic Scholar ID）")

            with ref_col2:
                if st.button("📤 查看参考文献 (References)", use_container_width=True):
                    with st.spinner("正在获取参考文献..."):
                        paper_id = paper.get("id", "")
                        references = get_paper_references(paper_id)
                        if references:
                            st.session_state.current_references = references
                            st.toast(f"找到 {len(references)} 篇参考文献")
                        else:
                            st.info("未找到参考文献信息")

            # 展示引用
            if st.session_state.get("current_citations"):
                with st.expander(f"📥 引用该论文的文献 ({len(st.session_state.current_citations)} 篇)", expanded=True):
                    cit_df = pd.DataFrame(st.session_state.current_citations)
                    st.dataframe(cit_df[["title", "year", "citation_count"]].head(20),
                                 use_container_width=True)

            if st.session_state.get("current_references"):
                with st.expander(f"📤 参考文献 ({len(st.session_state.current_references)} 篇)", expanded=True):
                    ref_df = pd.DataFrame(st.session_state.current_references)
                    st.dataframe(ref_df[["title", "year", "citation_count"]].head(20),
                                 use_container_width=True)


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
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总论文数", trends["total_papers"])
            with col2:
                yr = trends.get("year_range", (0, 0))
                st.metric("时间范围", f"{yr[0]}-{yr[1]}")
            with col3:
                if trends.get("top_categories"):
                    st.metric("热门领域", trends["top_categories"][0][0])
            with col4:
                if "citation_count" in df.columns:
                    st.metric("平均引用", f"{df['citation_count'].mean():.1f}")

            trend_col1, trend_col2 = st.columns(2)
            with trend_col1:
                if trends.get("yearly_counts"):
                    st.plotly_chart(plot_yearly_trend(trends["yearly_counts"]),
                                   use_container_width=True)
            with trend_col2:
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
                try:
                    if method == "LDA":
                        result = topic_modeling_lda(df, n_topics)
                    else:
                        result = topic_modeling_tfidf_kmeans(df, n_topics)
                    st.session_state.topic_result = result
                except Exception as e:
                    st.error(f"主题建模失败: {e}")

        if st.session_state.topic_result:
            result = st.session_state.topic_result
            topics = result["topics"]

            # 主题分布饼图 + 散点图
            topic_col1, topic_col2 = st.columns(2)
            with topic_col1:
                st.plotly_chart(plot_topic_distribution(topics), use_container_width=True)
            with topic_col2:
                if "df" in result:
                    st.plotly_chart(plot_topic_scatter(result["df"]), use_container_width=True)

            # 主题关键词
            for topic_name, topic_data in topics.items():
                with st.expander(f"📌 {topic_name}: {', '.join(topic_data['top_words'][:5])}"):
                    st.write(", ".join(topic_data["top_words"]))

        st.divider()

        # 关键词分析 - 词云 + 柱状图 + 热力图
        st.subheader("🔑 关键词分析")
        kw_col1, kw_col2 = st.columns(2)
        with kw_col1:
            st.plotly_chart(plot_keyword_bar(df), use_container_width=True)
        with kw_col2:
            # 词云
            cloud_data = plot_keyword_cloud_data(df)
            if cloud_data:
                try:
                    from streamlit_echarts import st_echarts
                    wordcloud_option = {
                        "tooltip": {},
                        "series": [{
                            "type": "wordCloud",
                            "gridSize": 8,
                            "sizeRange": [12, 60],
                            "rotationRange": [-45, 45],
                            "shape": "circle",
                            "textStyle": {
                                "fontFamily": "sans-serif",
                                "fontWeight": "bold",
                            },
                            "data": cloud_data[:40],
                        }]
                    }
                    st_echarts(wordcloud_option, height="400px")
                except ImportError:
                    # fallback: 用matplotlib词云
                    try:
                        from wordcloud import WordCloud
                        import matplotlib.pyplot as plt
                        freq = {d["name"]: d["value"] for d in cloud_data}
                        wc = WordCloud(width=600, height=400, background_color="white").generate_from_frequencies(freq)
                        fig_wc, ax_wc = plt.subplots(figsize=(8, 5))
                        ax_wc.imshow(wc, interpolation="bilinear")
                        ax_wc.axis("off")
                        st.pyplot(fig_wc)
                    except Exception:
                        st.info("安装 streamlit-echarts 或 wordcloud 以显示词云")

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
                    authors = p.get("authors", [])
                    if isinstance(authors, list):
                        authors = ", ".join(authors[:3])
                    st.markdown(f"- 📄 **{p['title']}** | {authors} | 引用: {p.get('citation_count', 0)}")
        else:
            st.info("数据不足以进行热点分析")


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

            if G.number_of_nodes() > 0:
                max_display = st.slider("最大显示节点数", 10, 200, 50)

                if G.number_of_nodes() > max_display:
                    top_nodes = sorted(G.nodes, key=lambda n: G.degree(n), reverse=True)[:max_display]
                    subG = G.subgraph(top_nodes)
                else:
                    subG = G

                # 尝试使用 streamlit-agraph
                use_agraph = False
                try:
                    from streamlit_agraph import agraph, Node, Edge, Config
                    use_agraph = True
                except ImportError:
                    pass

                if use_agraph and subG.number_of_nodes() <= 100:
                    # 交互式图谱
                    nodes = []
                    edges = []
                    color_map = {"paper": "#4A90D9", "author": "#E74C3C", "keyword": "#2ECC71"}
                    for node in subG.nodes:
                        ntype = subG.nodes[node].get("type", "")
                        color = color_map.get(ntype, f"hsl({hash(node) % 360}, 60%, 50%)")
                        size = min(10 + subG.degree(node) * 3, 40)
                        label = str(node)[:25]
                        nodes.append(Node(id=str(node), label=label, size=size, color=color,
                                         title=f"{node}\n度: {subG.degree(node)}"))
                    for u, v, data in subG.edges(data=True):
                        weight = data.get("weight", 1)
                        edges.append(Edge(source=str(u), target=str(v), width=min(weight, 5)))

                    config = Config(
                        width=800, height=600, directed=False,
                        physics=True, hierarchical=False,
                        nodeHighlightBehavior=True,
                        highlightColor="#F7A7A6",
                    )
                    agraph(nodes=nodes, edges=edges, config=config)

                    # 图例
                    if st.session_state.get("graph_type") == "knowledge":
                        st.markdown("**图例：** 🔵 论文 | 🔴 作者 | 🟢 关键词")
                else:
                    # Plotly fallback
                    pos = nx.spring_layout(subG, seed=42, k=2/np.sqrt(max(subG.number_of_nodes(), 1)))

                    edge_x, edge_y = [], []
                    for u, v in subG.edges():
                        x0, y0 = pos[u]
                        x1, y1 = pos[v]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])

                    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode="lines",
                                            line=dict(width=0.5, color="#888"), hoverinfo="none")

                    node_x = [pos[n][0] for n in subG.nodes()]
                    node_y = [pos[n][1] for n in subG.nodes()]
                    node_text = list(subG.nodes())
                    node_size = [min(5 + subG.degree(n) * 2, 30) for n in subG.nodes()]

                    if st.session_state.get("graph_type") == "knowledge":
                        cmap = {"paper": "blue", "author": "red", "keyword": "green"}
                        node_color = [cmap.get(subG.nodes[n].get("type", ""), "gray") for n in subG.nodes()]
                        showscale = False
                    else:
                        node_color = [subG.degree(n) for n in subG.nodes()]
                        showscale = True

                    node_trace = go.Scatter(
                        x=node_x, y=node_y, mode="markers+text",
                        text=[n[:20] for n in node_text], textposition="top center",
                        textfont=dict(size=8),
                        marker=dict(size=node_size, color=node_color,
                                    colorscale="YlOrRd" if showscale else None,
                                    showscale=showscale,
                                    line=dict(width=1, color="white")),
                        hovertext=node_text, hoverinfo="text",
                    )

                    fig = go.Figure(data=[edge_trace, node_trace])
                    fig.update_layout(
                        title=f"🌐 {graph_type}",
                        showlegend=False,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=600, template="plotly_white",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # 网络统计
                st.subheader("📊 网络统计")
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    degrees = dict(subG.degree())
                    top_deg = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
                    st.markdown("**核心节点 (度中心性)：**")
                    for node, deg in top_deg:
                        st.markdown(f"- {str(node)[:30]}: {deg}")
                with stat_col2:
                    st.metric("网络密度", f"{nx.density(subG):.4f}")
                    if not nx.is_directed(subG):
                        components = nx.number_connected_components(subG)
                        st.metric("连通分量数", components)
                with stat_col3:
                    if subG.number_of_nodes() > 2:
                        try:
                            with st.spinner("计算介数中心性..."):
                                betweenness = nx.betweenness_centrality(subG)
                            top_between = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
                            st.markdown("**桥梁节点 (介数中心性)：**")
                            for node, bc in top_between:
                                st.markdown(f"- {str(node)[:30]}: {bc:.3f}")
                        except Exception:
                            pass

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
                score = paper.get('relevance_score', 0)
                score_str = f" (相关度: {score:.2f})" if score > 0 else ""
                with st.expander(f"📄 {i+1}. {paper['title']}{score_str}"):
                    authors = paper.get("authors", [])
                    if isinstance(authors, list):
                        st.markdown(f"**作者：** {', '.join(authors[:5])}")
                    st.markdown(f"**发表日期：** {format_date(paper.get('published'))}")
                    st.markdown(f"**摘要：** {str(paper.get('abstract', ''))[:300]}...")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📖 标记已读", key=f"rec_read_{i}"):
                            mark_paper_read(profile, paper["title"])
                            st.toast("已标记已读")
                            st.rerun()
                    with col2:
                        if st.button("❤️ 收藏", key=f"rec_like_{i}"):
                            mark_paper_liked(profile, paper["title"])
                            st.toast("已收藏")
                            st.rerun()

        st.divider()

        # 相似论文推荐
        st.subheader("🔗 相似论文推荐")
        selected = st.selectbox("选择一篇论文，查找相似文献", df["title"].tolist(), key="sim_select")
        if st.button("查找相似论文"):
            with st.spinner("计算相似度..."):
                similar = similar_paper_recommend(df, selected, top_n=5)
                st.session_state.similar_papers = similar

        if "similar_papers" in st.session_state:
            for _, paper in st.session_state.similar_papers.iterrows():
                sim_score = paper.get('similarity', 0)
                st.markdown(f"- 📄 **{paper['title']}** (相似度: {sim_score:.2f})")


# ============ Tab 5: AI助手（新增） ============
with tab5:
    st.header("🤖 AI文献助手")

    df = st.session_state.papers_df

    if df.empty:
        st.info("请先在「文献检索」中搜索文献")
    else:
        ai_tab1, ai_tab2, ai_tab3 = st.tabs(["💬 论文问答", "📝 文献综述", "🔍 结构化提取"])

        # === 论文问答 ===
        with ai_tab1:
            st.subheader("💬 与论文对话")
            st.caption("基于已检索文献的内容，向AI提问获取洞察")

            # 展示历史
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_question = st.chat_input("输入您的问题，如：这些论文主要使用了哪些研究方法？")
            if user_question:
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                with st.chat_message("user"):
                    st.markdown(user_question)

                client = get_llm_client()
                if client:
                    # 找最相关的论文作为上下文
                    try:
                        from sklearn.feature_extraction.text import TfidfVectorizer
                        from sklearn.metrics.pairwise import cosine_similarity as cos_sim
                        texts = (df["title"].fillna("") + " " + df["abstract"].fillna("")).tolist()
                        all_texts = [user_question] + texts
                        vec = TfidfVectorizer(max_features=500, stop_words="english")
                        mat = vec.fit_transform(all_texts)
                        sims = cos_sim(mat[0:1], mat[1:]).flatten()
                        top_idx = sims.argsort()[-8:][::-1]
                        context_papers = df.iloc[top_idx]
                    except Exception:
                        context_papers = df.head(8)

                    context = ""
                    for idx, (_, p) in enumerate(context_papers.iterrows()):
                        context += f"\n[论文{idx+1}] {p['title']}\n摘要: {str(p.get('abstract', ''))[:400]}\n"

                    with st.chat_message("assistant"):
                        with st.spinner("AI思考中..."):
                            try:
                                resp = client.chat.completions.create(
                                    model=MODEL_NAME,
                                    messages=[
                                        {"role": "system", "content": f"""你是一个学术文献分析助手。根据以下论文信息回答用户的问题。
回答时请引用具体论文编号[论文X]，使答案有据可查。使用中文回答。

相关论文：
{context}"""},
                                        {"role": "user", "content": user_question},
                                    ],
                                    temperature=0.3,
                                    max_tokens=1500,
                                )
                                answer = resp.choices[0].message.content
                                st.markdown(answer)
                                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                            except Exception as e:
                                st.error(f"AI回答出错: {e}")
                else:
                    with st.chat_message("assistant"):
                        st.warning("请配置LLM API密钥以使用问答功能")

            if st.button("🗑️ 清除对话历史"):
                st.session_state.chat_history = []
                st.rerun()

        # === 文献综述 ===
        with ai_tab2:
            st.subheader("📝 AI生成文献综述")
            review_scope = st.slider("综述论文数量", 5, min(30, len(df)), min(10, len(df)))

            if st.button("生成文献综述报告", type="primary", key="gen_review"):
                client = get_llm_client()
                if client:
                    with st.spinner("AI正在生成文献综述报告..."):
                        top_papers = df.head(review_scope)
                        papers_text = ""
                        for _, p in top_papers.iterrows():
                            papers_text += f"\n标题: {p['title']}\n摘要: {str(p.get('abstract', ''))[:300]}\n"
                        try:
                            resp = client.chat.completions.create(
                                model=MODEL_NAME,
                                messages=[
                                    {"role": "system", "content": """你是一个学术文献综述专家。请根据以下论文信息，生成一份详细的文献综述报告，包括：
1. 研究领域概述
2. 主要研究方向和方法分类
3. 关键发现和贡献总结
4. 研究趋势和热点分析
5. 当前研究不足与未来方向建议

使用中文，保持学术风格，结构清晰。"""},
                                    {"role": "user", "content": papers_text},
                                ],
                                temperature=0.3,
                                max_tokens=3000,
                            )
                            report = resp.choices[0].message.content
                            st.markdown(report)
                            st.download_button("📥 下载报告", report, "literature_review.md", "text/markdown")
                        except Exception as e:
                            st.error(f"AI分析出错: {e}")
                else:
                    st.warning("请配置LLM API密钥")

        # === 结构化提取 ===
        with ai_tab3:
            st.subheader("🔍 结构化信息提取")
            st.caption("让AI从论文中提取自定义字段，生成结构化对比表")

            default_fields = "研究方法, 数据集, 关键发现, 局限性"
            custom_fields = st.text_input("自定义提取字段（逗号分隔）", value=default_fields)
            extract_count = st.slider("提取论文数", 3, min(20, len(df)), min(10, len(df)))

            if st.button("🔬 开始结构化提取", type="primary", key="struct_extract"):
                client = get_llm_client()
                if client:
                    with st.spinner("AI正在提取结构化信息..."):
                        fields = [f.strip() for f in custom_fields.split(",")]
                        top_papers = df.head(extract_count)
                        all_results = []

                        for _, p in top_papers.iterrows():
                            try:
                                resp = client.chat.completions.create(
                                    model=MODEL_NAME,
                                    messages=[
                                        {"role": "system", "content": f"""从论文信息中提取以下字段: {', '.join(fields)}
以JSON对象格式返回，只返回JSON，不要其他内容。如果无法确定某个字段，填"未知"。"""},
                                        {"role": "user", "content": f"标题: {p['title']}\n摘要: {str(p.get('abstract', ''))[:500]}"},
                                    ],
                                    temperature=0.1,
                                    max_tokens=500,
                                )
                                text = resp.choices[0].message.content.strip()
                                import re
                                match = re.search(r"\{.*\}", text, re.DOTALL)
                                if match:
                                    extracted = json.loads(match.group())
                                    extracted["论文标题"] = p["title"]
                                    all_results.append(extracted)
                            except Exception:
                                all_results.append({"论文标题": p["title"], **{f: "提取失败" for f in fields}})

                        if all_results:
                            result_df = pd.DataFrame(all_results)
                            cols = ["论文标题"] + [c for c in result_df.columns if c != "论文标题"]
                            st.dataframe(result_df[cols], use_container_width=True)
                            csv = result_df[cols].to_csv(index=False).encode("utf-8")
                            st.download_button("📥 下载提取结果", csv, "extracted_info.csv", "text/csv")
                else:
                    st.warning("请配置LLM API密钥")


# ============ Tab 6: 文献管理 ============
with tab6:
    st.header("📋 文献管理与导出")

    df = st.session_state.papers_df
    if df.empty:
        st.info("请先在「文献检索」中搜索文献")
    else:
        # 数据导出
        st.subheader("📥 数据导出")
        col1, col2, col3 = st.columns(3)
        with col1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📄 下载CSV", csv, "papers.csv", "text/csv", use_container_width=True)
        with col2:
            json_data = df.to_json(orient="records", force_ascii=False, indent=2)
            st.download_button("📋 下载JSON", json_data, "papers.json", "application/json", use_container_width=True)
        with col3:
            bibtex = generate_bibtex(df)
            st.download_button("📚 下载BibTeX", bibtex, "papers.bib", "text/plain", use_container_width=True)

        st.divider()

        # 文献标注
        st.subheader("🏷️ 文献标注")
        notes = load_notes()
        selected_paper = st.selectbox("选择论文", df["title"].tolist(), key="annotate_select")

        # 如果已有标注，预填
        existing_note = notes.get(selected_paper, "")
        annotation = st.text_area("添加笔记/标注", value=existing_note,
                                  placeholder="在此输入您对这篇论文的笔记...")

        note_col1, note_col2 = st.columns(2)
        with note_col1:
            if st.button("💾 保存标注", use_container_width=True):
                if annotation.strip():
                    notes[selected_paper] = annotation
                    save_notes(notes)
                    st.success("标注已保存")
                else:
                    st.warning("标注内容不能为空")
        with note_col2:
            if existing_note and st.button("🗑️ 删除标注", use_container_width=True):
                notes.pop(selected_paper, None)
                save_notes(notes)
                st.success("标注已删除")
                st.rerun()

        # 展示已有标注
        if notes:
            st.subheader("📝 已有标注")
            for title, note in notes.items():
                display_title = title if len(title) <= 60 else title[:60] + "..."
                with st.expander(f"📄 {display_title}"):
                    st.write(note)

        st.divider()

        # 数据统计面板
        st.subheader("📊 数据统计")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("总论文数", len(df))
        with stat_col2:
            st.metric("来源数", df["source"].nunique() if "source" in df.columns else 0)
        with stat_col3:
            unique_authors = set()
            for a in df["authors"]:
                if isinstance(a, list):
                    unique_authors.update(a)
            st.metric("独立作者数", len(unique_authors))
        with stat_col4:
            st.metric("总引用", int(df["citation_count"].sum()) if "citation_count" in df.columns else 0)


# ============ 页脚 ============
st.divider()
st.markdown("""
<p style="text-align:center;color:gray;font-size:0.8rem;">
    ScholarMind v2.0 | 基于AI大模型 | 数据来源: arXiv & Semantic Scholar
</p>
""", unsafe_allow_html=True)
