import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router";
import { IoArrowBack, IoArrowForward, IoChevronForward } from "react-icons/io5";
import type { LoteListagem, LoteStatus } from "../../types/lotes";
import { fetchLotes } from "../../services/lotes";
import { getItemImageUrl } from "../../services/itens";
import "./styles.css";

type LotStatus = "ao_vivo" | "em_breve" | "encerrado";
type StatusFilter = "todos" | LotStatus;

const initialTime = Date.now();
const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

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

function getLotStatus(
  lot: LoteListagem,
  currentTime: number,
): LotStatus | null {
  if (lot.status === "cancelado") {
    return null;
  }
  if (lot.status === "concluido") {
    return "encerrado";
  }
  if (
    lot.status === "em_breve" &&
    new Date(lot.data_inicio).getTime() <= currentTime
  ) {
    return new Date(lot.data_fim).getTime() > currentTime
      ? "ao_vivo"
      : "encerrado";
  }
  return lot.status;
}

function AuctionCard({
  lot,
  currentTime,
}: {
  lot: LoteListagem;
  currentTime: number;
}) {
  const status = getLotStatus(lot, currentTime);
  if (!status) {
    return null;
  }

  const startDate = new Date(lot.data_inicio);
  const endDate = new Date(lot.data_fim);
  const dateToDisplay = status === "ao_vivo" ? endDate : startDate;
  const countdownLabel =
    status === "ao_vivo"
      ? `Encerra em ${formatTimeRemaining(dateToDisplay, currentTime)}`
      : status === "em_breve"
        ? `Começa em ${formatTimeRemaining(dateToDisplay, currentTime)}`
        : "Leilão encerrado";

  return (
    <article className="auction-card">
      <div className="auction-card__artwork">
        <img
          alt={lot.item.titulo}
          decoding="async"
          loading="lazy"
          src={getItemImageUrl(lot.item.id)}
        />
      </div>

      <div className="auction-card__content">
        <div className="auction-card__heading">
          <span
            className={`auction-card__status auction-card__status--${status}`}
          >
            {getStatusLabel(status)}
          </span>
          <h2>{lot.item.titulo}</h2>
        </div>
        <p
          className={`auction-card__countdown${status === "ao_vivo" ? " is-live" : ""}`}
        >
          {countdownLabel}
        </p>
        <p className="auction-card__artist">
          {lot.item.info_artista ?? "Artista não informado"}
        </p>
        <p className="auction-card__value">
          Valor atual: {currencyFormatter.format(Number(lot.valor_atual))}
        </p>
        <div className="auction-card__footer">
          <Link
            className="auction-card__participate"
            to={`/lotes/${lot.id}/sala`}
          >
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
  const [currentTime, setCurrentTime] = useState(initialTime);
  const [lots, setLots] = useState<LoteListagem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    const timerId = window.setInterval(
      () => setCurrentTime(Date.now()),
      30_000,
    );
    return () => window.clearInterval(timerId);
  }, []);

  useEffect(() => {
    let isCurrentRequest = true;
    const apiStatus: LoteStatus | undefined =
      activeFilter === "encerrado"
        ? "concluido"
        : activeFilter === "todos"
          ? undefined
          : activeFilter;

    fetchLotes(0, 50, apiStatus)
      .then((response) => {
        if (isCurrentRequest) {
          setLots(response);
        }
      })
      .catch(() => {
        if (isCurrentRequest) {
          setLoadError("Não foi possível carregar os lotes. Tente novamente.");
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
  }, [activeFilter]);

  const handleFilterChange = (filter: StatusFilter) => {
    if (filter === activeFilter) {
      return;
    }

    setIsLoading(true);
    setLoadError("");
    setActiveFilter(filter);
  };

  const visibleLots = useMemo(
    () => lots.filter((lot) => getLotStatus(lot, currentTime) !== null),
    [currentTime, lots],
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
      <section
        aria-labelledby="auction-showcase-title"
        className="auction-showcase__intro"
      >
        <div>
          <span className="auction-showcase__eyebrow">
            Descubra novas obras
          </span>
          <h1 id="auction-showcase-title">Vitrine de Leilões</h1>
          <p>Encontre obras únicas e participe de leilões especiais.</p>
        </div>
      </section>

      <section aria-label="Filtrar leilões" className="auction-filters">
        {filterOptions.map((option) => (
          <button
            aria-pressed={activeFilter === option.value}
            className={`auction-filter${activeFilter === option.value ? " is-active" : ""}`}
            key={option.value}
            onClick={() => handleFilterChange(option.value)}
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
          {isLoading ? (
            <p className="auction-carousel__empty" role="status">
              Carregando lotes...
            </p>
          ) : loadError ? (
            <p className="auction-carousel__empty" role="alert">
              {loadError}
            </p>
          ) : visibleLots.length > 0 ? (
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
