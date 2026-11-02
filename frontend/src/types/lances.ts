import type { LoteListagem } from "./lotes";

export type CategoriaMeusLances = "meus-lances" | "lotes-vencidos";
export type SituacaoMeuLance = "liderando" | "superado" | "arrematado";

export interface LanceResumo {
  id: number;
  licitante_id: number;
  lote_id: number;
  valor: string;
  data_criacao: string;
}

export interface MeuLanceItem {
  lote: LoteListagem;
  lance: LanceResumo;
  situacao: SituacaoMeuLance;
}

export interface Pagina<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface LanceHistoricoItem {
  valor: string;
  data_criacao: string;
  eh_usuario_atual: boolean;
}
