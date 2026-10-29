const base =
  (import.meta as ImportMeta & { env: Record<string, string> }).env
    .VITE_API_BASE_URL || "";
export async function api<T>(path: string, method = "GET"): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base}/api${path}`, { method });
  } catch {
    throw new Error("Cannot reach the backend. Check that FastAPI is running.");
  }
  const body = await response.json().catch(() => null);
  if (!response.ok)
    throw new Error(
      typeof body?.detail === "string"
        ? body.detail.replaceAll("_", " ")
        : `Request failed (${response.status})`,
    );
  return body as T;
}
