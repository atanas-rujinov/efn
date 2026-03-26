import { api } from "./client";

export type Role = "driver" | "disabled";

export interface LoginPayload {
    email: string;
    password: string;
    role: Role;
}

export interface SignupDriverPayload {
    name: string;
    email: string;
    phone: string; // <-- ADDED
    password: string;
    role: "driver";
}

export interface SignupDisabledPayload {
    name: string;
    email: string;
    phone: string; // <-- ADDED
    password: string;
    role: "disabled";
    disability: string;
}

export type SignupPayload = SignupDriverPayload | SignupDisabledPayload;

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export interface Me {
    id: number;
    name: string;
    email: string;
    phone?: string; // Optional if you also return it in /auth/me
    role: Role;
    disability?: string;
}

export const authApi = {
    login: (payload: LoginPayload) =>
        api.post<AuthResponse>("/auth/login", payload),
    signup: (payload: SignupPayload) =>
        api.post<AuthResponse>("/auth/signup", payload),
    me: () => api.get<Me>("/auth/me"),
};
