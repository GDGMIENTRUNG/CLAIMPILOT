const base =
  (import.meta as ImportMeta & { env: Record<string, string> }).env
    .VITE_API_BASE_URL || "";
let csrfToken = "";
export function setCsrfToken(value: string) { csrfToken = value; }
export class ApiError extends Error {
  constructor(message: string, public status: number, public code: string) { super(message); }
}
export async function api<T>(path: string, method = "GET", payload?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base}/api${path}`, { method, credentials: "same-origin",
      headers: { ...(payload !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(method !== "GET" && csrfToken ? { "X-CSRF-Token": csrfToken } : {}) },
      body: payload === undefined ? undefined : JSON.stringify(payload) });
  } catch {
    throw new Error("Cannot reach the backend. Check that FastAPI is running.");
  }
  if (response.status === 204) return undefined as T;
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith('/auth/login')) window.dispatchEvent(new Event('claimpilot:expired'));
    throw new ApiError(typeof body?.detail === "string" ? body.detail.replaceAll("_", " ") : Array.isArray(body?.detail) ? body.detail.map((e: {msg: string}) => e.msg).join('; ') : `Request failed (${response.status})`, response.status, typeof body?.code === 'string' ? body.code : 'request_failed');
  }
  return body as T;
}
