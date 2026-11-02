import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router";
import { IoArrowBack, IoArrowForward, IoChevronForward } from "react-icons/io5";
import "./styles.css";

type LotStatus = "ao_vivo" | "em_breve" | "encerrado";
type StatusFilter = "todos" | LotStatus;

interface AuctionLot {
  id: number;
  title: string;
  artist: string;
  description: string;
  startsAt: Date;
  endsAt: Date;
  artwork: "blue" | "terracotta" | "green" | "violet" | "gold";
}

const now = Date.now();
const mockLots: AuctionLot[] = [
  {
    id: 1,
    title: "Composição em azul",
    artist: "Acervo contemporâneo",
    description: "Acrílica sobre tela",
    startsAt: new Date(now - 45 * 60_000),
    endsAt: new Date(now + 2 * 60 * 60_000 + 35 * 60_000),
    artwork: "blue",
  },
  {
    id: 2,
    title: "Formas do horizonte",
    artist: "Ateliê Aurora",
    description: "Óleo sobre tela",
    startsAt: new Date(now - 25 * 60_000),
    endsAt: new Date(now + 4 * 60 * 60_000 + 12 * 60_000),
    artwork: "terracotta",
  },
  {
    id: 3,
    title: "Jardim em movimento",
    artist: "Marina Costa",
    description: "Técnica mista",
    startsAt: new Date(now + 18 * 60 * 60_000),
    endsAt: new Date(now + 42 * 60 * 60_000),
    artwork: "green",
  },
  {
    id: 4,
    title: "Noite violeta",
    artist: "Estúdio Horizonte",
    description: "Aquarela sobre papel",
    startsAt: new Date(now + 2 * 24 * 60 * 60_000),
    endsAt: new Date(now + 3 * 24 * 60 * 60_000),
    artwork: "violet",
  },
  {
    id: 5,
    title: "Memórias douradas",
    artist: "Acervo clássico",
    description: "Gravura em edição limitada",
    startsAt: new Date(now - 4 * 24 * 60 * 60_000),
    endsAt: new Date(now - 3 * 24 * 60 * 60_000),
    artwork: "gold",
  },
];

const filterOptions: { label: string; value: StatusFilter }[] = [
  { label: "Todos", value: "todos" },
  { label: "Ao Vivo", value: "ao_vivo" },
  { label: "Em Breve", value: "em_breve" },
  { label: "Encerrados", value: "encerrado" },
];

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

function getStatusLabel(status: LotStatus): string {
  switch (status) {
    case "ao_vivo":
      return "Ao Vivo";
    case "em_breve":
      return "Em Breve";
    case "encerrado":
      return "Encerrado";
  }
}

function getLotStatus(lot: AuctionLot, currentTime: number): LotStatus {
  if (currentTime >= lot.endsAt.getTime()) {
    return "encerrado";
  }
  if (currentTime < lot.startsAt.getTime()) {
    return "em_breve";
  }
  return "ao_vivo";
}

function AuctionCard({
  lot,
  currentTime,
}: {
  lot: AuctionLot;
  currentTime: number;
}) {
  const status = getLotStatus(lot, currentTime);
  const dateToDisplay = status === "ao_vivo" ? lot.endsAt : lot.startsAt;
  const countdownLabel =
    status === "ao_vivo"
      ? `Encerra em ${formatTimeRemaining(dateToDisplay, currentTime)}`
      : status === "em_breve"
        ? `Começa em ${formatTimeRemaining(dateToDisplay, currentTime)}`
        : "Leilão encerrado";

  return (
    <article className="auction-card">
      <div
        aria-label={`Arte abstrata em tons de ${lot.artwork}`}
        className={`auction-card__artwork auction-card__artwork--${lot.artwork}`}
        role="img"
      >
        <span className="auction-card__artwork-label">Obra em destaque</span>
      </div>
      <div className="auction-card__content">
        <div className="auction-card__heading">
          <span className={`auction-card__status auction-card__status--${status}`}>
            {getStatusLabel(status)}
          </span>
          <h2>{lot.title}</h2>
        </div>
        <p
          className={`auction-card__countdown${status === "ao_vivo" ? " is-live" : ""}`}
        >
          {countdownLabel}
        </p>
        <p className="auction-card__artist">{lot.artist}</p>
        <p className="auction-card__description">{lot.description}</p>
        <div className="auction-card__footer">
          <Link className="auction-card__participate" to={`/lotes/${lot.id}/sala`}>
            {status === "encerrado" ? "Ver resultado" : "Participar do Leilão"}
          </Link>
          <Link className="auction-card__details" to={`/lotes/${lot.id}`}>
            Saber mais <IoChevronForward aria-hidden="true" />
          </Link>
        </div>
      </div>
    </article>
  );
}

const VitrinePage = () => {
  const carouselRef = useRef<HTMLDivElement>(null);
  const [activeFilter, setActiveFilter] = useState<StatusFilter>("todos");
  const [currentTime, setCurrentTime] = useState(now);

  useEffect(() => {
    const timerId = window.setInterval(() => setCurrentTime(Date.now()), 30_000);
    return () => window.clearInterval(timerId);
  }, []);

  const visibleLots = useMemo(
    () =>
      activeFilter === "todos"
        ? mockLots
        : mockLots.filter((lot) => getLotStatus(lot, currentTime) === activeFilter),
    [activeFilter, currentTime],
  );

  const scrollCarousel = (direction: -1 | 1) => {
    if (!carouselRef.current) {
      return;
    }

    carouselRef.current.scrollBy({
      left: direction * carouselRef.current.clientWidth * 0.8,
      behavior: "smooth",
    });
  };

  return (
    <main className="auction-showcase">
      <section aria-labelledby="auction-showcase-title" className="auction-showcase__intro">
        <div>
          <span className="auction-showcase__eyebrow">Descubra novas obras</span>
          <h1 id="auction-showcase-title">Vitrine de Leilões</h1>
          <p>Encontre obras únicas e participe de leilões especiais.</p>
        </div>
        <span className="auction-showcase__demo-note">Conteúdo demonstrativo</span>
      </section>

      <section aria-label="Filtrar leilões" className="auction-filters">
        {filterOptions.map((option) => (
          <button
            aria-pressed={activeFilter === option.value}
            className={`auction-filter${activeFilter === option.value ? " is-active" : ""}`}
            key={option.value}
            onClick={() => setActiveFilter(option.value)}
            type="button"
          >
            {option.label}
          </button>
        ))}
      </section>

      <section aria-label="Lotes de leilão" className="auction-carousel">
        <button
          aria-label="Ver lotes anteriores"
          className="auction-carousel__arrow auction-carousel__arrow--previous"
          onClick={() => scrollCarousel(-1)}
          type="button"
        >
          <IoArrowBack aria-hidden="true" />
        </button>
        <div className="auction-carousel__track" ref={carouselRef}>
          {visibleLots.length > 0 ? (
            visibleLots.map((lot) => (
              <AuctionCard currentTime={currentTime} key={lot.id} lot={lot} />
            ))
          ) : (
            <p className="auction-carousel__empty">
              Não há lotes nesta categoria no momento.
            </p>
          )}
        </div>
        <button
          aria-label="Ver próximos lotes"
          className="auction-carousel__arrow auction-carousel__arrow--next"
          onClick={() => scrollCarousel(1)}
          type="button"
        >
          <IoArrowForward aria-hidden="true" />
        </button>
      </section>
    </main>
  );
};

export default VitrinePage;
