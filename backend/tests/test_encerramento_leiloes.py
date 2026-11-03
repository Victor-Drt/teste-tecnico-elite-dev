from datetime import timedelta
from decimal import Decimal

import pytest

from app.models.carteiras import Carteira
from app.models.lances import Lance
from app.models.liquidacoes import LiquidacaoLote
from app.models.lotes import Lote, StatusLote
from app.core.time import utc_now_naive
from app.repositories.lotes import ativar_lotes_agendados
from app.schemas.lances import LanceCreate
from app.schemas.usuarios import UsuarioResponse
from app.services.lances import LanceService
from app.services.lotes import LoteService


@pytest.mark.lotes
def test_ativar_lotes_agendados_muda_status_apenas_quando_chega_o_inicio(
    lote_teste,
    itens_catalogo_teste,
    usuario_teste,
    db_session,
):
    agora = utc_now_naive()
    lote_teste.data_inicio = agora - timedelta(seconds=1)
    lote_teste.data_fim = agora + timedelta(hours=1)
    lote_futuro = Lote(
        item_id=itens_catalogo_teste[1].id,
        leiloeiro_id=usuario_teste.id,
        valor_inicial=200,
        valor_atual=200,
        incremento_minimo=20,
        data_inicio=agora + timedelta(hours=1),
        data_fim=agora + timedelta(hours=2),
    )
    db_session.add(lote_futuro)
    db_session.commit()
    db_session.refresh(lote_futuro)

    ativados = ativar_lotes_agendados(db_session, agora)

    db_session.refresh(lote_teste)
    db_session.refresh(lote_futuro)
    assert ativados == [lote_teste.id]
    assert lote_teste.status == StatusLote.AO_VIVO
    assert lote_futuro.status == StatusLote.EM_BREVE


@pytest.mark.lotes
def test_encerrar_lote_expirado_liquida_lance_vencedor_uma_unica_vez(
    lote_ao_vivo,
    usuario_licitante,
    outro_usuario_licitante,
    usuario_teste,
    carteira_licitante,
    carteira_outro_licitante,
    db_session,
):
    lance_service = LanceService(db_session)
    lance_service.criar_lance(
        UsuarioResponse.model_validate(usuario_licitante),
        LanceCreate(lote_id=lote_ao_vivo.id, valor=Decimal("120.00")),
    )

    lance_resumo = lance_service.criar_lance(
        UsuarioResponse.model_validate(outro_usuario_licitante),
        LanceCreate(lote_id=lote_ao_vivo.id, valor=Decimal("150.00")),
    )
    lance = db_session.query(Lance).filter(Lance.id == lance_resumo.id).one()
    lote_ao_vivo.data_fim = utc_now_naive() - timedelta(seconds=1)
    db_session.commit()

    resultado = LoteService(db_session).encerrar_lote_expirado(lote_ao_vivo.id)

    db_session.refresh(lote_ao_vivo)
    db_session.refresh(carteira_licitante)
    db_session.refresh(carteira_outro_licitante)
    carteira_leiloeiro = (
        db_session.query(Carteira)
        .filter(Carteira.usuario_id == usuario_teste.id)
        .one()
    )
    comprovante = (
        db_session.query(LiquidacaoLote)
        .filter(LiquidacaoLote.lote_id == lote_ao_vivo.id)
        .one()
    )

    assert resultado is not None
    assert resultado.vencedor_id == outro_usuario_licitante.id
    assert resultado.valor_liquidado == Decimal("150.00")
    assert lote_ao_vivo.status == StatusLote.CONCLUIDO
    assert lote_ao_vivo.vencedor_id == outro_usuario_licitante.id
    assert carteira_licitante.saldo_total == Decimal("1000.00")
    assert carteira_licitante.saldo_comprometido == Decimal("0.00")
    assert carteira_outro_licitante.saldo_total == Decimal("850.00")
    assert carteira_outro_licitante.saldo_comprometido == Decimal("0.00")
    assert carteira_leiloeiro.saldo_total == Decimal("150.00")
    assert comprovante.vencedor_id == outro_usuario_licitante.id
    assert comprovante.leiloeiro_id == usuario_teste.id
    assert comprovante.lance_id == lance.id
    assert comprovante.valor == Decimal("150.00")
    assert comprovante.hash_cadeia_lances == lance.hash_evento
    assert comprovante.quantidade_lances == 2
    assert len(lance.hash_anterior) == 64
    assert len(lance.hash_evento) == 64
    lance_inicial = (
        db_session.query(Lance)
        .filter(
            Lance.lote_id == lote_ao_vivo.id,
            Lance.id != lance.id,
        )
        .one()
    )
    assert lance_inicial.hash_anterior == "0" * 64
    assert lance.hash_anterior == lance_inicial.hash_evento

    auditoria = LoteService(db_session).buscar_auditoria_publica(
        lote_ao_vivo.id
    )
    assert auditoria.integridade_cadeia == "verificada"
    assert auditoria.hash_cadeia_lances == comprovante.hash_cadeia_lances

    resultado_repetido = LoteService(db_session).encerrar_lote_expirado(
        lote_ao_vivo.id
    )

    assert resultado_repetido is None
    assert db_session.query(LiquidacaoLote).count() == 1
    db_session.refresh(carteira_outro_licitante)
    assert carteira_outro_licitante.saldo_total == Decimal("850.00")
    assert carteira_outro_licitante.saldo_comprometido == Decimal("0.00")
    assert carteira_leiloeiro.saldo_total == Decimal("150.00")


@pytest.mark.lotes
def test_encerrar_lote_expirado_sem_lances_conclui_sem_transferencia(
    lote_ao_vivo,
    usuario_teste,
    db_session,
):
    lote_ao_vivo.data_fim = utc_now_naive() - timedelta(seconds=1)
    valor_inicial = lote_ao_vivo.valor_atual
    carteira_leiloeiro = Carteira(
        usuario_id=usuario_teste.id,
        saldo_total=Decimal("250.00"),
        saldo_comprometido=Decimal("0.00"),
    )
    db_session.add(carteira_leiloeiro)
    db_session.commit()

    resultado = LoteService(db_session).encerrar_lote_expirado(lote_ao_vivo.id)

    db_session.refresh(lote_ao_vivo)
    db_session.refresh(carteira_leiloeiro)
    comprovante = (
        db_session.query(LiquidacaoLote)
        .filter(LiquidacaoLote.lote_id == lote_ao_vivo.id)
        .one()
    )

    assert resultado is not None
    assert resultado.vencedor_id is None
    assert resultado.valor_liquidado == Decimal("0.00")
    assert lote_ao_vivo.status == StatusLote.CONCLUIDO
    assert lote_ao_vivo.vencedor_id is None
    assert lote_ao_vivo.valor_atual == valor_inicial
    assert carteira_leiloeiro.saldo_total == Decimal("250.00")
    assert carteira_leiloeiro.saldo_comprometido == Decimal("0.00")
    assert comprovante.vencedor_id is None
    assert comprovante.lance_id is None
    assert comprovante.valor == Decimal("0.00")


@pytest.mark.lotes
def test_nao_encerrar_lote_antes_do_prazo(
    lote_ao_vivo,
    db_session,
):
    resultado = LoteService(db_session).encerrar_lote_expirado(lote_ao_vivo.id)

    assert resultado is None
    assert lote_ao_vivo.status == StatusLote.AO_VIVO
    assert db_session.query(LiquidacaoLote).count() == 0


@pytest.mark.lotes
def test_nao_concluir_lote_se_reserva_do_vencedor_estiver_inconsistente(
    lote_ao_vivo,
    usuario_licitante,
    carteira_licitante,
    db_session,
):
    lote_ao_vivo.data_fim = utc_now_naive() - timedelta(seconds=1)
    lote_ao_vivo.valor_atual = Decimal("150.00")
    carteira_licitante.saldo_comprometido = Decimal("0.00")
    db_session.add(
        Lance(
            licitante_id=usuario_licitante.id,
            lote_id=lote_ao_vivo.id,
            valor=Decimal("150.00"),
        )
    )
    db_session.commit()

    with pytest.raises(ValueError, match="Saldo comprometido insuficiente"):
        LoteService(db_session).encerrar_lote_expirado(lote_ao_vivo.id)

    db_session.refresh(lote_ao_vivo)
    assert lote_ao_vivo.status == StatusLote.AO_VIVO
    assert lote_ao_vivo.vencedor_id is None
    assert db_session.query(LiquidacaoLote).count() == 0
    assert db_session.query(Carteira).filter_by(
        usuario_id=lote_ao_vivo.leiloeiro_id
    ).count() == 0


@pytest.mark.lotes
def test_nao_liquidar_lote_se_carteira_do_vencedor_nao_existir(
    lote_ao_vivo,
    usuario_licitante,
    db_session,
):
    lote_ao_vivo.data_fim = utc_now_naive() - timedelta(seconds=1)
    lote_ao_vivo.valor_atual = Decimal("150.00")
    db_session.add(
        Lance(
            licitante_id=usuario_licitante.id,
            lote_id=lote_ao_vivo.id,
            valor=Decimal("150.00"),
        )
    )
    db_session.commit()

    with pytest.raises(
        ValueError,
        match=f"Carteira do vencedor {usuario_licitante.id} do lote {lote_ao_vivo.id}",
    ):
        LoteService(db_session).encerrar_lote_expirado(lote_ao_vivo.id)

    db_session.refresh(lote_ao_vivo)
    assert lote_ao_vivo.status == StatusLote.AO_VIVO
    assert lote_ao_vivo.vencedor_id is None
    assert db_session.query(LiquidacaoLote).count() == 0
    assert db_session.query(Carteira).filter_by(
        usuario_id=usuario_licitante.id
    ).count() == 0


@pytest.mark.parametrize("adulteracao", ["alterar", "remover", "inserir"])
@pytest.mark.lotes
def test_auditoria_detecta_adulteracoes_no_historico_ancorado(
    adulteracao,
    lote_ao_vivo,
    usuario_licitante,
    outro_usuario_licitante,
    carteira_licitante,
    carteira_outro_licitante,
    db_session,
):
    lance_service = LanceService(db_session)
    lance_service.criar_lance(
        UsuarioResponse.model_validate(usuario_licitante),
        LanceCreate(lote_id=lote_ao_vivo.id, valor=Decimal("120.00")),
    )
    lance_service.criar_lance(
        UsuarioResponse.model_validate(outro_usuario_licitante),
        LanceCreate(lote_id=lote_ao_vivo.id, valor=Decimal("150.00")),
    )
    lance_service.criar_lance(
        UsuarioResponse.model_validate(usuario_licitante),
        LanceCreate(lote_id=lote_ao_vivo.id, valor=Decimal("170.00")),
    )
    lance_vencedor = lance_service.criar_lance(
        UsuarioResponse.model_validate(outro_usuario_licitante),
        LanceCreate(lote_id=lote_ao_vivo.id, valor=Decimal("190.00")),
    )
    lote_ao_vivo.data_fim = datetime.now() - timedelta(seconds=1)
    db_session.commit()
    LoteService(db_session).encerrar_lote_expirado(lote_ao_vivo.id)

    auditoria = LoteService(db_session).buscar_auditoria_publica(
        lote_ao_vivo.id
    )
    assert auditoria.integridade_cadeia == "verificada"

    lances = (
        db_session.query(Lance)
        .filter(Lance.lote_id == lote_ao_vivo.id)
        .order_by(Lance.data_criacao, Lance.id)
        .all()
    )
    if adulteracao == "alterar":
        lances[0].valor = Decimal("121.00")
    elif adulteracao == "remover":
        db_session.delete(lances[-2])
    else:
        db_session.add(
            Lance(
                licitante_id=usuario_licitante.id,
                lote_id=lote_ao_vivo.id,
                valor=Decimal("110.00"),
                data_criacao=utc_now_naive(),
            )
        )
    db_session.commit()
    db_session.expire(lote_ao_vivo, ["lances"])

    auditoria_adulterada = LoteService(db_session).buscar_auditoria_publica(
        lote_ao_vivo.id
    )
    assert auditoria_adulterada.integridade_cadeia == "inconsistente"
