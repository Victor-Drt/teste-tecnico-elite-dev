import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import {
  IoArrowBack,
  IoArrowForward,
  IoChevronForward,
  IoClose,
  IoShareSocialOutline,
} from "react-icons/io5";
import { fetchHistoricoLances, fetchMeusLances } from "../../services/lances";
import { getItemImageUrl } from "../../services/itens";
import type {
  CategoriaMeusLances,
  LanceHistoricoItem,
  MeuLanceItem,
} from "../../types/lances";
import "./styles.css";

const PAGE_SIZE = 20;
const HISTORY_PAGE_SIZE = 50;

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const dateTimeFormatter = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "medium",
  timeStyle: "short",
});

const statusLabels = {
  superado: "Lance Superado",
  liderando: "Maior lance",
  arrematado: "Arrematado",
} as const;

function formatDate(value: string): string {
  return dateTimeFormatter.format(new Date(value));
}

function getStatusDate(bid: MeuLanceItem): string {
  if (bid.situacao === "arrematado" || bid.lote.status === "concluido") {
    return `Encerrado em ${formatDate(bid.lote.data_fim)}`;
  }
  if (bid.situacao === "liderando") {
    return "Seu lance é o maior no momento";
  }
  return `Seu lance registrado em ${formatDate(bid.lance.data_criacao)}`;
}

function getOtherCategory(
  category: CategoriaMeusLances,
): CategoriaMeusLances {
  return category === "meus-lances" ? "lotes-vencidos" : "meus-lances";
}

const MeusArrematesPage = () => {
  const carouselRef = useRef<HTMLDivElement>(null);
  const [activeFilter, setActiveFilter] =
    useState<CategoriaMeusLances>("meus-lances");
  const activeFilterRef = useRef(activeFilter);
  const [bids, setBids] = useState<MeuLanceItem[]>([]);
  const [totals, setTotals] = useState<
    Record<CategoriaMeusLances, number | null>
  >({ "meus-lances": null, "lotes-vencidos": null });
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState("");
  const [loadMoreError, setLoadMoreError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [selectedBid, setSelectedBid] = useState<MeuLanceItem | null>(null);
  const selectedBidRef = useRef(selectedBid);
  const [history, setHistory] = useState<LanceHistoricoItem[]>([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [isHistoryLoadingMore, setIsHistoryLoadingMore] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [historyReloadKey, setHistoryReloadKey] = useState(0);
  const [shareFeedback, setShareFeedback] = useState<{
    loteId: number;
    message: string;
  } | null>(null);

  const closeHistory = () => {
    selectedBidRef.current = null;
    setSelectedBid(null);
  };

  useEffect(() => {
    let isCurrent = true;
    const otherCategory = getOtherCategory(activeFilter);

    Promise.all([
      fetchMeusLances(activeFilter, 0, PAGE_SIZE),
      fetchMeusLances(otherCategory, 0, 1),
    ])
      .then(([activePage, otherPage]) => {
        if (!isCurrent) {
          return;
        }
        setBids(activePage.items);
        setTotals({
          "meus-lances":
            activeFilter === "meus-lances"
              ? activePage.total
              : otherPage.total,
          "lotes-vencidos":
            activeFilter === "lotes-vencidos"
              ? activePage.total
              : otherPage.total,
        });
        carouselRef.current?.scrollTo({ left: 0 });
      })
      .catch(() => {
        if (isCurrent) {
          setError("Não foi possível carregar seus arremates.");
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
  }, [activeFilter, reloadKey]);

  useEffect(() => {
    if (!selectedBid) {
      return;
    }

    let isCurrent = true;

    fetchHistoricoLances(selectedBid.lote.id, 0, HISTORY_PAGE_SIZE)
      .then((page) => {
        if (isCurrent) {
          setHistory(page.items);
          setHistoryTotal(page.total);
        }
      })
      .catch(() => {
        if (isCurrent) {
          setHistoryError("Não foi possível carregar o histórico de lances.");
        }
      })
      .finally(() => {
        if (isCurrent) {
          setIsHistoryLoading(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [selectedBid, historyReloadKey]);

  useEffect(() => {
    if (!selectedBid) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        closeHistory();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedBid]);

  const scrollCarousel = (direction: -1 | 1) => {
    carouselRef.current?.scrollBy({
      left: direction * (carouselRef.current.clientWidth * 0.8),
      behavior: "smooth",
    });
  };

  const selectFilter = (category: CategoriaMeusLances) => {
    activeFilterRef.current = category;
    setIsLoading(true);
    setError("");
    setLoadMoreError("");
    setBids([]);
    if (category === activeFilter) {
      setReloadKey((key) => key + 1);
    } else {
      setActiveFilter(category);
    }
  };

  const retryLoadingBids = () => {
    setIsLoading(true);
    setError("");
    setReloadKey((key) => key + 1);
  };

  const openHistory = (bid: MeuLanceItem) => {
    selectedBidRef.current = bid;
    setHistory([]);
    setHistoryTotal(0);
    setHistoryError("");
    setIsHistoryLoading(true);
    setSelectedBid(bid);
  };

  const retryLoadingHistory = () => {
    setHistoryError("");
    setIsHistoryLoading(true);
    setHistoryReloadKey((key) => key + 1);
  };

  const shareAudit = async (loteId: number) => {
    const url = new URL(`/auditoria/${loteId}`, window.location.origin).toString();
    setShareFeedback(null);

    try {
      if (navigator.share) {
        await navigator.share({
          title: `Auditoria pública do lote #${loteId}`,
          text: "Confira os dados públicos do leilão.",
          url,
        });
        setShareFeedback({ loteId, message: "Auditoria compartilhada." });
        return;
      }

      await navigator.clipboard.writeText(url);
      setShareFeedback({ loteId, message: "Link da auditoria copiado." });
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        return;
      }

      try {
        await navigator.clipboard.writeText(url);
        setShareFeedback({ loteId, message: "Link da auditoria copiado." });
      } catch {
        setShareFeedback({
          loteId,
          message: `Não foi possível copiar. Compartilhe este link: ${url}`,
        });
      }
    }
  };

  const loadMoreBids = async () => {
    const category = activeFilter;
    setIsLoadingMore(true);
    setLoadMoreError("");
    try {
      const page = await fetchMeusLances(
        category,
        bids.length,
        PAGE_SIZE,
      );
      if (activeFilterRef.current === category) {
        setBids((current) => [...current, ...page.items]);
        setTotals((current) => ({ ...current, [category]: page.total }));
      }
    } catch {
      if (activeFilterRef.current === category) {
        setLoadMoreError("Não foi possível carregar mais lotes.");
      }
    } finally {
      setIsLoadingMore(false);
    }
  };

  const loadMoreHistory = async () => {
    if (!selectedBid) {
      return;
    }

    const lotId = selectedBid.lote.id;
    setIsHistoryLoadingMore(true);
    setHistoryError("");
    try {
      const page = await fetchHistoricoLances(
        lotId,
        history.length,
        HISTORY_PAGE_SIZE,
      );
      if (selectedBidRef.current?.lote.id === lotId) {
        setHistory((current) => [...current, ...page.items]);
        setHistoryTotal(page.total);
      }
    } catch {
      if (selectedBidRef.current?.lote.id === lotId) {
        setHistoryError("Não foi possível carregar mais lances.");
      }
    } finally {
      setIsHistoryLoadingMore(false);
    }
  };

  const visibleTotal = totals[activeFilter];

  return (
    <main className="my-auctions">
      <section aria-labelledby="my-auctions-title" className="my-auctions__intro">
        <div>
          <span className="my-auctions__eyebrow">Acompanhe sua atividade</span>
          <h1 id="my-auctions-title">Meus Arremates</h1>
          <p>Consulte seus lances e acompanhe as obras que você arrematou.</p>
        </div>
      </section>

      <div
        aria-label="Filtrar arremates"
        className="my-auctions__filters"
        role="group"
      >
        <button
          aria-pressed={activeFilter === "meus-lances"}
          className={`my-auctions__filter${activeFilter === "meus-lances" ? " is-active" : ""}`}
          onClick={() => selectFilter("meus-lances")}
          type="button"
        >
          Meus Lances
          <span>{totals["meus-lances"] ?? "…"}</span>
        </button>
        <button
          aria-pressed={activeFilter === "lotes-vencidos"}
          className={`my-auctions__filter${activeFilter === "lotes-vencidos" ? " is-active" : ""}`}
          onClick={() => selectFilter("lotes-vencidos")}
          type="button"
        >
          Lotes Vencidos
          <span>{totals["lotes-vencidos"] ?? "…"}</span>
        </button>
      </div>

      <section aria-label="Seus lotes" className="my-auctions__carousel">
        <button
          aria-label="Ver lotes anteriores"
          className="my-auctions__arrow my-auctions__arrow--previous"
          onClick={() => scrollCarousel(-1)}
          type="button"
        >
          <IoArrowBack aria-hidden="true" />
        </button>

        <div aria-live="polite" className="my-auctions__track" ref={carouselRef}>
          {isLoading ? (
            <p className="my-auctions__message">Carregando seus arremates…</p>
          ) : error ? (
            <div className="my-auctions__message" role="alert">
              <p>{error}</p>
              <button
                className="my-auctions__retry"
                onClick={retryLoadingBids}
                type="button"
              >
                Tentar novamente
              </button>
            </div>
          ) : bids.length > 0 ? (
            bids.map((bid) => (
              <article className="my-bid-card" key={bid.lote.id}>
                <img
                  alt={bid.lote.item.titulo}
                  className="my-bid-card__artwork"
                  loading="lazy"
                  src={getItemImageUrl(bid.lote.item.id)}
                />

                <div className="my-bid-card__content">
                  <div className="my-bid-card__title-row">
                    <h2>{bid.lote.item.titulo}</h2>
                    <span
                      className={`my-bid-card__badge my-bid-card__badge--${bid.situacao}`}
                    >
                      {statusLabels[bid.situacao]}
                    </span>
                  </div>
                  <p className="my-bid-card__artist">
                    {bid.lote.item.info_artista ?? "Artista não informado"}
                  </p>
                  <p
                    className={`my-bid-card__status-date my-bid-card__status-date--${bid.situacao}`}
                  >
                    {getStatusDate(bid)}
                  </p>
                  <p className="my-bid-card__amount">
                    Seu lance:{" "}
                    <strong>
                      {currencyFormatter.format(Number(bid.lance.valor))}
                    </strong>
                  </p>

                  <div className="my-bid-card__footer">
                    {bid.situacao === "arrematado" &&
                      bid.lote.status === "concluido" && (
                        <>
                          <Link
                            className="my-bid-card__receipt"
                            to={`/arremates/${bid.lote.id}/comprovante`}
                          >
                            Ver comprovante
                          </Link>
                          <button
                            aria-label={`Compartilhar auditoria do lote #${bid.lote.id}`}
                            className="my-bid-card__share"
                            onClick={() => shareAudit(bid.lote.id)}
                            type="button"
                          >
                            <IoShareSocialOutline aria-hidden="true" />
                            Compartilhar auditoria
                          </button>
                        </>
                      )}
                    <button
                      className="my-bid-card__history"
                      onClick={() => openHistory(bid)}
                      type="button"
                    >
                      Ver Histórico de Lances
                    </button>
                    <Link
                      className="my-bid-card__details"
                      to={`/lotes/${bid.lote.id}`}
                    >
                      Saber mais <IoChevronForward aria-hidden="true" />
                    </Link>
                  </div>
                  {shareFeedback?.loteId === bid.lote.id && (
                    <p className="my-bid-card__share-feedback" role="status">
                      {shareFeedback.message}
                    </p>
                  )}
                </div>
              </article>
            ))
          ) : (
            <p className="my-auctions__message">
              {activeFilter === "meus-lances"
                ? "Você ainda não participou de nenhum lote."
                : "Você ainda não arrematou nenhum lote."}
            </p>
          )}
        </div>

        <button
          aria-label="Ver próximos lotes"
          className="my-auctions__arrow my-auctions__arrow--next"
          onClick={() => scrollCarousel(1)}
          type="button"
        >
          <IoArrowForward aria-hidden="true" />
        </button>
      </section>

      {!isLoading && !error && visibleTotal !== null && bids.length < visibleTotal && (
        <div className="my-auctions__load-more">
          {loadMoreError && (
            <p className="my-auctions__load-error" role="alert">
              {loadMoreError}
            </p>
          )}
          <button
            disabled={isLoadingMore}
            onClick={loadMoreBids}
            type="button"
          >
            {isLoadingMore ? "Carregando…" : "Carregar mais lotes"}
          </button>
        </div>
      )}

      {selectedBid && (
        <div
          className="bid-history-overlay"
          onClick={(event) => {
            if (event.target === event.currentTarget) {
              closeHistory();
            }
          }}
        >
          <section
            aria-labelledby="bid-history-title"
            aria-modal="true"
            className="bid-history"
            role="dialog"
          >
            <div className="bid-history__header">
              <div>
                <span>Histórico de lances</span>
                <h2 id="bid-history-title">
                  {selectedBid.lote.item.titulo}
                </h2>
              </div>
              <button
                aria-label="Fechar histórico"
                className="bid-history__close"
                onClick={closeHistory}
                type="button"
              >
                <IoClose aria-hidden="true" />
              </button>
            </div>
            {isHistoryLoading ? (
              <p className="bid-history__message">Carregando histórico…</p>
            ) : historyError && history.length === 0 ? (
              <div className="bid-history__message" role="alert">
                <p>{historyError}</p>
                <button
                  onClick={retryLoadingHistory}
                  type="button"
                >
                  Tentar novamente
                </button>
              </div>
            ) : history.length === 0 ? (
              <p className="bid-history__message">
                Não há lances registrados neste lote.
              </p>
            ) : (
              <>
                <ol className="bid-history__list">
                  {history.map((entry, index) => (
                    <li
                      className={entry.eh_usuario_atual ? "is-current-user" : ""}
                      key={`${entry.data_criacao}-${index}`}
                    >
                      <div>
                        <strong>
                          {entry.eh_usuario_atual ? "Você" : "Outro participante"}
                        </strong>
                        <time>{formatDate(entry.data_criacao)}</time>
                      </div>
                      <span>
                        {currencyFormatter.format(Number(entry.valor))}
                      </span>
                    </li>
                  ))}
                </ol>
                {historyError && (
                  <p className="my-auctions__load-error" role="alert">
                    {historyError}
                  </p>
                )}
                {history.length < historyTotal && (
                  <button
                    className="bid-history__load-more"
                    disabled={isHistoryLoadingMore}
                    onClick={loadMoreHistory}
                    type="button"
                  >
                    {isHistoryLoadingMore
                      ? "Carregando…"
                      : "Carregar mais lances"}
                  </button>
                )}
              </>
            )}
          </section>
        </div>
      )}
    </main>
  );
};

export default MeusArrematesPage;
