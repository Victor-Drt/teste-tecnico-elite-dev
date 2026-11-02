import type { LoteListagem, LoteStatus } from "../types/lotes";
import { axiosClient } from "./api";

export async function fetchLotes(
  offset: number,
  limit: number,
  status?: LoteStatus,
): Promise<LoteListagem[]> {
  const response = await axiosClient.get<LoteListagem[]>("lotes/", {
    params: { offset, limit, status },
  });
  return response.data;
}