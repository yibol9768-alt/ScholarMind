"""
ScholarMind — 智能文献分析系统
NiceGUI + Vue/Quasar 现代前端
"""

import os, sys, json, re
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
import networkx as nx
from nicegui import ui, app
import plotly.graph_objects as go

from modules.data_collector import (
    search_openalex, search_arxiv, search_semantic_scholar,
    clean_and_standardize, save_papers, load_papers,
    get_paper_citations, get_paper_references,
)
from modules.info_extractor import (
    extract_keywords_tfidf, batch_extract_info_llm,
    build_knowledge_graph, build_author_collaboration_network, get_llm_client,
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
from config import MODEL_NAME

# ============================================================
#  State
# ============================================================
state = {
    "papers_df": load_papers(),
    "profile": load_user_profile(),
    "topic_result": None,
    "chat_history": [],
}


def fmt_date(d):
    if pd.isna(d): return ""
    try: return pd.Timestamp(d).strftime("%Y-%m-%d")
    except: return str(d)


def gen_bibtex(df):
    entries = []
    for i, row in df.iterrows():
        authors = row.get("authors", [])
        astr = " and ".join(authors) if isinstance(authors, list) else str(authors)
        fa = authors[0].split()[-1] if isinstance(authors, list) and authors else "unknown"
        yr = int(row["year"]) if pd.notna(row.get("year")) else "xxxx"
        entries.append(f"@article{{{fa}{yr}_{i},\n  title = {{{row.get('title','')}}},\n  author = {{{astr}}},\n  year = {{{yr}}},\n  doi = {{{row.get('doi','')}}},\n}}")
    return "\n\n".join(entries)


NOTES_PATH = os.path.join(os.path.dirname(__file__), "data", "notes.json")
def load_notes():
    if os.path.exists(NOTES_PATH):
        try:
            with open(NOTES_PATH, "r") as f: return json.load(f)
        except: return {}
    return {}
def save_notes(notes):
    os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
    with open(NOTES_PATH, "w") as f: json.dump(notes, f, ensure_ascii=False, indent=2)


def apple_layout(fig, title="", h=400):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family="Inter, -apple-system, sans-serif", color="#1d1d1f")),
        font=dict(family="Inter, -apple-system, sans-serif", color="#6e6e73", size=12),
        plot_bgcolor="#fff", paper_bgcolor="#fff", height=h,
        margin=dict(l=40, r=20, t=45, b=40),
        xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"),
        colorway=["#0071e3","#34c759","#ff9500","#af52de","#ff3b30","#5ac8fa","#ffcc00"],
    )
    return fig


# ============================================================
#  Global CSS
# ============================================================
ui.add_head_html(shared=True, code="""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; background: #f5f5f7 !important; }
.q-page { background: #f5f5f7 !important; }
.q-card { border-radius: 18px !important; border: 1px solid #e8e8ed !important; box-shadow: 0 2px 16px rgba(0,0,0,0.04) !important; }
.q-card:hover { box-shadow: 0 4px 24px rgba(0,0,0,0.08) !important; }
.q-tab { border-radius: 10px !important; font-weight: 500 !important; letter-spacing: -0.01em; }
.q-tab--active { background: #0071e3 !important; color: white !important; border-radius: 10px !important; }
.q-btn { border-radius: 980px !important; font-weight: 600 !important; letter-spacing: -0.005em; text-transform: none !important; }
.q-input .q-field__control, .q-select .q-field__control { border-radius: 12px !important; }
.q-expansion-item { border-radius: 14px !important; }
.stat-pill { background: #fff; border-radius: 14px; padding: 20px 24px; text-align: center; border: 1px solid #e8e8ed; }
.stat-num { font-size: 2rem; font-weight: 700; color: #1d1d1f; letter-spacing: -0.03em; }
.stat-label { font-size: 0.75rem; color: #86868b; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }
.paper-card { background: #fff; border-radius: 14px; padding: 16px 20px; margin-bottom: 8px; border: 1px solid #e8e8ed; transition: all 0.2s; cursor: pointer; }
.paper-card:hover { border-color: #0071e3; box-shadow: 0 2px 12px rgba(0,113,227,0.08); }
.paper-title { font-size: 0.95rem; font-weight: 600; color: #1d1d1f; line-height: 1.4; }
.paper-meta { font-size: 0.78rem; color: #86868b; margin-top: 4px; }
.paper-abstract { font-size: 0.82rem; color: #6e6e73; line-height: 1.6; margin-top: 6px; }
.tag { display: inline-block; background: #f5f5f7; color: #6e6e73; border-radius: 980px; padding: 2px 10px; font-size: 0.7rem; font-weight: 500; margin: 2px; border: 1px solid #e8e8ed; }
.tag-blue { background: rgba(0,113,227,0.06); color: #0071e3; border-color: rgba(0,113,227,0.12); }
.hero { text-align: center; padding: 40px 0 20px; }
.hero h1 { font-size: 2.8rem; font-weight: 700; color: #1d1d1f; letter-spacing: -0.03em; margin: 0; }
.hero p { font-size: 1.15rem; color: #86868b; margin-top: 6px; font-weight: 400; }
.section-title { font-size: 1.6rem; font-weight: 700; color: #1d1d1f; letter-spacing: -0.02em; margin: 30px 0 8px; }
.section-sub { font-size: 0.9rem; color: #86868b; margin-bottom: 20px; }
.chat-user { background: #0071e3; color: white; border-radius: 18px 18px 4px 18px; padding: 10px 16px; margin: 6px 0; max-width: 80%; margin-left: auto; }
.chat-ai { background: #fff; color: #1d1d1f; border-radius: 18px 18px 18px 4px; padding: 10px 16px; margin: 6px 0; max-width: 80%; border: 1px solid #e8e8ed; }
</style>
""")


# ============================================================
#  Main Page
# ============================================================
@ui.page("/")
def main_page():
    df = state["papers_df"]
    profile = state["profile"]

    # Hero
    ui.html('<div class="hero"><h1>ScholarMind</h1><p>AI-Powered Academic Literature Analysis</p></div>')

    # Stats
    if not df.empty:
        unique_authors = set()
        for a in df["authors"]:
            if isinstance(a, list): unique_authors.update(a)
        total_cites = int(df["citation_count"].sum()) if "citation_count" in df.columns else 0

        with ui.row().classes("w-full gap-4 justify-center mb-6"):
            for val, label in [(len(df), "Papers"), (len(unique_authors), "Authors"), (total_cites, "Citations"), (len(profile.get("liked_papers",[])), "Saved")]:
                ui.html(f'<div class="stat-pill" style="min-width:150px"><div class="stat-num">{val}</div><div class="stat-label">{label}</div></div>')

    # Tabs
    with ui.tabs().classes("w-full").props("no-caps dense inline-label") as tabs:
        search_tab = ui.tab("Search").props("icon=search")
        topics_tab = ui.tab("Topics").props("icon=analytics")
        graph_tab = ui.tab("Graph").props("icon=hub")
        rec_tab = ui.tab("Recommend").props("icon=recommend")
        ai_tab = ui.tab("AI Assistant").props("icon=smart_toy")
        lib_tab = ui.tab("Library").props("icon=library_books")

    with ui.tab_panels(tabs, value=search_tab).classes("w-full"):

        # ==================== SEARCH ====================
        with ui.tab_panel(search_tab):
            with ui.card().classes("w-full"):
                ui.html('<div class="section-title" style="margin-top:0">Discover Research</div><div class="section-sub">Search 250M+ papers from OpenAlex, arXiv, and Semantic Scholar</div>')

                with ui.row().classes("w-full items-center gap-3"):
                    search_input = ui.input(placeholder="e.g. diffusion model, transformer, LLM...").classes("flex-grow")
                    source_select = ui.select(["OpenAlex", "arXiv", "Semantic Scholar", "All"], value="OpenAlex").classes("w-40")
                    max_input = ui.number(value=30, min=5, max=200, step=5).classes("w-24").props("label=Max")

                results_container = ui.column().classes("w-full")
                detail_container = ui.column().classes("w-full")

                async def do_search():
                    if not search_input.value:
                        ui.notify("Please enter search keywords", type="warning")
                        return

                    results_container.clear()
                    detail_container.clear()
                    q = search_input.value
                    src = source_select.value
                    mx = int(max_input.value)

                    with results_container:
                        spinner = ui.spinner("dots", size="lg")

                    papers = []
                    if src in ["OpenAlex", "All"]:
                        papers.extend(search_openalex(q, mx))
                    if src in ["arXiv", "All"]:
                        papers.extend(search_arxiv(q, mx))
                    if src in ["Semantic Scholar", "All"]:
                        papers.extend(search_semantic_scholar(q, mx))

                    results_container.clear()

                    if not papers:
                        with results_container:
                            ui.html('<div style="text-align:center;padding:40px;color:#86868b">No papers found. Try different keywords.</div>')
                        return

                    new_df = clean_and_standardize(papers)
                    # TF-IDF keywords
                    try:
                        kw_dict = extract_keywords_tfidf(new_df)
                        for i, row in new_df.iterrows():
                            if row["title"] in kw_dict:
                                new_df.at[i, "keywords"] = kw_dict[row["title"]]
                    except: pass

                    state["papers_df"] = new_df
                    state["topic_result"] = None
                    save_papers(new_df)
                    add_search_history(profile, q)

                    ui.notify(f"Found {len(new_df)} papers", type="positive")
                    render_results(new_df)

                def render_results(rdf):
                    results_container.clear()
                    with results_container:
                        ui.html(f'<div class="section-title">Results ({len(rdf)} papers)</div>')
                        for _, p in rdf.head(50).iterrows():
                            authors = p.get("authors", [])
                            a_str = ", ".join(authors[:3]) if isinstance(authors, list) else ""
                            if isinstance(authors, list) and len(authors) > 3:
                                a_str += f" +{len(authors)-3}"
                            cites = int(p.get("citation_count", 0))
                            kws = p.get("keywords", [])
                            tags = ""
                            if isinstance(kws, list):
                                tags = "".join([f'<span class="tag">{k}</span>' for k in kws[:4]])

                            ui.html(f"""<div class="paper-card" onclick="this.style.borderColor='#0071e3'">
                                <div class="paper-title">{p['title']}</div>
                                <div class="paper-meta">{a_str} · {fmt_date(p.get('published'))} · {cites} citations</div>
                                <div class="paper-abstract">{str(p.get('abstract',''))[:200]}{'...' if len(str(p.get('abstract',''))) > 200 else ''}</div>
                                <div style="margin-top:6px">{tags}</div>
                            </div>""")

                with ui.row().classes("w-full mt-2"):
                    ui.button("Search", on_click=do_search, icon="search").props("color=primary unelevated").classes("flex-grow")

                # Show existing results
                if not df.empty:
                    render_results(df)

        # ==================== TOPICS ====================
        with ui.tab_panel(topics_tab):
            topics_content = ui.column().classes("w-full")

            def render_topics():
                topics_content.clear()
                df = state["papers_df"]
                if df.empty:
                    with topics_content:
                        ui.html('<div style="text-align:center;padding:60px;color:#86868b">Search for papers first</div>')
                    return

                with topics_content:
                    # Trends
                    trends = trend_analysis(df)
                    if trends and trends.get("yearly_counts"):
                        ui.html('<div class="section-title">Publishing Trends</div>')
                        with ui.row().classes("w-full gap-4"):
                            with ui.card().classes("flex-grow"):
                                from modules.visualizer import plot_yearly_trend
                                fig = plot_yearly_trend(trends["yearly_counts"])
                                apple_layout(fig, "Papers per Year")
                                ui.plotly(fig)
                            if trends.get("yearly_citations"):
                                with ui.card().classes("flex-grow"):
                                    from modules.visualizer import plot_citation_trend
                                    fig2 = plot_citation_trend(trends["yearly_citations"])
                                    apple_layout(fig2, "Citation Trends")
                                    ui.plotly(fig2)

                    # Topic modeling
                    ui.html('<div class="section-title">Topic Modeling</div>')
                    with ui.card().classes("w-full"):
                        with ui.row().classes("items-center gap-4"):
                            method_sel = ui.select(["LDA", "TF-IDF + KMeans"], value="LDA").classes("w-48")
                            n_slider = ui.slider(min=2, max=10, value=5).classes("flex-grow")
                            ui.label().bind_text_from(n_slider, "value", lambda v: f"{int(v)} topics")

                            def run_topics():
                                try:
                                    if method_sel.value == "LDA":
                                        result = topic_modeling_lda(df, int(n_slider.value))
                                    else:
                                        result = topic_modeling_tfidf_kmeans(df, int(n_slider.value))
                                    state["topic_result"] = result
                                    ui.notify("Topic analysis complete", type="positive")
                                    render_topic_results()
                                except Exception as e:
                                    ui.notify(f"Error: {e}", type="negative")

                            ui.button("Analyze", on_click=run_topics, icon="analytics").props("color=primary unelevated")

                    topic_results_area = ui.column().classes("w-full")

                    def render_topic_results():
                        topic_results_area.clear()
                        result = state.get("topic_result")
                        if not result: return
                        topics = result["topics"]
                        with topic_results_area:
                            if "df" in result:
                                with ui.card().classes("w-full"):
                                    from modules.visualizer import plot_topic_scatter
                                    fig = plot_topic_scatter(result["df"])
                                    apple_layout(fig, "Topic Clusters", 450)
                                    ui.plotly(fig)

                            for tn, td in topics.items():
                                tags = " ".join([f'<span class="tag tag-blue">{w}</span>' for w in td["top_words"]])
                                ui.html(f'<div class="paper-card"><div class="paper-title">{tn}</div><div style="margin-top:8px">{tags}</div></div>')

                    if state.get("topic_result"):
                        render_topic_results()

                    # Keywords
                    ui.html('<div class="section-title">Keyword Analysis</div>')
                    with ui.row().classes("w-full gap-4"):
                        with ui.card().classes("flex-grow"):
                            from modules.visualizer import plot_keyword_bar
                            fig = plot_keyword_bar(df)
                            apple_layout(fig, "Top Keywords")
                            ui.plotly(fig)
                        if trends and trends.get("keyword_trends"):
                            with ui.card().classes("flex-grow"):
                                from modules.visualizer import plot_keyword_trend_heatmap
                                fig = plot_keyword_trend_heatmap(trends["keyword_trends"])
                                apple_layout(fig, "Keyword Trends")
                                ui.plotly(fig)

                    # Hot topics
                    hot = identify_hot_topics(df)
                    if hot and hot.get("hot_keywords"):
                        ui.html(f'<div class="section-title">Hot Topics ({hot.get("period","")})</div>')
                        tags = " ".join([f'<span class="tag tag-blue">{k} ({v})</span>' for k, v in hot["hot_keywords"][:15]])
                        ui.html(f'<div class="paper-card">{tags}</div>')

            render_topics()

        # ==================== GRAPH ====================
        with ui.tab_panel(graph_tab):
            graph_content = ui.column().classes("w-full")

            def render_graph():
                graph_content.clear()
                df = state["papers_df"]
                if df.empty:
                    with graph_content:
                        ui.html('<div style="text-align:center;padding:60px;color:#86868b">Search for papers first</div>')
                    return

                with graph_content:
                    ui.html('<div class="section-title">Knowledge Graph</div><div class="section-sub">Explore relationships between papers, authors, and keywords</div>')

                    with ui.card().classes("w-full"):
                        with ui.row().classes("items-center gap-4"):
                            graph_sel = ui.select(["Author Collaboration", "Keyword Co-occurrence", "Paper-Author-Keyword"], value="Author Collaboration").classes("flex-grow")
                            max_nodes = ui.number(value=50, min=10, max=200, step=10).classes("w-28").props("label=Nodes")

                            graph_plot_area = ui.column().classes("w-full")

                            def build_graph():
                                gt = graph_sel.value
                                mn = int(max_nodes.value)

                                if gt == "Author Collaboration":
                                    G = build_author_collaboration_network(df)
                                elif gt == "Paper-Author-Keyword":
                                    G = build_knowledge_graph(df)
                                else:
                                    G = nx.Graph()
                                    for _, row in df.iterrows():
                                        kws = row.get("keywords", [])
                                        if isinstance(kws, str): kws = [k.strip() for k in kws.split(",")]
                                        if isinstance(kws, list):
                                            for i in range(len(kws)):
                                                for j in range(i+1, len(kws)):
                                                    if kws[i] and kws[j]:
                                                        if G.has_edge(kws[i], kws[j]): G[kws[i]][kws[j]]["weight"] += 1
                                                        else: G.add_edge(kws[i], kws[j], weight=1)

                                if G.number_of_nodes() == 0:
                                    ui.notify("Empty graph", type="warning")
                                    return

                                # Subgraph
                                if G.number_of_nodes() > mn:
                                    top = sorted(G.nodes, key=lambda n: G.degree(n), reverse=True)[:mn]
                                    subG = G.subgraph(top)
                                else:
                                    subG = G

                                pos = nx.spring_layout(subG, seed=42, k=2/np.sqrt(max(subG.number_of_nodes(),1)))

                                # Plotly
                                edge_x, edge_y = [], []
                                for u, v in subG.edges():
                                    x0, y0 = pos[u]; x1, y1 = pos[v]
                                    edge_x.extend([x0, x1, None]); edge_y.extend([y0, y1, None])

                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=0.4, color="#d2d2d7"), hoverinfo="none"))

                                cmap = {"paper":"#0071e3", "author":"#ff3b30", "keyword":"#34c759"}
                                nx_list = list(subG.nodes())
                                fig.add_trace(go.Scatter(
                                    x=[pos[n][0] for n in nx_list], y=[pos[n][1] for n in nx_list],
                                    mode="markers+text",
                                    text=[str(n)[:18] for n in nx_list], textposition="top center",
                                    textfont=dict(size=8, color="#1d1d1f"),
                                    marker=dict(
                                        size=[min(6+subG.degree(n)*2,28) for n in nx_list],
                                        color=[cmap.get(subG.nodes[n].get("type",""), "#86868b") for n in nx_list],
                                        line=dict(width=1, color="white")),
                                    hovertext=[f"{n} ({subG.degree(n)})" for n in nx_list], hoverinfo="text"))

                                apple_layout(fig, gt, 550)
                                fig.update_layout(
                                    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                                    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                                    showlegend=False)

                                graph_plot_area.clear()
                                with graph_plot_area:
                                    ui.plotly(fig).classes("w-full")

                                    with ui.row().classes("w-full gap-4 mt-4 justify-center"):
                                        for val, lbl in [(subG.number_of_nodes(), "Nodes"), (subG.number_of_edges(), "Edges"), (f"{nx.density(subG):.3f}", "Density")]:
                                            ui.html(f'<div class="stat-pill" style="min-width:100px"><div class="stat-num" style="font-size:1.4rem">{val}</div><div class="stat-label">{lbl}</div></div>')

                                    # Top nodes
                                    degrees = sorted(dict(subG.degree()).items(), key=lambda x: x[1], reverse=True)[:8]
                                    tags = " ".join([f'<span class="tag">{str(n)[:25]} ({d})</span>' for n, d in degrees])
                                    ui.html(f'<div style="margin-top:16px"><b>Key Nodes:</b> {tags}</div>')

                                ui.notify(f"Graph: {subG.number_of_nodes()} nodes, {subG.number_of_edges()} edges", type="positive")

                            ui.button("Build Graph", on_click=build_graph, icon="hub").props("color=primary unelevated")

            render_graph()

        # ==================== RECOMMEND ====================
        with ui.tab_panel(rec_tab):
            rec_content = ui.column().classes("w-full")

            def render_rec():
                rec_content.clear()
                df = state["papers_df"]
                if df.empty:
                    with rec_content:
                        ui.html('<div style="text-align:center;padding:60px;color:#86868b">Search for papers first</div>')
                    return

                with rec_content:
                    ui.html('<div class="section-title">Recommended For You</div>')

                    interests = profile.get("interests", [])
                    if interests:
                        tags = " ".join([f'<span class="tag tag-blue">{k}</span>' for k in interests[:12]])
                        ui.html(f'<div class="paper-card"><b>Your Interests:</b><div style="margin-top:6px">{tags}</div></div>')

                    rec_area = ui.column().classes("w-full")

                    def get_recs():
                        rec_area.clear()
                        recs = content_based_recommend(df, profile, top_n=10)
                        with rec_area:
                            for _, p in recs.iterrows():
                                score = p.get("relevance_score", 0)
                                badge = f'<span class="tag tag-blue">Relevance: {score:.0%}</span>' if score > 0 else ""
                                authors = p.get("authors", [])
                                a_str = ", ".join(authors[:3]) if isinstance(authors, list) else ""
                                ui.html(f"""<div class="paper-card">
                                    <div style="display:flex;justify-content:space-between;align-items:start">
                                        <div class="paper-title">{p['title']}</div>{badge}
                                    </div>
                                    <div class="paper-meta">{a_str} · {fmt_date(p.get('published'))}</div>
                                    <div class="paper-abstract">{str(p.get('abstract',''))[:200]}...</div>
                                </div>""")
                        ui.notify("Recommendations updated", type="positive")

                    ui.button("Get Recommendations", on_click=get_recs, icon="recommend").props("color=primary unelevated").classes("mb-4")

            render_rec()

        # ==================== AI ASSISTANT ====================
        with ui.tab_panel(ai_tab):
            df = state["papers_df"]
            if df.empty:
                ui.html('<div style="text-align:center;padding:60px;color:#86868b">Search for papers first</div>')
            else:
                ui.html('<div class="section-title">AI Assistant</div><div class="section-sub">Ask questions about your papers, generate reviews, extract structured data</div>')

                chat_area = ui.column().classes("w-full").style("max-height:500px;overflow-y:auto")
                for msg in state["chat_history"]:
                    cls = "chat-user" if msg["role"] == "user" else "chat-ai"
                    with chat_area:
                        ui.html(f'<div class="{cls}">{msg["content"]}</div>')

                with ui.row().classes("w-full items-center gap-2 mt-4"):
                    chat_input = ui.input(placeholder="Ask about your papers...").classes("flex-grow")

                    async def send_chat():
                        q = chat_input.value
                        if not q: return
                        chat_input.value = ""

                        state["chat_history"].append({"role": "user", "content": q})
                        with chat_area:
                            ui.html(f'<div class="chat-user">{q}</div>')

                        client = get_llm_client()
                        if not client:
                            with chat_area:
                                ui.html('<div class="chat-ai">Please configure LLM API key in .env</div>')
                            return

                        # Find relevant papers
                        try:
                            from sklearn.feature_extraction.text import TfidfVectorizer
                            from sklearn.metrics.pairwise import cosine_similarity as cs
                            texts = (df["title"].fillna("") + " " + df["abstract"].fillna("")).tolist()
                            vec = TfidfVectorizer(max_features=500, stop_words="english")
                            mat = vec.fit_transform([q] + texts)
                            sims = cs(mat[0:1], mat[1:]).flatten()
                            top_idx = sims.argsort()[-8:][::-1]
                            ctx_papers = df.iloc[top_idx]
                        except:
                            ctx_papers = df.head(8)

                        context = ""
                        for idx, (_, p) in enumerate(ctx_papers.iterrows()):
                            context += f"\n[Paper {idx+1}] {p['title']}\nAbstract: {str(p.get('abstract',''))[:400]}\n"

                        try:
                            resp = client.chat.completions.create(
                                model=MODEL_NAME,
                                messages=[
                                    {"role": "system", "content": f"You are a research assistant. Answer based on papers below. Cite as [Paper X]. Use Chinese.\n\nPapers:\n{context}"},
                                    {"role": "user", "content": q},
                                ],
                                temperature=0.3, max_tokens=1500,
                            )
                            answer = resp.choices[0].message.content
                            state["chat_history"].append({"role": "assistant", "content": answer})
                            with chat_area:
                                ui.html(f'<div class="chat-ai">{answer}</div>')
                        except Exception as e:
                            with chat_area:
                                ui.html(f'<div class="chat-ai" style="color:#ff3b30">Error: {e}</div>')

                    ui.button("Send", on_click=send_chat, icon="send").props("color=primary unelevated")

                # Review button
                ui.separator().classes("my-4")

                async def gen_review():
                    client = get_llm_client()
                    if not client:
                        ui.notify("Configure LLM API key", type="warning"); return
                    ui.notify("Generating review...", type="info")
                    papers_text = ""
                    for _, p in df.head(15).iterrows():
                        papers_text += f"\nTitle: {p['title']}\nAbstract: {str(p.get('abstract',''))[:300]}\n"
                    try:
                        resp = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=[
                                {"role": "system", "content": "Generate a comprehensive literature review in Chinese: 1) Field overview 2) Key directions 3) Main findings 4) Trends 5) Future work. Academic style."},
                                {"role": "user", "content": papers_text},
                            ],
                            temperature=0.3, max_tokens=3000,
                        )
                        review = resp.choices[0].message.content
                        with ui.dialog() as dialog, ui.card().classes("w-full max-w-3xl"):
                            ui.html(f'<div class="section-title" style="margin-top:0">Literature Review</div>')
                            ui.markdown(review)
                        dialog.open()
                    except Exception as e:
                        ui.notify(f"Error: {e}", type="negative")

                ui.button("Generate Literature Review", on_click=gen_review, icon="description").props("unelevated outline").classes("w-full")

        # ==================== LIBRARY ====================
        with ui.tab_panel(lib_tab):
            df = state["papers_df"]
            if df.empty:
                ui.html('<div style="text-align:center;padding:60px;color:#86868b">Your library is empty</div>')
            else:
                ui.html('<div class="section-title">Library</div>')

                unique_authors = set()
                for a in df["authors"]:
                    if isinstance(a, list): unique_authors.update(a)

                with ui.row().classes("w-full gap-4 justify-center mb-6"):
                    for val, lbl in [(len(df), "Papers"), (df["source"].nunique() if "source" in df.columns else 0, "Sources"), (len(unique_authors), "Authors"), (int(df["citation_count"].sum()) if "citation_count" in df.columns else 0, "Citations")]:
                        ui.html(f'<div class="stat-pill" style="min-width:120px"><div class="stat-num" style="font-size:1.4rem">{val}</div><div class="stat-label">{lbl}</div></div>')

                # Export
                with ui.card().classes("w-full"):
                    ui.html('<div style="font-weight:600;font-size:1rem;margin-bottom:12px">Export Data</div>')
                    with ui.row().classes("gap-3"):
                        ui.button("CSV", on_click=lambda: ui.download(df.to_csv(index=False).encode(), "papers.csv"), icon="table_chart").props("outline unelevated")
                        ui.button("JSON", on_click=lambda: ui.download(df.to_json(orient="records", force_ascii=False, indent=2).encode(), "papers.json"), icon="data_object").props("outline unelevated")
                        ui.button("BibTeX", on_click=lambda: ui.download(gen_bibtex(df).encode(), "papers.bib"), icon="format_quote").props("outline unelevated")

    # Footer
    ui.html('<div style="text-align:center;padding:30px 0 10px;color:#86868b;font-size:0.72rem;letter-spacing:0.02em">ScholarMind v3.0 · Powered by AI · Data from OpenAlex, arXiv & Semantic Scholar</div>')


# ============================================================
#  Run
# ============================================================
ui.run(
    title="ScholarMind",
    port=8080,
    reload=False,
    show=False,
    dark=False,
    favicon="📚",
)
