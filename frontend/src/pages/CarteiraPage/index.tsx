import axios from "axios";
import { useEffect, useState, type FormEvent } from "react";
import walletIllustration from "../../assets/carteira_wallet_diag.svg";
import { depositToWallet, fetchWallet } from "../../services/carteiras";
import type { Wallet } from "../../types/carteiras";
import "./styles.css";

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError<{ detail?: string }>(error)) {
    return (
      error.response?.data?.detail ??
      "Não foi possível concluir a operação. Tente novamente."
    );
  }
  return "Ocorreu um erro inesperado. Tente novamente.";
}

const CarteiraPage = () => {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [depositAmount, setDepositAmount] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isDepositing, setIsDepositing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    let isCurrent = true;

    fetchWallet()
      .then((userWallet) => {
        if (isCurrent) {
          setWallet(userWallet);
        }
      })
      .catch((error: unknown) => {
        if (isCurrent) {
          setErrorMessage(getErrorMessage(error));
        }
      })
      .finally(() => {
        if (isCurrent) {
          setIsLoading(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const handleDeposit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    const amount = Number(depositAmount);
    if (!Number.isFinite(amount) || amount <= 0) {
      setErrorMessage("Informe um valor de depósito maior que zero.");
      return;
    }

    setIsDepositing(true);
    try {
      const updatedWallet = await depositToWallet(depositAmount);
      setWallet(updatedWallet);
      setDepositAmount("");
      setSuccessMessage("Depósito realizado com sucesso.");
    } catch (error: unknown) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsDepositing(false);
    }
  };

  return (
    <main className="wallet-page">
      <div className="wallet-page__content">
        <section aria-labelledby="wallet-title" className="wallet-card">
          <span className="wallet-card__eyebrow">Área financeira</span>
          <h1 id="wallet-title">Sua Carteira</h1>

          {isLoading ? (
            <p className="wallet-page__message" role="status">
              Carregando saldo...
            </p>
          ) : errorMessage && !wallet ? (
            <p className="wallet-page__error" role="alert">
              {errorMessage}
            </p>
          ) : wallet ? (
            <>
              <dl className="wallet-balances">
                <div className="wallet-balance wallet-balance--total">
                  <dt>Saldo Total</dt>
                  <dd>
                    {currencyFormatter.format(Number(wallet.saldo_total))}
                  </dd>
                </div>
                <div className="wallet-balance wallet-balance--available">
                  <dt>Saldo Disponível</dt>
                  <dd>
                    {currencyFormatter.format(
                      Number(wallet.saldo_disponivel),
                    )}
                  </dd>
                </div>
                <div className="wallet-balance wallet-balance--committed">
                  <dt>Saldo Comprometido</dt>
                  <dd>
                    {currencyFormatter.format(
                      Number(wallet.saldo_comprometido),
                    )}
                  </dd>
                </div>
              </dl>

              <form className="wallet-deposit" onSubmit={handleDeposit}>
                <div className="wallet-deposit__heading">
                  <span className="wallet-deposit__icon" aria-hidden="true">
                    +
                  </span>
                  <div>
                    <h2>Realizar Depósito</h2>
                    <p>Adicione saldo à sua carteira</p>
                  </div>
                </div>
                <label className="wallet-deposit__amount" htmlFor="deposit-amount">
                  <span>R$</span>
                  <input
                    autoComplete="off"
                    id="deposit-amount"
                    inputMode="decimal"
                    min="0.01"
                    name="amount"
                    onChange={(event) => setDepositAmount(event.target.value)}
                    placeholder="0,00"
                    required
                    step="0.01"
                    type="number"
                    value={depositAmount}
                  />
                </label>
                <button
                  className="wallet-deposit__submit"
                  disabled={isDepositing || !depositAmount}
                  type="submit"
                >
                  {isDepositing ? "PROCESSANDO..." : "DEPOSITAR"}
                </button>
              </form>

              {errorMessage && (
                <p className="wallet-page__error" role="alert">
                  {errorMessage}
                </p>
              )}
              {successMessage && (
                <p className="wallet-page__success" role="status">
                  {successMessage}
                </p>
              )}
            </>
          ) : (
            <p className="wallet-page__error" role="alert">
              Não foi possível carregar sua carteira.
            </p>
          )}
        </section>

        <div className="wallet-page__illustration">
          <img
            alt="Ilustração de pessoas organizando uma carteira financeira"
            src={walletIllustration}
          />
        </div>
      </div>
    </main>
  );
};

export default CarteiraPage;
