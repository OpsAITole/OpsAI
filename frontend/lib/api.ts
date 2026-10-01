export type ApiStatus = {
  service: string;
  status: string;
  version: string;
  environment: string;
};

export type UserRole = "ADMIN" | "TECHNICIAN" | "VIEWER";

export type User = {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type IncidentStatus = "NEW" | "INVESTIGATING" | "WAITING" | "RESOLVED" | "CLOSED";
export type IncidentPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type IncidentSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type IncidentCategory =
  | "NETWORK"
  | "WINDOWS"
  | "LINUX"
  | "DATABASE"
  | "APPLICATION"
  | "SECURITY"
  | "VPN"
  | "DNS"
  | "CLOUD"
  | "HARDWARE"
  | "OTHER";

export type Incident = {
  id: string;
  ticket_number: string;
  title: string;
  description: string;
  status: IncidentStatus;
  priority: IncidentPriority;
  severity: IncidentSeverity;
  category: IncidentCategory;
  affected_service: string | null;
  affected_system: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
};

export type IncidentTimelineEvent = {
  id: string;
  type: string;
  message: string;
  at: string;
};

export type IncidentDetail = Incident & {
  timeline: IncidentTimelineEvent[];
};

export type IncidentListResponse = {
  items: Incident[];
  total: number;
};

export type IncidentCreateInput = {
  title: string;
  description?: string;
  category: IncidentCategory;
  priority: IncidentPriority;
  severity?: IncidentSeverity;
  affected_service?: string | null;
  affected_system?: string | null;
};

export type IncidentUpdateInput = {
  title?: string;
  description?: string;
  status?: IncidentStatus;
  priority?: IncidentPriority;
  severity?: IncidentSeverity;
  category?: IncidentCategory;
  affected_service?: string | null;
  affected_system?: string | null;
};

export type IncidentListParams = {
  search?: string;
  status?: IncidentStatus | "";
  priority?: IncidentPriority | "";
  category?: IncidentCategory | "";
  created_from?: string;
  created_to?: string;
  sort_by?: "created_at" | "updated_at" | "priority" | "status" | "title" | "ticket_number";
  sort_dir?: "asc" | "desc";
  offset?: number;
  limit?: number;
};

export const INCIDENT_STATUSES: IncidentStatus[] = [
  "NEW",
  "INVESTIGATING",
  "WAITING",
  "RESOLVED",
  "CLOSED",
];

export const INCIDENT_PRIORITIES: IncidentPriority[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export const INCIDENT_CATEGORIES: IncidentCategory[] = [
  "NETWORK",
  "WINDOWS",
  "LINUX",
  "DATABASE",
  "APPLICATION",
  "SECURITY",
  "VPN",
  "DNS",
  "CLOUD",
  "HARDWARE",
  "OTHER",
];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "opsai_access_token";
const USER_KEY = "opsai_user";

export function getApiBaseUrl(): string {
  return API_URL.replace(/\/$/, "");
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function storeSession(token: string, user: User): void {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession(): void {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

export function canWriteIncidents(user: User | null): boolean {
  return user?.role === "ADMIN" || user?.role === "TECHNICIAN";
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string | { msg: string }[] };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  } catch {
    /* ignore */
  }
  return `Request failed (${response.status})`;
}

async function authFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const access = getStoredToken();
  if (!access) throw new Error("Not authenticated");
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${access}`);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(`${getApiBaseUrl()}${path}`, { ...init, headers, cache: "no-store" });
}

export async function fetchApiStatus(): Promise<ApiStatus> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/status`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Status request failed (${response.status})`);
  }

  return response.json() as Promise<ApiStatus>;
}

export async function registerUser(input: {
  email: string;
  password: string;
  name: string;
}): Promise<User> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<User>;
}

export async function loginUser(input: {
  email: string;
  password: string;
}): Promise<TokenResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<TokenResponse>;
}

export async function fetchMe(token?: string): Promise<User> {
  const access = token ?? getStoredToken();
  if (!access) throw new Error("Not authenticated");
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${access}` },
    cache: "no-store",
  });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<User>;
}

export async function logoutUser(): Promise<void> {
  const access = getStoredToken();
  if (access) {
    try {
      await fetch(`${getApiBaseUrl()}/api/v1/auth/logout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${access}` },
      });
    } catch {
      /* client still clears local session */
    }
  }
  clearSession();
}

export async function listIncidents(params: IncidentListParams = {}): Promise<IncidentListResponse> {
  const query = new URLSearchParams();
  if (params.search) query.set("search", params.search);
  if (params.status) query.set("status", params.status);
  if (params.priority) query.set("priority", params.priority);
  if (params.category) query.set("category", params.category);
  if (params.created_from) query.set("created_from", params.created_from);
  if (params.created_to) query.set("created_to", params.created_to);
  if (params.sort_by) query.set("sort_by", params.sort_by);
  if (params.sort_dir) query.set("sort_dir", params.sort_dir);
  if (params.offset != null) query.set("offset", String(params.offset));
  if (params.limit != null) query.set("limit", String(params.limit));
  const qs = query.toString();
  const response = await authFetch(`/api/v1/incidents${qs ? `?${qs}` : ""}`);
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<IncidentListResponse>;
}

export async function getIncident(id: string): Promise<IncidentDetail> {
  const response = await authFetch(`/api/v1/incidents/${id}`);
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<IncidentDetail>;
}

export async function createIncident(input: IncidentCreateInput): Promise<Incident> {
  const response = await authFetch("/api/v1/incidents", {
    method: "POST",
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<Incident>;
}

export async function updateIncident(id: string, input: IncidentUpdateInput): Promise<Incident> {
  const response = await authFetch(`/api/v1/incidents/${id}`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<Incident>;
}

export async function deleteIncident(id: string): Promise<void> {
  const response = await authFetch(`/api/v1/incidents/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error(await parseError(response));
}
