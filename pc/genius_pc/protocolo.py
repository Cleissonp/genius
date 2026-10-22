"""Protocolo de linha usado entre o Arduino e o cliente pygame.

Formato: texto ASCII, um comando por linha (\\n), 115200 8N1.

Arduino -> PC: READY, OK REMOTO, OK STANDALONE, B<0-3>
PC -> Arduino: M1, M0, A, L<i>,<ms>, T<i>,<ms>
"""

from __future__ import annotations

BAUD_PADRAO = 115200

ENTRAR_REMOTO = "M1"
SAIR_REMOTO = "M0"
TUDO_OFF = "A"

TipoEvento = tuple[str, int | None]


def _validar_indice(indice: int) -> None:
    if indice not in (0, 1, 2, 3):
        raise ValueError(f"índice deve ser 0..3, recebido {indice!r}")


def _duracao(duracao_ms: int) -> int:
    duracao_ms = int(duracao_ms)
    if duracao_ms < 0:
        raise ValueError("duração não pode ser negativa")
    return min(duracao_ms, 60_000)


def comando_led(indice: int, duracao_ms: int) -> str:
    _validar_indice(indice)
    return f"L{indice},{_duracao(duracao_ms)}"


def comando_tom(indice: int, duracao_ms: int) -> str:
    _validar_indice(indice)
    return f"T{indice},{_duracao(duracao_ms)}"


def decodificar(linha: str) -> TipoEvento | None:
    """Converte uma linha do Arduino em (tipo, índice); ignora lixo."""
    linha = linha.strip()
    if not linha:
        return None
    if linha == "READY":
        return ("pronto", None)
    if linha == "OK REMOTO":
        return ("remoto", None)
    if linha == "OK STANDALONE":
        return ("standalone", None)
    if linha == "PONG":
        return ("pong", None)
    if len(linha) == 2 and linha[0] in ("B", "R") and linha[1] in "0123":
        tipo = "botao" if linha[0] == "B" else "soltar"
        return (tipo, int(linha[1]))
    return None
