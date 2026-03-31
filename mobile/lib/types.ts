// ScholarMind 类型定义

export type ModuleId = "M1" | "M2" | "M3" | "M4" | "M5" | "M6" | "M7" | "M8" | "M9";

export type ModuleStatus = "waiting" | "running" | "completed" | "failed" | "skipped";

export type TaskStatus =
  | "pending"
  | "running"
  | "paused"
  | "review"
  | "completed"
  | "failed"
  | "aborted";

export interface ModuleState {
  module_id: ModuleId;
  status: ModuleStatus;
  percent: number;
  message: string;
}

export interface Task {
  id: string;
  title: string;
  topic: string;
  description?: string;
  status: TaskStatus;
  modules: ModuleState[];
  created_at: string;
  updated_at?: string;
}

export interface LogEntry {
  id: string;
  task_id: string;
  module_id: ModuleId | "system";
  level: "info" | "warn" | "error";
  message: string;
  timestamp: string;
}

export interface ReviewDimension {
  name: string;
  score: number;
  maxScore: number;
  comment: string;
}

export type ReviewDecision = "accept" | "weak_accept" | "weak_reject" | "reject";

export interface ReviewResult {
  task_id: string;
  overall_score: number;
  decision: ReviewDecision;
  dimensions: ReviewDimension[];
  summary: string;
  timestamp: string;
}

export const MODULE_NAMES: Record<ModuleId, string> = {
  M1: "文献调研",
  M2: "研究空白",
  M3: "Idea 生成",
  M4: "代码生成",
  M5: "实验设计",
  M6: "实验执行",
  M7: "结果分析",
  M8: "论文写作",
  M9: "评审打分",
};
