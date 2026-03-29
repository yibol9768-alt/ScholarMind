"""文献数据收集与预处理模块
支持 OpenAlex（主力，免费无限频）、arXiv、Semantic Scholar 三大数据源。
"""

import json
import os
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import requests

from config import DATA_DIR, S2_API_KEY

# OpenAlex polite pool (提供 email 可获更高限频)
OPENALEX_EMAIL = "scholarmind@example.com"


def search_openalex(query: str, max_results: int = 50, sort_by: str = "relevance") -> list[dict]:
    """从 OpenAlex 搜索文献（免费，无限频限制，2.5亿+文献）"""
    url = "https://api.openalex.org/works"
    sort_map = {
        "relevance": "relevance_score:desc",
        "date": "publication_date:desc",
        "cited": "cited_by_count:desc",
    }
    params = {
        "search": query,
        "per_page": min(max_results, 100),
        "sort": sort_map.get(sort_by, "relevance_score:desc"),
        "mailto": OPENALEX_EMAIL,
    }
    papers = []
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("results", []):
            # 提取作者
            authors = []
            for authorship in item.get("authorships", []):
                name = authorship.get("author", {}).get("display_name", "")
                if name:
                    authors.append(name)

            # 提取关键词/概念
            keywords = []
            for concept in item.get("concepts", [])[:8]:
                kw = concept.get("display_name", "")
                if kw:
                    keywords.append(kw)

            # 提取领域
            categories = []
            for topic in item.get("topics", [])[:5]:
                cat = topic.get("display_name", "")
                if cat:
                    categories.append(cat)

            paper = {
                "id": item.get("id", ""),
                "title": item.get("title", "") or "",
                "abstract": _reconstruct_abstract(item.get("abstract_inverted_index")),
                "authors": authors,
                "published": item.get("publication_date", "") or "",
                "updated": "",
                "categories": categories,
                "doi": item.get("doi", "") or "",
                "pdf_url": (item.get("primary_location") or {}).get("pdf_url", "") or
                           (item.get("best_oa_location") or {}).get("pdf_url", "") or "",
                "source": "openalex",
                "keywords": keywords,
                "citation_count": item.get("cited_by_count", 0) or 0,
                "reference_count": len(item.get("referenced_works", [])),
            }
            if paper["title"]:  # 过滤无标题
                papers.append(paper)
    except Exception as e:
        print(f"OpenAlex API error: {e}")
    return papers


def _reconstruct_abstract(inverted_index: dict | None) -> str:
    """从 OpenAlex 倒排索引重建摘要文本"""
    if not inverted_index:
        return ""
    try:
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return " ".join(w for _, w in word_positions)
    except Exception:
        return ""


def search_arxiv(query: str, max_results: int = 50, sort_by: str = "relevance") -> list[dict]:
    """从 arXiv 搜索文献（有限频限制，作为备选）"""
    try:
        import arxiv
        sort_map = {
            "relevance": arxiv.SortCriterion.Relevance,
            "date": arxiv.SortCriterion.SubmittedDate,
        }
        client = arxiv.Client(num_retries=3, page_size=min(max_results, 50))
        search = arxiv.Search(
            query=query,
            max_results=min(max_results, 50),  # 限制数量减少429
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
    """从 Semantic Scholar 搜索文献（有限频限制，作为备选）"""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY

    params = {
        "query": query,
        "limit": min(max_results, 50),
        "fields": "title,abstract,authors,year,citationCount,referenceCount,fieldsOfStudy,publicationDate,externalIds,url",
    }
    if year:
        params["year"] = year

    papers = []
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code == 429:
                wait = 3 * (attempt + 1)
                print(f"S2 rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
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
            break
        except Exception as e:
            print(f"Semantic Scholar API error (attempt {attempt+1}): {e}")
            if attempt < 2:
                time.sleep(2)
    return papers


def get_paper_citations(paper_id: str) -> list[dict]:
    """获取论文的引用关系"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    params = {"fields": "title,authors,year,citationCount", "limit": 50}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
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
    params = {"fields": "title,authors,year,citationCount", "limit": 50}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
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
    df = df.drop_duplicates(subset=["title"], keep="first")
    df["title"] = df["title"].str.strip().str.replace(r"\s+", " ", regex=True)
    df["abstract"] = df["abstract"].str.strip().str.replace(r"\s+", " ", regex=True)
    df["published"] = pd.to_datetime(df["published"], errors="coerce")
    df["year"] = df["published"].dt.year
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
