import { axiosClient } from "./api";
import type { AuditoriaPublica } from "../types/auditoria";

export async function fetchAuditoriaPublica(
  loteId: number,
): Promise<AuditoriaPublica> {
  const response = await axiosClient.get<AuditoriaPublica>(
    `lotes/${loteId}/auditoria`,
  );
  return response.data;
}
