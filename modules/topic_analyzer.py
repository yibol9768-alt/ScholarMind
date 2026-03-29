"""主题建模与趋势分析模块
识别研究领域主题、趋势和热点。
"""

from collections import Counter
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def topic_modeling_lda(df: pd.DataFrame, n_topics: int = 5, top_words: int = 10) -> dict:
    """LDA主题建模"""
    texts = (df["title"].fillna("") + " " + df["abstract"].fillna("")).tolist()
    if len(texts) < n_topics:
        n_topics = max(2, len(texts))

    vectorizer = CountVectorizer(
        max_features=2000,
        stop_words="english",
        min_df=2 if len(texts) > 10 else 1,
        max_df=0.95,
    )
    doc_term = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=20,
    )
    doc_topics = lda.fit_transform(doc_term)

    topics = {}
    for i, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-top_words:][::-1]
        top_terms = [(feature_names[j], float(topic[j])) for j in top_indices]
        topics[f"Topic {i+1}"] = {
            "terms": top_terms,
            "top_words": [t[0] for t in top_terms],
        }

    # 每篇文献的主题分配
    df = df.copy()
    df["dominant_topic"] = doc_topics.argmax(axis=1)
    df["topic_label"] = df["dominant_topic"].apply(lambda x: f"Topic {x+1}")
    df["topic_score"] = doc_topics.max(axis=1)

    return {
        "topics": topics,
        "doc_topics": doc_topics,
        "df": df,
        "n_topics": n_topics,
    }


def topic_modeling_tfidf_kmeans(df: pd.DataFrame, n_clusters: int = 5) -> dict:
    """TF-IDF + KMeans 主题聚类"""
    texts = (df["title"].fillna("") + " " + df["abstract"].fillna("")).tolist()
    if len(texts) < n_clusters:
        n_clusters = max(2, len(texts))

    vectorizer = TfidfVectorizer(
        max_features=2000,
        stop_words="english",
        min_df=1,
        max_df=0.95,
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(tfidf_matrix)

    # 降维用于可视化
    svd = TruncatedSVD(n_components=2, random_state=42)
    coords = svd.fit_transform(tfidf_matrix)

    # 提取每个聚类的关键词
    topics = {}
    for i in range(n_clusters):
        center = kmeans.cluster_centers_[i]
        top_indices = center.argsort()[-10:][::-1]
        top_terms = [(feature_names[j], float(center[j])) for j in top_indices]
        topics[f"Cluster {i+1}"] = {
            "terms": top_terms,
            "top_words": [t[0] for t in top_terms],
            "size": int((clusters == i).sum()),
        }

    df = df.copy()
    df["cluster"] = clusters
    df["cluster_label"] = [f"Cluster {c+1}" for c in clusters]
    df["x"] = coords[:, 0]
    df["y"] = coords[:, 1]

    return {
        "topics": topics,
        "df": df,
        "n_clusters": n_clusters,
    }


def trend_analysis(df: pd.DataFrame) -> dict:
    """趋势分析：按年份统计发表数量、热门关键词变化等"""
    if df.empty or "year" not in df.columns:
        return {}

    df_valid = df.dropna(subset=["year"])
    df_valid = df_valid.copy()
    df_valid["year"] = df_valid["year"].astype(int)

    # 年度论文数量趋势
    yearly_counts = df_valid.groupby("year").size().reset_index(name="count")

    # 年度引用趋势
    yearly_citations = None
    if "citation_count" in df_valid.columns:
        yearly_citations = df_valid.groupby("year")["citation_count"].agg(["mean", "sum"]).reset_index()
        yearly_citations.columns = ["year", "avg_citations", "total_citations"]

    # 年度关键词热度
    keyword_trends = {}
    for year, group in df_valid.groupby("year"):
        all_keywords = []
        for kws in group["keywords"]:
            if isinstance(kws, list):
                all_keywords.extend(kws)
            elif isinstance(kws, str):
                all_keywords.extend([k.strip() for k in kws.split(",")])
        keyword_trends[int(year)] = Counter(all_keywords).most_common(10)

    # 热门研究领域
    all_categories = []
    for cats in df_valid.get("categories", pd.Series(dtype=object)):
        if isinstance(cats, list):
            all_categories.extend(cats)
    top_categories = Counter(all_categories).most_common(15)

    return {
        "yearly_counts": yearly_counts.to_dict("records"),
        "yearly_citations": yearly_citations.to_dict("records") if yearly_citations is not None else [],
        "keyword_trends": keyword_trends,
        "top_categories": top_categories,
        "total_papers": len(df_valid),
        "year_range": (int(df_valid["year"].min()), int(df_valid["year"].max())) if len(df_valid) > 0 else (0, 0),
    }


def identify_hot_topics(df: pd.DataFrame, recent_years: int = 3) -> list[dict]:
    """识别近几年的热点主题"""
    if df.empty or "year" not in df.columns:
        return []

    df_valid = df.dropna(subset=["year"]).copy()
    df_valid["year"] = df_valid["year"].astype(int)
    max_year = df_valid["year"].max()
    recent_df = df_valid[df_valid["year"] >= max_year - recent_years]

    if recent_df.empty:
        return []

    # 提取最近几年的所有关键词
    all_keywords = []
    for kws in recent_df["keywords"]:
        if isinstance(kws, list):
            all_keywords.extend(kws)
        elif isinstance(kws, str):
            all_keywords.extend([k.strip() for k in kws.split(",")])

    hot_keywords = Counter(all_keywords).most_common(20)

    # 找出高引用论文
    hot_papers = []
    if "citation_count" in recent_df.columns:
        hot_papers = recent_df.nlargest(10, "citation_count")[
            ["title", "authors", "year", "citation_count"]
        ].to_dict("records")

    return {
        "hot_keywords": hot_keywords,
        "hot_papers": hot_papers,
        "period": f"{max_year - recent_years}-{max_year}",
    }
