import type { ItemLoteListagem } from "./lotes";

export interface LanceAuditoriaPublica {
  participante: string;
  valor: string;
  data_criacao: string;
}

export interface AuditoriaPublica {
  lote_id: number;
  item: ItemLoteListagem;
  data_inicio: string;
  data_fim: string;
  valor_arrematado: string;
  vencedor: string;
  total_participantes: number;
  total_lances: number;
  lances: LanceAuditoriaPublica[];
  hash_sha256: string;
}
