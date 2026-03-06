"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import type { User } from "../types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
  getAccessToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const getAccessToken = useCallback(() => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }, []);

  const fetchUser = useCallback(async (token: string): Promise<User | null> => {
    try {
      const res = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        const u = await fetchUser(token);
        if (u) {
          setUser(u);
        } else {
          // Try refresh
          const refreshToken = localStorage.getItem("refresh_token");
          if (refreshToken) {
            try {
              const res = await fetch(`${API_URL}/auth/refresh`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh_token: refreshToken }),
              });
              if (res.ok) {
                const tokens = await res.json();
                localStorage.setItem("access_token", tokens.access_token);
                localStorage.setItem("refresh_token", tokens.refresh_token);
                const u2 = await fetchUser(tokens.access_token);
                if (u2) setUser(u2);
              } else {
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
              }
            } catch {
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
            }
          }
        }
      }
      setIsLoading(false);
    };
    init();
  }, [fetchUser]);

  const login = async (email: string, password: string): Promise<User> => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "Login failed");
    }
    const tokens = await res.json();
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    const u = await fetchUser(tokens.access_token);
    if (!u) throw new Error("Failed to fetch user");
    setUser(u);
    return u;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, getAccessToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
