import type { ItemLoteListagem } from "./lotes";

export interface ComprovanteArremate {
  id: number;
  lote_id: number;
  lance_id: number;
  item: ItemLoteListagem;
  valor: string;
  data_inicio: string;
  data_fim: string;
  data_liquidacao: string;
}
