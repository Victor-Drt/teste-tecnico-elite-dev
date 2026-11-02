import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import axios from "axios";
import { Link, useParams } from "react-router";
import {
  IoArrowBack,
  IoPeopleOutline,
  IoTimeOutline,
} from "react-icons/io5";
import { criarLance, getSalaLeilaoWebSocketUrl } from "../../services/lances";
import { fetchLoteVitrine } from "../../services/lotes";
import { getItemImageUrl } from "../../services/itens";
import type {
  LancePublico,
  SalaLeilaoEvent,
  SalaInicialEvent,
} from "../../types/lances";
import type { LoteVitrine } from "../../types/lotes";
import "./styles.css";

type PageState =
  | { loteId: string; status: "loading" }
  | { loteId: string; status: "error"; message: string }
  | { loteId: string; status: "loaded"; lot: LoteVitrine };

type RoomState = {
  loteId: number;
  lances: LancePublico[];
  lanceAtual: LancePublico | null;
  participantes: SalaInicialEvent["participantes"];
  participanteUsuario: string | null;
  situacaoUsuario: SalaInicialEvent["usuario"]["situacao"];
  valorAtual: string;
  dataFim: string;
};

type SocketStatus = "connecting" | "connected" | "disconnected";

const initialTime = Date.now();
const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

function getBidErrorMessage(error: unknown): string {
  if (axios.isAxiosError<{ detail?: unknown }>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }

  return "Não foi possível registrar seu lance. Atualize o valor e tente novamente.";
}

function formatCountdown(target: Date, currentTime: number): string {
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

function sortHistory(lances: LancePublico[]): LancePublico[] {
  return [...lances].sort(
    (first, second) =>
      new Date(second.data_criacao).getTime() -
        new Date(first.data_criacao).getTime() ||
      second.id - first.id,
  );
}

function isLancePublico(value: unknown): value is LancePublico {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof value.id === "number" &&
    "participante" in value &&
    typeof value.participante === "string" &&
    "lote_id" in value &&
    typeof value.lote_id === "number" &&
    "valor" in value &&
    typeof value.valor === "string" &&
    "data_criacao" in value &&
    typeof value.data_criacao === "string"
  );
}

function isParticipant(
  value: unknown,
): value is SalaInicialEvent["participantes"][number] {
  return (
    typeof value === "object" &&
    value !== null &&
    "participante" in value &&
    typeof value.participante === "string" &&
    "posicao" in value &&
    typeof value.posicao === "number" &&
    "situacao" in value &&
    (value.situacao === "ganhando" || value.situacao === "superado")
  );
}

function isSalaInicialEvent(value: unknown): value is SalaInicialEvent {
  if (
    typeof value !== "object" ||
    value === null ||
    !("tipo" in value) ||
    value.tipo !== "sala_inicial" ||
    !("lote" in value) ||
    typeof value.lote !== "object" ||
    value.lote === null ||
    !("id" in value.lote) ||
    typeof value.lote.id !== "number" ||
    !("status" in value.lote) ||
    typeof value.lote.status !== "string" ||
    !("data_fim" in value.lote) ||
    typeof value.lote.data_fim !== "string" ||
    !("valor_atual" in value.lote) ||
    typeof value.lote.valor_atual !== "string" ||
    !("lance_atual" in value) ||
    (value.lance_atual !== null && !isLancePublico(value.lance_atual)) ||
    !("historico_lances" in value) ||
    !Array.isArray(value.historico_lances) ||
    !value.historico_lances.every(isLancePublico) ||
    !("participantes" in value) ||
    !Array.isArray(value.participantes) ||
    !value.participantes.every(isParticipant) ||
    !("usuario" in value) ||
    typeof value.usuario !== "object" ||
    value.usuario === null ||
    !("participante" in value.usuario) ||
    (value.usuario.participante !== null &&
      typeof value.usuario.participante !== "string") ||
    !("posicao" in value.usuario) ||
    (value.usuario.posicao !== null &&
      typeof value.usuario.posicao !== "number") ||
    !("situacao" in value.usuario) ||
    (value.usuario.situacao !== "ganhando" &&
      value.usuario.situacao !== "superado" &&
      value.usuario.situacao !== "sem_lance")
  ) {
    return false;
  }
  return true;
}

function isLanceBidEvent(value: unknown): value is Extract<
  SalaLeilaoEvent,
  { tipo: "lance_atualizado" }
> {
  if (
    typeof value !== "object" ||
    value === null ||
    !("tipo" in value) ||
    value.tipo !== "lance_atualizado" ||
    !("lote_id" in value) ||
    typeof value.lote_id !== "number" ||
    !("lance" in value) ||
    !isLancePublico(value.lance) ||
    !("lance_atual" in value) ||
    (value.lance_atual !== null && !isLancePublico(value.lance_atual)) ||
    !("valor_atual" in value) ||
    typeof value.valor_atual !== "string" ||
    !("data_fim" in value) ||
    typeof value.data_fim !== "string" ||
    !("participantes" in value) ||
    !Array.isArray(value.participantes) ||
    !value.participantes.every(isParticipant)
  ) {
    return false;
  }
  return true;
}

function parseRoomEvent(rawMessage: string): SalaLeilaoEvent {
  const value: unknown = JSON.parse(rawMessage);
  if (isSalaInicialEvent(value) || isLanceBidEvent(value)) {
    return value;
  }
  throw new Error("Evento da sala de leilão inválido.");
}

function getRoomStatusLabel(status: RoomState["situacaoUsuario"]): string {
  switch (status) {
    case "ganhando":
      return "Você está ganhando";
    case "superado":
      return "Você foi superado";
    default:
      return "Faça seu primeiro lance";
  }
}

const LeilaoPage = () => {
  const { loteId = "" } = useParams();
  const [pageState, setPageState] = useState<PageState>({
    loteId: "",
    status: "loading",
  });
  const [room, setRoom] = useState<RoomState | null>(null);
  const [socketStatus, setSocketStatus] =
    useState<SocketStatus>("connecting");
  const [socketError, setSocketError] = useState("");
  const [bidValue, setBidValue] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [bidError, setBidError] = useState("");
  const [currentTime, setCurrentTime] = useState(initialTime);

  const isCurrentPage = pageState.loteId === loteId;
  const lot =
    isCurrentPage && pageState.status === "loaded" ? pageState.lot : null;
  const isLoading = !isCurrentPage || pageState.status === "loading";
  const pageError =
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
          setBidError("");
          setSocketError("");
          setSocketStatus("connecting");
          setBidValue(
            (Number(response.valor_atual) +
              Number(response.incremento_minimo)).toFixed(2),
          );
        }
      })
      .catch(() => {
        if (isCurrentRequest) {
          setPageState({
            loteId,
            status: "error",
            message: "Não foi possível carregar os dados deste lote.",
          });
        }
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [loteId]);

  useEffect(() => {
    if (!lot) {
      return;
    }

    let isCurrentSocket = true;
    const socket = new WebSocket(getSalaLeilaoWebSocketUrl(lot.id));

    socket.onopen = () => {
      if (isCurrentSocket) {
        setSocketStatus("connected");
        setSocketError("");
      }
    };

    socket.onmessage = (event: MessageEvent<string>) => {
      if (!isCurrentSocket) {
        return;
      }
      try {
        const message = parseRoomEvent(event.data);
        if (message.tipo === "sala_inicial") {
          setRoom({
            loteId: lot.id,
            lances: sortHistory(message.historico_lances),
            lanceAtual: message.lance_atual,
            participantes: message.participantes,
            participanteUsuario: message.usuario.participante,
            situacaoUsuario: message.usuario.situacao,
            valorAtual: message.lote.valor_atual,
            dataFim: message.lote.data_fim,
          });
          setBidValue(
            (
              Number(message.lote.valor_atual) +
              Number(lot.incremento_minimo)
            ).toFixed(2),
          );
        } else {
          setRoom((current) => {
            if (!current || current.loteId !== lot.id) {
              return current;
            }
            const existing = current.lances.filter(
              (bid) => bid.id !== message.lance.id,
            );
            const currentParticipant = message.participantes.find(
              (participant) =>
                participant.participante === current.participanteUsuario,
            );
            return {
              ...current,
              lances: sortHistory([...existing, message.lance]),
              lanceAtual: message.lance_atual,
              participantes: message.participantes,
              situacaoUsuario: currentParticipant?.situacao ?? "sem_lance",
              valorAtual: message.valor_atual,
              dataFim: message.data_fim,
            };
          });
          setBidValue(
            (
              Number(message.valor_atual) +
              Number(lot.incremento_minimo)
            ).toFixed(2),
          );
        }
      } catch {
        setSocketError("A sala recebeu uma atualização inválida.");
      }
    };

    socket.onerror = () => {
      if (isCurrentSocket) {
        setSocketError("Não foi possível conectar à sala de lances.");
      }
    };

    socket.onclose = (event) => {
      if (isCurrentSocket) {
        setSocketStatus("disconnected");
        if (event.code === 1008) {
          setSocketError("Este lote não está disponível para lances ao vivo.");
        } else if (event.code !== 1000) {
          setSocketError("A conexão com a sala de lances foi interrompida.");
        }
      }
    };

    return () => {
      isCurrentSocket = false;
      socket.close(1000);
    };
  }, [lot]);

  useEffect(() => {
    const timerId = window.setInterval(
      () => setCurrentTime(Date.now()),
      1000,
    );
    return () => window.clearInterval(timerId);
  }, []);

  const handleBid = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!lot || !activeRoom) {
      setBidError("Aguarde a conexão com a sala de lances.");
      return;
    }

    const amount = Number(bidValue);
    const minimumBid =
      Number(room!.valorAtual) + Number(lot.incremento_minimo);
    if (!Number.isFinite(amount) || amount < minimumBid) {
      setBidError(
        `O lance mínimo permitido é ${currencyFormatter.format(minimumBid)}.`,
      );
      return;
    }

    setIsSubmitting(true);
    setBidError("");
    try {
      const newBid = await criarLance({
        lote_id: lot.id,
        valor: amount.toFixed(2),
      });
      setRoom((current) => {
        if (!current || current.loteId !== lot.id) {
          return current;
        }
        const lances = sortHistory([
          newBid,
          ...current.lances.filter((bid) => bid.id !== newBid.id),
        ]);
        const participantes = current.participantes.some(
          (participant) => participant.participante === newBid.participante,
        )
          ? current.participantes
          : [
              ...current.participantes,
              {
                participante: newBid.participante,
                posicao: current.participantes.length + 1,
                situacao: "ganhando" as const,
              },
            ];
        return {
          ...current,
          lances,
          lanceAtual: newBid,
          participantes,
          participanteUsuario: newBid.participante,
          situacaoUsuario: "ganhando",
          valorAtual: newBid.valor,
        };
      });
      setBidValue(
        (amount + Number(lot.incremento_minimo)).toFixed(2),
      );
    } catch (error) {
      setBidError(getBidErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <main className="live-auction-page">
        <p className="live-auction-page__message" role="status">
          Carregando sala de lances...
        </p>
      </main>
    );
  }

  if (pageError || !lot) {
    return (
      <main className="live-auction-page">
        <p className="live-auction-page__message" role="alert">
          {pageError || "Não foi possível encontrar este lote."}
        </p>
        <Link className="live-auction-page__back" to="/vitrine">
          <IoArrowBack aria-hidden="true" /> Voltar para a vitrine
        </Link>
      </main>
    );
  }

  const activeRoom = room?.loteId === lot.id ? room : null;
  const endTime = new Date(activeRoom?.dataFim ?? lot.data_fim);
  const isLive = lot.status === "ao_vivo" && endTime.getTime() > currentTime;
  const currentValue = activeRoom?.valorAtual ?? lot.valor_atual;
  const minimumBid = Number(currentValue) + Number(lot.incremento_minimo);
  const history = activeRoom?.lances ?? [];
  const participants = activeRoom?.participantes ?? [];

  return (
    <main className="live-auction-page">
      <div className="live-auction">
        <section
          aria-labelledby="live-auction-artwork-title"
          className="live-auction__artwork-panel"
        >
          <div className="live-auction__artwork-heading">
            <span>Lote #{lot.id}</span>
            <h1 id="live-auction-artwork-title">{lot.item.titulo}</h1>
          </div>
          <figure className="live-auction__artwork">
            <img
              alt={lot.item.titulo}
              decoding="async"
              src={getItemImageUrl(lot.item.id)}
            />
          </figure>
          <div className="live-auction__artwork-caption">
            <strong>{lot.item.info_artista ?? "Artista não informado"}</strong>
            <p>{lot.item.descricao ?? "Sem descrição disponível para esta obra."}</p>
          </div>
        </section>

        <section
          aria-labelledby="live-auction-bid-title"
          className="live-auction__bid-panel"
        >
          <div className="live-auction__status-row">
            <span
              className={`live-auction__user-status${activeRoom?.situacaoUsuario === "ganhando" ? " is-winning" : activeRoom?.situacaoUsuario === "superado" ? " is-outbid" : ""}`}
            >
              {activeRoom
                ? getRoomStatusLabel(activeRoom.situacaoUsuario)
                : "Conectando..."}
            </span>
            <span
              className={`live-auction__live-badge${isLive ? "" : " is-closed"}`}
            >
              <span aria-hidden="true">•</span>{" "}
              {isLive ? "Ao Vivo" : "Encerrado"}
            </span>
          </div>

          {socketError && (
            <p className="live-auction__connection-error" role="alert">
              {socketError}
            </p>
          )}

          <section aria-labelledby="live-auction-bid-title" className="current-bid">
            <span id="live-auction-bid-title">Lance atual</span>
            <strong>{currencyFormatter.format(Number(currentValue))}</strong>
            {activeRoom?.lanceAtual && (
              <small>
                Lance de {activeRoom.lanceAtual.participante}
              </small>
            )}
          </section>

          <div className="live-auction__stats">
            <div className="live-auction__stat">
              <span>Tempo restante</span>
              <strong className={isLive ? "is-live" : ""}>
                <IoTimeOutline aria-hidden="true" />
                {isLive
                  ? formatCountdown(endTime, currentTime)
                  : "Leilão encerrado"}
              </strong>
            </div>
            <div className="live-auction__stat">
              <span>Participantes</span>
              <strong>
                <IoPeopleOutline aria-hidden="true" />
                {participants.length}
              </strong>
            </div>
          </div>

          <form className="live-auction__bid-form" onSubmit={handleBid}>
            <label htmlFor="next-bid-value">Valor do próximo lance</label>
            <div className="live-auction__next-value">
              {currencyFormatter.format(minimumBid)}
            </div>
            <input
              aria-label="Valor do lance em reais"
              id="next-bid-value"
              min={minimumBid}
              onChange={(event) => setBidValue(event.target.value)}
              required
              step="0.01"
              type="number"
              value={bidValue}
            />
            {bidError && (
              <p className="live-auction__bid-error" role="alert">
                {bidError}
              </p>
            )}
            <button
              disabled={
                !isLive ||
                !activeRoom ||
                socketStatus !== "connected" ||
                isSubmitting
              }
              type="submit"
            >
              {isSubmitting
                ? "Registrando lance..."
                : !isLive
                  ? "Leilão encerrado"
                  : "Dar Lance"}
            </button>
            {socketStatus === "disconnected" && !socketError && (
              <small className="live-auction__socket-status">
                Reconecte à sala para continuar dando lances.
              </small>
            )}
          </form>

          <section
            aria-labelledby="live-auction-history-title"
            className="bid-history"
          >
            <h2 id="live-auction-history-title">Histórico de lances</h2>
            {socketStatus === "connecting" && !activeRoom ? (
              <p className="bid-history__empty">Conectando ao histórico...</p>
            ) : history.length > 0 ? (
              <ol className="bid-history__list">
                {history.slice(0, 20).map((bid) => (
                  <li key={bid.id}>
                    <div>
                      <strong>
                        {bid.participante === activeRoom?.participanteUsuario
                          ? "Você"
                          : bid.participante}
                      </strong>
                      <time>
                        {new Intl.DateTimeFormat("pt-BR", {
                          hour: "2-digit",
                          minute: "2-digit",
                        }).format(new Date(bid.data_criacao))}
                      </time>
                    </div>
                    <span>{currencyFormatter.format(Number(bid.valor))}</span>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="bid-history__empty">
                Ainda não há lances neste lote.
              </p>
            )}
          </section>
        </section>
      </div>
    </main>
  );
};

export default LeilaoPage;
