"""智能推荐与个性化服务模块
根据用户兴趣和历史行为推荐文献。
"""

import json
import os
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import DATA_DIR


USER_PROFILE_PATH = os.path.join(DATA_DIR, "user_profile.json")


def load_user_profile() -> dict:
    """加载用户画像"""
    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"interests": [], "read_papers": [], "liked_papers": [], "search_history": []}


def save_user_profile(profile: dict):
    """保存用户画像"""
    with open(USER_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def update_user_interests(profile: dict, keywords: list[str]):
    """更新用户兴趣"""
    profile["interests"].extend(keywords)
    # 保留最近的兴趣，按频率排序
    counter = Counter(profile["interests"])
    profile["interests"] = [k for k, _ in counter.most_common(50)]
    save_user_profile(profile)


def mark_paper_read(profile: dict, paper_title: str):
    """标记论文为已读"""
    if paper_title not in profile["read_papers"]:
        profile["read_papers"].append(paper_title)
        save_user_profile(profile)


def mark_paper_liked(profile: dict, paper_title: str):
    """标记论文为喜欢"""
    if paper_title not in profile["liked_papers"]:
        profile["liked_papers"].append(paper_title)
        save_user_profile(profile)


def add_search_history(profile: dict, query: str):
    """添加搜索历史"""
    profile["search_history"].append(query)
    profile["search_history"] = profile["search_history"][-50:]  # 保留最近50条
    save_user_profile(profile)


def content_based_recommend(df: pd.DataFrame, profile: dict, top_n: int = 10) -> pd.DataFrame:
    """基于内容的推荐"""
    if df.empty or not profile.get("interests"):
        return df.head(top_n)

    # 构建用户兴趣文本
    user_text = " ".join(profile["interests"])
    if profile.get("search_history"):
        user_text += " " + " ".join(profile["search_history"][-10:])

    # 构建文献文本
    paper_texts = (df["title"].fillna("") + " " + df["abstract"].fillna("")).tolist()
    all_texts = [user_text] + paper_texts

    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words="english",
    )
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # 计算用户与每篇文献的相似度
    user_vec = tfidf_matrix[0:1]
    paper_vecs = tfidf_matrix[1:]
    similarities = cosine_similarity(user_vec, paper_vecs).flatten()

    df = df.copy()
    df["relevance_score"] = similarities

    # 排除已读论文
    read_papers = set(profile.get("read_papers", []))
    df_unread = df[~df["title"].isin(read_papers)]

    if df_unread.empty:
        df_unread = df

    return df_unread.nlargest(top_n, "relevance_score")


def similar_paper_recommend(df: pd.DataFrame, target_title: str, top_n: int = 5) -> pd.DataFrame:
    """基于相似度的论文推荐"""
    if df.empty:
        return df

    paper_texts = (df["title"].fillna("") + " " + df["abstract"].fillna("")).tolist()

    vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(paper_texts)

    # 找到目标论文
    target_idx = None
    for i, title in enumerate(df["title"]):
        if title == target_title:
            target_idx = i
            break

    if target_idx is None:
        return df.head(top_n)

    similarities = cosine_similarity(tfidf_matrix[target_idx:target_idx+1], tfidf_matrix).flatten()
    df = df.copy()
    df["similarity"] = similarities

    # 排除自身
    return df[df["title"] != target_title].nlargest(top_n, "similarity")
