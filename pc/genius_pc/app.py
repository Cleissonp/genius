"""Janela pygame: visual neon, efeitos e integração com o Arduino."""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

import pygame

from .audio import Sons
from .conexao import ConexaoSerial
from .jogo import EstadoJogo, EventoJogo, JogoGenius
from .protocolo import TUDO_OFF, comando_led, comando_tom

LARGURA, ALTURA = 1280, 800
QUADROS_POR_SEGUNDO = 60

FUNDO = (7, 10, 20)
FUNDO2 = (15, 21, 38)
TEXTO = (232, 240, 255)
TEXTO_FRACO = (132, 152, 182)
ACENTO = (116, 255, 214)
OURO = (255, 214, 102)
VERMELHO = (255, 64, 104)
BRANCO = (245, 250, 255)

CORES = [
    (52, 255, 154),   # 0 verde
    (255, 74, 112),   # 1 rosa
    (74, 163, 255),   # 2 azul
    (255, 209, 92),   # 3 amarelo
]

ARQUIVO_RECORDE = Path.home() / ".genius_neon.json"


def misturar(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def _carregar_recorde() -> dict[str, int]:
    try:
        dados = json.loads(ARQUIVO_RECORDE.read_text(encoding="utf-8"))
        return {
            "rodada": int(dados.get("rodada", 0)),
            "pontuacao": int(dados.get("pontuacao", 0)),
        }
    except (OSError, ValueError, TypeError):
        return {"rodada": 0, "pontuacao": 0}


def _criar_brilho(cor: tuple[int, int, int], tamanho: int = 256) -> pygame.Surface:
    brilho = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
    centro = tamanho // 2
    for raio in range(centro, 0, -1):
        alpha = int(105 * (1 - raio / centro) ** 2)
        pygame.draw.circle(brilho, (*cor, alpha), (centro, centro), raio)
    return brilho


def _criar_fundo(tamanho: tuple[int, int]) -> pygame.Surface:
    largura, altura = tamanho
    fundo = pygame.Surface(tamanho)
    for y in range(altura):
        t = y / max(1, altura - 1)
        cor = misturar((5, 8, 16), (18, 27, 50), t)
        pygame.draw.line(fundo, cor, (0, y), (largura, y))
    halo = _criar_brilho((46, 120, 200), 640)
    halo.set_alpha(46)
    fundo.blit(halo, (largura // 2 - 320, int(altura * 0.5) - 320))
    halo2 = _criar_brilho((180, 60, 140), 420)
    halo2.set_alpha(24)
    fundo.blit(halo2, (int(largura * 0.82) - 210, int(altura * 0.15) - 210))
    return fundo


@dataclass
class Particula:
    x: float
    y: float
    vx: float
    vy: float
    vida: float
    vida_max: float
    cor: tuple[int, int, int]
    tamanho: float


@dataclass
class Onda:
    x: float
    y: float
    raio_max: float
    vida: float
    vida_max: float
    cor: tuple[int, int, int]


@dataclass
class TextoFlutuante:
    texto: str
    x: float
    y: float
    cor: tuple[int, int, int]
    vida: float
    vida_max: float
    tamanho: int


@dataclass
class Poeira:
    x: float
    y: float
    vx: float
    vy: float
    tamanho: float
    brilho: float


class Aplicativo:
    def __init__(
        self,
        conexao: ConexaoSerial | None = None,
        tela_cheia: bool = False,
        mudo: bool = False,
        teste: bool = False,
    ) -> None:
        pygame.init()
        pygame.display.set_caption("Genius Neon — pygame + Arduino")
        self.tela_cheia = tela_cheia
        self.teste = teste
        self.quadros = 0
        self.relogio = pygame.time.Clock()
        self.tela = self._criar_janela()
        self._definir_icone()

        self.conexao = conexao
        self.conexao_perdida = False
        self.sons = Sons()
        self.sons.definir_mudo(mudo)

        self.jogo = JogoGenius()
        self.recorde = _carregar_recorde()
        self.novo_recorde = False

        self.fontes: dict[tuple[int, bool], pygame.font.Font] = {}
        self.brilhos = [_criar_brilho(cor) for cor in CORES]
        self.niveis = [0.0, 0.0, 0.0, 0.0]
        self.acesos = [False, False, False, False]

        self.tempo = 0.0
        self.pulso = 0.0
        self.ultima_cor = ACENTO
        self.tremor = 0.0
        self.flash_cor = BRANCO
        self.flash_alpha = 0.0
        self.pausado = False
        self.agenda: list[tuple[float, str]] = []
        self.banner: tuple[str, tuple[int, int, int], float, float] | None = None
        self.particulas: list[Particula] = []
        self.ondas: list[Onda] = []
        self.textos: list[TextoFlutuante] = []
        self.poeira: list[Poeira] = []

        self.rects: list[pygame.Rect] = []
        self.tabuleiro = pygame.Rect(0, 0, 0, 0)
        self._reconstruir()
        self._criar_poeira()

    # ------------------------------------------------------------------ setup

    def _criar_janela(self) -> pygame.Surface:
        if self.tela_cheia:
            info = pygame.display.Info()
            return pygame.display.set_mode(
                (info.current_w, info.current_h), pygame.FULLSCREEN
            )
        return pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)

    def _definir_icone(self) -> None:
        icone = pygame.Surface((64, 64), pygame.SRCALPHA)
        for i, cor in enumerate(CORES):
            x = 4 + (i % 2) * 31
            y = 4 + (i // 2) * 31
            pygame.draw.rect(icone, cor, (x, y, 25, 25), border_radius=6)
        pygame.display.set_icon(icone)

    def _fonte(self, tamanho: int, negrito: bool = True) -> pygame.font.Font:
        chave = (tamanho, negrito)
        if chave not in self.fontes:
            self.fontes[chave] = pygame.font.SysFont(
                "Segoe UI", tamanho, bold=negrito
            )
        return self.fontes[chave]

    def _reconstruir(self) -> None:
        largura, altura = self.tela.get_size()
        self.fundo = _criar_fundo((largura, altura))
        self.camada = pygame.Surface((largura, altura), pygame.SRCALPHA)
        self._calcular_layout()

    def _calcular_layout(self) -> None:
        largura, altura = self.tela.get_size()
        topo, base = 132, 116
        lado = min(int(largura * 0.56), altura - topo - base)
        lado = max(260, min(lado, largura - 80))
        x = (largura - lado) // 2
        y = topo + max(0, (altura - topo - base - lado) // 2)
        vao = max(8, int(lado * 0.028))
        celula = (lado - vao) / 2
        self.rects = [
            pygame.Rect(x, y, celula, celula),
            pygame.Rect(x + celula + vao, y, celula, celula),
            pygame.Rect(x, y + celula + vao, celula, celula),
            pygame.Rect(
                x + celula + vao, y + celula + vao, celula, celula
            ),
        ]
        self.tabuleiro = pygame.Rect(x, y, lado, lado)

    def _criar_poeira(self) -> None:
        largura, altura = self.tela.get_size()
        self.poeira = [
            Poeira(
                x=random.uniform(0, largura),
                y=random.uniform(0, altura),
                vx=random.uniform(-6, 6),
                vy=random.uniform(-18, -4),
                tamanho=random.uniform(1.0, 2.8),
                brilho=random.uniform(0.1, 0.55),
            )
            for _ in range(38)
        ]

    # ------------------------------------------------------------------ entrada

    def executar(self) -> None:
        rodando = True
        while rodando:
            if self.teste:
                dt = 1.0 / QUADROS_POR_SEGUNDO
                self.relogio.tick(0)
                self.quadros += 1
                if self.quadros == 30:
                    self._iniciar_jogo()
                if self.quadros > 240:
                    rodando = False
            else:
                dt = min(self.relogio.tick(QUADROS_POR_SEGUNDO) / 1000.0, 0.05)

            for evento in pygame.event.get():
                if self._tratar_evento(evento) is False:
                    rodando = False
            self._atualizar(dt)
            self._desenhar()
            pygame.display.flip()

        self._encerrar()

    def _tratar_evento(self, evento: pygame.event.Event) -> bool | None:
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.VIDEORESIZE and not self.tela_cheia:
            self.tela = pygame.display.set_mode(
                (max(900, evento.w), max(600, evento.h)), pygame.RESIZABLE
            )
            self._reconstruir()
            return None
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return False
            if evento.key == pygame.K_F11:
                self._alternar_tela_cheia()
            elif evento.key == pygame.K_m:
                mudo = self.sons.alternar_mudo()
                if mudo:
                    self._enviar(comando_tom(0, 0))
                self._mostrar_banner("SOM OFF" if mudo else "SOM ON", OURO, 0.8)
            elif evento.key == pygame.K_p:
                self._alternar_pausa()
            elif evento.key == pygame.K_r:
                if self.jogo.estado is not EstadoJogo.MENU:
                    self._iniciar_jogo(forcar=True)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.jogo.pode_reiniciar:
                    self._iniciar_jogo()
            else:
                indice = self._indice_da_tecla(evento.key)
                if indice is not None:
                    self._entrada(indice)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.jogo.estado in (EstadoJogo.MENU, EstadoJogo.GAME_OVER):
                if self.jogo.pode_reiniciar:
                    self._iniciar_jogo()
                return None
            for indice, rect in enumerate(self.rects):
                if rect.collidepoint(evento.pos):
                    self._entrada(indice)
                    break
        elif evento.type == pygame.JOYDEVICEADDED:
            self._iniciar_joystick(evento.device_index)
        elif evento.type == pygame.JOYBUTTONDOWN:
            if evento.button in (0, 1, 2, 3):
                self._entrada(evento.button)
            elif evento.button in (7, 9):
                if self.jogo.pode_reiniciar:
                    self._iniciar_jogo()
        return None

    def _iniciar_joystick(self, indice: int) -> None:
        try:
            joystick = pygame.joystick.Joystick(indice)
            joystick.init()
        except pygame.error:
            pass

    @staticmethod
    def _indice_da_tecla(tecla: int) -> int | None:
        return {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_a: 0,
            pygame.K_s: 1,
            pygame.K_d: 2,
            pygame.K_f: 3,
            pygame.K_KP7: 0,
            pygame.K_KP9: 1,
            pygame.K_KP1: 2,
            pygame.K_KP3: 3,
        }.get(tecla)

    def _alternar_tela_cheia(self) -> None:
        if self.teste:
            return
        self.tela_cheia = not self.tela_cheia
        if self.tela_cheia:
            largura, altura = pygame.display.get_desktop_sizes()[0]
            self.tela = pygame.display.set_mode(
                (largura, altura), pygame.FULLSCREEN
            )
        else:
            self.tela = pygame.display.set_mode(
                (LARGURA, ALTURA), pygame.RESIZABLE
            )
        self._reconstruir()

    def _alternar_pausa(self) -> None:
        if self.jogo.estado in (EstadoJogo.MENU, EstadoJogo.GAME_OVER):
            return
        self.pausado = not self.pausado
        if self.pausado:
            self.agenda.clear()
            self._enviar(TUDO_OFF)
            self.sons.parar()
        self._mostrar_banner("PAUSADO" if self.pausado else "CONTINUANDO", OURO, 0.9)

    # ------------------------------------------------------------------ jogo

    def _entrada(self, indice: int) -> None:
        if self.pausado:
            return
        if self.jogo.estado in (EstadoJogo.MENU, EstadoJogo.GAME_OVER):
            if self.jogo.pode_reiniciar:
                self._iniciar_jogo()
            return
        if self.jogo.estado is not EstadoJogo.ENTRADA:
            return
        self._processar_eventos(self.jogo.pressionar(indice))

    def _iniciar_jogo(self, forcar: bool = False) -> None:
        if not forcar and not self.jogo.pode_reiniciar:
            return
        self.pausado = False
        self.novo_recorde = False
        self.particulas.clear()
        self.ondas.clear()
        self.textos.clear()
        self.agenda.clear()
        self.banner = None
        self.niveis = [0.0, 0.0, 0.0, 0.0]
        self.acesos = [False, False, False, False]
        self.sons.parar()
        self._enviar(TUDO_OFF)
        self._processar_eventos(self.jogo.iniciar(forcar=forcar))

    def _processar_eventos(self, eventos: list[EventoJogo]) -> None:
        for evento in eventos:
            tipo = evento.tipo
            if tipo == "passo_on" and evento.indice is not None:
                indice = evento.indice
                duracao = max(60, int(evento.duracao * 1000))
                self.niveis[indice] = 1.0
                self.acesos[indice] = True
                self.sons.tocar_tom(indice)
                self._enviar(comando_led(indice, duracao))
                self._enviar_tom(indice, duracao)
                self._onda(indice, grande=False)
                self._faiscar(indice, 10)
                self.pulso = 1.0
                self.ultima_cor = CORES[indice]
            elif tipo == "passo_off" and evento.indice is not None:
                indice = evento.indice
                self.acesos[indice] = False
                self._enviar(comando_led(indice, 0))
                self._enviar_tom(indice, 0)
            elif tipo == "acerto" and evento.indice is not None:
                indice = evento.indice
                self.niveis[indice] = 1.0
                self.acesos[indice] = False
                self.sons.tocar_tom(indice)
                self._enviar(comando_led(indice, 130))
                self._enviar_tom(indice, 110)
                self._onda(indice, grande=False)
                self._faiscar(indice, 16)
                self.pulso = max(self.pulso, 0.7)
                if evento.combo >= 2:
                    self._texto_flutuante(
                        f"COMBO x{evento.combo}",
                        self.tabuleiro.centerx,
                        self.tabuleiro.top - 18,
                        ACENTO,
                        0.7,
                        22,
                    )
            elif tipo == "erro" and evento.indice is not None:
                self.tremor = 24.0
                self.flash_cor = VERMELHO
                self.flash_alpha = 190.0
                self.sons.tocar("erro")
                self.acesos = [False, False, False, False]
                self._onda(evento.indice, grande=True)
                self._explosao(evento.indice, 46)
                self._arduino_erro()
            elif tipo == "rodada_completa":
                self._mostrar_banner(
                    f"RODADA {evento.rodada:02d} COMPLETA", ACENTO, 1.0
                )
                self._texto_flutuante(
                    f"+{evento.ganho}",
                    self.tabuleiro.centerx,
                    self.tabuleiro.centery,
                    OURO,
                    1.1,
                    44,
                )
                self.sons.tocar("rodada")
                self._piscar_tudo(180)
            elif tipo == "nova_rodada":
                self.pulso = 1.0
                self._enviar(TUDO_OFF)
            elif tipo == "inicio":
                self.sons.tocar("inicio")
                self._arduino_inicio()
            elif tipo == "sua_vez":
                self.pulso = max(self.pulso, 0.6)
            elif tipo == "fim_de_jogo":
                self.sons.tocar("gameover")
                self._arduino_gameover()
                self._registrar_recorde()

    def _registrar_recorde(self) -> None:
        mudou = False
        if self.jogo.rodada > self.recorde.get("rodada", 0):
            self.recorde["rodada"] = self.jogo.rodada
            mudou = True
        if self.jogo.pontuacao > self.recorde.get("pontuacao", 0):
            self.recorde["pontuacao"] = self.jogo.pontuacao
            mudou = True
        self.novo_recorde = mudou
        if mudou:
            try:
                ARQUIVO_RECORDE.write_text(
                    json.dumps(self.recorde), encoding="utf-8"
                )
            except OSError:
                pass

    # ------------------------------------------------------------------ arduino

    def _enviar(self, comando: str) -> None:
        if self.conexao is not None:
            self.conexao.enviar(comando)

    def _enviar_tom(self, indice: int, duracao_ms: int) -> None:
        if not self.sons.mudo:
            self._enviar(comando_tom(indice, duracao_ms))

    def _agendar(self, atraso: float, comando: str) -> None:
        self.agenda.append((atraso, comando))

    def _arduino_inicio(self) -> None:
        self._enviar(TUDO_OFF)
        for indice in range(4):
            self._agendar(indice * 0.12, comando_led(indice, 140))
            self._agendar(indice * 0.12, comando_tom(indice, 120))

    def _arduino_erro(self) -> None:
        self.agenda.clear()
        self._enviar(TUDO_OFF)
        for indice in range(4):
            self._enviar(comando_led(indice, 650))
        self._enviar_tom(3, 750)
        self._agendar(0.95, TUDO_OFF)

    def _arduino_gameover(self) -> None:
        self.agenda.clear()
        self._enviar(TUDO_OFF)
        for indice in range(4):
            self._agendar(0.05 * indice, comando_led(indice, 800))
        self._agendar(0.05, comando_tom(3, 900))
        self._agendar(1.1, TUDO_OFF)

    def _piscar_tudo(self, duracao_ms: int) -> None:
        for indice in range(4):
            self._enviar(comando_led(indice, duracao_ms))

    # ------------------------------------------------------------------ update

    def _atualizar(self, dt: float) -> None:
        self.tempo += dt
        if self.conexao is not None:
            for tipo, indice in self.conexao.eventos():
                if tipo == "botao" and indice is not None:
                    self._entrada(indice)
                elif tipo == "desconectado":
                    self.conexao_perdida = True

        if not self.pausado:
            self._processar_eventos(self.jogo.atualizar(dt))
            restante = []
            for quando, comando in self.agenda:
                quando -= dt
                if quando <= 0:
                    # mudo: filtros para não acionar o buzzer/LED agendados
                    if not (self.sons.mudo and comando.startswith("T")):
                        self._enviar(comando)
                else:
                    restante.append((quando, comando))
            self.agenda = restante

        for indice in range(4):
            alvo = 1.0 if self.acesos[indice] else 0.0
            self.niveis[indice] += (alvo - self.niveis[indice]) * min(
                1.0, dt * 14.0
            )

        self.pulso = max(0.0, self.pulso - dt * 2.6)
        self.tremor = max(0.0, self.tremor - dt * 55.0)
        self.flash_alpha = max(0.0, self.flash_alpha - dt * 360.0)
        if self.banner is not None:
            texto, cor, duracao, restante = self.banner
            restante -= dt
            self.banner = (
                (texto, cor, duracao, restante) if restante > 0 else None
            )

        self._atualizar_efeitos(dt)

    def _atualizar_efeitos(self, dt: float) -> None:
        largura, altura = self.tela.get_size()
        for particula in self.particulas:
            particula.x += particula.vx * dt
            particula.y += particula.vy * dt
            particula.vy += 210.0 * dt
            particula.vx *= 0.985
            particula.vida -= dt
        self.particulas = [p for p in self.particulas if p.vida > 0]

        for onda in self.ondas:
            onda.vida -= dt
        self.ondas = [o for o in self.ondas if o.vida > 0]

        for texto in self.textos:
            texto.y -= 32.0 * dt
            texto.vida -= dt
        self.textos = [t for t in self.textos if t.vida > 0]

        for po in self.poeira:
            po.x += po.vx * dt
            po.y += po.vy * dt
            if po.y < -4:
                po.y = altura + 4
                po.x = random.uniform(0, largura)
            if po.x < -4:
                po.x = largura + 4
            elif po.x > largura + 4:
                po.x = -4

    def _onda(self, indice: int, grande: bool) -> None:
        rect = self.rects[indice]
        self.ondas.append(
            Onda(
                rect.centerx,
                rect.centery,
                rect.width * (1.05 if grande else 0.62),
                0.55,
                0.55,
                CORES[indice],
            )
        )

    def _faiscar(self, indice: int, quantidade: int) -> None:
        rect = self.rects[indice]
        for _ in range(quantidade):
            angulo = random.uniform(0, math.tau)
            velocidade = random.uniform(35, 190)
            vida = random.uniform(0.25, 0.65)
            self.particulas.append(
                Particula(
                    x=rect.centerx + math.cos(angulo) * rect.width * 0.15,
                    y=rect.centery + math.sin(angulo) * rect.height * 0.15,
                    vx=math.cos(angulo) * velocidade,
                    vy=math.sin(angulo) * velocidade - 40,
                    vida=vida,
                    vida_max=vida,
                    cor=misturar(CORES[indice], BRANCO, random.uniform(0, 0.5)),
                    tamanho=random.uniform(1.5, 4.5),
                )
            )

    def _explosao(self, indice: int, quantidade: int) -> None:
        rect = self.rects[indice]
        for _ in range(quantidade):
            angulo = random.uniform(0, math.tau)
            velocidade = random.uniform(80, 480)
            vida = random.uniform(0.4, 1.0)
            self.particulas.append(
                Particula(
                    x=rect.centerx,
                    y=rect.centery,
                    vx=math.cos(angulo) * velocidade,
                    vy=math.sin(angulo) * velocidade,
                    vida=vida,
                    vida_max=vida,
                    cor=misturar(VERMELHO, OURO, random.uniform(0, 0.6)),
                    tamanho=random.uniform(2, 6),
                )
            )

    def _texto_flutuante(
        self,
        texto: str,
        x: float,
        y: float,
        cor: tuple[int, int, int],
        vida: float,
        tamanho: int,
    ) -> None:
        self.textos.append(TextoFlutuante(texto, x, y, cor, vida, vida, tamanho))

    def _mostrar_banner(
        self, texto: str, cor: tuple[int, int, int], duracao: float
    ) -> None:
        self.banner = (texto, cor, duracao, duracao)

    def _encerrar(self) -> None:
        if self.conexao is not None:
            self.conexao.tudo_off()
            self.conexao.fechar()
        self.sons.parar()
        pygame.quit()

    # ---------------------------------------------------------------- desenho

    def _desenhar(self) -> None:
        self.tela.blit(self.fundo, (0, 0))
        self._desenhar_atmosfera()
        if self.jogo.estado is not EstadoJogo.MENU:
            self._desenhar_tabuleiro()
            self._desenhar_efeitos()
            self._desenhar_hud()
        self._desenhar_textos()
        self._desenhar_banner()
        if self.jogo.estado is EstadoJogo.MENU:
            self._desenhar_menu()
        elif self.jogo.estado is EstadoJogo.GAME_OVER:
            self._desenhar_gameover()
        if self.pausado:
            self._desenhar_pausa()
        self._desenhar_flash()
        self._desenhar_conexao()

    def _texto(
        self,
        texto: str,
        tamanho: int,
        cor: tuple[int, int, int],
        centro: tuple[float, float] | None = None,
        topleft: tuple[float, float] | None = None,
        alpha: int = 255,
        negrito: bool = True,
    ) -> pygame.Rect:
        fonte = self._fonte(tamanho, negrito)
        imagem = fonte.render(texto, True, cor)
        if alpha < 255:
            imagem = imagem.copy()
            imagem.set_alpha(max(0, min(255, alpha)))
        if centro is not None:
            rect = imagem.get_rect(center=(int(centro[0]), int(centro[1])))
        else:
            rect = imagem.get_rect(
                topleft=(int(topleft[0]), int(topleft[1]))
            )
        sombra = fonte.render(texto, True, (0, 0, 0))
        sombra.set_alpha(int(max(0, min(255, alpha)) * 0.55))
        self.tela.blit(sombra, (rect.x + 2, rect.y + 2))
        self.tela.blit(imagem, rect)
        return rect

    def _deslocamento_tremor(self) -> tuple[int, int]:
        if self.tremor <= 0.2:
            return (0, 0)
        return (
            int(random.uniform(-self.tremor, self.tremor)),
            int(random.uniform(-self.tremor, self.tremor)),
        )

    def _desenhar_atmosfera(self) -> None:
        if not hasattr(self, "_brilho_ambiente"):
            self._brilho_ambiente = _criar_brilho((60, 150, 220), 512)
        lado = int(max(self.tabuleiro.width, self.tabuleiro.height) * 1.95)
        halo = pygame.transform.smoothscale(self._brilho_ambiente, (lado, lado))
        halo.set_alpha(int(26 + 48 * self.pulso))
        self.tela.blit(
            halo,
            (
                self.tabuleiro.centerx - lado // 2,
                self.tabuleiro.centery - lado // 2,
            ),
        )
        for po in self.poeira:
            cor = misturar(FUNDO, (150, 190, 255), po.brilho)
            pygame.draw.circle(
                self.tela,
                cor,
                (int(po.x), int(po.y)),
                max(1, int(po.tamanho)),
            )

    def _desenhar_tabuleiro(self) -> None:
        ox, oy = self._deslocamento_tremor()
        moldura = self.tabuleiro.inflate(18, 18).move(ox, oy)
        pygame.draw.rect(
            self.tela, (11, 16, 30), moldura, border_radius=30
        )
        pygame.draw.rect(
            self.tela,
            misturar(FUNDO2, ACENTO, 0.28),
            moldura,
            width=2,
            border_radius=30,
        )
        for indice, rect_base in enumerate(self.rects):
            rect = rect_base.move(ox, oy)
            nivel = self.niveis[indice]
            cor = CORES[indice]
            if nivel > 0.02:
                brilho = pygame.transform.smoothscale(
                    self.brilhos[indice],
                    (int(rect.width * 1.8), int(rect.height * 1.8)),
                )
                brilho.set_alpha(int(185 * min(1.0, nivel)))
                self.tela.blit(
                    brilho,
                    (
                        rect.centerx - brilho.get_width() // 2,
                        rect.centery - brilho.get_height() // 2,
                    ),
                )

            base = misturar(FUNDO2, cor, 0.17)
            preenchimento = misturar(base, cor, 0.84 * nivel)
            if nivel > 0.82:
                preenchimento = misturar(
                    preenchimento, BRANCO, (nivel - 0.82) * 0.9
                )
            raio = max(12, int(rect.width * 0.10))
            pygame.draw.rect(
                self.tela, preenchimento, rect, border_radius=raio
            )
            pygame.draw.rect(
                self.tela,
                misturar(cor, BRANCO, 0.35),
                rect,
                width=2 + int(2 * nivel),
                border_radius=raio,
            )
            if nivel > 0.05:
                interno = rect.inflate(-10, -10)
                pygame.draw.rect(
                    self.tela,
                    misturar(preenchimento, BRANCO, 0.18),
                    interno,
                    width=1,
                    border_radius=max(8, raio - 4),
                )

            self._desenhar_simbolo(rect, indice, nivel)

            numero = str(indice + 1)
            fonte = self._fonte(max(13, int(rect.width * 0.045)))
            cor_numero = misturar(preenchimento, BRANCO, 0.55)
            imagem = fonte.render(numero, True, cor_numero)
            imagem.set_alpha(150 if nivel < 0.5 else 220)
            self.tela.blit(
                imagem,
                (
                    rect.right - imagem.get_width() - 14,
                    rect.bottom - imagem.get_height() - 10,
                ),
            )

    def _desenhar_simbolo(
        self, rect: pygame.Rect, indice: int, nivel: float
    ) -> None:
        raio = max(8, int(rect.width * 0.085))
        cx, cy = rect.centerx, rect.centery - int(rect.height * 0.02)
        base = misturar(FUNDO2, CORES[indice], 0.17)
        preenchimento = misturar(base, CORES[indice], 0.84 * nivel)
        cor = misturar(preenchimento, BRANCO, 0.55)
        espessura = max(2, int(rect.width * 0.008))
        if indice == 0:
            pygame.draw.circle(self.tela, cor, (cx, cy), raio, espessura)
        elif indice == 1:
            pontos = [
                (cx, cy - raio),
                (cx + raio, cy),
                (cx, cy + raio),
                (cx - raio, cy),
            ]
            pygame.draw.polygon(self.tela, cor, pontos, espessura)
        elif indice == 2:
            pontos = [
                (cx, cy - raio),
                (cx + raio, cy + raio),
                (cx - raio, cy + raio),
            ]
            pygame.draw.polygon(self.tela, cor, pontos, espessura)
        else:
            pygame.draw.rect(
                self.tela,
                cor,
                (cx - raio, cy - raio, raio * 2, raio * 2),
                espessura,
                border_radius=3,
            )

    def _desenhar_efeitos(self) -> None:
        self.camada.fill((0, 0, 0, 0))
        for onda in self.ondas:
            t = 1.0 - onda.vida / onda.vida_max
            raio = int(onda.raio_max * (1.0 - (1.0 - t) ** 3))
            alpha = int(150 * (1.0 - t))
            if raio > 0 and alpha > 0:
                pygame.draw.circle(
                    self.camada,
                    (*onda.cor, alpha),
                    (int(onda.x), int(onda.y)),
                    raio,
                    width=max(1, int(3 * (1 - t)) + 1),
                )
        for particula in self.particulas:
            proporcao = max(0.0, particula.vida / particula.vida_max)
            alpha = int(255 * proporcao)
            raio = max(1, int(particula.tamanho * (0.35 + 0.65 * proporcao)))
            pygame.draw.circle(
                self.camada,
                (*particula.cor, alpha),
                (int(particula.x), int(particula.y)),
                raio,
            )
        self.tela.blit(self.camada, (0, 0))

    def _desenhar_hud(self) -> None:
        largura, _ = self.tela.get_size()
        self._texto("PONTOS", 13, TEXTO_FRACO, topleft=(44, 26))
        self._texto(
            f"{self.jogo.pontuacao:06d}", 36, TEXTO, topleft=(42, 42)
        )
        self._texto("RODADA", 13, TEXTO_FRACO, centro=(largura / 2, 28))
        self._texto(
            f"{self.jogo.rodada:02d}",
            40,
            ACENTO,
            centro=(largura / 2, 60),
        )
        recorde = max(self.recorde.get("pontuacao", 0), self.jogo.pontuacao)
        self._texto(
            "RECORDE", 13, TEXTO_FRACO, topleft=(largura - 190, 26)
        )
        self._texto(
            f"{recorde:06d}", 30, OURO, topleft=(largura - 194, 46)
        )

        if (
            self.jogo.estado is EstadoJogo.ENTRADA
            and self.jogo.combo >= 2
        ):
            pulso = 1.0 + 0.06 * math.sin(self.tempo * 12)
            self._texto(
                f"COMBO x{self.jogo.combo}",
                int(22 * pulso),
                ACENTO,
                centro=(largura / 2, 112),
            )

        if self.jogo.estado is EstadoJogo.ENTRADA:
            total = len(self.jogo.sequencia)
            if total <= 14:
                y = self.tabuleiro.bottom + 24
                espaco = 18
                inicio = self.tabuleiro.centerx - (total - 1) * espaco / 2
                for posicao in range(total):
                    x = inicio + posicao * espaco
                    if posicao < self.jogo.indice_entrada:
                        pygame.draw.circle(self.tela, ACENTO, (int(x), y), 4)
                    else:
                        pygame.draw.circle(
                            self.tela, (60, 78, 108), (int(x), y), 4, 1
                        )
            else:
                self._texto(
                    f"{self.jogo.indice_entrada}/{total}",
                    15,
                    TEXTO_FRACO,
                    centro=(self.tabuleiro.centerx, self.tabuleiro.bottom + 24),
                )

        altura = self.tela.get_height()
        if self.jogo.estado is EstadoJogo.TOCANDO:
            self._texto(
                "OBSERVE",
                18,
                TEXTO_FRACO,
                centro=(largura / 2, altura - 48),
            )
        elif self.jogo.estado is EstadoJogo.ENTRADA:
            brilho = int(160 + 95 * (0.5 + 0.5 * math.sin(self.tempo * 5)))
            self._texto(
                "SUA VEZ",
                20,
                ACENTO,
                centro=(largura / 2, altura - 48),
                alpha=brilho,
            )
        elif self.jogo.estado is EstadoJogo.FIM_RODADA:
            self._texto(
                f"RODADA {self.jogo.rodada:02d} VENCIDA",
                18,
                OURO,
                centro=(largura / 2, altura - 48),
            )

        self._texto(
            "1–4 · A S D F · MOUSE   |   P PAUSA · M SOM · F11 TELA",
            13,
            TEXTO_FRACO,
            topleft=(44, altura - 32),
        )

    def _desenhar_textos(self) -> None:
        for texto in self.textos:
            alpha = int(255 * min(1.0, texto.vida * 2.5))
            self._texto(
                texto.texto,
                texto.tamanho,
                texto.cor,
                centro=(texto.x, texto.y),
                alpha=alpha,
            )

    def _desenhar_banner(self) -> None:
        if self.banner is None:
            return
        texto, cor, duracao, restante = self.banner
        progresso = 1.0 - restante / max(0.001, duracao)
        alpha = int(255 * min(1.0, progresso * 8.0, (1 - progresso) * 4.0))
        if alpha <= 0:
            return
        self._texto(
            texto,
            42,
            cor,
            centro=(self.tabuleiro.centerx, self.tabuleiro.centery),
            alpha=alpha,
        )

    def _desenhar_menu(self) -> None:
        largura, altura = self.tela.get_size()
        sombra = pygame.Surface((largura, altura), pygame.SRCALPHA)
        sombra.fill((4, 7, 14, 196))
        self.tela.blit(sombra, (0, 0))

        centro_x = largura / 2
        tamanho_titulo = min(112, int(largura * 0.10))
        fonte = self._fonte(tamanho_titulo)
        titulo = fonte.render("GENIUS", True, (188, 255, 240))
        y_titulo = altura * 0.29
        halo = _criar_brilho(ACENTO)
        halo = pygame.transform.smoothscale(
            halo,
            (
                int(titulo.get_width() * 1.25),
                int(titulo.get_height() * 2.1),
            ),
        )
        halo.set_alpha(42)
        self.tela.blit(
            halo,
            (
                centro_x - halo.get_width() / 2,
                y_titulo - halo.get_height() / 2,
            ),
        )
        self.tela.blit(
            titulo,
            (
                centro_x - titulo.get_width() / 2,
                y_titulo - titulo.get_height() / 2,
            ),
        )
        self._texto(
            "M E M Ó R I A   N E O N",
            18,
            TEXTO_FRACO,
            centro=(centro_x, y_titulo + tamanho_titulo * 0.62),
        )

        for indice, cor in enumerate(CORES):
            x = centro_x + (indice - 1.5) * 40
            pygame.draw.circle(
                self.tela, cor, (int(x), int(y_titulo + tamanho_titulo * 0.88)), 5
            )

        self._texto(
            f"RECORDE   RODADA {self.recorde.get('rodada', 0):02d}   ·   "
            f"{self.recorde.get('pontuacao', 0):06d} PTS",
            19,
            OURO,
            centro=(centro_x, altura * 0.47),
        )

        caixa = pygame.Rect(0, 0, min(700, largura - 80), 96)
        caixa.center = (int(centro_x), int(altura * 0.59))
        pygame.draw.rect(self.tela, (12, 18, 34), caixa, border_radius=18)
        pygame.draw.rect(
            self.tela,
            misturar(FUNDO2, ACENTO, 0.22),
            caixa,
            width=1,
            border_radius=18,
        )
        self._texto(
            "TECLADO    1 2 3 4   ·   A S D F   ·   MOUSE",
            17,
            TEXTO,
            centro=(centro_x, caixa.top + 30),
        )
        if self.conexao is not None and not self.conexao_perdida:
            if self.conexao.remoto_confirmado:
                linha = "ARDUINO   BOTÕES FÍSICOS + LEDS + BUZZER"
                cor = ACENTO
            else:
                linha = "ARDUINO   PORTA ABERTA — SEM CONFIRMAÇÃO"
                cor = OURO
        else:
            linha = "ARDUINO   NÃO CONECTADO — MODO DEMO"
            cor = OURO
        self._texto(
            linha,
            17,
            cor,
            centro=(centro_x, caixa.top + 66),
        )

        alpha = int(150 + 95 * (0.5 + 0.5 * math.sin(self.tempo * 3.2)))
        self._texto(
            "ENTER  ·  TOQUE UM BOTÃO  ·  CLIQUE PARA COMEÇAR",
            20,
            TEXTO,
            centro=(centro_x, altura * 0.73),
            alpha=alpha,
        )
        self._texto(
            "pygame-ce + pyserial   ·   F11 tela cheia   ·   M som",
            13,
            TEXTO_FRACO,
            centro=(centro_x, altura - 38),
        )

    def _desenhar_gameover(self) -> None:
        largura, altura = self.tela.get_size()
        sombra = pygame.Surface((largura, altura), pygame.SRCALPHA)
        sombra.fill((14, 3, 9, 202))
        self.tela.blit(sombra, (0, 0))

        t = min(1.0, self.jogo.tempo_decorrido / 0.35)
        ease = 1.0 - (1.0 - t) ** 3
        centro_x = largura / 2
        y_titulo = altura * 0.25 + (1 - ease) * 26

        fonte = self._fonte(94)
        titulo = fonte.render("GAME OVER", True, VERMELHO)
        glow = pygame.transform.smoothscale(
            pygame.transform.smoothscale(
                titulo,
                (max(1, titulo.get_width() // 8), max(1, titulo.get_height() // 8)),
            ),
            titulo.get_size(),
        )
        glow.set_alpha(int(80 * ease))
        self.tela.blit(
            glow,
            (
                centro_x - titulo.get_width() / 2,
                y_titulo - titulo.get_height() / 2,
            ),
        )
        self.tela.blit(
            titulo,
            (
                centro_x - titulo.get_width() / 2,
                y_titulo - titulo.get_height() / 2,
            ),
        )

        self._texto(
            f"VOCÊ CHEGOU À RODADA {self.jogo.rodada:02d}",
            22,
            TEXTO_FRACO,
            centro=(centro_x, y_titulo + 82),
        )
        self._texto(
            f"{self.jogo.pontuacao:06d} PONTOS",
            42,
            TEXTO,
            centro=(centro_x, y_titulo + 132),
        )

        if self.novo_recorde:
            alpha = int(180 + 75 * (0.5 + 0.5 * math.sin(self.tempo * 6)))
            self._texto(
                "NOVO RECORDE!",
                26,
                OURO,
                centro=(centro_x, y_titulo + 190),
                alpha=alpha,
            )
        else:
            self._texto(
                f"RECORDE  {self.recorde.get('rodada', 0):02d}  ·  "
                f"{self.recorde.get('pontuacao', 0):06d} PTS",
                18,
                TEXTO_FRACO,
                centro=(centro_x, y_titulo + 190),
            )

        if self.jogo.pode_reiniciar:
            alpha = int(150 + 95 * (0.5 + 0.5 * math.sin(self.tempo * 4)))
            self._texto(
                "ENTER  ·  BOTÃO  ·  CLIQUE PARA RECOMEÇAR",
                19,
                ACENTO,
                centro=(centro_x, altura * 0.76),
                alpha=alpha,
            )

    def _desenhar_pausa(self) -> None:
        largura, altura = self.tela.get_size()
        sombra = pygame.Surface((largura, altura), pygame.SRCALPHA)
        sombra.fill((4, 7, 14, 150))
        self.tela.blit(sombra, (0, 0))
        self._texto(
            "PAUSADO", 66, OURO, centro=(largura / 2, altura * 0.46)
        )
        self._texto(
            "P para continuar",
            18,
            TEXTO_FRACO,
            centro=(largura / 2, altura * 0.46 + 62),
        )

    def _desenhar_flash(self) -> None:
        if self.flash_alpha <= 1:
            return
        largura, altura = self.tela.get_size()
        flash = pygame.Surface((largura, altura), pygame.SRCALPHA)
        flash.fill((*self.flash_cor, int(min(220, self.flash_alpha))))
        self.tela.blit(flash, (0, 0))

    def _desenhar_conexao(self) -> None:
        largura, altura = self.tela.get_size()
        y = altura - 28
        if self.conexao is None:
            texto, cor = "DEMO · TECLADO", OURO
        elif self.conexao_perdida:
            texto, cor = "ARDUINO DESCONECTADO", VERMELHO
        elif not self.conexao.remoto_confirmado:
            texto, cor = (
                f"ARDUINO · {self.conexao.porta or 'SERIAL'} · SEM RESPOSTA",
                OURO,
            )
        else:
            texto, cor = f"ARDUINO · {self.conexao.porta or 'SERIAL'}", ACENTO
        fonte = self._fonte(13)
        imagem = fonte.render(texto, True, cor)
        x = largura - 32 - imagem.get_width()
        pygame.draw.circle(self.tela, cor, (x - 12, y), 4)
        self.tela.blit(imagem, (x, y - imagem.get_height() // 2))
