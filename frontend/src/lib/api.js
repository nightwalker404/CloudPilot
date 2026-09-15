const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const BASE_URL_KEY = "cloudpilot:baseUrl";
const USER_ID_KEY = "cloudpilot:userId";

export function getBaseUrl() {
  return localStorage.getItem(BASE_URL_KEY) || DEFAULT_BASE_URL;
}
export function setBaseUrl(url) {
  localStorage.setItem(BASE_URL_KEY, url);
}
export function getUserId() {
  return localStorage.getItem(USER_ID_KEY) || "demo-user";
}
export function setUserId(id) {
  localStorage.setItem(USER_ID_KEY, id);
}

function authHeaders() {
  return { "Content-Type": "application/json", "X-User-ID": getUserId() };
}

async function request(path, opts = {}) {
  const url = `${getBaseUrl()}${path}`;
  const startedAt = Date.now();
  let res;
  try {
    res = await fetch(url, { ...opts, headers: { ...authHeaders(), ...(opts.headers || {}) } });
  } catch (err) {
    throw new ApiError(`Network error calling ${path}: ${err.message}`, {
      url, method: opts.method || "GET", ok: false, status: 0, durationMs: Date.now() - startedAt,
    });
  }
  const raw = await res.text();
  let data = raw;
  try { data = raw ? JSON.parse(raw) : null; } catch { /* leave as text */ }

  const trace = {
    url,
    method: opts.method || "GET",
    requestBody: opts.body ? safeParse(opts.body) : null,
    status: res.status,
    ok: res.ok,
    response: data,
    durationMs: Date.now() - startedAt,
    at: new Date().toISOString(),
  };

  if (!res.ok) {
    const detail = data && data.detail ? data.detail : raw;
    throw new ApiError(`${res.status}: ${detail}`, trace);
  }
  return { data, trace };
}

function safeParse(body) {
  try { return JSON.parse(body); } catch { return body; }
}

export class ApiError extends Error {
  constructor(message, trace) {
    super(message);
    this.trace = trace;
  }
}

export const api = {
  health: () => request("/health"),
  listConversations: () => request("/conversations"),
  createConversation: () => request("/conversations", { method: "POST" }),
  getConversation: (id) => request(`/conversations/${id}`),
  deleteConversation: (id) => request(`/conversations/${id}`, { method: "DELETE" }),
  chat: (body) => request("/chat", { method: "POST", body: JSON.stringify(body) }),
};
