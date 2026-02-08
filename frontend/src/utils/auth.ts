import axios from "axios";

const API_BASE = import.meta.env.DEV ? "/api/auth" : "https://hyperspace-0w29.onrender.com/api/auth";
const TOKEN_KEY = "orbital_nexus_token";
const USER_KEY = "orbital_nexus_user";

export interface User {
  phone: string;
  name: string;
  village: string;
}

interface AuthResponse {
  token: string;
  user: User;
}

/** Save token + user to localStorage */
function persist(token: string, user: User) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/** Sign up a new farmer */
export async function signup(
  phone: string,
  password: string,
  name: string,
  village: string
): Promise<User> {
  const res = await axios.post<AuthResponse>(`${API_BASE}/signup`, {
    phone,
    password,
    name,
    village,
  });
  persist(res.data.token, res.data.user);
  return res.data.user;
}

/** Login with phone + password */
export async function login(phone: string, password: string): Promise<User> {
  const res = await axios.post<AuthResponse>(`${API_BASE}/login`, {
    phone,
    password,
  });
  persist(res.data.token, res.data.user);
  return res.data.user;
}

/** Logout — clear stored session */
export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/** Get stored token */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/** Get stored user (fast, no API call) */
export function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

/** Check if user is logged in */
export function isLoggedIn(): boolean {
  return !!getToken();
}
