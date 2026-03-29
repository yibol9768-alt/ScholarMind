"""文献数据收集与预处理模块
从arXiv和Semantic Scholar抓取文献数据，清洗、标准化和存储。
"""

import json
import os
import time
from datetime import datetime
from typing import Optional

import arxiv
import pandas as pd
import requests

from config import DATA_DIR, S2_API_KEY


def search_arxiv(query: str, max_results: int = 50, sort_by: str = "relevance") -> list[dict]:
    """从arXiv搜索文献"""
    sort_map = {
        "relevance": arxiv.SortCriterion.Relevance,
        "date": arxiv.SortCriterion.SubmittedDate,
    }
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_map.get(sort_by, arxiv.SortCriterion.Relevance),
        )
        papers = []
        for result in client.results(search):
            paper = {
                "id": result.entry_id,
                "title": result.title,
                "abstract": result.summary,
                "authors": [a.name for a in result.authors],
                "published": result.published.strftime("%Y-%m-%d") if result.published else "",
                "updated": result.updated.strftime("%Y-%m-%d") if result.updated else "",
                "categories": result.categories,
                "doi": result.doi or "",
                "pdf_url": result.pdf_url or "",
                "source": "arxiv",
                "keywords": result.categories,
                "citation_count": 0,
                "reference_count": 0,
            }
            papers.append(paper)
        return papers
    except Exception as e:
        print(f"arXiv API error: {e}")
        return []


def search_semantic_scholar(query: str, max_results: int = 50, year: Optional[str] = None) -> list[dict]:
    """从Semantic Scholar搜索文献"""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY

    params = {
        "query": query,
        "limit": min(max_results, 100),
        "fields": "title,abstract,authors,year,citationCount,referenceCount,fieldsOfStudy,publicationDate,externalIds,url",
    }
    if year:
        params["year"] = year

    papers = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            paper = {
                "id": item.get("paperId", ""),
                "title": item.get("title", ""),
                "abstract": item.get("abstract", "") or "",
                "authors": [a.get("name", "") for a in item.get("authors", [])],
                "published": item.get("publicationDate", "") or "",
                "updated": "",
                "categories": item.get("fieldsOfStudy", []) or [],
                "doi": (item.get("externalIds") or {}).get("DOI", ""),
                "pdf_url": item.get("url", ""),
                "source": "semantic_scholar",
                "keywords": item.get("fieldsOfStudy", []) or [],
                "citation_count": item.get("citationCount", 0),
                "reference_count": item.get("referenceCount", 0),
            }
            papers.append(paper)
    except Exception as e:
        print(f"Semantic Scholar API error: {e}")
    return papers


def get_paper_citations(paper_id: str) -> list[dict]:
    """获取论文的引用关系"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    params = {
        "fields": "title,authors,year,citationCount",
        "limit": 50,
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "id": c["citingPaper"].get("paperId", ""),
                "title": c["citingPaper"].get("title", ""),
                "authors": [a.get("name", "") for a in c["citingPaper"].get("authors", [])],
                "year": c["citingPaper"].get("year"),
                "citation_count": c["citingPaper"].get("citationCount", 0),
            }
            for c in data.get("data", [])
            if c.get("citingPaper", {}).get("title")
        ]
    except Exception:
        return []


def get_paper_references(paper_id: str) -> list[dict]:
    """获取论文的参考文献"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    params = {
        "fields": "title,authors,year,citationCount",
        "limit": 50,
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "id": r["citedPaper"].get("paperId", ""),
                "title": r["citedPaper"].get("title", ""),
                "authors": [a.get("name", "") for a in r["citedPaper"].get("authors", [])],
                "year": r["citedPaper"].get("year"),
                "citation_count": r["citedPaper"].get("citationCount", 0),
            }
            for r in data.get("data", [])
            if r.get("citedPaper", {}).get("title")
        ]
    except Exception:
        return []


def clean_and_standardize(papers: list[dict]) -> pd.DataFrame:
    """清洗和标准化文献数据"""
    df = pd.DataFrame(papers)
    if df.empty:
        return df
    # 去重
    df = df.drop_duplicates(subset=["title"], keep="first")
    # 清洗文本
    df["title"] = df["title"].str.strip().str.replace(r"\s+", " ", regex=True)
    df["abstract"] = df["abstract"].str.strip().str.replace(r"\s+", " ", regex=True)
    # 标准化日期
    df["published"] = pd.to_datetime(df["published"], errors="coerce")
    df["year"] = df["published"].dt.year
    # 填充缺失值
    df["abstract"] = df["abstract"].fillna("")
    if "citation_count" not in df.columns:
        df["citation_count"] = 0
    df["citation_count"] = df["citation_count"].fillna(0).astype(int)
    if "reference_count" not in df.columns:
        df["reference_count"] = 0
    df["reference_count"] = df["reference_count"].fillna(0).astype(int)
    return df.reset_index(drop=True)


def save_papers(df: pd.DataFrame, filename: str = "papers.json"):
    """保存文献数据到JSON文件"""
    path = os.path.join(DATA_DIR, filename)
    df.to_json(path, orient="records", force_ascii=False, indent=2, date_format="iso")
    return path


def load_papers(filename: str = "papers.json") -> pd.DataFrame:
    """加载已保存的文献数据"""
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            df = pd.read_json(path, orient="records")
            df["published"] = pd.to_datetime(df["published"], errors="coerce")
            df["year"] = df["published"].dt.year
            if "citation_count" not in df.columns:
                df["citation_count"] = 0
            return df
        except Exception as e:
            print(f"Error loading papers: {e}")
            return pd.DataFrame()
    return pd.DataFrame()
