import { createContext, useContext } from "react";
import type { Task, LogEntry, ReviewResult } from "./types";

export interface TaskState {
  tasks: Task[];
  currentTask: Task | null;
  logs: LogEntry[];
  reviewResult: ReviewResult | null;
  loading: boolean;
  error: string | null;
}

export type TaskAction =
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "SET_TASKS"; payload: Task[] }
  | { type: "SET_CURRENT_TASK"; payload: Task | null }
  | { type: "UPDATE_TASK"; payload: Task }
  | { type: "SET_LOGS"; payload: LogEntry[] }
  | { type: "SET_REVIEW"; payload: ReviewResult | null };

export const initialTaskState: TaskState = {
  tasks: [],
  currentTask: null,
  logs: [],
  reviewResult: null,
  loading: false,
  error: null,
};

export function taskReducer(state: TaskState, action: TaskAction): TaskState {
  switch (action.type) {
    case "SET_LOADING":
      return { ...state, loading: action.payload };
    case "SET_ERROR":
      return { ...state, error: action.payload, loading: false };
    case "SET_TASKS":
      return { ...state, tasks: action.payload, loading: false };
    case "SET_CURRENT_TASK":
      return { ...state, currentTask: action.payload, loading: false };
    case "UPDATE_TASK":
      return {
        ...state,
        tasks: state.tasks.map((t) =>
          t.id === action.payload.id ? action.payload : t
        ),
        currentTask:
          state.currentTask?.id === action.payload.id
            ? action.payload
            : state.currentTask,
      };
    case "SET_LOGS":
      return { ...state, logs: action.payload };
    case "SET_REVIEW":
      return { ...state, reviewResult: action.payload };
    default:
      return state;
  }
}

export interface TaskContextValue {
  state: TaskState;
  fetchTasks: () => Promise<void>;
  fetchTask: (id: string) => Promise<void>;
  createTask: (topic: string, description?: string) => Promise<Task>;
  pauseTask: (id: string) => Promise<void>;
  resumeTask: (id: string) => Promise<void>;
  abortTask: (id: string) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  fetchLogs: (taskId: string) => Promise<void>;
  fetchReviewResult: (taskId: string) => Promise<void>;
}

export const TaskContext = createContext<TaskContextValue | null>(null);

export function useTaskContext(): TaskContextValue {
  const ctx = useContext(TaskContext);
  if (!ctx) throw new Error("useTaskContext must be used within TaskProvider");
  return ctx;
}
