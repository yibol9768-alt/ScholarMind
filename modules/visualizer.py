"""可视化模块
提供各类图表生成函数，用于Streamlit界面展示。
"""

import json
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_yearly_trend(yearly_counts: list[dict]) -> go.Figure:
    """年度论文发表趋势图"""
    df = pd.DataFrame(yearly_counts)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["year"], y=df["count"], name="论文数量",
                         marker_color="steelblue"))
    fig.add_trace(go.Scatter(x=df["year"], y=df["count"], name="趋势线",
                             mode="lines+markers", line=dict(color="red", width=2)))
    fig.update_layout(
        title="📊 年度论文发表趋势",
        xaxis_title="年份", yaxis_title="论文数量",
        template="plotly_white", height=400,
    )
    return fig


def plot_citation_trend(yearly_citations: list[dict]) -> go.Figure:
    """年度引用趋势图"""
    df = pd.DataFrame(yearly_citations)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["year"], y=df["total_citations"], name="总引用数",
                         marker_color="lightblue", yaxis="y"))
    fig.add_trace(go.Scatter(x=df["year"], y=df["avg_citations"], name="平均引用数",
                             mode="lines+markers", line=dict(color="orange", width=2), yaxis="y2"))
    fig.update_layout(
        title="📈 年度引用趋势",
        xaxis_title="年份",
        yaxis=dict(title="总引用数", side="left"),
        yaxis2=dict(title="平均引用数", side="right", overlaying="y"),
        template="plotly_white", height=400,
    )
    return fig


def plot_topic_distribution(topics: dict) -> go.Figure:
    """主题分布饼图"""
    labels = list(topics.keys())
    sizes = [topics[t].get("size", len(topics[t].get("top_words", []))) for t in labels]
    text_labels = [", ".join(topics[t]["top_words"][:3]) for t in labels]

    fig = go.Figure(data=[go.Pie(
        labels=[f"{l}\n({t})" for l, t in zip(labels, text_labels)],
        values=sizes,
        textinfo="label+percent",
        hovertext=text_labels,
    )])
    fig.update_layout(title="🎯 主题分布", height=450)
    return fig


def plot_topic_scatter(df: pd.DataFrame) -> go.Figure:
    """主题聚类散点图"""
    if "x" not in df.columns or "y" not in df.columns:
        return go.Figure()

    fig = px.scatter(
        df, x="x", y="y",
        color="cluster_label" if "cluster_label" in df.columns else "topic_label",
        hover_data=["title"],
        title="🔬 论文主题聚类分布",
        template="plotly_white",
    )
    fig.update_layout(height=500)
    return fig


def plot_keyword_cloud_data(df: pd.DataFrame) -> list[dict]:
    """生成关键词词云数据"""
    all_keywords = []
    for kws in df.get("keywords", pd.Series(dtype=object)):
        if isinstance(kws, list):
            all_keywords.extend(kws)
        elif isinstance(kws, str):
            all_keywords.extend([k.strip() for k in kws.split(",")])

    counter = Counter(all_keywords)
    return [{"name": k, "value": v} for k, v in counter.most_common(50)]


def plot_keyword_bar(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """关键词频率柱状图"""
    all_keywords = []
    for kws in df.get("keywords", pd.Series(dtype=object)):
        if isinstance(kws, list):
            all_keywords.extend(kws)
        elif isinstance(kws, str):
            all_keywords.extend([k.strip() for k in kws.split(",")])

    counter = Counter(all_keywords)
    top_kw = counter.most_common(top_n)
    if not top_kw:
        return go.Figure()

    kws, counts = zip(*top_kw)
    fig = go.Figure(go.Bar(
        x=list(counts)[::-1], y=list(kws)[::-1],
        orientation="h", marker_color="teal",
    ))
    fig.update_layout(
        title=f"🔑 Top {top_n} 关键词",
        xaxis_title="频次", yaxis_title="",
        template="plotly_white", height=max(400, top_n * 25),
    )
    return fig


def plot_author_stats(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """高产作者统计"""
    all_authors = []
    for authors in df["authors"]:
        if isinstance(authors, list):
            all_authors.extend(authors)
        elif isinstance(authors, str):
            all_authors.extend([a.strip() for a in authors.split(",")])

    counter = Counter(all_authors)
    top_authors = counter.most_common(top_n)
    if not top_authors:
        return go.Figure()

    names, counts = zip(*top_authors)
    fig = go.Figure(go.Bar(
        x=list(counts)[::-1], y=list(names)[::-1],
        orientation="h", marker_color="coral",
    ))
    fig.update_layout(
        title=f"👨‍🔬 Top {top_n} 高产作者",
        xaxis_title="论文数", yaxis_title="",
        template="plotly_white", height=max(400, top_n * 25),
    )
    return fig


def plot_collaboration_network(G: nx.Graph, max_nodes: int = 50) -> dict:
    """生成作者合作网络数据（用于streamlit-agraph）"""
    if len(G.nodes) == 0:
        return {"nodes": [], "edges": []}

    # 按论文数量选取top节点
    nodes_by_degree = sorted(G.nodes, key=lambda n: G.degree(n), reverse=True)[:max_nodes]
    subG = G.subgraph(nodes_by_degree)

    nodes = []
    for node in subG.nodes:
        paper_count = subG.nodes[node].get("paper_count", G.degree(node))
        nodes.append({
            "id": node,
            "label": node,
            "size": min(5 + paper_count * 3, 30),
            "color": f"hsl({hash(node) % 360}, 70%, 50%)",
        })

    edges = []
    for u, v, data in subG.edges(data=True):
        edges.append({
            "source": u,
            "target": v,
            "weight": data.get("weight", 1),
        })

    return {"nodes": nodes, "edges": edges}


def plot_keyword_trend_heatmap(keyword_trends: dict) -> go.Figure:
    """关键词趋势热力图"""
    if not keyword_trends:
        return go.Figure()

    # 收集所有关键词
    all_kws = Counter()
    for year, kws in keyword_trends.items():
        for kw, count in kws:
            all_kws[kw] += count

    top_kws = [k for k, _ in all_kws.most_common(15)]
    years = sorted(keyword_trends.keys())

    z = []
    for kw in top_kws:
        row = []
        for year in years:
            count = 0
            for k, c in keyword_trends[year]:
                if k == kw:
                    count = c
                    break
            row.append(count)
        z.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=z, x=[str(y) for y in years], y=top_kws,
        colorscale="YlOrRd",
    ))
    fig.update_layout(
        title="🔥 关键词年度趋势热力图",
        xaxis_title="年份", yaxis_title="关键词",
        template="plotly_white", height=500,
    )
    return fig
