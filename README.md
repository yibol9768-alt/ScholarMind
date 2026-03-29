# 📚 ScholarMind - 智能文献分析系统

> 基于AI大模型的学术文献智能分析、知识挖掘与可视化平台

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
  <img src="https://img.shields.io/badge/LLM-OpenAI Compatible-blueviolet" />
</p>

---

## 项目简介

随着科研产出的快速增长，科研人员面临着海量的学术文献数据。**ScholarMind** 是一个基于AI大模型的智能文献分析系统，能够自动从海量学术文献中提取关键信息，进行深度分析、知识挖掘和交互式编辑，为科研人员提供全面的文献分析报告和洞察。

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit 前端界面                    │
│  ┌──────────┬──────────┬──────────┬──────────┬─────┐ │
│  │ 文献检索  │ 主题趋势  │ 知识图谱  │ 智能推荐  │ 管理 │ │
│  └──────────┴──────────┴──────────┴──────────┴─────┘ │
├─────────────────────────────────────────────────────┤
│                    核心分析引擎                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │
│  │ NLP/LLM     │ │ 主题建模     │ │ 推荐算法         │ │
│  │ 关键词提取   │ │ LDA/KMeans  │ │ TF-IDF相似度    │ │
│  │ 信息抽取    │ │ 趋势分析     │ │ 用户画像        │ │
│  └─────────────┘ └─────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────┤
│                    数据采集层                          │
│  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │   arXiv API      │  │  Semantic Scholar API    │  │
│  └──────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 功能模块

### 1. 文献数据收集与预处理

- 支持从 **arXiv** 和 **Semantic Scholar** 两大学术数据库自动检索
- 自动数据清洗：去重、文本标准化、日期格式统一
- 本地 JSON 持久化存储，支持 CSV/JSON 导出

### 2. 关键信息提取与知识图谱

- **LLM 模式**：调用大模型提取关键词、研究方法、核心贡献等结构化信息
- **TF-IDF 模式**：无需 API 密钥，基于统计方法自动提取关键词
- **知识图谱构建**：基于 NetworkX 构建论文-作者-关键词三元组网络
- **作者合作网络**：自动发现共同作者关系与合作强度
- **引用网络**：追踪论文间引用与被引关系

### 3. 主题建模与趋势分析

- **LDA 主题建模**：自动发现文献集合中的隐含主题
- **TF-IDF + KMeans 聚类**：基于文本相似度的论文聚类分析
- **年度趋势分析**：论文发表数量、引用量随时间变化
- **关键词热度追踪**：年度关键词频率热力图
- **热点识别**：自动识别近年高频关键词和高引用论文

### 4. 智能推荐与个性化服务

- **用户画像系统**：记录研究兴趣、阅读历史、收藏偏好
- **个性化推荐**：基于 TF-IDF + 余弦相似度的内容推荐
- **相似论文发现**：选定论文后自动推荐相似文献
- **阅读标记与收藏**：支持论文阅读状态管理

### 5. 交互式可视化界面

- **论文发表趋势图**（柱状图 + 折线图）
- **引用趋势图**（双轴图表）
- **主题聚类散点图**（降维可视化）
- **关键词频率柱状图**
- **关键词年度热力图**
- **作者合作网络图**（力导向布局）
- **知识图谱网络图**（论文-作者-关键词）
- **高产作者统计**

## 快速启动

### 环境要求

- Python 3.10+
- pip

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/ScholarMind.git
cd ScholarMind

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 LLM API（可选）
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 启动应用

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501` 即可使用。

### LLM 配置说明

系统支持任何 OpenAI 兼容的 API（OpenAI、DeepSeek、通义千问等）：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
```

> **无需 LLM 也可运行**：未配置 API Key 时，系统自动使用 TF-IDF 统计方法替代大模型进行关键词提取和分析。

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端框架** | Streamlit |
| **数据可视化** | Plotly |
| **数据源** | arXiv API, Semantic Scholar API |
| **NLP/ML** | scikit-learn (TF-IDF, LDA, KMeans) |
| **LLM** | OpenAI 兼容 API |
| **知识图谱** | NetworkX |
| **数据处理** | Pandas, NumPy |

## 项目结构

```
ScholarMind/
├── app.py                     # Streamlit 主应用入口
├── config.py                  # 全局配置（API Key、路径等）
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量模板
├── data/                      # 本地数据存储
│   ├── papers.json            # 文献数据缓存
│   ├── user_profile.json      # 用户画像
│   └── notes.json             # 文献标注笔记
├── modules/
│   ├── data_collector.py      # 文献数据收集与预处理
│   ├── info_extractor.py      # 关键信息提取与知识图谱
│   ├── topic_analyzer.py      # 主题建模与趋势分析
│   ├── recommender.py         # 智能推荐引擎
│   └── visualizer.py          # 可视化图表生成
└── static/                    # 静态资源
```

## 使用演示

### 文献检索

输入研究关键词（如 "large language model"），系统自动从 arXiv 和 Semantic Scholar 检索相关文献，进行清洗和标准化处理后展示。

### 主题分析

选择 LDA 或 KMeans 方法，设定主题数量，系统自动进行主题建模并生成可视化报告，包括主题关键词、聚类散点图、趋势热力图等。

### 知识图谱

自动构建三种网络：
- **作者合作网络**：展示研究者之间的协作关系
- **关键词共现网络**：发现研究主题之间的关联
- **论文-作者-关键词图谱**：全景式知识结构展示

### 智能推荐

基于用户研究兴趣和阅读历史，自动推荐相关文献；支持选定任一论文查找相似文献。

## License

MIT License
