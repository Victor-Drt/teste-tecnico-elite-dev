import type { Wallet } from "../types/carteiras";
import { axiosClient } from "./api";

export async function fetchWallet(): Promise<Wallet> {
  const response = await axiosClient.get<Wallet>("carteiras/minha");
  return response.data;
}

export async function depositToWallet(valor: string): Promise<Wallet> {
  const response = await axiosClient.post<Wallet>("carteiras/depositar", {
    valor,
  });
  return response.data;
}
