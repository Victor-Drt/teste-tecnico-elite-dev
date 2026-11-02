import type { CreateUserData, User } from "../types/usuarios";
import { axiosClient } from "./api";

export async function register(userData: CreateUserData): Promise<User> {
    const response = await axiosClient.post<User>("usuarios/criar", userData);
    return response.data;
}

export async function fetchUser(): Promise<User> {
    const response = await axiosClient.get<User>("usuarios/perfil");
    return response.data;
}