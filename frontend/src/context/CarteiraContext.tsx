import axios from "axios";
import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { fetchWallet } from "../services/carteiras";
import type { User } from "../types/usuarios";
import type { Wallet } from "../types/carteiras";
import { CarteiraContext } from "./useCarteira";

function getWalletErrorMessage(error: unknown): string {
  if (axios.isAxiosError<{ detail?: string }>(error)) {
    return (
      error.response?.data?.detail ??
      "Não foi possível carregar sua carteira."
    );
  }
  return "Não foi possível carregar sua carteira.";
}

export function CarteiraProvider({
  user,
  children,
}: {
  user: User;
  children: ReactNode;
}) {
  const [wallet, setWalletState] = useState<Wallet | null>(null);
  const [isLoading, setIsLoading] = useState(user.papel === "licitante");
  const [loadError, setLoadError] = useState("");

  const setWallet = useCallback((nextWallet: Wallet) => {
    setWalletState(nextWallet);
    setLoadError("");
    setIsLoading(false);
  }, []);

  const refreshWallet = useCallback(async () => {
    if (user.papel !== "licitante") {
      return;
    }

    try {
      setWallet(await fetchWallet());
    } catch (error: unknown) {
      setLoadError(getWalletErrorMessage(error));
    }
  }, [setWallet, user.papel]);

  useEffect(() => {
    if (user.papel !== "licitante") {
      return;
    }

    let isCurrent = true;

    fetchWallet()
      .then((userWallet) => {
        if (isCurrent) {
          setWallet(userWallet);
        }
      })
      .catch((error: unknown) => {
        if (isCurrent) {
          setLoadError(getWalletErrorMessage(error));
          setIsLoading(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [setWallet, user.papel]);

  const value = useMemo(
    () => ({ wallet, isLoading, loadError, setWallet, refreshWallet }),
    [wallet, isLoading, loadError, setWallet, refreshWallet],
  );

  return (
    <CarteiraContext.Provider value={value}>{children}</CarteiraContext.Provider>
  );
}
