import type { Wallet } from "../types/carteiras";
import { axiosClient } from "./api";

export async function fetchWallet(): Promise<Wallet> {
  const response = await axiosClient.get<Wallet>("carteiras/minha");
  return response.data;
}
