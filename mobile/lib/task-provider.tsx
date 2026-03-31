import { useReducer, useCallback, type ReactNode } from "react";
import {
  TaskContext,
  taskReducer,
  initialTaskState,
} from "./task-store";
import {
  isDemoMode,
  fetchTasksApi,
  fetchTaskApi,
  createTaskApi,
  pauseTaskApi,
  resumeTaskApi,
  abortTaskApi,
  deleteTaskApi,
  fetchLogsApi,
  fetchReviewApi,
} from "./api";
import { DEMO_TASKS, DEMO_LOGS, DEMO_REVIEW } from "./mock-data";
import type { Task } from "./types";

export function TaskProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(taskReducer, initialTaskState);

  const fetchTasks = useCallback(async () => {
    dispatch({ type: "SET_LOADING", payload: true });
    dispatch({ type: "SET_ERROR", payload: null });
    try {
      if (isDemoMode()) {
        dispatch({ type: "SET_TASKS", payload: DEMO_TASKS });
        return;
      }
      const tasks = await fetchTasksApi();
      dispatch({ type: "SET_TASKS", payload: tasks });
    } catch (e: any) {
      dispatch({ type: "SET_ERROR", payload: e.message });
      // Fallback to demo data on error
      dispatch({ type: "SET_TASKS", payload: DEMO_TASKS });
    }
  }, []);

  const fetchTask = useCallback(async (id: string) => {
    dispatch({ type: "SET_LOADING", payload: true });
    try {
      if (isDemoMode()) {
        const task = DEMO_TASKS.find((t) => t.id === id) || null;
        dispatch({ type: "SET_CURRENT_TASK", payload: task });
        return;
      }
      const task = await fetchTaskApi(id);
      dispatch({ type: "SET_CURRENT_TASK", payload: task });
    } catch {
      const task = DEMO_TASKS.find((t) => t.id === id) || null;
      dispatch({ type: "SET_CURRENT_TASK", payload: task });
    }
  }, []);

  const createTask = useCallback(
    async (topic: string, description?: string): Promise<Task> => {
      if (isDemoMode()) {
        const newTask: Task = {
          id: `demo-${Date.now()}`,
          title: topic.slice(0, 30),
          topic,
          description,
          status: "pending",
          modules: [
            { module_id: "M1", status: "waiting", percent: 0, message: "等待开始" },
            { module_id: "M2", status: "waiting", percent: 0, message: "等待开始" },
            { module_id: "M3", status: "waiting", percent: 0, message: "等待开始" },
            { module_id: "M4", status: "waiting", percent: 0, message: "等待开始" },
            { module_id: "M5", status: "waiting", percent: 0, message: "等待开始" },
            { module_id: "M6", status: "waiting", percent: 0, message: "等待开始" },
            { module_id: "M7", status: "waiting", percent: 0, message: "等待开始" },
            { module_id: "M8", status: "waiting", percent: 0, message: "等待开始" },
            { module_id: "M9", status: "waiting", percent: 0, message: "等待开始" },
          ],
          created_at: new Date().toISOString(),
        };
        dispatch({
          type: "SET_TASKS",
          payload: [newTask, ...state.tasks],
        });
        return newTask;
      }
      const task = await createTaskApi(topic, description);
      dispatch({ type: "SET_TASKS", payload: [task, ...state.tasks] });
      return task;
    },
    [state.tasks]
  );

  const pauseTask = useCallback(async (id: string) => {
    if (!isDemoMode()) await pauseTaskApi(id);
    dispatch({
      type: "UPDATE_TASK",
      payload: {
        ...(state.currentTask || DEMO_TASKS.find((t) => t.id === id)!),
        status: "paused",
      },
    });
  }, [state.currentTask]);

  const resumeTask = useCallback(async (id: string) => {
    if (!isDemoMode()) await resumeTaskApi(id);
    dispatch({
      type: "UPDATE_TASK",
      payload: {
        ...(state.currentTask || DEMO_TASKS.find((t) => t.id === id)!),
        status: "running",
      },
    });
  }, [state.currentTask]);

  const abortTask = useCallback(async (id: string) => {
    if (!isDemoMode()) await abortTaskApi(id);
    dispatch({
      type: "UPDATE_TASK",
      payload: {
        ...(state.currentTask || DEMO_TASKS.find((t) => t.id === id)!),
        status: "aborted",
      },
    });
  }, [state.currentTask]);

  const deleteTask = useCallback(async (id: string) => {
    if (!isDemoMode()) await deleteTaskApi(id);
    dispatch({
      type: "SET_TASKS",
      payload: state.tasks.filter((t) => t.id !== id),
    });
  }, [state.tasks]);

  const fetchLogs = useCallback(async (taskId: string) => {
    try {
      if (isDemoMode()) {
        dispatch({
          type: "SET_LOGS",
          payload: DEMO_LOGS.filter((l) => l.task_id === taskId),
        });
        return;
      }
      const logs = await fetchLogsApi(taskId);
      dispatch({ type: "SET_LOGS", payload: logs });
    } catch {
      dispatch({
        type: "SET_LOGS",
        payload: DEMO_LOGS.filter((l) => l.task_id === taskId),
      });
    }
  }, []);

  const fetchReviewResult = useCallback(async (taskId: string) => {
    try {
      if (isDemoMode()) {
        dispatch({
          type: "SET_REVIEW",
          payload: taskId === DEMO_REVIEW.task_id ? DEMO_REVIEW : null,
        });
        return;
      }
      const review = await fetchReviewApi(taskId);
      dispatch({ type: "SET_REVIEW", payload: review });
    } catch {
      dispatch({
        type: "SET_REVIEW",
        payload: taskId === DEMO_REVIEW.task_id ? DEMO_REVIEW : null,
      });
    }
  }, []);

  return (
    <TaskContext.Provider
      value={{
        state,
        fetchTasks,
        fetchTask,
        createTask,
        pauseTask,
        resumeTask,
        abortTask,
        deleteTask,
        fetchLogs,
        fetchReviewResult,
      }}
    >
      {children}
    </TaskContext.Provider>
  );
}
