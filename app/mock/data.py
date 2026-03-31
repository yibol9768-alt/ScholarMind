from __future__ import annotations

WORKFLOW_STEPS = [
    ("exploration", "领域探索与科研入门"),
    ("collection", "文献获取与预处理"),
    ("extraction", "关键信息提取"),
    ("trends", "主题建模与趋势分析"),
    ("gaps", "研究空白识别与选题开题"),
    ("ideas", "可信 Idea 生成与打分"),
    ("repository", "生成代码仓库"),
    ("experiment_design", "实验设计与研究实施"),
    ("agent_run", "自动化进行 Agent 实验"),
    ("results", "结果分析"),
    ("writing", "论文写作"),
    ("validation", "可信验证与全程可追溯支持"),
]

USER_PROFILE = {
    "name": "林知行",
    "role": "计算机学院 · 博士三年级",
    "email": "lin.zhixing@scholarmind.ai",
}

HISTORY_GROUPS = [
    {
        "title": "今天",
        "items": [
            {"id": "conv-1", "title": "多模态医学文献趋势分析", "page": "trends"},
            {"id": "conv-2", "title": "RAG 综述论文摘要整理", "page": "collection"},
            {"id": "conv-3", "title": "知识图谱构建可行性", "page": "extraction"},
        ],
    },
    {
        "title": "近 7 天",
        "items": [
            {"id": "conv-4", "title": "研究空白识别与开题准备", "page": "gaps"},
            {"id": "conv-5", "title": "实验复现实验日志审阅", "page": "results"},
        ],
    },
    {
        "title": "近 30 天",
        "items": [
            {"id": "conv-6", "title": "论文引言自动生成草稿", "page": "writing"},
            {"id": "conv-7", "title": "可信验证审计链检查", "page": "validation"},
        ],
    },
]

CHAT_SUGGESTIONS = [
    {
        "title": "分析研究趋势",
        "desc": "识别近三年热点主题和主题演化",
        "prompt": "请帮我分析多模态医学文献的研究趋势，并给出值得继续跟踪的主题。",
        "target": "trends",
    },
    {
        "title": "总结 RAG 文献",
        "desc": "快速汇总高被引论文与关键结论",
        "prompt": "请总结 RAG 方向近三年的代表性论文与主要结论。",
        "target": "collection",
    },
    {
        "title": "抽取知识网络",
        "desc": "构建作者、方法、任务的关系视图",
        "prompt": "请从现有文献中抽取知识网络，并展示作者、方法与任务之间的联系。",
        "target": "extraction",
    },
    {
        "title": "识别研究空白",
        "desc": "定位尚未被充分验证的问题空间",
        "prompt": "请根据当前热点与已有工作，识别值得切入的研究空白。",
        "target": "gaps",
    },
    {
        "title": "生成研究 Idea",
        "desc": "输出候选研究想法并做可信评分",
        "prompt": "请基于当前研究空白生成 3 个可执行的研究 idea，并给出创新性与可行性评分。",
        "target": "ideas",
    },
    {
        "title": "查看实验进展",
        "desc": "进入自动化 Agent 实验运行看板",
        "prompt": "请展示当前 Agent 实验的运行进展与异常项。",
        "target": "agent_run",
    },
]

CHAT_MESSAGES = [
    {"role": "assistant", "content": "欢迎回来。你可以从聊天开始，也可以直接进入工作流页面继续推进你的科研项目。"},
    {"role": "assistant", "content": "当前项目已经完成文献获取与结构化抽取，趋势分析结果待确认。"},
]

EXPLORATION_RESULT = {
    "keywords": ["多模态学习", "医学影像报告", "临床问答", "检索增强生成", "可信 AI"],
    "summary": "该方向聚焦于将医学影像、文本病历与大模型推理结合，用于临床问答、报告生成与文献辅助诊断。",
    "directions": ["医学影像与文本联合检索", "临床场景下的可信 RAG", "模型解释性与事实核验"],
    "papers": [
        "Med-PaLM 2 for medical question answering",
        "Multimodal RAG in Radiology Reports",
        "Trustworthy LLMs for Clinical Decision Support",
    ],
    "authors": ["Greg Corrado", "Eric Topol", "Zhengliang Liu"],
    "institutions": ["Google Research", "Stanford", "Mayo Clinic"],
}

COLLECTION_SOURCES = ["arXiv", "PubMed", "Crossref", "Semantic Scholar"]
LITERATURE_RESULTS = [
    ("Multimodal Retrieval-Augmented Generation for Radiology", "2025", "PubMed"),
    ("Trustworthy Clinical LLMs with Citation Grounding", "2024", "Semantic Scholar"),
    ("Benchmarking Med-RAG Pipelines", "2024", "arXiv"),
    ("Multi-agent Literature Mining in Biomedicine", "2023", "Crossref"),
]
EXTRACTION_CARDS = [
    ("作者提取", "共识别 86 位作者，12 个核心合作团体"),
    ("摘要提取", "完成 48 篇论文摘要标准化切分"),
    ("关键词提取", "识别高频术语 132 个，已归并同义词"),
    ("引用关系", "构建引用边 284 条，检测到 4 个核心簇"),
    ("实体识别", "识别疾病、方法、数据集等实体 210 个"),
]
TREND_TOPICS = [
    ("可信 RAG", "热度 +18%", "临床问答、证据链"),
    ("多智能体科研流程", "热度 +13%", "自动综述、实验编排"),
    ("医学多模态对齐", "热度 +10%", "图像-文本联合建模"),
]
TREND_RANKING = [
    "Trustworthy Medical RAG Systems",
    "Agentic Literature Review Frameworks",
    "Clinical Evidence Alignment with LLMs",
]
GAP_ITEMS = [
    {
        "title": "面向临床事实核验的细粒度证据绑定",
        "reason": "现有研究多停留在段落级引用，缺乏句级证据与图像证据协同验证。",
        "risk": "需要高质量标注数据集",
    },
    {
        "title": "多智能体综述流程的错误传递控制",
        "reason": "多数工作关注效率，较少讨论 Agent 间错误累积与校正机制。",
        "risk": "实验流程复杂，评估成本较高",
    },
    {
        "title": "医学多模态 RAG 的可复现基准",
        "reason": "公开 benchmark 缺失，结果可比性弱。",
        "risk": "需要统一任务定义与数据许可",
    },
]
IDEAS = [
    {
        "id": "idea-1",
        "title": "句级证据绑定的医学多模态 RAG",
        "core": "在检索与生成之间加入句级证据绑定层，并联动影像证据。",
        "innovation": 91,
        "feasibility": 78,
        "risk": "中",
        "reason": "兼顾临床可信性与系统可实现性，适合做主线选题。",
        "detail": "推荐先从放射报告场景切入，构建句级引用标注和对照实验。",
    },
    {
        "id": "idea-2",
        "title": "多 Agent 综述工作流中的自校验机制",
        "core": "为不同 Agent 增加交叉审稿与证据回查模块。",
        "innovation": 86,
        "feasibility": 81,
        "risk": "低",
        "reason": "工程成本可控，适合快速演示和论文投稿。",
        "detail": "可使用 reviewer agent 复核摘要、方法与引用链是否一致。",
    },
    {
        "id": "idea-3",
        "title": "医学多模态 RAG 统一基准生成器",
        "core": "自动整理数据源、任务定义与评价协议，生成 benchmark 模板。",
        "innovation": 83,
        "feasibility": 74,
        "risk": "中高",
        "reason": "社区价值高，但基准设计工作量较大。",
        "detail": "适合作为中长期项目，前期先做小规模试点数据集。",
    },
]
REPOSITORY_TREE = {
    "README.md": "# ScholarMind Experiment\n\nA prototype repository generated from the selected idea.\n",
    "configs/experiment.yaml": "dataset: med-rag\nmodel: qwen2.5\nretriever: bge-m3\n",
    "src/pipeline.py": "class Pipeline:\n    def run(self):\n        return 'mock run'\n",
    "src/retrieval/evidence_linker.py": "def bind_sentence_evidence():\n    return []\n",
    "scripts/train.sh": "python -m src.pipeline\n",
    "reports/template.md": "## Result Summary\n\n- Metrics\n- Error cases\n",
}
EXPERIMENT_CONFIG = {
    "plans": ["基础对照实验", "证据绑定实验", "消融实验"],
    "datasets": ["MedQA", "MIMIC-CXR", "PubMedQA"],
    "models": ["Qwen2.5-32B", "Llama-3.1-70B", "Mixtral-8x22B"],
    "params": ["batch=8", "lr=1e-5", "epoch=3", "retrieval_topk=5"],
}
AGENT_SUBTASKS = [
    ("数据清洗", "completed"),
    ("证据索引构建", "completed"),
    ("RAG 基线实验", "running"),
    ("误差案例归因", "pending"),
    ("实验报告汇总", "pending"),
]
AGENT_LOGS = [
    "[09:10:12] 初始化实验工作区",
    "[09:10:21] 加载数据集 MIMIC-CXR",
    "[09:10:47] 建立向量索引",
    "[09:11:03] 启动基线实验",
    "[09:11:25] 同步 reviewer agent 规则",
    "[09:11:58] 收集第一批验证结果",
]
RESULT_METRICS = [
    ("Citation Precision", "91.2%", "+5.2%"),
    ("Answer Faithfulness", "88.6%", "+4.8%"),
    ("Clinical Consistency", "84.1%", "+2.6%"),
    ("Latency", "1.8s", "-0.3s"),
]
WRITING_SECTIONS = {
    "摘要": "本文提出一种句级证据绑定的医学多模态 RAG 框架，以提升临床问答中的可追溯性与事实一致性。",
    "引言": "随着大模型在科研和医疗场景中的广泛应用，如何让生成内容具备可靠证据支撑成为关键问题。",
    "相关工作": "现有工作主要集中于 RAG、临床问答和多模态对齐，但缺乏针对证据粒度的系统研究。",
    "方法": "我们设计 Evidence Linker 模块，在检索结果、生成句子与影像证据之间建立显式绑定关系。",
    "实验": "在 MIMIC-CXR 与 PubMedQA 数据集上进行对比实验，并设计多维度可信性评估指标。",
    "结论": "方法在引用精度、事实一致性和可解释性方面均优于基线模型，适合进一步扩展至临床辅助决策。",
}
VALIDATION_TIMELINE = [
    "文献抓取结果已记录源站与时间戳",
    "知识抽取过程已保存实体版本",
    "Idea 评分依据与风险解释已归档",
    "实验参数与日志可追溯",
    "论文段落与引用来源已建立映射",
]
