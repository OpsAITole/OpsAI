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
