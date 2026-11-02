interface Wallet {
  id: number;
  usuario_id: number;
  saldo_total: string;
  saldo_comprometido: string;
  saldo_disponivel: string;
  data_criacao: string;
}

export type { Wallet };
