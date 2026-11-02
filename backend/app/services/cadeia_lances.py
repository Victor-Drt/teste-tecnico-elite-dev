import hashlib
import json
from collections.abc import Sequence

from app.models.lances import Lance

HASH_INICIAL_CADEIA = "0" * 64


def ordenar_lances(lances: Sequence[Lance]) -> list[Lance]:
    return sorted(lances, key=lambda lance: (lance.data_criacao, lance.id))


def mapear_participantes(lances: Sequence[Lance]) -> dict[int, str]:
    participantes: dict[int, str] = {}
    for lance in ordenar_lances(lances):
        if lance.licitante_id not in participantes:
            participantes[lance.licitante_id] = (
                f"Participante #{len(participantes) + 1}"
            )
    return participantes


def obter_sufixo_cadeia(lances: Sequence[Lance]) -> list[Lance] | None:
    lances_ordenados = ordenar_lances(lances)
    inicio_cadeia = next(
        (
            indice
            for indice, lance in enumerate(lances_ordenados)
            if lance.hash_anterior is not None or lance.hash_evento is not None
        ),
        None,
    )
    if inicio_cadeia is None:
        return []

    sufixo = lances_ordenados[inicio_cadeia:]
    if any(
        lance.hash_anterior is None or lance.hash_evento is None
        for lance in sufixo
    ):
        return None
    return sufixo


def calcular_hash_lance(
    lance: Lance,
    participante: str,
    hash_anterior: str,
) -> str:
    dados = {
        "versao": 1,
        "lance_id": lance.id,
        "lote_id": lance.lote_id,
        "participante": participante,
        "valor": format(lance.valor, ".2f"),
        "data_criacao": lance.data_criacao.isoformat(),
        "hash_anterior": hash_anterior,
    }
    conteudo = json.dumps(
        dados,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(conteudo).hexdigest()


def verificar_cadeia_lances(
    lances: Sequence[Lance],
    hash_ancora: str,
) -> bool:
    hash_anterior = HASH_INICIAL_CADEIA
    participantes: dict[int, str] = {}

    for lance in ordenar_lances(lances):
        if lance.hash_anterior != hash_anterior or not lance.hash_evento:
            return False

        participante = participantes.get(lance.licitante_id)
        if participante is None:
            participante = f"Participante #{len(participantes) + 1}"
            participantes[lance.licitante_id] = participante

        hash_calculado = calcular_hash_lance(
            lance,
            participante,
            hash_anterior,
        )
        if lance.hash_evento != hash_calculado:
            return False
        hash_anterior = lance.hash_evento

    return hash_anterior == hash_ancora
