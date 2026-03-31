import AsyncStorage from "@react-native-async-storage/async-storage";
import type { Task, LogEntry, ReviewResult } from "./types";

const BACKEND_URL_KEY = "scholarmind_backend_url";
const DEMO_MODE_KEY = "scholarmind_demo_mode";

let cachedUrl: string | null = null;
let _isDemoMode: boolean | null = null;

export async function getBackendUrl(): Promise<string> {
  if (cachedUrl !== null) return cachedUrl;
  const stored = await AsyncStorage.getItem(BACKEND_URL_KEY);
  cachedUrl = stored || "";
  return cachedUrl;
}

export async function setBackendUrl(url: string): Promise<void> {
  const trimmed = url.replace(/\/+$/, "");
  cachedUrl = trimmed;
  await AsyncStorage.setItem(BACKEND_URL_KEY, trimmed);
  // Reset demo mode cache
  _isDemoMode = null;
}

export function isDemoMode(): boolean {
  if (_isDemoMode !== null) return _isDemoMode;
  // If no cached URL yet, assume demo mode
  if (cachedUrl === null) return true;
  return cachedUrl === "";
}

export async function testConnection(url?: string): Promise<boolean> {
  const base = url?.replace(/\/+$/, "") || (await getBackendUrl());
  if (!base) return false;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    const res = await fetch(`${base}/api/trpc/tasks.list`, {
      signal: controller.signal,
    });
    clearTimeout(timeout);
    return res.ok || res.status === 200;
  } catch {
    return false;
  }
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const base = await getBackendUrl();
  if (!base) throw new Error("未配置后端地址");
  const res = await fetch(`${base}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Task APIs
export async function fetchTasksApi(): Promise<Task[]> {
  const result = await apiFetch<{ result: { data: { json: Task[] } } }>(
    "/api/trpc/tasks.list"
  );
  return result?.result?.data?.json ?? [];
}

export async function fetchTaskApi(id: string): Promise<Task> {
  const input = encodeURIComponent(JSON.stringify({ 0: { json: { id } } }));
  const result = await apiFetch<any>(`/api/trpc/tasks.get?batch=1&input=${input}`);
  return result?.[0]?.result?.data?.json;
}

export async function createTaskApi(
  topic: string,
  description?: string
): Promise<Task> {
  const result = await apiFetch<any>("/api/trpc/tasks.create", {
    method: "POST",
    body: JSON.stringify({ "0": { json: { topic, description } } }),
  });
  return result?.[0]?.result?.data?.json;
}

export async function pauseTaskApi(id: string): Promise<void> {
  await apiFetch("/api/trpc/tasks.pause", {
    method: "POST",
    body: JSON.stringify({ "0": { json: { id } } }),
  });
}

export async function resumeTaskApi(id: string): Promise<void> {
  await apiFetch("/api/trpc/tasks.resume", {
    method: "POST",
    body: JSON.stringify({ "0": { json: { id } } }),
  });
}

export async function abortTaskApi(id: string): Promise<void> {
  await apiFetch("/api/trpc/tasks.abort", {
    method: "POST",
    body: JSON.stringify({ "0": { json: { id } } }),
  });
}

export async function deleteTaskApi(id: string): Promise<void> {
  await apiFetch("/api/trpc/tasks.delete", {
    method: "POST",
    body: JSON.stringify({ "0": { json: { id } } }),
  });
}

export async function fetchLogsApi(taskId: string): Promise<LogEntry[]> {
  const input = encodeURIComponent(JSON.stringify({ 0: { json: { taskId } } }));
  const result = await apiFetch<any>(`/api/trpc/tasks.logs?batch=1&input=${input}`);
  return result?.[0]?.result?.data?.json ?? [];
}

export async function fetchReviewApi(taskId: string): Promise<ReviewResult> {
  const input = encodeURIComponent(JSON.stringify({ 0: { json: { taskId } } }));
  const result = await apiFetch<any>(`/api/trpc/tasks.reviewResult?batch=1&input=${input}`);
  return result?.[0]?.result?.data?.json;
}

export async function submitReviewApi(
  taskId: string,
  approved: boolean,
  comment?: string
): Promise<void> {
  await apiFetch("/api/trpc/tasks.humanReview", {
    method: "POST",
    body: JSON.stringify({ "0": { json: { taskId, approved, comment } } }),
  });
}
