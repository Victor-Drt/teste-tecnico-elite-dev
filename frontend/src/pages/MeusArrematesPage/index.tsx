import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import {
  IoArrowBack,
  IoArrowForward,
  IoClose,
  IoChevronForward,
} from "react-icons/io5";
import "./styles.css";

type BidFilter = "meus-lances" | "lotes-vencidos";
type BidStatus = "superado" | "liderando" | "arrematado";
type ArtworkStyle = "blue" | "terracotta" | "green" | "violet";

interface BidHistoryEntry {
  bidder: string;
  amount: number;
  date: string;
  isCurrentUser?: boolean;
}

interface AuctionBid {
  id: number;
  title: string;
  artist: string;
  artwork: ArtworkStyle;
  status: BidStatus;
  statusDate: string;
  userBid: number;
  history: BidHistoryEntry[];
}

const mockBids: AuctionBid[] = [
  {
    id: 11,
    title: "Composição em azul",
    artist: "Acervo contemporâneo",
    artwork: "blue",
    status: "superado",
    statusDate: "Seu lance foi superado hoje, às 14:32",
    userBid: 15000,
    history: [
      { bidder: "Mariana S.", amount: 16800, date: "Hoje, 14:32" },
      {
        bidder: "Você",
        amount: 15000,
        date: "Hoje, 14:18",
        isCurrentUser: true,
      },
      { bidder: "Carlos R.", amount: 13500, date: "Hoje, 13:57" },
    ],
  },
  {
    id: 12,
    title: "Formas do horizonte",
    artist: "Ateliê Aurora",
    artwork: "terracotta",
    status: "liderando",
    statusDate: "Seu lance é o maior no momento",
    userBid: 8200,
    history: [
      {
        bidder: "Você",
        amount: 8200,
        date: "Hoje, 12:45",
        isCurrentUser: true,
      },
      { bidder: "Pedro M.", amount: 7600, date: "Hoje, 12:20" },
      { bidder: "Você", amount: 6800, date: "Hoje, 11:52" },
    ],
  },
  {
    id: 13,
    title: "Jardim em movimento",
    artist: "Marina Costa",
    artwork: "green",
    status: "superado",
    statusDate: "Seu lance foi superado ontem",
    userBid: 12400,
    history: [
      { bidder: "Rafael T.", amount: 13900, date: "Ontem, 18:04" },
      {
        bidder: "Você",
        amount: 12400,
        date: "Ontem, 17:46",
        isCurrentUser: true,
      },
      { bidder: "Ana L.", amount: 11200, date: "Ontem, 17:10" },
    ],
  },
  {
    id: 14,
    title: "Noite violeta",
    artist: "Estúdio Horizonte",
    artwork: "violet",
    status: "arrematado",
    statusDate: "Arrematado em 28 de outubro de 2026",
    userBid: 22300,
    history: [
      {
        bidder: "Você",
        amount: 22300,
        date: "28 out. 2026, 20:15",
        isCurrentUser: true,
      },
      { bidder: "Lucia P.", amount: 20800, date: "28 out. 2026, 20:02" },
      { bidder: "Você", amount: 19500, date: "28 out. 2026, 19:48" },
    ],
  },
];

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const statusLabels: Record<BidStatus, string> = {
  superado: "Lance Superado",
  liderando: "Maior lance",
  arrematado: "Arrematado",
};

function getVisibleBids(filter: BidFilter): AuctionBid[] {
  return filter === "lotes-vencidos"
    ? mockBids.filter((bid) => bid.status === "arrematado")
    : mockBids.filter((bid) => bid.status !== "arrematado");
}

const MeusArrematesPage = () => {
  const carouselRef = useRef<HTMLDivElement>(null);
  const [activeFilter, setActiveFilter] = useState<BidFilter>("meus-lances");
  const [selectedBid, setSelectedBid] = useState<AuctionBid | null>(null);
  const visibleBids = getVisibleBids(activeFilter);

  useEffect(() => {
    if (!selectedBid) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSelectedBid(null);
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

  return (
    <main className="my-auctions">
      <section aria-labelledby="my-auctions-title" className="my-auctions__intro">
        <div>
          <span className="my-auctions__eyebrow">Acompanhe sua atividade</span>
          <h1 id="my-auctions-title">Meus Arremates</h1>
          <p>Consulte seus lances e acompanhe as obras que você arrematou.</p>
        </div>
        <span className="my-auctions__demo-note">Conteúdo demonstrativo</span>
      </section>

      <div aria-label="Filtrar arremates" className="my-auctions__filters">
        <button
          aria-pressed={activeFilter === "meus-lances"}
          className={`my-auctions__filter${activeFilter === "meus-lances" ? " is-active" : ""}`}
          onClick={() => setActiveFilter("meus-lances")}
          type="button"
        >
          Meus Lances
          <span>{getVisibleBids("meus-lances").length}</span>
        </button>
        <button
          aria-pressed={activeFilter === "lotes-vencidos"}
          className={`my-auctions__filter${activeFilter === "lotes-vencidos" ? " is-active" : ""}`}
          onClick={() => setActiveFilter("lotes-vencidos")}
          type="button"
        >
          Lotes Vencidos
          <span>{getVisibleBids("lotes-vencidos").length}</span>
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

        <div className="my-auctions__track" ref={carouselRef}>
          {visibleBids.length > 0 ? (
            visibleBids.map((bid) => (
              <article className="my-bid-card" key={bid.id}>
                <div
                  aria-label={`Imagem demonstrativa da obra ${bid.title}`}
                  className={`my-bid-card__artwork my-bid-card__artwork--${bid.artwork}`}
                  role="img"
                >
                  <span>Obra em destaque</span>
                </div>

                <div className="my-bid-card__content">
                  <div className="my-bid-card__title-row">
                    <h2>{bid.title}</h2>
                    <span
                      className={`my-bid-card__badge my-bid-card__badge--${bid.status}`}
                    >
                      {statusLabels[bid.status]}
                    </span>
                  </div>
                  <p className="my-bid-card__artist">{bid.artist}</p>
                  <p
                    className={`my-bid-card__status-date my-bid-card__status-date--${bid.status}`}
                  >
                    {bid.statusDate}
                  </p>
                  <p className="my-bid-card__amount">
                    Seu lance:{" "}
                    <strong>{currencyFormatter.format(bid.userBid)}</strong>
                  </p>

                  <div className="my-bid-card__footer">
                    <button
                      className="my-bid-card__history"
                      onClick={() => setSelectedBid(bid)}
                      type="button"
                    >
                      Ver Histórico de Lances
                    </button>
                    <Link
                      className="my-bid-card__details"
                      to={`/lotes/${bid.id}`}
                    >
                      Saber mais <IoChevronForward aria-hidden="true" />
                    </Link>
                  </div>
                </div>
              </article>
            ))
          ) : (
            <p className="my-auctions__empty">
              Ainda não há lotes nesta categoria.
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

      {selectedBid && (
        <div
          className="bid-history-overlay"
          onClick={(event) => {
            if (event.target === event.currentTarget) {
              setSelectedBid(null);
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
                <span>Histórico demonstrativo</span>
                <h2 id="bid-history-title">Lances: {selectedBid.title}</h2>
              </div>
              <button
                aria-label="Fechar histórico"
                className="bid-history__close"
                onClick={() => setSelectedBid(null)}
                type="button"
              >
                <IoClose aria-hidden="true" />
              </button>
            </div>
            <ol className="bid-history__list">
              {selectedBid.history.map((entry, index) => (
                <li
                  className={entry.isCurrentUser ? "is-current-user" : ""}
                  key={`${entry.bidder}-${entry.date}-${index}`}
                >
                  <div>
                    <strong>{entry.bidder}</strong>
                    <time>{entry.date}</time>
                  </div>
                  <span>{currencyFormatter.format(entry.amount)}</span>
                </li>
              ))}
            </ol>
          </section>
        </div>
      )}
    </main>
  );
};

export default MeusArrematesPage;
