import axios from "axios";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { IoArrowBack, IoPrintOutline } from "react-icons/io5";
import { getItemImageUrl } from "../../services/itens";
import { fetchComprovanteArremate } from "../../services/comprovantes";
import type { ComprovanteArremate } from "../../types/comprovantes";
import "./styles.css";

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const dateTimeFormatter = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "long",
  timeStyle: "short",
});

function formatDate(value: string): string {
  return dateTimeFormatter.format(new Date(value));
}

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError<{ detail?: string }>(error)) {
    if (error.response?.status === 404) {
      return "Este comprovante não está disponível para sua conta.";
    }
    return (
      error.response?.data?.detail ??
      "Não foi possível carregar o comprovante. Tente novamente."
    );
  }
  return "Ocorreu um erro inesperado ao carregar o comprovante.";
}

const ComprovanteArrematePage = () => {
  const { loteId: loteIdParam } = useParams<{ loteId: string }>();
  const loteId = Number(loteIdParam);
  const hasValidLoteId = Number.isSafeInteger(loteId) && loteId > 0;
  const [receipt, setReceipt] = useState<ComprovanteArremate | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!hasValidLoteId) {
      return;
    }

    let isCurrent = true;
    fetchComprovanteArremate(loteId)
      .then((data) => {
        if (isCurrent) {
          setReceipt(data);
        }
      })
      .catch((requestError: unknown) => {
        if (isCurrent) {
          setErrorMessage(getErrorMessage(requestError));
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
  }, [hasValidLoteId, loteId]);

  return (
    <main className="receipt-page">
      <Link className="receipt-page__back" to="/arremates">
        <IoArrowBack aria-hidden="true" />
        Voltar para Meus Arremates
      </Link>

      {!hasValidLoteId ? (
        <section className="receipt-page__state" role="alert">
          <h1>Comprovante indisponível</h1>
          <p>Identificador de lote inválido.</p>
          <Link to="/arremates">Voltar para Meus Arremates</Link>
        </section>
      ) : isLoading ? (
        <p className="receipt-page__message" role="status">
          Carregando comprovante…
        </p>
      ) : errorMessage ? (
        <section className="receipt-page__state" role="alert">
          <h1>Comprovante indisponível</h1>
          <p>{errorMessage}</p>
          <Link to="/arremates">Voltar para Meus Arremates</Link>
        </section>
      ) : receipt ? (
        <article className="receipt">
          <header className="receipt__header">
            <div>
              <span className="receipt__eyebrow">Liquidação concluída</span>
              <h1>Comprovante de arremate</h1>
              <p>
                Documento privado referente à liquidação deste lote.
              </p>
            </div>
            <span className="receipt__status">LIQUIDADO</span>
          </header>

          <div className="receipt__reference">
            <span>Comprovante</span>
            <strong>AR-{String(receipt.id).padStart(8, "0")}</strong>
          </div>

          <section aria-label="Item arrematado" className="receipt__item">
            <img
              alt={receipt.item.titulo}
              src={getItemImageUrl(receipt.item.id)}
            />
            <div>
              <span>Lote #{receipt.lote_id}</span>
              <h2>{receipt.item.titulo}</h2>
              <p>{receipt.item.info_artista ?? "Artista não informado"}</p>
            </div>
          </section>

          <dl className="receipt__details">
            <div className="receipt__details--highlight">
              <dt>Valor liquidado</dt>
              <dd>{currencyFormatter.format(Number(receipt.valor))}</dd>
            </div>
            <div>
              <dt>Arrematante</dt>
              <dd>Você</dd>
            </div>
            <div>
              <dt>Crédito ao leiloeiro</dt>
              <dd>{currencyFormatter.format(Number(receipt.valor))}</dd>
            </div>
            <div>
              <dt>Início do leilão</dt>
              <dd>{formatDate(receipt.data_inicio)}</dd>
            </div>
            <div>
              <dt>Data de encerramento</dt>
              <dd>{formatDate(receipt.data_fim)}</dd>
            </div>
            <div>
              <dt>Data da liquidação</dt>
              <dd>{formatDate(receipt.data_liquidacao)}</dd>
            </div>
            <div>
              <dt>Referência do lance vencedor</dt>
              <dd>#{receipt.lance_id}</dd>
            </div>
          </dl>

          <p className="receipt__privacy">
            Este comprovante é privado e só pode ser consultado pela conta
            vencedora. Para compartilhar a verificação pública do leilão, use
            a auditoria do lote.
          </p>

          <footer className="receipt__actions">
            <Link
              className="receipt__audit"
              to={`/auditoria/${receipt.lote_id}`}
            >
              Ver auditoria pública
            </Link>
            <button
              className="receipt__print"
              onClick={() => window.print()}
              type="button"
            >
              <IoPrintOutline aria-hidden="true" />
              Imprimir / salvar como PDF
            </button>
          </footer>
        </article>
      ) : (
        <p className="receipt-page__state" role="alert">
          Não foi possível carregar o comprovante.
        </p>
      )}
    </main>
  );
};

export default ComprovanteArrematePage;
