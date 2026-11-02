export interface ItemSummary {
  id: number;
  titulo: string;
  data_exibicao: string | null;
  info_artista: string | null;
  imagem_id: string;
  imagem_url: string;
}

export interface ItemDetails extends ItemSummary {
  id_externo: number;
  descricao: string | null;
  numero_referencia: string | null;
}
