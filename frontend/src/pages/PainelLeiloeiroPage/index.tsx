import { useEffect, useMemo, useRef, useState } from "react";
import { IoArrowBack, IoArrowForward, IoChevronForward, IoClose } from "react-icons/io5";
import { fetchLancesPorLote } from "../../services/lances";
import { getItemImageUrl } from "../../services/itens";
import { fetchLotes } from "../../services/lotes";
import type { LancePublico } from "../../types/lances";
import type { LoteListagem, LoteStatus } from "../../types/lotes";
import "./styles.css";

type StatusFilter = LoteStatus;
type ModalState =
  | { type: "details"; lot: LoteListagem }
  | { type: "history"; lot: LoteListagem }
  | null;

const PAGE_SIZE = 100;
const initialTime = Date.now();

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const dateTimeFormatter = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "medium",
  timeStyle: "short",
});

const filters: { label: string; value: StatusFilter }[] = [
  { label: "Ao Vivo", value: "ao_vivo" },
  { label: "Em breve", value: "em_breve" },
  { label: "Concluído", value: "concluido" },
  { label: "Cancelado", value: "cancelado" },
];

const statusLabels: Record<LoteStatus, string> = {
  ao_vivo: "Ao Vivo",
  em_breve: "Em breve",
  concluido: "Concluído",
  cancelado: "Cancelado",
};

function formatTimeRemaining(target: Date, currentTime: number): string {
  const remainingMilliseconds = target.getTime() - currentTime;
  if (remainingMilliseconds <= 0) {
    return "Encerrado";
  }

  const totalMinutes = Math.floor(remainingMilliseconds / 60_000);
  const days = Math.floor(totalMinutes / (24 * 60));
  const hours = Math.floor((totalMinutes % (24 * 60)) / 60);
  const minutes = totalMinutes % 60;

  if (days > 0) {
    return `${days}d ${hours}h ${minutes}min`;
  }
  if (hours > 0) {
    return `${hours}h ${minutes}min`;
  }
  return `${minutes}min`;
}

function getStatusDate(lot: LoteListagem, currentTime: number): string {
  if (lot.status === "ao_vivo") {
    return `Encerra em ${formatTimeRemaining(new Date(lot.data_fim), currentTime)}`;
  }
  if (lot.status === "em_breve") {
    return `Começa em ${formatTimeRemaining(new Date(lot.data_inicio), currentTime)}`;
  }
  return `${lot.status === "cancelado" ? "Cancelado em" : "Encerrado em"} ${dateTimeFormatter.format(new Date(lot.data_fim))}`;
}

async function fetchAllLots(status: LoteStatus): Promise<LoteListagem[]> {
  const lots: LoteListagem[] = [];
  let offset = 0;
  let page: LoteListagem[];

  do {
    page = await fetchLotes(offset, PAGE_SIZE, status);
    lots.push(...page);
    offset += page.length;
  } while (page.length === PAGE_SIZE);

  return lots;
}

function getHistoryRows(lances: LancePublico[]): LancePublico[] {
  return [...lances].sort(
    (first, second) =>
      new Date(second.data_criacao).getTime() -
        new Date(first.data_criacao).getTime() ||
      second.id - first.id,
  );
}

const PainelLeiloeiroPage = () => {
  const carouselRef = useRef<HTMLDivElement>(null);
  const [lotsByStatus, setLotsByStatus] = useState<
    Record<LoteStatus, LoteListagem[]>
  >({
    ao_vivo: [],
    em_breve: [],
    concluido: [],
    cancelado: [],
  });
  const [activeFilter, setActiveFilter] = useState<StatusFilter>("ao_vivo");
  const [currentTime, setCurrentTime] = useState(initialTime);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [retryKey, setRetryKey] = useState(0);
  const [modal, setModal] = useState<ModalState>(null);
  const [history, setHistory] = useState<LancePublico[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");

  useEffect(() => {
    const timerId = window.setInterval(
      () => setCurrentTime(Date.now()),
      30_000,
    );
    return () => window.clearInterval(timerId);
  }, []);

  useEffect(() => {
    let isCurrentRequest = true;
    const statuses: LoteStatus[] = [
      "ao_vivo",
      "em_breve",
      "concluido",
      "cancelado",
    ];

    Promise.all(statuses.map((status) => fetchAllLots(status)))
      .then((results) => {
        if (isCurrentRequest) {
          setLotsByStatus({
            ao_vivo: results[0],
            em_breve: results[1],
            concluido: results[2],
            cancelado: results[3],
          });
        }
      })
      .catch(() => {
        if (isCurrentRequest) {
          setLoadError("Não foi possível carregar seus lotes.");
        }
      })
      .finally(() => {
        if (isCurrentRequest) {
          setIsLoading(false);
        }
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [retryKey]);

  useEffect(() => {
    if (modal?.type !== "history") {
      return;
    }

    let isCurrentRequest = true;

    fetchLancesPorLote(modal.lot.id)
      .then((lances) => {
        if (isCurrentRequest) {
          setHistory(getHistoryRows(lances));
        }
      })
      .catch(() => {
        if (isCurrentRequest) {
          setHistoryError("Não foi possível carregar o histórico de lances.");
        }
      })
      .finally(() => {
        if (isCurrentRequest) {
          setHistoryLoading(false);
        }
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [modal]);

  useEffect(() => {
    if (!modal) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setModal(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [modal]);

  const lots = lotsByStatus[activeFilter];
  const totalCollected = useMemo(
    () =>
      lotsByStatus.concluido
        .filter((lot) => lot.vencedor_id !== null)
        .reduce((total, lot) => total + Number(lot.valor_atual), 0),
    [lotsByStatus.concluido],
  );

  const scrollCarousel = (direction: -1 | 1) => {
    carouselRef.current?.scrollBy({
      left: direction * carouselRef.current.clientWidth * 0.8,
      behavior: "smooth",
    });
  };

  const retryLoading = () => {
    setIsLoading(true);
    setLoadError("");
    setRetryKey((key) => key + 1);
  };

  const openHistory = (lot: LoteListagem) => {
    setHistory([]);
    setHistoryLoading(true);
    setHistoryError("");
    setModal({ type: "history", lot });
  };

  return (
    <main className="auctioneer-lots">
      <section
        aria-labelledby="auctioneer-lots-title"
        className="auctioneer-lots__intro"
      >
        <div>
          <span className="auctioneer-lots__eyebrow">
            Gerencie seus leilões
          </span>
          <h1 id="auctioneer-lots-title">Meus Lotes</h1>
          <p>Acompanhe os lotes que você criou e os lances recebidos.</p>
        </div>
        <aside
          aria-label="Total arrecadado nos lotes concluídos"
          className="auctioneer-revenue"
        >
          <span>Total Arrecadado</span>
          <strong>{currencyFormatter.format(totalCollected)}</strong>
          <small>Soma dos valores finais dos lotes concluídos com vencedor</small>
        </aside>
      </section>

      <div
        aria-label="Filtrar lotes por status"
        className="auctioneer-lots__filters"
        role="group"
      >
        {filters.map((filter) => (
          <button
            aria-pressed={activeFilter === filter.value}
            className={`auctioneer-lots__filter${activeFilter === filter.value ? " is-active" : ""}`}
            key={filter.value}
            onClick={() => {
              setActiveFilter(filter.value);
              carouselRef.current?.scrollTo({ left: 0 });
            }}
            type="button"
          >
            {filter.label}
            <span>{lotsByStatus[filter.value].length}</span>
          </button>
        ))}
      </div>

      <section
        aria-label={`Lotes ${statusLabels[activeFilter]}`}
        className="auctioneer-lots__carousel"
      >
        <button
          aria-label="Ver lotes anteriores"
          className="auctioneer-lots__arrow auctioneer-lots__arrow--previous"
          onClick={() => scrollCarousel(-1)}
          type="button"
        >
          <IoArrowBack aria-hidden="true" />
        </button>
        <div
          aria-live="polite"
          className="auctioneer-lots__track"
          ref={carouselRef}
        >
          {isLoading ? (
            <p className="auctioneer-lots__message" role="status">
              Carregando seus lotes...
            </p>
          ) : loadError ? (
            <div className="auctioneer-lots__message" role="alert">
              <p>{loadError}</p>
              <button onClick={retryLoading} type="button">
                Tentar novamente
              </button>
            </div>
          ) : lots.length > 0 ? (
            lots.map((lot) => (
              <article className="auctioneer-lot-card" key={lot.id}>
                <div className="auctioneer-lot-card__artwork">
                  <img
                    alt={lot.item.titulo}
                    decoding="async"
                    loading="lazy"
                    src={getItemImageUrl(lot.item.id)}
                  />
                </div>
                <div className="auctioneer-lot-card__content">
                  <div className="auctioneer-lot-card__heading">
                    <span
                      className={`auctioneer-lot-card__badge auctioneer-lot-card__badge--${lot.status}`}
                    >
                      {statusLabels[lot.status]}
                    </span>
                    <h2>{lot.item.titulo}</h2>
                  </div>
                  <p
                    className={`auctioneer-lot-card__date auctioneer-lot-card__date--${lot.status}`}
                  >
                    {getStatusDate(lot, currentTime)}
                  </p>
                  <p className="auctioneer-lot-card__artist">
                    {lot.item.info_artista ?? "Artista não informado"}
                  </p>
                  <p className="auctioneer-lot-card__value">
                    {lot.status === "em_breve"
                      ? "Valor inicial"
                      : lot.status === "concluido"
                        ? "Valor final"
                        : "Valor atual"}
                    :{" "}
                    <strong>
                      {currencyFormatter.format(Number(lot.valor_atual))}
                    </strong>
                  </p>
                  <div className="auctioneer-lot-card__footer">
                    <button
                      className="auctioneer-lot-card__history"
                      onClick={() => openHistory(lot)}
                      type="button"
                    >
                      Ver Histórico de Lances
                    </button>
                    <button
                      className="auctioneer-lot-card__details"
                      onClick={() => setModal({ type: "details", lot })}
                      type="button"
                    >
                      Detalhes <IoChevronForward aria-hidden="true" />
                    </button>
                  </div>
                </div>
              </article>
            ))
          ) : (
            <p className="auctioneer-lots__message">
              Não há lotes com este status no momento.
            </p>
          )}
        </div>
        <button
          aria-label="Ver próximos lotes"
          className="auctioneer-lots__arrow auctioneer-lots__arrow--next"
          onClick={() => scrollCarousel(1)}
          type="button"
        >
          <IoArrowForward aria-hidden="true" />
        </button>
      </section>

      {modal && (
        <div
          className="auctioneer-modal-overlay"
          onClick={(event) => {
            if (event.target === event.currentTarget) {
              setModal(null);
            }
          }}
        >
          <section
            aria-labelledby="auctioneer-modal-title"
            aria-modal="true"
            className="auctioneer-modal"
            role="dialog"
          >
            <div className="auctioneer-modal__header">
              <div>
                <span>
                  {modal.type === "history"
                    ? "Lances recebidos"
                    : "Informações do lote"}
                </span>
                <h2 id="auctioneer-modal-title">{modal.lot.item.titulo}</h2>
              </div>
              <button
                aria-label="Fechar"
                className="auctioneer-modal__close"
                onClick={() => setModal(null)}
                type="button"
              >
                <IoClose aria-hidden="true" />
              </button>
            </div>

            {modal.type === "details" ? (
              <dl className="auctioneer-lot-details">
                <div>
                  <dt>Status</dt>
                  <dd>{statusLabels[modal.lot.status]}</dd>
                </div>
                <div>
                  <dt>Artista</dt>
                  <dd>{modal.lot.item.info_artista ?? "Não informado"}</dd>
                </div>
                <div>
                  <dt>Início</dt>
                  <dd>{dateTimeFormatter.format(new Date(modal.lot.data_inicio))}</dd>
                </div>
                <div>
                  <dt>Encerramento</dt>
                  <dd>{dateTimeFormatter.format(new Date(modal.lot.data_fim))}</dd>
                </div>
                <div>
                  <dt>Valor</dt>
                  <dd>{currencyFormatter.format(Number(modal.lot.valor_atual))}</dd>
                </div>
                <div>
                  <dt>Vencedor</dt>
                  <dd>
                    {modal.lot.vencedor_id
                      ? `Licitante #${modal.lot.vencedor_id}`
                      : "Ainda sem vencedor"}
                  </dd>
                </div>
              </dl>
            ) : historyLoading ? (
              <p className="auctioneer-modal__message" role="status">
                Carregando histórico...
              </p>
            ) : historyError ? (
              <div className="auctioneer-modal__message" role="alert">
                <p>{historyError}</p>
                <button
                  onClick={() => openHistory(modal.lot)}
                  type="button"
                >
                  Tentar novamente
                </button>
              </div>
            ) : history.length > 0 ? (
              <ol className="auctioneer-history">
                {history.map((bid) => (
                  <li key={bid.id}>
                    <div>
                      <strong>{bid.participante}</strong>
                      <time>
                        {dateTimeFormatter.format(new Date(bid.data_criacao))}
                      </time>
                    </div>
                    <span>{currencyFormatter.format(Number(bid.valor))}</span>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="auctioneer-modal__message">
                Este lote ainda não recebeu lances.
              </p>
            )}
          </section>
        </div>
      )}
    </main>
  );
};

export default PainelLeiloeiroPage;
