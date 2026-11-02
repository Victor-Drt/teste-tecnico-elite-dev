import type {
  LoteCreate,
  LoteListagem,
  LoteStatus,
  LoteVitrine,
} from "../types/lotes";
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

export async function fetchLoteVitrine(loteId: number): Promise<LoteVitrine> {
  const response = await axiosClient.get<LoteVitrine>(
    `lotes/${loteId}/vitrine`,
  );
  return response.data;
}

export async function createLote(data: LoteCreate): Promise<void> {
  await axiosClient.post("lotes/", data);
}