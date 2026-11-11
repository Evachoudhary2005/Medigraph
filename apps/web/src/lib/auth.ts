// Auth token storage + API wrapper.
// Everything in localStorage under "medigraph.token" and "medigraph.user".

export type AuthUser = {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "clinician" | "patient";
};

const TOKEN_KEY = "medigraph.token";
const USER_KEY = "medigraph.user";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

export function setAuth(token: string, user: AuthUser) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

// Authed fetch — adds bearer token when present.
export async function authedFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", "Bearer " + token);
  return fetch(input, { ...init, headers });
}

export async function login(email: string, password: string): Promise<{ ok: boolean; error?: string }> {
  try {
    const r = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!r.ok) {
      const text = await r.text();
      return { ok: false, error: text };
    }
    const j = await r.json();
    setAuth(j.access_token, j.user);
    return { ok: true };
  } catch (e: any) {
    return { ok: false, error: e?.message ?? String(e) };
  }
}

export function logout() {
  clearAuth();
  window.location.href = "/login";
}