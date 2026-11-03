import { createContext, useContext } from "react";
import type { Wallet } from "../types/carteiras";

export interface CarteiraContextValue {
  wallet: Wallet | null;
  isLoading: boolean;
  loadError: string;
  setWallet: (wallet: Wallet) => void;
  refreshWallet: () => Promise<void>;
}

export const CarteiraContext = createContext<CarteiraContextValue | null>(null);

export function useCarteira(): CarteiraContextValue {
  const context = useContext(CarteiraContext);
  if (context === null) {
    throw new Error("useCarteira deve ser usado dentro de CarteiraProvider.");
  }
  return context;
}
