from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.models.carteiras import Carteira
from app.models.lances import Lance
from app.models.liquidacoes import LiquidacaoLote
from app.models.lotes import StatusLote
from app.services.lotes import LoteService


@pytest.mark.lotes
def test_encerrar_lote_expirado_liquida_lance_vencedor_uma_unica_vez(
    lote_ao_vivo,
    usuario_licitante,
    usuario_teste,
    carteira_licitante,
    db_session,
):
    lote_ao_vivo.data_fim = datetime.now() - timedelta(seconds=1)
    lote_ao_vivo.valor_atual = Decimal("150.00")
    carteira_licitante.saldo_total = Decimal("500.00")
    carteira_licitante.saldo_comprometido = Decimal("150.00")
    lance = Lance(
        licitante_id=usuario_licitante.id,
        lote_id=lote_ao_vivo.id,
        valor=Decimal("150.00"),
    )
    db_session.add(lance)
    db_session.commit()

    resultado = LoteService(db_session).encerrar_lote_expirado(lote_ao_vivo.id)

    db_session.refresh(lote_ao_vivo)
    db_session.refresh(carteira_licitante)
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
    assert resultado.vencedor_id == usuario_licitante.id
    assert resultado.valor_liquidado == Decimal("150.00")
    assert lote_ao_vivo.status == StatusLote.CONCLUIDO
    assert lote_ao_vivo.vencedor_id == usuario_licitante.id
    assert carteira_licitante.saldo_total == Decimal("350.00")
    assert carteira_licitante.saldo_comprometido == Decimal("0.00")
    assert carteira_leiloeiro.saldo_total == Decimal("150.00")
    assert comprovante.vencedor_id == usuario_licitante.id
    assert comprovante.lance_id == lance.id
    assert comprovante.valor == Decimal("150.00")

    resultado_repetido = LoteService(db_session).encerrar_lote_expirado(
        lote_ao_vivo.id
    )

    assert resultado_repetido is None
    assert db_session.query(LiquidacaoLote).count() == 1
    assert carteira_leiloeiro.saldo_total == Decimal("150.00")


@pytest.mark.lotes
def test_encerrar_lote_expirado_sem_lances_conclui_sem_transferencia(
    lote_ao_vivo,
    usuario_teste,
    db_session,
):
    lote_ao_vivo.data_fim = datetime.now() - timedelta(seconds=1)
    valor_inicial = lote_ao_vivo.valor_atual
    db_session.commit()

    resultado = LoteService(db_session).encerrar_lote_expirado(lote_ao_vivo.id)

    db_session.refresh(lote_ao_vivo)
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
    assert db_session.query(Carteira).filter_by(usuario_id=usuario_teste.id).count() == 0
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
    lote_ao_vivo.data_fim = datetime.now() - timedelta(seconds=1)
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
