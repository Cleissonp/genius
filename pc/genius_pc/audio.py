"""Sons sintetizados em tempo de execução (sem arquivos de áudio)."""

from __future__ import annotations

import numpy as np
import pygame

TAXA = 44_100


def _envelope(n: int, ataque: float, liberacao: float, sustento: float = 0.65) -> np.ndarray:
    env = np.ones(n, dtype=np.float64)
    a = max(1, min(n, int(TAXA * ataque)))
    r = max(1, min(n - a, int(TAXA * liberacao)))
    env[:a] = np.linspace(0.0, 1.0, a, endpoint=False)
    if r > 1:
        env[-r:] *= np.linspace(1.0, 0.0, r)
    env[a : n - r] = sustento
    return env


def _estereo(mono: np.ndarray, volume: float = 0.55) -> pygame.mixer.Sound:
    mono = np.clip(mono * volume, -1.0, 1.0)
    dados = np.column_stack(
        [(mono * 32767).astype(np.int16), (mono * 32767).astype(np.int16)]
    )
    return pygame.sndarray.make_sound(np.ascontiguousarray(dados))


def _tom(freq: float, duracao: float = 0.55) -> np.ndarray:
    n = int(TAXA * duracao)
    t = np.arange(n, dtype=np.float64) / TAXA
    vibrato = 0.003 * np.sin(2 * np.pi * 5.2 * t)
    fase = 2 * np.pi * freq * t + vibrato
    onda = (
        0.62 * np.sin(fase)
        + 0.28 * np.sin(2 * fase + 0.3)
        + 0.12 * np.sin(3 * fase + 0.7)
    )
    env = _envelope(n, 0.006, 0.20, sustento=0.55)
    # pequeno "click" percussivo no ataque para dar peso
    ataque = np.exp(-t * 55) * 0.18 * np.sin(2 * np.pi * freq * 0.5 * t)
    return onda * env + ataque


def _erro() -> np.ndarray:
    duracao = 0.8
    n = int(TAXA * duracao)
    t = np.arange(n, dtype=np.float64) / TAXA
    freq = np.linspace(240.0, 55.0, n)
    fase = np.cumsum(2 * np.pi * freq / TAXA)
    rng = np.random.default_rng(7)
    ruido = rng.normal(0.0, 0.12, n)
    onda = 0.55 * np.tanh(3.0 * np.sin(fase)) + 0.3 * np.sin(2 * fase) + ruido
    env = _envelope(n, 0.004, 0.45, sustento=0.5)
    return onda * env


def _arpejo(notas: list[float], passo: float, cauda: float = 0.25) -> np.ndarray:
    partes = []
    for freq in notas:
        partes.append(_tom(freq, passo + cauda))
    total = int(TAXA * (passo * (len(notas) - 1) + passo + cauda))
    saida = np.zeros(total, dtype=np.float64)
    for i, parte in enumerate(partes):
        inicio = int(i * passo * TAXA)
        fim = min(total, inicio + len(parte))
        saida[inicio:fim] += parte[: fim - inicio]
    pico = np.max(np.abs(saida)) or 1.0
    return saida / pico


class Sons:
    """Carrega os timbres uma vez; falha de áudio não impede o jogo."""

    def __init__(self) -> None:
        self.disponivel = False
        self.mudo = False
        self.tons: list[pygame.mixer.Sound] = []
        self.efeitos: dict[str, pygame.mixer.Sound] = {}
        self._inicializar()

    def _inicializar(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=TAXA, size=-16, channels=2, buffer=512
                )
            pygame.mixer.set_num_channels(16)
            self.tons = [
                _estereo(_tom(freq), 0.50)
                for freq in (880.0, 440.0, 392.0, 294.0)
            ]
            self.efeitos = {
                "erro": _estereo(_erro(), 0.65),
                "inicio": _estereo(_arpejo([440.0, 554.37, 659.25, 880.0], 0.10), 0.5),
                "rodada": _estereo(_arpejo([659.25, 987.77], 0.09, 0.18), 0.5),
                "gameover": _estereo(_arpejo([392.0, 329.63, 261.63, 196.0], 0.15, 0.35), 0.6),
            }
            self.disponivel = True
        except (pygame.error, OSError):
            self.disponivel = False

    def definir_mudo(self, mudo: bool) -> None:
        self.mudo = mudo
        if mudo and self.disponivel:
            pygame.mixer.stop()

    def alternar_mudo(self) -> bool:
        self.definir_mudo(not self.mudo)
        return self.mudo

    def tocar(self, nome: str) -> None:
        if not self.disponivel or self.mudo:
            return
        som = self.efeitos.get(nome)
        if som is not None:
            som.play()

    def tocar_tom(self, indice: int) -> None:
        if not self.disponivel or self.mudo:
            return
        if 0 <= indice < len(self.tons):
            self.tons[indice].play()

    def parar(self) -> None:
        if self.disponivel:
            pygame.mixer.stop()
