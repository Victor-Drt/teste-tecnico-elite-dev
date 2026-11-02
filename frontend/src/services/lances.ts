import type {
  CategoriaMeusLances,
  LanceCreate,
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

export async function criarLance(data: LanceCreate): Promise<LanceResumo> {
  const response = await axiosClient.post<LanceResumo>("lances/", data);
  return response.data;
}

export function getSalaLeilaoWebSocketUrl(loteId: number): string {
  const apiUrl = new URL(axiosClient.defaults.baseURL ?? window.location.origin);
  apiUrl.protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";
  apiUrl.pathname = `${apiUrl.pathname.replace(/\/+$/, "")}/ws/leilao/${loteId}`;
  apiUrl.search = "";
  apiUrl.hash = "";
  return apiUrl.toString();
}
