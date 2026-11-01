import type { LoginResponse } from "../types/auth";
import { axiosClient } from "./api";


export async function login(email: string, senha: string): Promise<void> {
  await axiosClient.post<LoginResponse>("auth/token", { email, senha });
}