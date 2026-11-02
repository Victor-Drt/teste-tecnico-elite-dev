import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import {
  IoArrowBack,
  IoArrowForward,
  IoChevronForward,
  IoClose,
} from "react-icons/io5";
import { createLote } from "../../services/lotes";
import { fetchItemDetails, fetchItens, getItemImageUrl } from "../../services/itens";
import type { ItemDetails, ItemSummary } from "../../types/itens";
import "./styles.css";

const PAGE_SIZE = 50;

type ModalState =
  | { type: "details"; item: ItemSummary }
  | { type: "create"; item: ItemSummary }
  | null;

function getDefaultDates() {
  const startsAt = new Date(Date.now() + 60 * 60 * 1000);
  const endsAt = new Date(Date.now() + 24 * 60 * 60 * 1000);
  const toLocalInputValue = (date: Date) => {
    const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
    return localDate.toISOString().slice(0, 16);
  };

  return {
    startsAt: toLocalInputValue(startsAt),
    endsAt: toLocalInputValue(endsAt),
  };
}

const ItensPage = () => {
  const carouselRef = useRef<HTMLDivElement>(null);
  const [items, setItems] = useState<ItemSummary[]>([]);
  const [totalLoaded, setTotalLoaded] = useState(0);
  const [hasMoreItems, setHasMoreItems] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [loadMoreError, setLoadMoreError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [modal, setModal] = useState<ModalState>(null);
  const [itemDetails, setItemDetails] = useState<ItemDetails | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");
  const [isCreatingLot, setIsCreatingLot] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");
  const [formValues, setFormValues] = useState(() => getDefaultDates());

  useEffect(() => {
    let isCurrentRequest = true;

    fetchItens(0, PAGE_SIZE)
      .then((response) => {
        if (isCurrentRequest) {
          setItems(response);
          setTotalLoaded(response.length);
          setHasMoreItems(response.length === PAGE_SIZE);
          carouselRef.current?.scrollTo({ left: 0 });
        }
      })
      .catch(() => {
        if (isCurrentRequest) {
          setLoadError("Não foi possível carregar os itens. Tente novamente.");
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
  }, [reloadKey]);

  useEffect(() => {
    if (modal?.type !== "details") {
      return;
    }

    let isCurrentRequest = true;
    fetchItemDetails(modal.item.id)
      .then((details) => {
        if (isCurrentRequest) {
          setItemDetails(details);
        }
      })
      .catch(() => {
        if (isCurrentRequest) {
          setDetailsError("Não foi possível carregar os detalhes deste item.");
        }
      })
      .finally(() => {
        if (isCurrentRequest) {
          setDetailsLoading(false);
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

  const scrollCarousel = (direction: -1 | 1) => {
    carouselRef.current?.scrollBy({
      left: direction * carouselRef.current.clientWidth * 0.8,
      behavior: "smooth",
    });
  };

  const retryLoading = () => {
    setIsLoading(true);
    setLoadError("");
    setReloadKey((key) => key + 1);
  };

  const loadMore = async () => {
    setIsLoadingMore(true);
    setLoadMoreError("");
    try {
      const nextItems = await fetchItens(totalLoaded, PAGE_SIZE);
      setItems((current) => [...current, ...nextItems]);
      setTotalLoaded((current) => current + nextItems.length);
      setHasMoreItems(nextItems.length === PAGE_SIZE);
    } catch {
      setLoadMoreError("Não foi possível carregar mais itens.");
    } finally {
      setIsLoadingMore(false);
    }
  };

  const openDetails = (item: ItemSummary) => {
    setItemDetails(null);
    setDetailsError("");
    setDetailsLoading(true);
    setModal({ type: "details", item });
  };

  const retryDetails = () => {
    if (!modal || modal.type !== "details") {
      return;
    }
    setItemDetails(null);
    setDetailsError("");
    setDetailsLoading(true);
    setModal({ ...modal });
  };

  const openCreateForm = (item: ItemSummary) => {
    setCreateError("");
    setFormValues(getDefaultDates());
    setModal({ type: "create", item });
  };

  const handleCreateLot = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!modal || modal.type !== "create") {
      return;
    }

    const formData = new FormData(event.currentTarget);
    const startDate = String(formData.get("data_inicio"));
    const endDate = String(formData.get("data_fim"));
    const startingValue = Number(formData.get("valor_inicial"));
    const minimumIncrement = Number(formData.get("incremento_minimo"));

    if (
      !Number.isFinite(startingValue) ||
      !Number.isFinite(minimumIncrement) ||
      startingValue <= 0 ||
      minimumIncrement <= 0
    ) {
      setCreateError("Informe valores iniciais e incrementos maiores que zero.");
      return;
    }
    if (new Date(endDate) <= new Date(startDate)) {
      setCreateError("O encerramento precisa ser posterior ao início do lote.");
      return;
    }

    setIsCreatingLot(true);
    setCreateError("");
    try {
      await createLote({
        item_id: modal.item.id,
        data_inicio: `${startDate}:00`,
        data_fim: `${endDate}:00`,
        valor_inicial: startingValue.toFixed(2),
        incremento_minimo: minimumIncrement.toFixed(2),
      });
      setCreateSuccess(`Lote de "${modal.item.titulo}" criado com sucesso.`);
      setModal(null);
    } catch {
      setCreateError("Não foi possível criar o lote. Verifique os dados e tente novamente.");
    } finally {
      setIsCreatingLot(false);
    }
  };

  return (
    <main className="items-page">
      <section aria-labelledby="items-page-title" className="items-page__intro">
        <div>
          <span className="items-page__eyebrow">Catálogo de obras</span>
          <h1 id="items-page-title">Itens</h1>
          <p>Escolha uma obra do catálogo e crie seu lote.</p>
        </div>
      </section>

      {createSuccess && (
        <p className="items-page__success" role="status">
          {createSuccess}
          <button
            aria-label="Fechar mensagem"
            onClick={() => setCreateSuccess("")}
            type="button"
          >
            <IoClose aria-hidden="true" />
          </button>
        </p>
      )}

      <section aria-label="Itens disponíveis" className="items-page__carousel">
        <button
          aria-label="Ver itens anteriores"
          className="items-page__arrow items-page__arrow--previous"
          onClick={() => scrollCarousel(-1)}
          type="button"
        >
          <IoArrowBack aria-hidden="true" />
        </button>

        <div aria-live="polite" className="items-page__track" ref={carouselRef}>
          {isLoading ? (
            <p className="items-page__message" role="status">
              Carregando itens...
            </p>
          ) : loadError ? (
            <div className="items-page__message" role="alert">
              <p>{loadError}</p>
              <button onClick={retryLoading} type="button">
                Tentar novamente
              </button>
            </div>
          ) : items.length > 0 ? (
            items.map((item) => (
              <article className="item-card" key={item.id}>
                <div className="item-card__artwork">
                  <img
                    alt={item.titulo}
                    decoding="async"
                    loading="lazy"
                    src={getItemImageUrl(item.id)}
                  />
                </div>
                <div className="item-card__content">
                  <h2>{item.titulo}</h2>
                  <p>{item.info_artista ?? "Artista não informado"}</p>
                  <div className="item-card__footer">
                    <button
                      className="item-card__create"
                      onClick={() => openCreateForm(item)}
                      type="button"
                    >
                      Criar Lote
                    </button>
                    <button
                      className="item-card__details"
                      onClick={() => openDetails(item)}
                      type="button"
                    >
                      Detalhes <IoChevronForward aria-hidden="true" />
                    </button>
                  </div>
                </div>
              </article>
            ))
          ) : (
            <p className="items-page__message">
              Não há itens disponíveis no catálogo.
            </p>
          )}
        </div>

        <button
          aria-label="Ver próximos itens"
          className="items-page__arrow items-page__arrow--next"
          onClick={() => scrollCarousel(1)}
          type="button"
        >
          <IoArrowForward aria-hidden="true" />
        </button>
      </section>

      {!isLoading && !loadError && hasMoreItems && (
        <div className="items-page__load-more">
          {loadMoreError && (
            <p role="alert">{loadMoreError}</p>
          )}
          <button disabled={isLoadingMore} onClick={loadMore} type="button">
            {isLoadingMore ? "Carregando..." : "Carregar mais itens"}
          </button>
        </div>
      )}

      {modal && (
        <div
          className="items-modal-overlay"
          onClick={(event) => {
            if (event.target === event.currentTarget && !isCreatingLot) {
              setModal(null);
            }
          }}
        >
          <section
            aria-labelledby="items-modal-title"
            aria-modal="true"
            className="items-modal"
            role="dialog"
          >
            <div className="items-modal__header">
              <div>
                <span>
                  {modal.type === "create" ? "Novo leilão" : "Detalhes da obra"}
                </span>
                <h2 id="items-modal-title">{modal.item.titulo}</h2>
              </div>
              <button
                aria-label="Fechar"
                className="items-modal__close"
                disabled={isCreatingLot}
                onClick={() => setModal(null)}
                type="button"
              >
                <IoClose aria-hidden="true" />
              </button>
            </div>

            {modal.type === "details" ? (
              detailsLoading ? (
                <p className="items-modal__message" role="status">
                  Carregando detalhes...
                </p>
              ) : detailsError ? (
                <div className="items-modal__message" role="alert">
                  <p>{detailsError}</p>
                  <button onClick={retryDetails} type="button">
                    Tentar novamente
                  </button>
                </div>
              ) : itemDetails ? (
                <dl className="item-details">
                  <div>
                    <dt>Artista</dt>
                    <dd>{itemDetails.info_artista ?? "Não informado"}</dd>
                  </div>
                  <div>
                    <dt>Data da obra</dt>
                    <dd>{itemDetails.data_exibicao ?? "Não informada"}</dd>
                  </div>
                  <div>
                    <dt>Referência</dt>
                    <dd>{itemDetails.numero_referencia ?? "Não informada"}</dd>
                  </div>
                  <div>
                    <dt>Descrição</dt>
                    <dd>{itemDetails.descricao ?? "Sem descrição disponível."}</dd>
                  </div>
                </dl>
              ) : null
            ) : (
              <form className="create-lot-form" onSubmit={handleCreateLot}>
                <p>
                  Defina o período do leilão, o valor inicial e o incremento
                  mínimo para esta obra.
                </p>
                <label>
                  Início do leilão
                  <input
                    min={formValues.startsAt}
                    name="data_inicio"
                    onChange={(event) =>
                      setFormValues((values) => ({
                        ...values,
                        startsAt: event.target.value,
                      }))
                    }
                    required
                    type="datetime-local"
                    value={formValues.startsAt}
                  />
                </label>
                <label>
                  Encerramento do leilão
                  <input
                    min={formValues.startsAt}
                    name="data_fim"
                    onChange={(event) =>
                      setFormValues((values) => ({
                        ...values,
                        endsAt: event.target.value,
                      }))
                    }
                    required
                    type="datetime-local"
                    value={formValues.endsAt}
                  />
                </label>
                <div className="create-lot-form__values">
                  <label>
                    Valor inicial (R$)
                    <input
                      min="0.01"
                      name="valor_inicial"
                      required
                      step="0.01"
                      type="number"
                    />
                  </label>
                  <label>
                    Incremento mínimo (R$)
                    <input
                      min="0.01"
                      name="incremento_minimo"
                      required
                      step="0.01"
                      type="number"
                    />
                  </label>
                </div>
                {createError && (
                  <p className="create-lot-form__error" role="alert">
                    {createError}
                  </p>
                )}
                <button
                  className="create-lot-form__submit"
                  disabled={isCreatingLot}
                  type="submit"
                >
                  {isCreatingLot ? "Criando lote..." : "Confirmar criação"}
                </button>
              </form>
            )}
          </section>
        </div>
      )}
    </main>
  );
};

export default ItensPage;
