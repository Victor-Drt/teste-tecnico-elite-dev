import { API_BASE_URL } from "../config/api";

export function getItemImageUrl(itemId: number): string {
  return `${API_BASE_URL.replace(/\/+$/, "")}/itens/${itemId}/imagem`;
}
