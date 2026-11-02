import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { fetchLoteVitrine } from "../../services/lotes";
import { getItemImageUrl } from "../../services/itens";
import type { LoteStatus, LoteVitrine } from "../../types/lotes";
import "./styles.css";

type PageState =
  | { loteId: string; status: "loading" }
  | { loteId: string; status: "error"; message: string }
  | { loteId: string; status: "loaded"; lot: LoteVitrine };

type DisplayStatus = "ao_vivo" | "em_breve" | "encerrado";

const initialTime = Date.now();

function getDisplayStatus(status: LoteStatus): DisplayStatus {
  return status === "concluido" || status === "cancelado"
    ? "encerrado"
    : status;
}

function formatTimeRemaining(target: Date, currentTime: number): string {
  const remainingSeconds = Math.max(
    0,
    Math.floor((target.getTime() - currentTime) / 1000),
  );
  const days = Math.floor(remainingSeconds / 86_400);
  const hours = Math.floor((remainingSeconds % 86_400) / 3_600);
  const minutes = Math.floor((remainingSeconds % 3_600) / 60);
  const seconds = remainingSeconds % 60;
  const clock = [hours, minutes, seconds]
    .map((value) => String(value).padStart(2, "0"))
    .join(":");

  return days > 0 ? `${days}d ${clock}` : clock;
}

function AuctionCountdown({
  status,
  startsAt,
  endsAt,
  currentTime,
}: {
  status: DisplayStatus;
  startsAt: Date;
  endsAt: Date;
  currentTime: number;
}) {
  if (status === "encerrado") {
    return <span className="item-details__countdown">Leilão encerrado</span>;
  }

  const target = status === "ao_vivo" ? endsAt : startsAt;
  const label =
    status === "ao_vivo" ? "Encerra em" : "Começa em";

  return (
    <span
      className={`item-details__countdown${status === "ao_vivo" ? " is-live" : ""}`}
    >
      {label} {formatTimeRemaining(target, currentTime)}
    </span>
  );
}

const ItemDetalhesPage = () => {
  const { loteId = "" } = useParams();
  const [pageState, setPageState] = useState<PageState>({
    loteId: "",
    status: "loading",
  });
  const [currentTime, setCurrentTime] = useState(initialTime);
  const isCurrentPage = pageState.loteId === loteId;
  const lot = isCurrentPage && pageState.status === "loaded"
    ? pageState.lot
    : null;
  const isLoading = !isCurrentPage || pageState.status === "loading";
  const errorMessage =
    isCurrentPage && pageState.status === "error" ? pageState.message : "";

  useEffect(() => {
    let isCurrentRequest = true;
    const parsedLotId = Number(loteId);

    if (!Number.isSafeInteger(parsedLotId) || parsedLotId < 1) {
      Promise.resolve().then(() => {
        if (isCurrentRequest) {
          setPageState({
            loteId,
            status: "error",
            message: "O lote solicitado é inválido.",
          });
        }
      });
      return () => {
        isCurrentRequest = false;
      };
    }

    fetchLoteVitrine(parsedLotId)
      .then((response) => {
        if (isCurrentRequest) {
          setPageState({ loteId, status: "loaded", lot: response });
        }
      })
      .catch(() => {
        if (isCurrentRequest) {
          setPageState({
            loteId,
            status: "error",
            message: "Não foi possível carregar os detalhes deste lote.",
          });
        }
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [loteId]);

  useEffect(() => {
    const timerId = window.setInterval(
      () => setCurrentTime(Date.now()),
      1000,
    );
    return () => window.clearInterval(timerId);
  }, []);

  if (isLoading) {
    return (
      <main className="item-details-page">
        <h1>Detalhes do Item</h1>
        <p className="item-details-page__message" role="status">
          Carregando detalhes do lote...
        </p>
      </main>
    );
  }

  if (errorMessage || !lot) {
    return (
      <main className="item-details-page">
        <h1>Detalhes do Item</h1>
        <p className="item-details-page__message" role="alert">
          {errorMessage || "Não foi possível encontrar este lote."}
        </p>
        <Link className="item-details-page__back" to="/vitrine">
          Voltar para a vitrine
        </Link>
      </main>
    );
  }

  const status = getDisplayStatus(lot.status);
  const startsAt = new Date(lot.data_inicio);
  const endsAt = new Date(lot.data_fim);

  return (
    <main className="item-details-page">
      <h1>Detalhes do Item</h1>

      <div className="item-details">
        <section
          aria-labelledby="item-details-title"
          className="item-details__information"
        >
          <span
            className={`item-details__status item-details__status--${status}`}
          >
            {status === "ao_vivo"
              ? "Ao Vivo"
              : status === "em_breve"
                ? "Em Breve"
                : "Encerrado"}
          </span>
          <h2 id="item-details-title">{lot.item.titulo}</h2>
          <p className="item-details__artist">
            {lot.item.info_artista ?? "Artista não informado"}
          </p>
          <p className="item-details__description">
            {lot.item.descricao ??
              "Não há descrição disponível para esta obra."}
          </p>

          <div className="item-details__footer">
            {status === "ao_vivo" ? (
              <Link
                className="item-details__participate"
                to={`/lotes/${lot.id}/sala`}
              >
                Participar do Leilão
              </Link>
            ) : (
              <button
                className="item-details__participate"
                disabled
                type="button"
              >
                {status === "em_breve"
                  ? "Leilão ainda não começou"
                  : "Leilão encerrado"}
              </button>
            )}
            <AuctionCountdown
              currentTime={currentTime}
              endsAt={endsAt}
              startsAt={startsAt}
              status={status}
            />
          </div>
        </section>

        <figure className="item-details__image">
          <img
            alt={lot.item.titulo}
            decoding="async"
            src={getItemImageUrl(lot.item.id)}
          />
        </figure>
      </div>
    </main>
  );
};

export default ItemDetalhesPage;
