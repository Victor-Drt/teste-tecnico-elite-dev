import { isAxiosError } from "axios";
import { useEffect, useState } from "react";
import {
  IoCalendarOutline,
  IoCheckmarkCircle,
  IoPeopleOutline,
  IoShieldCheckmarkOutline,
  IoTrophyOutline,
} from "react-icons/io5";
import { useParams } from "react-router";
import { fetchAuditoriaPublica } from "../../services/auditoria";
import { getItemImageUrl } from "../../services/itens";
import type { AuditoriaPublica } from "../../types/auditoria";
import "./styles.css";

type PageState =
  | { loteId: string; status: "loading" }
  | { loteId: string; status: "error"; message: string }
  | { loteId: string; status: "loaded"; audit: AuditoriaPublica };

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const dateTimeFormatter = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "medium",
  timeStyle: "short",
});

function formatDate(value: string): string {
  return dateTimeFormatter.format(new Date(value));
}

function AuditMessage({
  isLoading,
  message,
  onRetry,
}: {
  isLoading: boolean;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="audit-page">
      <main className="audit-card">
        <nav aria-label="Navegação da auditoria" className="audit-navbar">
          <span>Registro público de leilão</span>
          <span className="audit-navbar__note">Consulta pública</span>
        </nav>
        <section
          aria-live="polite"
          className="audit-feedback"
          role={isLoading ? "status" : "alert"}
        >
          <h1>
            {isLoading ? "Carregando auditoria" : "Auditoria indisponível"}
          </h1>
          <p>{message}</p>
          {onRetry && (
            <button onClick={onRetry} type="button">
              Tentar novamente
            </button>
          )}
        </section>
      </main>
    </div>
  );
}

const AuditoriaPage = () => {
  const { loteId = "" } = useParams();
  const [reloadKey, setReloadKey] = useState(0);
  const [pageState, setPageState] = useState<PageState>({
    loteId: "",
    status: "loading",
  });
  const isCurrentPage = pageState.loteId === loteId;
  const audit =
    isCurrentPage && pageState.status === "loaded" ? pageState.audit : null;
  const isLoading = !isCurrentPage || pageState.status === "loading";
  const errorMessage =
    isCurrentPage && pageState.status === "error" ? pageState.message : "";

  useEffect(() => {
    let isCurrent = true;
    const parsedLotId = Number(loteId);

    if (!Number.isSafeInteger(parsedLotId) || parsedLotId < 1) {
      Promise.resolve().then(() => {
        if (isCurrent) {
          setPageState({
            loteId,
            status: "error",
            message: "O identificador do lote é inválido.",
          });
        }
      });
      return () => {
        isCurrent = false;
      };
    }

    fetchAuditoriaPublica(parsedLotId)
      .then((response) => {
        if (isCurrent) {
          setPageState({ loteId, status: "loaded", audit: response });
        }
      })
      .catch((error: unknown) => {
        if (!isCurrent) {
          return;
        }

        const message = isAxiosError<{ detail?: string }>(error)
          ? error.response?.status === 404
            ? "Este lote não possui uma auditoria pública disponível."
            : error.response?.status === 409
              ? error.response.data.detail ??
                "Os dados do encerramento não correspondem ao histórico de lances."
              : "Não foi possível carregar os dados da auditoria."
          : "Não foi possível carregar os dados da auditoria.";
        setPageState({ loteId, status: "error", message });
      });

    return () => {
      isCurrent = false;
    };
  }, [loteId, reloadKey]);

  if (isLoading) {
    return (
      <AuditMessage
        isLoading
        message="Buscando os dados públicos do lote..."
      />
    );
  }

  if (errorMessage || !audit) {
    return (
      <AuditMessage
        isLoading={false}
        message={errorMessage || "Não foi possível encontrar esta auditoria."}
        onRetry={() => setReloadKey((key) => key + 1)}
      />
    );
  }

  return (
    <div className="audit-page">
      <main className="audit-card">
        <nav aria-label="Navegação da auditoria" className="audit-navbar">
          <span>Registro público de leilão</span>
          <span className="audit-navbar__note">Consulta pública</span>
        </nav>

        <div className="audit-content">
          <header className="audit-header">
            <div>
              <p className="audit-eyebrow">Auditoria pública</p>
              <h1>Lote #{audit.lote_id}</h1>
              <p className="audit-header__subtitle">
                Registro de encerramento e histórico público do leilão
              </p>
            </div>
            <span className="audit-status-badge">
              <IoCheckmarkCircle aria-hidden="true" />
              Encerrado
            </span>
          </header>

          <div className="audit-grid">
            <div className="audit-column">
              <section aria-labelledby="audit-item-title">
                <div className="audit-section-heading">
                  <div>
                    <p className="audit-eyebrow">Obra arrematada</p>
                    <h2 id="audit-item-title">{audit.item.titulo}</h2>
                  </div>
                </div>

                <figure className="audit-item-figure">
                  <img
                    alt={audit.item.titulo}
                    className="audit-artwork"
                    decoding="async"
                    src={getItemImageUrl(audit.item.id)}
                  />
                  <figcaption>
                    {audit.item.info_artista ?? "Artista não informado"}
                    {audit.item.data_exibicao
                      ? ` · ${audit.item.data_exibicao}`
                      : ""}
                  </figcaption>
                </figure>
              </section>

              <section
                aria-labelledby="audit-cryptography-title"
                className="audit-crypto"
              >
                <div className="audit-crypto__heading">
                  <span className="audit-crypto__icon">
                    <IoShieldCheckmarkOutline aria-hidden="true" />
                  </span>
                  <div>
                    <h2 id="audit-cryptography-title">
                      Integridade do histórico
                    </h2>
                    <p>Cadeia SHA-256 dos lances</p>
                  </div>
                  <span
                    className="audit-hash-status"
                    data-integrity={audit.integridade_cadeia}
                  >
                    {audit.integridade_cadeia === "verificada"
                      ? "Cadeia verificada"
                      : audit.integridade_cadeia === "inconsistente"
                        ? "Divergência detectada"
                        : "Não verificada"}
                  </span>
                </div>
                <div className="audit-hash">
                  <span>Âncora gravada na liquidação</span>
                  <code>
                    {audit.hash_cadeia_lances ??
                      "Não há âncora persistida para este histórico."}
                  </code>
                  {audit.quantidade_lances_ancorada !== null && (
                    <span>
                      Quantidade de lances no encerramento:{" "}
                      {audit.quantidade_lances_ancorada}
                    </span>
                  )}
                </div>
                <div className="audit-hash">
                  <span>Fingerprint dos dados apresentados</span>
                  <code>{audit.hash_sha256}</code>
                </div>
                <p className="audit-crypto__algorithm">
                  {audit.integridade_cadeia === "verificada"
                    ? "Os hashes de cada lance e a âncora da liquidação correspondem ao histórico atual."
                    : audit.integridade_cadeia === "inconsistente"
                      ? "A cadeia atual não corresponde à âncora persistida. O histórico pode ter sido alterado."
                      : "Este registro não possui uma âncora de cadeia e não pode ser verificado retroativamente."}{" "}
                  A âncora está no mesmo banco: alguém que reescreva todo o
                  histórico e a âncora poderá recalcular a cadeia.
                </p>
              </section>
            </div>

            <div className="audit-column">
              <section
                aria-labelledby="audit-winner-title"
                className="audit-winner"
              >
                <div className="audit-winner__label">
                  <IoTrophyOutline aria-hidden="true" />
                  <span id="audit-winner-title">Lance vencedor</span>
                </div>
                <p className="audit-winner__amount">
                  {currencyFormatter.format(Number(audit.valor_arrematado))}
                </p>
                <p className="audit-winner__participant">
                  Arrematado por <strong>{audit.vencedor}</strong>
                </p>
              </section>

              <section
                aria-label="Dados de encerramento e participantes"
                className="audit-stats"
              >
                <div className="audit-stat">
                  <span className="audit-stat__icon">
                    <IoCalendarOutline aria-hidden="true" />
                  </span>
                  <div>
                    <span className="audit-stat__label">Encerramento</span>
                    <strong>{formatDate(audit.data_fim)}</strong>
                  </div>
                </div>
                <div className="audit-stat">
                  <span className="audit-stat__icon">
                    <IoPeopleOutline aria-hidden="true" />
                  </span>
                  <div>
                    <span className="audit-stat__label">Participantes</span>
                    <strong>{audit.total_participantes} participantes</strong>
                    <span className="audit-stat__detail">anonimizados</span>
                  </div>
                </div>
              </section>

              <section
                aria-labelledby="audit-history-title"
                className="audit-history"
              >
                <div className="audit-history__heading">
                  <div>
                    <p className="audit-eyebrow">Transparência do processo</p>
                    <h2 id="audit-history-title">Histórico de lances</h2>
                  </div>
                  <span>{audit.total_lances} registros</span>
                </div>
                <ol className="audit-bids">
                  {audit.lances
                    .slice()
                    .reverse()
                    .map((bid, index) => (
                      <li
                        className={`audit-bid${index === 0 ? " audit-bid--winner" : ""}`}
                        key={`${bid.data_criacao}-${index}`}
                      >
                        <span className="audit-bid__position">
                          {String(audit.total_lances - index).padStart(2, "0")}
                        </span>
                        <div className="audit-bid__details">
                          <strong>{bid.participante}</strong>
                          <time dateTime={bid.data_criacao}>
                            {formatDate(bid.data_criacao)}
                          </time>
                        </div>
                        <strong className="audit-bid__amount">
                          {currencyFormatter.format(Number(bid.valor))}
                        </strong>
                        <details className="audit-bid__proof">
                          <summary>Prova SHA-256 do lance</summary>
                          <span>Hash anterior</span>
                          <code>
                            {bid.hash_anterior ?? "Hash não registrado"}
                          </code>
                          <span>Hash do evento</span>
                          <code>{bid.hash_evento ?? "Hash não registrado"}</code>
                        </details>
                      </li>
                    ))}
                </ol>
              </section>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AuditoriaPage;
