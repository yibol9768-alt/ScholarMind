import type { Task, LogEntry, ReviewResult, ModuleId } from "./types";

export interface ModuleIODetail {
  moduleId: ModuleId;
  input: string;
  output: string;
  keyFindings?: string[];
  duration: string;
  hasReview?: boolean;
}

export const DEMO_TASKS: Task[] = [
  {
    id: "demo-1",
    title: "LLM 在科学发现中的应用研究",
    topic: "大语言模型在科学发现中的应用，包括假设生成、实验设计和论文写作的自动化",
    description: "研究领域: NLP / 自然语言处理\n目标会议/期刊: NeurIPS",
    status: "running",
    modules: [
      { module_id: "M1", status: "completed", percent: 100, message: "已检索 47 篇相关论文" },
      { module_id: "M2", status: "completed", percent: 100, message: "识别出 3 个研究空白" },
      { module_id: "M3", status: "completed", percent: 100, message: "生成 5 个创新 Idea，最高分 7.8" },
      { module_id: "M4", status: "running", percent: 65, message: "正在生成实验代码..." },
      { module_id: "M5", status: "waiting", percent: 0, message: "等待代码生成完成" },
      { module_id: "M6", status: "waiting", percent: 0, message: "等待实验设计" },
      { module_id: "M7", status: "waiting", percent: 0, message: "等待实验执行" },
      { module_id: "M8", status: "waiting", percent: 0, message: "等待结果分析" },
      { module_id: "M9", status: "waiting", percent: 0, message: "等待论文写作" },
    ],
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "demo-2",
    title: "多模态学习研究空白分析",
    topic: "在多模态学习领域寻找研究空白并提出创新想法",
    status: "completed",
    modules: [
      { module_id: "M1", status: "completed", percent: 100, message: "已检索 62 篇相关论文" },
      { module_id: "M2", status: "completed", percent: 100, message: "识别出 5 个研究空白" },
      { module_id: "M3", status: "completed", percent: 100, message: "生成 8 个 Idea，最高分 8.2" },
      { module_id: "M4", status: "completed", percent: 100, message: "代码仓库已生成" },
      { module_id: "M5", status: "completed", percent: 100, message: "实验方案已设计" },
      { module_id: "M6", status: "completed", percent: 100, message: "5 组实验全部完成" },
      { module_id: "M7", status: "completed", percent: 100, message: "结果达标，F1=0.847" },
      { module_id: "M8", status: "completed", percent: 100, message: "论文 LaTeX 已生成" },
      { module_id: "M9", status: "completed", percent: 100, message: "综合评分 6.8/10" },
    ],
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: "demo-3",
    title: "图神经网络论文写作",
    topic: "基于实验结果，撰写一篇关于图神经网络的学术论文",
    description: "运行模块: M8, M9",
    status: "paused",
    modules: [
      { module_id: "M8", status: "running", percent: 40, message: "正在撰写方法论章节..." },
      { module_id: "M9", status: "waiting", percent: 0, message: "等待论文写作" },
    ],
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: "demo-4",
    title: "Transformer 时间序列预测实验",
    topic: "复现 Transformer 架构在时间序列预测上的实验",
    status: "failed",
    modules: [
      { module_id: "M4", status: "completed", percent: 100, message: "代码已生成" },
      { module_id: "M5", status: "completed", percent: 100, message: "实验方案已设计" },
      { module_id: "M6", status: "failed", percent: 30, message: "CUDA OOM: GPU 内存不足" },
      { module_id: "M7", status: "skipped", percent: 0, message: "已跳过" },
    ],
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
];

export const DEMO_LOGS: LogEntry[] = [
  { id: "log-1", task_id: "demo-1", module_id: "M1", level: "info", message: "开始文献调研，搜索关键词: LLM scientific discovery", timestamp: new Date(Date.now() - 3500000).toISOString() },
  { id: "log-2", task_id: "demo-1", module_id: "M1", level: "info", message: "Brave Search 返回 120 条结果，开始筛选", timestamp: new Date(Date.now() - 3400000).toISOString() },
  { id: "log-3", task_id: "demo-1", module_id: "M1", level: "info", message: "Semantic Scholar 检索到 47 篇高相关论文", timestamp: new Date(Date.now() - 3300000).toISOString() },
  { id: "log-4", task_id: "demo-1", module_id: "M2", level: "info", message: "开始分析文献空白，构建 RAG 索引", timestamp: new Date(Date.now() - 3200000).toISOString() },
  { id: "log-5", task_id: "demo-1", module_id: "M2", level: "warn", message: "Semantic Scholar API 限流，等待 30s 后重试", timestamp: new Date(Date.now() - 3100000).toISOString() },
  { id: "log-6", task_id: "demo-1", module_id: "M2", level: "info", message: "识别出 3 个研究空白方向", timestamp: new Date(Date.now() - 3000000).toISOString() },
  { id: "log-7", task_id: "demo-1", module_id: "M3", level: "info", message: "开始树搜索 Idea 生成，深度=3", timestamp: new Date(Date.now() - 2900000).toISOString() },
  { id: "log-8", task_id: "demo-1", module_id: "M3", level: "info", message: "生成 5 个候选 Idea，进行新颖性检查", timestamp: new Date(Date.now() - 2800000).toISOString() },
  { id: "log-9", task_id: "demo-1", module_id: "M4", level: "info", message: "Aider 开始生成实验代码仓库", timestamp: new Date(Date.now() - 2700000).toISOString() },
  { id: "log-10", task_id: "demo-1", module_id: "M4", level: "info", message: "正在生成 model.py, train.py, evaluate.py...", timestamp: new Date(Date.now() - 2600000).toISOString() },
];

export const DEMO_REVIEW: ReviewResult = {
  task_id: "demo-2",
  overall_score: 6.8,
  decision: "weak_accept",
  dimensions: [
    { name: "新颖性", score: 7, maxScore: 10, comment: "提出了一种新的多模态融合方法，在视觉-语言对齐方面有创新" },
    { name: "方法论", score: 7, maxScore: 10, comment: "方法设计合理，理论基础扎实，但缺少与最新 baseline 的对比" },
    { name: "实验设计", score: 6, maxScore: 10, comment: "实验覆盖了主要数据集，但消融实验不够充分" },
    { name: "写作质量", score: 7, maxScore: 10, comment: "论文结构清晰，语言流畅，图表质量较高" },
    { name: "影响力", score: 7, maxScore: 10, comment: "研究方向有较大应用前景，但需要更多实际场景验证" },
  ],
  summary: "本文提出了一种基于注意力机制的多模态融合框架，在多个基准数据集上取得了有竞争力的结果。主要优点是方法新颖且实验结果稳定，但消融实验和与最新方法的对比有待加强。建议补充更多分析后可考虑接收。",
  timestamp: new Date(Date.now() - 43200000).toISOString(),
};

export const DEMO_MODULE_IO: ModuleIODetail[] = [
  { moduleId: "M1", input: "研究主题关键词", output: "文献综述报告 + 47 篇论文列表", keyFindings: ["LLM 在假设生成方面表现优异", "自动实验设计仍是开放问题", "多智能体协作是新趋势"], duration: "5-10 分钟", hasReview: false },
  { moduleId: "M2", input: "M1 文献综述", output: "3 个研究空白方向 + 可行性评估", keyFindings: ["跨领域知识迁移不足", "实验可重复性验证缺失", "人机协作模式待探索"], duration: "3-5 分钟", hasReview: false },
  { moduleId: "M3", input: "研究空白 + 文献", output: "5 个创新 Idea + 打分排名", keyFindings: ["最高分 Idea: 基于 LLM 的自动假设验证框架", "新颖性检查通过率 60%"], duration: "5-8 分钟", hasReview: true },
  { moduleId: "M4", input: "最优 Idea 描述", output: "完整实验代码仓库", duration: "8-15 分钟", hasReview: false },
  { moduleId: "M5", input: "代码仓库 + Idea", output: "实验方案 + 超参搜索空间", duration: "3-5 分钟", hasReview: false },
  { moduleId: "M6", input: "实验方案 + 代码", output: "实验结果 + final_info.json", duration: "10-30 分钟", hasReview: false },
  { moduleId: "M7", input: "实验结果数据", output: "分析报告 + 是否达标判断", duration: "2-3 分钟", hasReview: true },
  { moduleId: "M8", input: "全部前序产出", output: "LaTeX 论文源文件", keyFindings: ["5 阶段写作: 大纲→逐节→一致性→引用→审计"], duration: "10-20 分钟", hasReview: false },
  { moduleId: "M9", input: "论文 + 文献库", output: "NeurIPS 风格评审报告", duration: "5-8 分钟", hasReview: false },
];
