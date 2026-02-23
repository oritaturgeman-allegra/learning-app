/**
 * Typed API client for the learning app backend.
 * All functions return ApiResponse<T> matching backend response shapes.
 */

import type {
  ApiResponse,
  ConfigData,
  GameResultData,
  GameResultRequest,
  PracticedWordsData,
  ProgressData,
  ResetData,
} from "./types";

const API_BASE = "/api/game";

async function fetchJson<T>(url: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<ApiResponse<T>>;
}

export async function loadConfig(
  subject?: string,
  sessionSlug?: string,
): Promise<ApiResponse<ConfigData>> {
  const params = new URLSearchParams();
  if (subject) params.set("subject", subject);
  if (sessionSlug) params.set("session_slug", sessionSlug);
  const qs = params.toString();
  return fetchJson<ConfigData>(`${API_BASE}/config${qs ? `?${qs}` : ""}`);
}

export async function loadProgress(): Promise<ApiResponse<ProgressData>> {
  return fetchJson<ProgressData>(`${API_BASE}/progress`);
}

export async function saveGameResult(
  data: GameResultRequest,
): Promise<ApiResponse<GameResultData>> {
  return fetchJson<GameResultData>(`${API_BASE}/result`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function getPracticedWords(
  sessionSlug?: string,
): Promise<ApiResponse<PracticedWordsData>> {
  const qs = sessionSlug ? `?session_slug=${encodeURIComponent(sessionSlug)}` : "";
  return fetchJson<PracticedWordsData>(`${API_BASE}/practiced-words${qs}`);
}

export async function resetPracticedWords(): Promise<ApiResponse<ResetData>> {
  return fetchJson<ResetData>(`${API_BASE}/reset`, { method: "POST" });
}
