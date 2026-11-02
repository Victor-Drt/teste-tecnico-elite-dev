import {
  IoCalendarOutline,
  IoCheckmarkCircle,
  IoPeopleOutline,
  IoShieldCheckmarkOutline,
  IoTrophyOutline,
} from "react-icons/io5";
import { useParams } from "react-router";
import "./styles.css";

const bidHistory = [
  { participant: 9, amount: "R$ 12.500,00", time: "14:32:08" },
  { participant: 14, amount: "R$ 11.800,00", time: "14:29:41" },
  { participant: 3, amount: "R$ 10.950,00", time: "14:26:17" },
  { participant: 21, amount: "R$ 9.700,00", time: "14:20:53" },
];

const AuditoriaPage = () => {
  const { loteId } = useParams();

  return (
    <div className="audit-page">
      <main className="audit-card">
        <nav aria-label="Navegação da auditoria" className="audit-navbar">
          <span>Registro público de leilão</span>
          <span className="audit-navbar__note">Demonstração de interface</span>
        </nav>

        <div className="audit-content">
          <header className="audit-header">
            <div>
              <p className="audit-eyebrow">Auditoria pública</p>
              <h1>Lote #{loteId}</h1>
              <p className="audit-header__subtitle">
                Registro de encerramento e integridade do leilão
              </p>
            </div>
            <span className="audit-integrity-badge">
              <IoCheckmarkCircle aria-hidden="true" />
              Íntegro
            </span>
          </header>

          <div className="audit-grid">
            <div className="audit-column">
              <section aria-labelledby="audit-item-title">
                <div className="audit-section-heading">
                  <div>
                    <p className="audit-eyebrow">Obra arrematada</p>
                    <h2 id="audit-item-title">Composição em azul nº 3</h2>
                  </div>
                </div>

                <figure className="audit-item-figure">
                  <div
                    aria-label="Ilustração abstrata da obra do lote"
                    className="audit-artwork"
                    role="img"
                  >
                    <svg aria-hidden="true" viewBox="0 0 640 400">
                      <rect fill="#e8e8f1" height="400" width="640" />
                      <rect fill="#39334e" height="318" width="496" x="72" y="41" />
                      <circle cx="211" cy="158" fill="#7569cc" r="77" />
                      <path
                        d="M288 80h213v102H288z"
                        fill="#a5a0d4"
                        transform="rotate(18 394 131)"
                      />
                      <path
                        d="M126 284c62-79 120-65 182-12s112 63 206 4v83H126z"
                        fill="#63599e"
                      />
                      <circle cx="431" cy="238" fill="#d2cfea" r="33" />
                    </svg>
                  </div>
                  <figcaption>
                    Prévia ilustrativa da obra · Acervo de arte contemporânea
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
                      Integridade criptográfica
                    </h2>
                    <p>Registro protegido e validado</p>
                  </div>
                  <span className="audit-authenticated">
                    <IoCheckmarkCircle aria-hidden="true" />
                    Autenticado
                  </span>
                </div>
                <div className="audit-hash">
                  <span>Hash SHA-256 do registro</span>
                  <code>
                    7e3b91a4c82f6d05e1a739bc4f028d61
                    <wbr />
                    b5a8e2049d7c31f6a0e82b5c13d94700
                  </code>
                </div>
                <p className="audit-crypto__algorithm">
                  Algoritmo SHA-256 · Validação do bloco concluída
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
                <p className="audit-winner__amount">R$ 12.500,00</p>
                <p className="audit-winner__participant">
                  Arrematado por <strong>Participante #9</strong>
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
                    <strong>18/10/2025</strong>
                    <span className="audit-stat__detail">às 14:32</span>
                  </div>
                </div>
                <div className="audit-stat">
                  <span className="audit-stat__icon">
                    <IoPeopleOutline aria-hidden="true" />
                  </span>
                  <div>
                    <span className="audit-stat__label">Participantes</span>
                    <strong>12 participantes</strong>
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
                  <span>{bidHistory.length} registros</span>
                </div>
                <ol className="audit-bids">
                  {bidHistory.map((bid, index) => (
                    <li
                      className={`audit-bid${index === 0 ? " audit-bid--winner" : ""}`}
                      key={bid.participant}
                    >
                      <span className="audit-bid__position">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <div className="audit-bid__details">
                        <strong>Participante #{bid.participant}</strong>
                        <span>{bid.time}</span>
                      </div>
                      <strong className="audit-bid__amount">{bid.amount}</strong>
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
