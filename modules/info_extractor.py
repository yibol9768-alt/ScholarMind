"""关键信息提取与知识图谱构建模块
利用LLM从文献中提取关键信息，构建知识图谱。
"""

import json
import re
from collections import Counter, defaultdict

import networkx as nx
import pandas as pd
from openai import OpenAI

from config import MODEL_NAME, OPENAI_API_KEY, OPENAI_BASE_URL


def get_llm_client():
    """获取LLM客户端"""
    if not OPENAI_API_KEY:
        return None
    return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


def extract_keywords_llm(title: str, abstract: str) -> list[str]:
    """使用LLM提取关键词"""
    client = get_llm_client()
    if not client or not abstract:
        return []
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个学术文献分析专家。请从给定的论文标题和摘要中提取5-8个核心关键词，以JSON数组形式返回。只返回JSON数组，不要其他内容。"},
                {"role": "user", "content": f"标题：{title}\n摘要：{abstract}"},
            ],
            temperature=0.1,
            max_tokens=200,
        )
        text = resp.choices[0].message.content.strip()
        # 尝试解析JSON
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []
    except Exception as e:
        print(f"LLM keyword extraction error: {e}")
        return []


def extract_keywords_tfidf(df: pd.DataFrame, top_n: int = 8) -> dict[str, list[str]]:
    """使用TF-IDF提取关键词（不依赖LLM的备选方案）"""
    from sklearn.feature_extraction.text import TfidfVectorizer

    texts = (df["title"] + " " + df["abstract"]).tolist()
    if not texts:
        return {}

    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.9,
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    result = {}
    for i, row in enumerate(tfidf_matrix):
        scores = row.toarray().flatten()
        top_indices = scores.argsort()[-top_n:][::-1]
        keywords = [feature_names[j] for j in top_indices if scores[j] > 0]
        result[df.iloc[i]["title"]] = keywords
    return result


def batch_extract_info_llm(papers: list[dict], batch_size: int = 5) -> list[dict]:
    """批量使用LLM提取论文关键信息"""
    client = get_llm_client()
    if not client:
        return papers

    results = []
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i + batch_size]
        papers_text = ""
        for j, p in enumerate(batch):
            papers_text += f"\n论文{j+1}:\n标题: {p.get('title','')}\n摘要: {p.get('abstract','')[:500]}\n\n"

        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": """你是学术文献分析专家。对于每篇论文，请提取以下信息并以JSON数组格式返回：
- keywords: 5-8个核心关键词
- research_method: 研究方法（实验/理论/综述/模拟等）
- main_contribution: 一句话概括主要贡献
- research_field: 研究领域
只返回JSON数组，不要其他内容。"""},
                    {"role": "user", "content": papers_text},
                ],
                temperature=0.1,
                max_tokens=1500,
            )
            text = resp.choices[0].message.content.strip()
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                extracted = json.loads(match.group())
                for j, p in enumerate(batch):
                    if j < len(extracted):
                        p.update(extracted[j])
                    results.append(p)
            else:
                results.extend(batch)
        except Exception as e:
            print(f"Batch extraction error: {e}")
            results.extend(batch)
    return results


def build_knowledge_graph(df: pd.DataFrame) -> nx.Graph:
    """构建知识图谱：论文-作者-关键词关系网络"""
    G = nx.Graph()

    for _, row in df.iterrows():
        title = row["title"]
        # 添加论文节点
        G.add_node(title, type="paper", year=row.get("year"),
                    citation_count=row.get("citation_count", 0))

        # 添加作者节点和边
        authors = row.get("authors", [])
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",")]
        for author in authors[:5]:  # 限制作者数量
            if author:
                G.add_node(author, type="author")
                G.add_edge(title, author, relation="authored_by")

        # 添加关键词节点和边
        keywords = row.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",")]
        for kw in keywords[:8]:
            if kw:
                G.add_node(kw, type="keyword")
                G.add_edge(title, kw, relation="has_keyword")

    return G


def build_author_collaboration_network(df: pd.DataFrame) -> nx.Graph:
    """构建作者合作网络"""
    G = nx.Graph()
    author_paper_count = Counter()

    for _, row in df.iterrows():
        authors = row.get("authors", [])
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",")]

        for author in authors:
            if author:
                author_paper_count[author] += 1

        # 建立共同作者关系
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                if authors[i] and authors[j]:
                    if G.has_edge(authors[i], authors[j]):
                        G[authors[i]][authors[j]]["weight"] += 1
                    else:
                        G.add_edge(authors[i], authors[j], weight=1)

    # 设置节点属性
    for author, count in author_paper_count.items():
        if G.has_node(author):
            G.nodes[author]["paper_count"] = count

    return G


def build_citation_network(papers_with_refs: list[dict]) -> nx.DiGraph:
    """构建引用网络"""
    G = nx.DiGraph()
    for paper in papers_with_refs:
        title = paper.get("title", "")
        G.add_node(title, **{k: v for k, v in paper.items() if k != "references"})
        for ref in paper.get("references", []):
            ref_title = ref.get("title", "")
            if ref_title:
                G.add_node(ref_title)
                G.add_edge(title, ref_title, relation="cites")
    return G
