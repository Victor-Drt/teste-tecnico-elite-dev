export type LoteStatus = "em_breve" | "ao_vivo" | "concluido" | "cancelado";

export interface ItemLoteListagem {
  id: number;
  titulo: string;
  data_exibicao: string | null;
  info_artista: string | null;
  imagem_id: string;
  imagem_url: string;
}

export interface LoteListagem {
  id: number;
  item_id: number;
  data_inicio: string;
  data_fim: string;
  valor_atual: string;
  status: LoteStatus;
  vencedor_id: number | null;
  item: ItemLoteListagem;
}

export interface LoteVitrine extends LoteListagem {
  item: ItemLoteListagem & {
    descricao: string | null;
  };
}

export interface LoteCreate {
  item_id: number;
  data_inicio: string;
  data_fim: string;
  valor_inicial: string;
  incremento_minimo: string;
}
