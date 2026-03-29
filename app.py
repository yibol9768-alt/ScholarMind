"""
ScholarMind - 智能文献分析系统
Apple-inspired UI Design
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import re
import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

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
    plot_keyword_trend_heatmap, plot_keyword_cloud_data,
)
from config import MODEL_NAME

# ============================================================
#  Page Config
# ============================================================
st.set_page_config(
    page_title="ScholarMind",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
#  Apple-Inspired Theme CSS
# ============================================================
st.markdown("""
<style>
/* ---- Import SF Pro fallback ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---- Root variables ---- */
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f7;
    --bg-card: #ffffff;
    --text-primary: #1d1d1f;
    --text-secondary: #6e6e73;
    --text-tertiary: #86868b;
    --accent: #0071e3;
    --accent-hover: #0077ed;
    --border: #d2d2d7;
    --border-light: #e8e8ed;
    --radius-card: 18px;
    --radius-btn: 980px;
    --radius-input: 12px;
    --shadow-card: 0 4px 24px rgba(0,0,0,0.06);
    --shadow-hover: 0 8px 32px rgba(0,0,0,0.10);
    --font: 'Inter', 'SF Pro Display', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
    --transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

/* ---- Global ---- */
html, body, [data-testid="stAppViewContainer"] {
    font-family: var(--font) !important;
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary);
}
[data-testid="stMain"] {
    background-color: var(--bg-secondary) !important;
}
.main .block-container {
    max-width: 1200px;
    padding: 2rem 3rem 4rem;
}

/* ---- Hide Streamlit defaults ---- */
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] {
    background: var(--bg-primary);
    border-right: 1px solid var(--border-light);
}

/* ---- Hero Header ---- */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.1;
}
.hero p {
    font-size: 1.25rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
    font-weight: 400;
    letter-spacing: -0.01em;
}

/* ---- Cards ---- */
.card {
    background: var(--bg-card);
    border-radius: var(--radius-card);
    padding: 2rem;
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border-light);
    transition: var(--transition);
    margin-bottom: 1.5rem;
}
.card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}
.card-header {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}
.card-sub {
    font-size: 0.9rem;
    color: var(--text-tertiary);
    margin-bottom: 1.5rem;
}

/* ---- Stat Pill ---- */
.stat-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 1.5rem 0;
}
.stat-pill {
    background: var(--bg-secondary);
    border-radius: 14px;
    padding: 1rem 1.5rem;
    flex: 1;
    min-width: 140px;
    text-align: center;
    border: 1px solid var(--border-light);
}
.stat-pill .num {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}
.stat-pill .label {
    font-size: 0.8rem;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

/* ---- Section title ---- */
.section-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin: 3rem 0 0.5rem;
}
.section-sub {
    font-size: 1rem;
    color: var(--text-secondary);
    margin-bottom: 2rem;
}

/* ---- Paper card ---- */
.paper-item {
    background: var(--bg-card);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    border: 1px solid var(--border-light);
    transition: var(--transition);
}
.paper-item:hover {
    border-color: var(--accent);
    box-shadow: 0 2px 12px rgba(0,113,227,0.08);
}
.paper-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    line-height: 1.4;
}
.paper-meta {
    font-size: 0.8rem;
    color: var(--text-tertiary);
    margin-top: 0.4rem;
}
.paper-abstract {
    font-size: 0.88rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-top: 0.5rem;
}

/* ---- Tags ---- */
.tag {
    display: inline-block;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border-radius: 980px;
    padding: 0.2rem 0.65rem;
    font-size: 0.72rem;
    font-weight: 500;
    margin: 0.15rem 0.2rem;
    border: 1px solid var(--border-light);
}
.tag-accent {
    background: rgba(0,113,227,0.08);
    color: var(--accent);
    border-color: rgba(0,113,227,0.15);
}

/* ---- Streamlit overrides ---- */
/* Tabs */
[data-baseweb="tab-list"] {
    background: var(--bg-primary);
    border-radius: 14px;
    padding: 4px;
    gap: 4px !important;
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-card);
}
[data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    color: var(--text-secondary) !important;
    letter-spacing: -0.005em;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: var(--accent) !important;
    color: #fff !important;
}

/* Buttons */
.stButton > button {
    border-radius: var(--radius-btn) !important;
    padding: 0.55rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: -0.005em;
    border: none !important;
    transition: var(--transition) !important;
}
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: var(--accent) !important;
    color: #fff !important;
}
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background-color: var(--accent-hover) !important;
    transform: scale(1.02);
}
.stButton > button[data-testid="stBaseButton-secondary"] {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
.stTextArea textarea,
.stSelectbox > div > div {
    border-radius: var(--radius-input) !important;
    border-color: var(--border) !important;
    font-family: var(--font) !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,113,227,0.15) !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border-radius: 12px !important;
}

/* Metric */
[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    font-size: 1.8rem !important;
    letter-spacing: -0.02em;
}
[data-testid="stMetricLabel"] {
    color: var(--text-tertiary) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid var(--border-light) !important;
    margin: 2rem 0 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid var(--border-light) !important;
}

/* Chat */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    border: 1px solid var(--border-light) !important;
    padding: 1rem 1.25rem !important;
}

/* Download buttons */
.stDownloadButton > button {
    border-radius: var(--radius-btn) !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-primary) !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: var(--bg-secondary) !important;
}

/* Plotly charts - white background */
.js-plotly-plot .plotly .main-svg {
    border-radius: 14px;
}

/* Toast */
[data-testid="stToast"] {
    border-radius: 14px !important;
}

/* Sidebar */
[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
#  Hero Header
# ============================================================
st.markdown("""
<div class="hero">
    <h1>ScholarMind</h1>
    <p>AI-Powered Academic Literature Analysis</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
#  Helpers
# ============================================================
NOTES_PATH = os.path.join(os.path.dirname(__file__), "data", "notes.json")


def load_notes():
    if os.path.exists(NOTES_PATH):
        try:
            with open(NOTES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_notes(notes):
    os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
    with open(NOTES_PATH, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def fmt_date(d):
    if pd.isna(d):
        return ""
    try:
        return pd.Timestamp(d).strftime("%Y-%m-%d")
    except Exception:
        return str(d)


def generate_bibtex(df):
    entries = []
    for i, row in df.iterrows():
        authors = row.get("authors", [])
        if isinstance(authors, list):
            author_str = " and ".join(authors)
        else:
            author_str = str(authors)
        first_author = authors[0].split()[-1] if isinstance(authors, list) and authors else "unknown"
        year = int(row["year"]) if pd.notna(row.get("year")) else "xxxx"
        key = f"{first_author}{year}_{i}"
        entry = f"@article{{{key},\n  title = {{{row.get('title', '')}}},\n  author = {{{author_str}}},\n  year = {{{year}}},\n  doi = {{{row.get('doi', '')}}},\n}}"
        entries.append(entry)
    return "\n\n".join(entries)


def render_stat_pills(stats: list[tuple]):
    """Render Apple-style stat pills. stats = [(value, label), ...]"""
    pills = ""
    for val, label in stats:
        pills += f'<div class="stat-pill"><div class="num">{val}</div><div class="label">{label}</div></div>'
    st.markdown(f'<div class="stat-row">{pills}</div>', unsafe_allow_html=True)


def render_paper_card(paper, show_abstract=True):
    """Render a paper in Apple card style"""
    title = paper.get("title", "")
    authors = paper.get("authors", [])
    if isinstance(authors, list):
        authors_str = ", ".join(authors[:4])
        if len(authors) > 4:
            authors_str += f" +{len(authors)-4}"
    else:
        authors_str = str(authors)
    date = fmt_date(paper.get("published"))
    cites = int(paper.get("citation_count", 0))
    source = paper.get("source", "")

    keywords = paper.get("keywords", [])
    tags_html = ""
    if isinstance(keywords, list):
        for kw in keywords[:5]:
            tags_html += f'<span class="tag">{kw}</span>'

    abstract_html = ""
    if show_abstract:
        abstract = str(paper.get("abstract", ""))[:250]
        if abstract:
            abstract_html = f'<div class="paper-abstract">{abstract}...</div>'

    meta_parts = [f for f in [authors_str, date, f"{cites} citations" if cites else "", source] if f]

    return f"""<div class="paper-item">
        <div class="paper-title">{title}</div>
        <div class="paper-meta">{" · ".join(meta_parts)}</div>
        {abstract_html}
        <div style="margin-top:0.5rem">{tags_html}</div>
    </div>"""


def apple_plotly_layout(fig, title="", height=420):
    """Apply Apple-style to plotly figures"""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, family="Inter, SF Pro Display, sans-serif", color="#1d1d1f"), x=0, y=0.97),
        font=dict(family="Inter, SF Pro Display, sans-serif", color="#6e6e73", size=12),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor="#f0f0f0", zerolinecolor="#e8e8ed"),
        yaxis=dict(gridcolor="#f0f0f0", zerolinecolor="#e8e8ed"),
        colorway=["#0071e3", "#34c759", "#ff9500", "#af52de", "#ff3b30", "#5ac8fa", "#ffcc00", "#ff2d55"],
    )
    return fig


# ============================================================
#  Init Session State
# ============================================================
if "papers_df" not in st.session_state:
    st.session_state.papers_df = load_papers()
if "user_profile" not in st.session_state:
    st.session_state.user_profile = load_user_profile()
if "topic_result" not in st.session_state:
    st.session_state.topic_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

profile = st.session_state.user_profile

# ============================================================
#  Quick Stats Bar
# ============================================================
df_all = st.session_state.papers_df
if not df_all.empty:
    unique_authors = set()
    for a in df_all["authors"]:
        if isinstance(a, list):
            unique_authors.update(a)
    total_cites = int(df_all["citation_count"].sum()) if "citation_count" in df_all.columns else 0
    render_stat_pills([
        (len(df_all), "Papers"),
        (len(unique_authors), "Authors"),
        (total_cites, "Citations"),
        (len(profile.get("liked_papers", [])), "Saved"),
    ])

# ============================================================
#  Tabs
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Search", "Topics & Trends", "Knowledge Graph",
    "Recommend", "AI Assistant", "Library"
])

# ============================================================
#  TAB 1 — Search
# ============================================================
with tab1:
    st.markdown('<div class="card"><div class="card-header">Discover Research</div><div class="card-sub">Search millions of papers from arXiv and Semantic Scholar</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        query = st.text_input("Search", placeholder="e.g. large language model, transformer, diffusion model...", label_visibility="collapsed")
    with col2:
        max_results = st.number_input("Max", 10, 200, 30, step=10, label_visibility="collapsed")
    with col3:
        data_source = st.selectbox("Source", ["Both", "arXiv", "Semantic Scholar"], label_visibility="collapsed")

    scol1, scol2, scol3 = st.columns([2, 1, 1])
    with scol1:
        search_clicked = st.button("Search Papers", type="primary", use_container_width=True)
    with scol2:
        sort_option = st.selectbox("Sort by", ["relevance", "date"], label_visibility="collapsed")
    with scol3:
        use_llm = st.checkbox("LLM Extract", value=False, help="Use AI to extract richer metadata")

    st.markdown('</div>', unsafe_allow_html=True)

    if search_clicked and query:
        with st.spinner("Searching..."):
            papers = []
            if data_source in ["arXiv", "Both"]:
                ap = search_arxiv(query, max_results, sort_option)
                papers.extend(ap)
                if ap:
                    st.toast(f"arXiv: {len(ap)} papers")
            if data_source in ["Semantic Scholar", "Both"]:
                sp = search_semantic_scholar(query, max_results)
                papers.extend(sp)
                if sp:
                    st.toast(f"Semantic Scholar: {len(sp)} papers")

            if papers:
                df = clean_and_standardize(papers)
                try:
                    llm_client = get_llm_client()
                    if use_llm and llm_client:
                        with st.spinner("AI extracting metadata..."):
                            enriched = batch_extract_info_llm(df.to_dict("records"))
                            df = pd.DataFrame(enriched)
                            df["published"] = pd.to_datetime(df["published"], errors="coerce")
                            df["year"] = df["published"].dt.year
                    else:
                        kw_dict = extract_keywords_tfidf(df)
                        for i, row in df.iterrows():
                            if row["title"] in kw_dict:
                                df.at[i, "keywords"] = kw_dict[row["title"]]
                except Exception as e:
                    st.warning(f"Keyword extraction issue: {e}")

                st.session_state.papers_df = df
                st.session_state.topic_result = None
                save_papers(df)
                add_search_history(profile, query)
                st.success(f"Found {len(df)} papers")
                st.rerun()
            else:
                st.error("No papers found. Try different keywords or check your network connection.")

    # Results
    df = st.session_state.papers_df
    if not df.empty:
        # Filters
        st.markdown('<p class="section-title">Results</p>', unsafe_allow_html=True)

        fcol1, fcol2 = st.columns([2, 1])
        with fcol1:
            title_filter = st.text_input("Filter by title", placeholder="Type to filter...", label_visibility="collapsed")
        years = []
        year_range = None
        with fcol2:
            if "year" in df.columns:
                years = sorted(df["year"].dropna().unique())
                if len(years) >= 2:
                    year_range = st.slider("Year range", int(min(years)), int(max(years)),
                                           (int(min(years)), int(max(years))), label_visibility="collapsed")

        filtered_df = df.copy()
        if year_range and len(years) >= 2:
            filtered_df = filtered_df[(filtered_df["year"] >= year_range[0]) & (filtered_df["year"] <= year_range[1])]
        if title_filter:
            filtered_df = filtered_df[filtered_df["title"].str.contains(title_filter, case=False, na=False)]

        # Paper list
        for _, paper in filtered_df.head(30).iterrows():
            st.markdown(render_paper_card(paper), unsafe_allow_html=True)

        if len(filtered_df) > 30:
            st.info(f"Showing 30 of {len(filtered_df)} papers. Use filters to narrow down.")

        # Paper detail
        st.markdown('<p class="section-title">Paper Detail</p>', unsafe_allow_html=True)
        selected_title = st.selectbox("Select a paper", filtered_df["title"].tolist(), label_visibility="collapsed")

        if selected_title:
            paper = filtered_df[filtered_df["title"] == selected_title].iloc[0]

            st.markdown(f"""<div class="card">
                <div class="card-header">{paper['title']}</div>
            """, unsafe_allow_html=True)

            dcol1, dcol2 = st.columns([3, 1])
            with dcol1:
                authors = paper.get("authors", [])
                if isinstance(authors, list):
                    st.markdown(f"**Authors:** {', '.join(authors)}")
                st.markdown(f"**Date:** {fmt_date(paper.get('published'))} · **Source:** {paper.get('source', '')}")
                if paper.get("doi"):
                    st.markdown(f"**DOI:** {paper['doi']}")
                if paper.get("main_contribution"):
                    st.markdown(f"**Contribution:** {paper['main_contribution']}")
                st.markdown(f"**Abstract:** {paper.get('abstract', 'N/A')}")
            with dcol2:
                st.metric("Citations", int(paper.get("citation_count", 0)))
                keywords = paper.get("keywords", [])
                if isinstance(keywords, list) and keywords:
                    tags = "".join([f'<span class="tag tag-accent">{k}</span>' for k in keywords[:8]])
                    st.markdown(f"**Keywords:**<br>{tags}", unsafe_allow_html=True)
                if paper.get("pdf_url"):
                    st.link_button("View Paper", paper["pdf_url"], use_container_width=True)

                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("Read", key="d_read", use_container_width=True):
                        mark_paper_read(profile, selected_title)
                        st.toast("Marked as read")
                        st.rerun()
                with bc2:
                    if st.button("Save", key="d_save", use_container_width=True):
                        mark_paper_liked(profile, selected_title)
                        kws = paper.get("keywords", [])
                        if isinstance(kws, list):
                            update_user_interests(profile, kws)
                        st.toast("Saved!")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

            # Citations
            st.markdown('<p class="section-title" style="font-size:1.3rem">Citation Explorer</p>', unsafe_allow_html=True)
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Cited By", use_container_width=True):
                    with st.spinner("Loading citations..."):
                        cits = get_paper_citations(paper.get("id", ""))
                        st.session_state.current_citations = cits if cits else []
                        if not cits:
                            st.info("No citation data found")
            with cc2:
                if st.button("References", use_container_width=True):
                    with st.spinner("Loading references..."):
                        refs = get_paper_references(paper.get("id", ""))
                        st.session_state.current_references = refs if refs else []
                        if not refs:
                            st.info("No reference data found")

            if st.session_state.get("current_citations"):
                cdf = pd.DataFrame(st.session_state.current_citations)
                st.markdown(f"**{len(cdf)} papers cite this work:**")
                for _, c in cdf.head(10).iterrows():
                    st.markdown(f"""<div class="paper-item"><div class="paper-title">{c['title']}</div>
                        <div class="paper-meta">{c.get('year', '')} · {c.get('citation_count', 0)} citations</div></div>""",
                        unsafe_allow_html=True)

            if st.session_state.get("current_references"):
                rdf = pd.DataFrame(st.session_state.current_references)
                st.markdown(f"**{len(rdf)} references:**")
                for _, r in rdf.head(10).iterrows():
                    st.markdown(f"""<div class="paper-item"><div class="paper-title">{r['title']}</div>
                        <div class="paper-meta">{r.get('year', '')} · {r.get('citation_count', 0)} citations</div></div>""",
                        unsafe_allow_html=True)


# ============================================================
#  TAB 2 — Topics & Trends
# ============================================================
with tab2:
    df = st.session_state.papers_df
    if df.empty:
        st.markdown('<div class="card" style="text-align:center;padding:4rem"><div class="card-header">No Data Yet</div><div class="card-sub">Search for papers first to see topic analysis</div></div>', unsafe_allow_html=True)
    else:
        # Trends
        st.markdown('<p class="section-title">Publishing Trends</p>', unsafe_allow_html=True)
        trends = trend_analysis(df)
        if trends and trends.get("yearly_counts"):
            tcol1, tcol2 = st.columns(2)
            with tcol1:
                fig = plot_yearly_trend(trends["yearly_counts"])
                apple_plotly_layout(fig, "Papers per Year")
                st.plotly_chart(fig, use_container_width=True)
            with tcol2:
                if trends.get("yearly_citations"):
                    fig2 = plot_citation_trend(trends["yearly_citations"])
                    apple_plotly_layout(fig2, "Citation Trends")
                    st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # Topic Modeling
        st.markdown('<p class="section-title">Topic Modeling</p><p class="section-sub">Discover hidden themes in the literature</p>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        tmcol1, tmcol2, tmcol3 = st.columns([2, 1, 1])
        with tmcol1:
            method = st.selectbox("Method", ["LDA", "TF-IDF + KMeans"], label_visibility="collapsed")
        with tmcol2:
            n_topics = st.slider("Topics", 2, 10, 5, label_visibility="collapsed")
        with tmcol3:
            if st.button("Analyze Topics", type="primary", use_container_width=True):
                with st.spinner("Modeling topics..."):
                    try:
                        if method == "LDA":
                            result = topic_modeling_lda(df, n_topics)
                        else:
                            result = topic_modeling_tfidf_kmeans(df, n_topics)
                        st.session_state.topic_result = result
                    except Exception as e:
                        st.error(f"Topic modeling failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.topic_result:
            result = st.session_state.topic_result
            topics = result["topics"]

            tcol1, tcol2 = st.columns(2)
            with tcol1:
                fig = plot_topic_distribution(topics)
                apple_plotly_layout(fig, "Topic Distribution", 400)
                st.plotly_chart(fig, use_container_width=True)
            with tcol2:
                if "df" in result:
                    fig = plot_topic_scatter(result["df"])
                    apple_plotly_layout(fig, "Topic Clusters", 400)
                    st.plotly_chart(fig, use_container_width=True)

            for topic_name, topic_data in topics.items():
                words = topic_data["top_words"]
                tags = " ".join([f'<span class="tag tag-accent">{w}</span>' for w in words])
                st.markdown(f'<div class="paper-item"><div class="paper-title">{topic_name}</div><div style="margin-top:0.5rem">{tags}</div></div>', unsafe_allow_html=True)

        st.divider()

        # Keywords
        st.markdown('<p class="section-title">Keyword Analysis</p>', unsafe_allow_html=True)
        kcol1, kcol2 = st.columns(2)
        with kcol1:
            fig = plot_keyword_bar(df)
            apple_plotly_layout(fig, "Top Keywords")
            st.plotly_chart(fig, use_container_width=True)
        with kcol2:
            if trends and trends.get("keyword_trends"):
                fig = plot_keyword_trend_heatmap(trends["keyword_trends"])
                apple_plotly_layout(fig, "Keyword Heatmap")
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Wordcloud fallback
                cloud_data = plot_keyword_cloud_data(df)
                if cloud_data:
                    try:
                        from wordcloud import WordCloud
                        import matplotlib.pyplot as plt
                        freq = {d["name"]: d["value"] for d in cloud_data}
                        wc = WordCloud(width=600, height=400, background_color="white",
                                       color_func=lambda *a, **kw: "#0071e3").generate_from_frequencies(freq)
                        fig_wc, ax = plt.subplots(figsize=(8, 5))
                        ax.imshow(wc, interpolation="bilinear")
                        ax.axis("off")
                        fig_wc.patch.set_facecolor("white")
                        st.pyplot(fig_wc)
                    except Exception:
                        pass

        # Hot topics
        hot = identify_hot_topics(df)
        if hot and hot.get("hot_keywords"):
            st.markdown(f'<p class="section-title">Hot Topics <span style="font-size:0.9rem;color:#6e6e73">({hot.get("period", "")})</span></p>', unsafe_allow_html=True)
            tags = " ".join([f'<span class="tag tag-accent">{k} ({v})</span>' for k, v in hot["hot_keywords"][:15]])
            st.markdown(f'<div class="card">{tags}</div>', unsafe_allow_html=True)


# ============================================================
#  TAB 3 — Knowledge Graph
# ============================================================
with tab3:
    df = st.session_state.papers_df
    if df.empty:
        st.markdown('<div class="card" style="text-align:center;padding:4rem"><div class="card-header">No Data Yet</div><div class="card-sub">Search for papers first to build knowledge graphs</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="section-title">Knowledge Graph</p><p class="section-sub">Explore relationships between papers, authors, and keywords</p>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        gcol1, gcol2 = st.columns([2, 1])
        with gcol1:
            graph_type = st.selectbox("Network Type", ["Author Collaboration", "Keyword Co-occurrence", "Paper-Author-Keyword"], label_visibility="collapsed")
        with gcol2:
            if st.button("Build Graph", type="primary", use_container_width=True):
                with st.spinner("Building network..."):
                    if graph_type == "Author Collaboration":
                        G = build_author_collaboration_network(df)
                        st.session_state.current_graph = G
                        st.session_state.graph_type = "collaboration"
                    elif graph_type == "Paper-Author-Keyword":
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
        st.markdown('</div>', unsafe_allow_html=True)

        if "current_graph" in st.session_state:
            G = st.session_state.current_graph

            render_stat_pills([
                (G.number_of_nodes(), "Nodes"),
                (G.number_of_edges(), "Edges"),
                (f"{nx.density(G):.3f}", "Density"),
                (nx.number_connected_components(G) if not nx.is_directed(G) and G.number_of_nodes() > 0 else "—", "Components"),
            ])

            if G.number_of_nodes() > 0:
                max_display = st.slider("Display nodes", 10, min(200, G.number_of_nodes()), min(50, G.number_of_nodes()))

                if G.number_of_nodes() > max_display:
                    top_n = sorted(G.nodes, key=lambda n: G.degree(n), reverse=True)[:max_display]
                    subG = G.subgraph(top_n)
                else:
                    subG = G

                # Interactive graph with streamlit-agraph
                try:
                    from streamlit_agraph import agraph, Node, Edge, Config

                    color_map = {"paper": "#0071e3", "author": "#ff3b30", "keyword": "#34c759"}
                    nodes = []
                    edges = []
                    for node in subG.nodes:
                        ntype = subG.nodes[node].get("type", "")
                        color = color_map.get(ntype, "#86868b")
                        size = min(10 + subG.degree(node) * 3, 40)
                        nodes.append(Node(id=str(node), label=str(node)[:22], size=size, color=color,
                                         font={"size": 10, "color": "#1d1d1f"},
                                         title=f"{node}\nConnections: {subG.degree(node)}"))
                    for u, v, data in subG.edges(data=True):
                        edges.append(Edge(source=str(u), target=str(v),
                                         width=min(data.get("weight", 1), 5),
                                         color="#d2d2d7"))

                    config = Config(width=800, height=550, directed=False, physics=True,
                                    nodeHighlightBehavior=True, highlightColor="#0071e3",
                                    collapsible=False,
                                    node={"highlightStrokeColor": "#0071e3"})
                    agraph(nodes=nodes, edges=edges, config=config)

                    if st.session_state.get("graph_type") == "knowledge":
                        st.markdown('<div style="text-align:center;margin:1rem 0"><span class="tag" style="background:#0071e3;color:#fff">Paper</span> <span class="tag" style="background:#ff3b30;color:#fff">Author</span> <span class="tag" style="background:#34c759;color:#fff">Keyword</span></div>', unsafe_allow_html=True)
                except ImportError:
                    # Plotly fallback
                    pos = nx.spring_layout(subG, seed=42, k=2/np.sqrt(max(subG.number_of_nodes(), 1)))
                    edge_x, edge_y = [], []
                    for u, v in subG.edges():
                        x0, y0 = pos[u]; x1, y1 = pos[v]
                        edge_x.extend([x0, x1, None]); edge_y.extend([y0, y1, None])

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=0.5, color="#d2d2d7"), hoverinfo="none"))
                    node_x = [pos[n][0] for n in subG.nodes()]
                    node_y = [pos[n][1] for n in subG.nodes()]
                    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text",
                                             text=[str(n)[:18] for n in subG.nodes()], textposition="top center",
                                             textfont=dict(size=8, color="#1d1d1f"),
                                             marker=dict(size=[min(6+subG.degree(n)*2,28) for n in subG.nodes()],
                                                         color=[subG.degree(n) for n in subG.nodes()],
                                                         colorscale=[[0,"#d2d2d7"],[1,"#0071e3"]], showscale=False,
                                                         line=dict(width=1, color="white")),
                                             hovertext=list(subG.nodes()), hoverinfo="text"))
                    apple_plotly_layout(fig, graph_type, 550)
                    fig.update_layout(xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                                      yaxis=dict(showgrid=False, showticklabels=False, zeroline=False), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                # Top nodes
                degrees = sorted(dict(subG.degree()).items(), key=lambda x: x[1], reverse=True)[:8]
                st.markdown("**Key Nodes:**")
                tags = " ".join([f'<span class="tag">{str(n)[:25]} ({d})</span>' for n, d in degrees])
                st.markdown(tags, unsafe_allow_html=True)

        # Author stats
        st.divider()
        st.markdown('<p class="section-title" style="font-size:1.3rem">Top Authors</p>', unsafe_allow_html=True)
        fig = plot_author_stats(df)
        apple_plotly_layout(fig, "")
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
#  TAB 4 — Recommendations
# ============================================================
with tab4:
    df = st.session_state.papers_df
    if df.empty:
        st.markdown('<div class="card" style="text-align:center;padding:4rem"><div class="card-header">No Data Yet</div><div class="card-sub">Search for papers to get personalized recommendations</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="section-title">Recommended For You</p>', unsafe_allow_html=True)

        if profile.get("interests"):
            tags = " ".join([f'<span class="tag tag-accent">{k}</span>' for k in profile["interests"][:12]])
            st.markdown(f'<div class="card"><div class="card-header" style="font-size:1rem">Your Interests</div><div style="margin-top:0.5rem">{tags}</div></div>', unsafe_allow_html=True)

        if st.button("Get Recommendations", type="primary", use_container_width=True):
            with st.spinner("Computing recommendations..."):
                recommended = content_based_recommend(df, profile, top_n=10)
                st.session_state.recommended_papers = recommended

        if "recommended_papers" in st.session_state:
            for _, paper in st.session_state.recommended_papers.iterrows():
                score = paper.get("relevance_score", 0)
                score_html = f'<span class="tag tag-accent">Relevance: {score:.0%}</span>' if score > 0 else ""
                st.markdown(f"""<div class="paper-item">
                    <div style="display:flex;justify-content:space-between;align-items:start">
                        <div class="paper-title">{paper['title']}</div>{score_html}
                    </div>
                    <div class="paper-meta">{', '.join(paper['authors'][:3]) if isinstance(paper.get('authors'), list) else ''} · {fmt_date(paper.get('published'))}</div>
                    <div class="paper-abstract">{str(paper.get('abstract',''))[:200]}...</div>
                </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<p class="section-title" style="font-size:1.3rem">Find Similar Papers</p>', unsafe_allow_html=True)
        selected = st.selectbox("Select a paper", df["title"].tolist(), key="sim_sel", label_visibility="collapsed")
        if st.button("Find Similar", use_container_width=True):
            with st.spinner("Computing similarity..."):
                similar = similar_paper_recommend(df, selected, top_n=5)
                for _, p in similar.iterrows():
                    sim = p.get("similarity", 0)
                    st.markdown(f"""<div class="paper-item">
                        <div style="display:flex;justify-content:space-between">
                            <div class="paper-title">{p['title']}</div>
                            <span class="tag">Similarity: {sim:.0%}</span>
                        </div></div>""", unsafe_allow_html=True)


# ============================================================
#  TAB 5 — AI Assistant
# ============================================================
with tab5:
    df = st.session_state.papers_df
    if df.empty:
        st.markdown('<div class="card" style="text-align:center;padding:4rem"><div class="card-header">No Data Yet</div><div class="card-sub">Search for papers to use the AI assistant</div></div>', unsafe_allow_html=True)
    else:
        ai_tab1, ai_tab2, ai_tab3 = st.tabs(["Chat", "Literature Review", "Extract"])

        with ai_tab1:
            st.markdown('<p class="section-title" style="font-size:1.3rem">Ask About Your Papers</p>', unsafe_allow_html=True)

            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_q = st.chat_input("Ask a question about the papers...")
            if user_q:
                st.session_state.chat_history.append({"role": "user", "content": user_q})
                with st.chat_message("user"):
                    st.markdown(user_q)

                client = get_llm_client()
                if client:
                    try:
                        from sklearn.feature_extraction.text import TfidfVectorizer
                        from sklearn.metrics.pairwise import cosine_similarity as cs
                        texts = (df["title"].fillna("") + " " + df["abstract"].fillna("")).tolist()
                        vec = TfidfVectorizer(max_features=500, stop_words="english")
                        mat = vec.fit_transform([user_q] + texts)
                        sims = cs(mat[0:1], mat[1:]).flatten()
                        top_idx = sims.argsort()[-8:][::-1]
                        ctx_papers = df.iloc[top_idx]
                    except Exception:
                        ctx_papers = df.head(8)

                    context = ""
                    for idx, (_, p) in enumerate(ctx_papers.iterrows()):
                        context += f"\n[Paper {idx+1}] {p['title']}\nAbstract: {str(p.get('abstract', ''))[:400]}\n"

                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            try:
                                resp = client.chat.completions.create(
                                    model=MODEL_NAME,
                                    messages=[
                                        {"role": "system", "content": f"You are a research assistant. Answer based on the papers below. Cite papers as [Paper X]. Use Chinese.\n\nPapers:\n{context}"},
                                        {"role": "user", "content": user_q},
                                    ],
                                    temperature=0.3, max_tokens=1500,
                                )
                                answer = resp.choices[0].message.content
                                st.markdown(answer)
                                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    with st.chat_message("assistant"):
                        st.warning("Please configure LLM API key in .env file")

            if st.session_state.chat_history and st.button("Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

        with ai_tab2:
            st.markdown('<p class="section-title" style="font-size:1.3rem">Generate Literature Review</p>', unsafe_allow_html=True)
            review_n = st.slider("Number of papers to review", 5, min(30, len(df)), min(10, len(df)))
            if st.button("Generate Review", type="primary", key="gen_rev"):
                client = get_llm_client()
                if client:
                    with st.spinner("Generating review..."):
                        papers_text = ""
                        for _, p in df.head(review_n).iterrows():
                            papers_text += f"\nTitle: {p['title']}\nAbstract: {str(p.get('abstract', ''))[:300]}\n"
                        try:
                            resp = client.chat.completions.create(
                                model=MODEL_NAME,
                                messages=[
                                    {"role": "system", "content": "You are an academic literature review expert. Generate a comprehensive review in Chinese covering: 1) Field overview 2) Key research directions 3) Main findings 4) Trends 5) Future directions. Be structured and academic."},
                                    {"role": "user", "content": papers_text},
                                ],
                                temperature=0.3, max_tokens=3000,
                            )
                            review = resp.choices[0].message.content
                            st.markdown(f'<div class="card">{review}</div>', unsafe_allow_html=True)
                            st.download_button("Download Review", review, "review.md", "text/markdown")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please configure LLM API key")

        with ai_tab3:
            st.markdown('<p class="section-title" style="font-size:1.3rem">Structured Extraction</p><p class="section-sub">Extract custom fields from papers into a comparison table</p>', unsafe_allow_html=True)

            fields_input = st.text_input("Fields to extract (comma-separated)", value="Research Method, Dataset, Key Finding, Limitation")
            extract_n = st.slider("Papers to extract", 3, min(15, len(df)), min(8, len(df)))

            if st.button("Extract", type="primary", key="struct_ext"):
                client = get_llm_client()
                if client:
                    fields = [f.strip() for f in fields_input.split(",")]
                    all_results = []
                    progress = st.progress(0)

                    for idx, (_, p) in enumerate(df.head(extract_n).iterrows()):
                        progress.progress((idx + 1) / extract_n)
                        try:
                            resp = client.chat.completions.create(
                                model=MODEL_NAME,
                                messages=[
                                    {"role": "system", "content": f"Extract these fields from the paper: {', '.join(fields)}. Return as JSON object. Only return JSON."},
                                    {"role": "user", "content": f"Title: {p['title']}\nAbstract: {str(p.get('abstract', ''))[:500]}"},
                                ],
                                temperature=0.1, max_tokens=500,
                            )
                            text = resp.choices[0].message.content.strip()
                            match = re.search(r"\{.*\}", text, re.DOTALL)
                            if match:
                                extracted = json.loads(match.group())
                                extracted["Paper"] = p["title"][:50]
                                all_results.append(extracted)
                        except Exception:
                            all_results.append({"Paper": p["title"][:50], **{f: "—" for f in fields}})

                    progress.empty()
                    if all_results:
                        rdf = pd.DataFrame(all_results)
                        cols = ["Paper"] + [c for c in rdf.columns if c != "Paper"]
                        st.dataframe(rdf[cols], use_container_width=True)
                        st.download_button("Download CSV", rdf[cols].to_csv(index=False).encode("utf-8"), "extracted.csv", "text/csv")
                else:
                    st.warning("Please configure LLM API key")


# ============================================================
#  TAB 6 — Library
# ============================================================
with tab6:
    df = st.session_state.papers_df
    if df.empty:
        st.markdown('<div class="card" style="text-align:center;padding:4rem"><div class="card-header">Your Library is Empty</div><div class="card-sub">Search and save papers to build your library</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="section-title">Library</p>', unsafe_allow_html=True)

        render_stat_pills([
            (len(df), "Papers"),
            (df["source"].nunique() if "source" in df.columns else 0, "Sources"),
            (len(set(a for al in df["authors"] if isinstance(al, list) for a in al)), "Authors"),
            (int(df["citation_count"].sum()) if "citation_count" in df.columns else 0, "Total Citations"),
        ])

        # Export
        st.markdown('<div class="card"><div class="card-header" style="font-size:1.1rem">Export Data</div>', unsafe_allow_html=True)
        ecol1, ecol2, ecol3 = st.columns(3)
        with ecol1:
            st.download_button("CSV", df.to_csv(index=False).encode("utf-8"), "papers.csv", "text/csv", use_container_width=True)
        with ecol2:
            st.download_button("JSON", df.to_json(orient="records", force_ascii=False, indent=2), "papers.json", "application/json", use_container_width=True)
        with ecol3:
            st.download_button("BibTeX", generate_bibtex(df), "papers.bib", "text/plain", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Notes
        st.markdown('<p class="section-title" style="font-size:1.3rem">Paper Notes</p>', unsafe_allow_html=True)
        notes = load_notes()
        sel_paper = st.selectbox("Select paper", df["title"].tolist(), key="note_sel", label_visibility="collapsed")
        existing = notes.get(sel_paper, "")
        note_text = st.text_area("Note", value=existing, placeholder="Write your notes...", label_visibility="collapsed")

        ncol1, ncol2 = st.columns(2)
        with ncol1:
            if st.button("Save Note", type="primary", use_container_width=True):
                if note_text.strip():
                    notes[sel_paper] = note_text
                    save_notes(notes)
                    st.toast("Note saved")
                else:
                    st.warning("Note cannot be empty")
        with ncol2:
            if existing and st.button("Delete Note", use_container_width=True):
                notes.pop(sel_paper, None)
                save_notes(notes)
                st.toast("Note deleted")
                st.rerun()

        if notes:
            for title, note in notes.items():
                disp = title if len(title) <= 50 else title[:50] + "..."
                with st.expander(disp):
                    st.write(note)


# ============================================================
#  Footer
# ============================================================
st.markdown("""
<div style="text-align:center;padding:3rem 0 1rem;color:#86868b;font-size:0.75rem;letter-spacing:0.02em">
    ScholarMind v2.0 · Powered by AI · Data from arXiv & Semantic Scholar
</div>
""", unsafe_allow_html=True)
