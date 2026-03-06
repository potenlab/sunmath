export interface User {
  id: number;
  email: string;
  name: string;
  role: "admin" | "student";
  student_id: number | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  role: "admin" | "student";
  grade_level?: number;
}
