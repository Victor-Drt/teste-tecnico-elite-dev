import { axiosClient } from "./api";
import type { ComprovanteArremate } from "../types/comprovantes";

export async function fetchComprovanteArremate(
  loteId: number,
): Promise<ComprovanteArremate> {
  const response = await axiosClient.get<ComprovanteArremate>(
    `lotes/${loteId}/comprovante`,
  );
  return response.data;
}
