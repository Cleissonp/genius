"""Regras do Genius, sem pygame nem serial (fácil de testar)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto

CORES = 4


class EstadoJogo(Enum):
    MENU = auto()
    TOCANDO = auto()
    ENTRADA = auto()
    FIM_RODADA = auto()
    GAME_OVER = auto()


@dataclass(frozen=True)
class EventoJogo:
    tipo: str
    indice: int | None = None
    duracao: float = 0.0
    rodada: int = 0
    pontuacao: int = 0
    combo: int = 0
    ganho: int = 0


class JogoGenius:
    """Máquina de estados com timers avançados por `atualizar(dt)`.

    Eventos emitidos: inicio, nova_rodada, passo_on, passo_off, sua_vez,
    acerto, erro, rodada_completa, fim_de_jogo.
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng if rng is not None else random.Random()
        self.limpar()

    def limpar(self) -> None:
        self.sequencia: list[int] = []
        self.rodada = 0
        self.pontuacao = 0
        self.combo = 0
        self.estado = EstadoJogo.MENU
        self.indice_entrada = 0
        self._pos_tocando = 0
        self._timer = 0.0
        self._aceso = False
        self._tempo_estado = 0.0

    def iniciar(self, forcar: bool = False) -> list[EventoJogo]:
        """Começa uma partida nova (menu ou game over)."""
        if not forcar and self.estado not in (
            EstadoJogo.MENU,
            EstadoJogo.GAME_OVER,
        ):
            return []
        self.limpar()
        self.rodada = 1
        self.sequencia = [self.rng.randrange(CORES)]
        self.estado = EstadoJogo.TOCANDO
        self._timer = 0.75  # respiro para o jingle de início
        return [
            EventoJogo("inicio"),
            EventoJogo("nova_rodada", rodada=self.rodada),
        ]

    @property
    def pode_reiniciar(self) -> bool:
        return self.estado is EstadoJogo.MENU or (
            self.estado is EstadoJogo.GAME_OVER and self._tempo_estado >= 0.9
        )

    @property
    def tempo_decorrido(self) -> float:
        return self._tempo_estado

    def _duracao_passo(self) -> float:
        return max(0.22, 0.55 - 0.028 * (self.rodada - 1))

    def _gap(self) -> float:
        return max(0.07, 0.15 - 0.006 * (self.rodada - 1))

    def atualizar(self, dt: float) -> list[EventoJogo]:
        if dt < 0:
            dt = 0.0
        if self.estado is EstadoJogo.GAME_OVER:
            self._tempo_estado += dt
            return []

        if self.estado is EstadoJogo.TOCANDO:
            self._timer -= dt
            if self._timer > 0:
                return []
            if self._aceso:
                indice = self.sequencia[self._pos_tocando - 1]
                self._aceso = False
                self._timer = self._gap()
                return [EventoJogo("passo_off", indice=indice, rodada=self.rodada)]
            if self._pos_tocando < len(self.sequencia):
                indice = self.sequencia[self._pos_tocando]
                self._pos_tocando += 1
                duracao = self._duracao_passo()
                self._aceso = True
                self._timer = duracao
                return [
                    EventoJogo(
                        "passo_on",
                        indice=indice,
                        duracao=duracao,
                        rodada=self.rodada,
                    )
                ]
            self.estado = EstadoJogo.ENTRADA
            self.indice_entrada = 0
            self.combo = 0
            self._tempo_estado = 0.0
            return [
                EventoJogo(
                    "sua_vez", rodada=self.rodada, pontuacao=self.pontuacao
                )
            ]

        if self.estado is EstadoJogo.FIM_RODADA:
            self._timer -= dt
            if self._timer <= 0:
                self.rodada += 1
                self.sequencia.append(self.rng.randrange(CORES))
                self.estado = EstadoJogo.TOCANDO
                self._pos_tocando = 0
                self._aceso = False
                self._timer = 0.0
                return [
                    EventoJogo("nova_rodada", rodada=self.rodada)
                ]
        return []

    def pressionar(self, indice: int) -> list[EventoJogo]:
        if self.estado is not EstadoJogo.ENTRADA or not 0 <= indice < CORES:
            return []
        if indice == self.sequencia[self.indice_entrada]:
            self.combo += 1
            self.indice_entrada += 1
            eventos = [
                EventoJogo(
                    "acerto",
                    indice=indice,
                    rodada=self.rodada,
                    pontuacao=self.pontuacao,
                    combo=self.combo,
                )
            ]
            if self.indice_entrada == len(self.sequencia):
                ganho = self.rodada * 100 + self.combo * 15
                self.pontuacao += ganho
                self.estado = EstadoJogo.FIM_RODADA
                self._timer = 0.9
                eventos.append(
                    EventoJogo(
                        "rodada_completa",
                        rodada=self.rodada,
                        pontuacao=self.pontuacao,
                        combo=self.combo,
                        ganho=ganho,
                    )
                )
            return eventos

        self.estado = EstadoJogo.GAME_OVER
        self._tempo_estado = 0.0
        return [
            EventoJogo(
                "erro",
                indice=indice,
                rodada=self.rodada,
                pontuacao=self.pontuacao,
            ),
            EventoJogo(
                "fim_de_jogo",
                rodada=self.rodada,
                pontuacao=self.pontuacao,
            ),
        ]
