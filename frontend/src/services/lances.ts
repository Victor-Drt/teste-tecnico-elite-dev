import type {
  CategoriaMeusLances,
  LanceHistoricoItem,
  LanceResumo,
  MeuLanceItem,
  Pagina,
} from "../types/lances";
import { axiosClient } from "./api";

export async function fetchMeusLances(
  categoria: CategoriaMeusLances,
  offset = 0,
  limit = 20,
): Promise<Pagina<MeuLanceItem>> {
  const response = await axiosClient.get<Pagina<MeuLanceItem>>("lances/meus", {
    params: { categoria, offset, limit },
  });
  return response.data;
}

export async function fetchHistoricoLances(
  loteId: number,
  offset = 0,
  limit = 50,
): Promise<Pagina<LanceHistoricoItem>> {
  const response = await axiosClient.get<Pagina<LanceHistoricoItem>>(
    `lances/lotes/${loteId}/historico`,
    { params: { offset, limit } },
  );
  return response.data;
}

export async function fetchLancesPorLote(
  loteId: number,
): Promise<LanceResumo[]> {
  const response = await axiosClient.get<LanceResumo[]>(
    `lances/lotes/${loteId}`,
  );
  return response.data;
}
