import { API_BASE_URL } from "../config/api";
import type { ItemDetails, ItemSummary } from "../types/itens";
import { axiosClient } from "./api";

export function getItemImageUrl(itemId: number): string {
  return `${API_BASE_URL.replace(/\/+$/, "")}/itens/${itemId}/imagem`;
}

export async function fetchItens(
  offset: number,
  limit: number,
): Promise<ItemSummary[]> {
  const response = await axiosClient.get<ItemSummary[]>("itens/", {
    params: { offset, limit },
  });
  return response.data;
}

export async function fetchItemDetails(itemId: number): Promise<ItemDetails> {
  const response = await axiosClient.get<ItemDetails>(`itens/${itemId}`);
  return response.data;
}
