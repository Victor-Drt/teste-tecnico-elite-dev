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

export interface LancePublico {
  id: number;
  participante: string;
  lote_id: number;
  valor: string;
  data_criacao: string;
}

export interface LanceCreate {
  lote_id: number;
  valor: string;
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

export interface LanceBidEvent {
  tipo: "lance_atualizado";
  lote_id: number;
  lance: LancePublico;
  lance_atual: LancePublico | null;
  valor_atual: string;
  data_fim: string;
  participantes: Array<{
    participante: string;
    posicao: number;
    situacao: "ganhando" | "superado";
  }>;
}

export interface SalaInicialEvent {
  tipo: "sala_inicial";
  lote: {
    id: number;
    status: string;
    data_fim: string;
    valor_atual: string;
  };
  lance_atual: LancePublico | null;
  historico_lances: LancePublico[];
  participantes: LanceBidEvent["participantes"];
  usuario: {
    participante: string | null;
    posicao: number | null;
    situacao: "ganhando" | "superado" | "sem_lance";
  };
}

export type SalaLeilaoEvent = SalaInicialEvent | LanceBidEvent;
