import type { ItemLoteListagem } from "./lotes";

export interface LanceAuditoriaPublica {
  participante: string;
  valor: string;
  data_criacao: string;
  hash_anterior: string | null;
  hash_evento: string | null;
}

export type IntegridadeCadeia =
  | "verificada"
  | "inconsistente"
  | "nao_verificada";

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
  integridade_cadeia: IntegridadeCadeia;
  hash_cadeia_lances: string | null;
  quantidade_lances_ancorada: number | null;
}
