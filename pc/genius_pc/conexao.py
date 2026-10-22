"""Conexão serial com o Arduino, com leitura em thread e fila de eventos."""

from __future__ import annotations

import queue
import threading
import time

import serial
from serial.tools import list_ports

from .protocolo import (
    BAUD_PADRAO,
    ENTRAR_REMOTO,
    TUDO_OFF,
    comando_led,
    comando_tom,
    decodificar,
)

_IDS_ARDUINO = ("2341", "2a03", "1a86", "0403", "10c4", "1b4f")


def listar_portas() -> list[dict[str, str]]:
    portas = []
    for porta in list_ports.comports():
        portas.append(
            {
                "porta": porta.device,
                "descricao": porta.description or "",
                "fabricante": porta.manufacturer or "",
                "hwid": porta.hwid or "",
            }
        )
    return portas


def _pontuar_porta(info: dict[str, str]) -> int:
    texto = " ".join(info.values()).lower()
    if "bluetooth" in texto or "bthenum" in texto:
        return -1
    pontos = 0
    if "arduino" in texto:
        pontos += 100
    if any(ident in texto for ident in _IDS_ARDUINO):
        pontos += 50
    if "ch340" in texto or "wch" in texto:
        pontos += 40
    if "usb serial" in texto or "usb-serial" in texto:
        pontos += 10
    return pontos


def detectar_porta() -> str | None:
    candidatas = [(_pontuar_porta(info), info) for info in listar_portas()]
    candidatas = [(p, i) for p, i in candidatas if p >= 0]
    if not candidatas:
        return None
    candidatas.sort(key=lambda item: item[0], reverse=True)
    return candidatas[0][1]["porta"]


class ConexaoSerial:
    """Abra com `abrir()`; use `eventos()` no loop e `enviar()` para comandos."""

    def __init__(self, porta: str | None = None, baud: int = BAUD_PADRAO) -> None:
        self.porta_solicitada = porta
        self.baud = baud
        self.porta: str | None = None
        self.descricao = ""
        self._ser: serial.Serial | None = None
        self._fila: queue.Queue[tuple[str, int | None]] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._parar = threading.Event()
        self._trava = threading.Lock()
        self._buffer = bytearray()
        self._ack_remoto = threading.Event()
        self._falhou = False
        self._fechada = False

    @property
    def conectado(self) -> bool:
        return self._ser is not None and self._ser.is_open and not self._falhou

    @property
    def remoto_confirmado(self) -> bool:
        return self._ack_remoto.is_set()

    def abrir(self) -> bool:
        porta = self.porta_solicitada or detectar_porta()
        if not porta:
            return False
        try:
            self._ser = serial.Serial(
                porta,
                self.baud,
                timeout=0.05,
                write_timeout=0.5,
            )
        except (serial.SerialException, OSError) as erro:
            self._fila.put(("erro_abertura", None))
            self.descricao = str(erro)
            return False

        self.porta = porta
        info = next((p for p in listar_portas() if p["porta"] == porta), None)
        self.descricao = " · ".join(
            parte
            for parte in (
                porta,
                (info or {}).get("descricao", ""),
            )
            if parte
        )

        # A abertura da porta reinicia o Arduino (DTR); espere o bootloader.
        time.sleep(2.0)
        try:
            self._ser.reset_input_buffer()
        except (serial.SerialException, OSError):
            pass

        self._thread = threading.Thread(
            target=self._ler, name="genius-serial", daemon=True
        )
        self._thread.start()

        # Repete o pedido de modo remoto caso o sketch ainda esteja iniciando.
        limite = time.monotonic() + 3.5
        while time.monotonic() < limite and not self._ack_remoto.is_set():
            self.enviar(ENTRAR_REMOTO)
            self._ack_remoto.wait(0.4)
        return True

    def _ler(self) -> None:
        while not self._parar.is_set():
            try:
                assert self._ser is not None
                dados = self._ser.read(256)
            except (serial.SerialException, OSError):
                break
            if not dados:
                continue
            self._buffer.extend(dados)
            while b"\n" in self._buffer:
                bruto, _, resto = self._buffer.partition(b"\n")
                self._buffer = bytearray(resto)
                linha = bruto.decode("ascii", "replace").strip()
                evento = decodificar(linha)
                if evento is None:
                    continue
                if evento[0] == "remoto":
                    self._ack_remoto.set()
                self._fila.put(evento)

        if not self._parar.is_set() and not self._falhou:
            self._falhou = True
            self._fila.put(("desconectado", None))

    def eventos(self) -> list[tuple[str, int | None]]:
        saida = []
        while True:
            try:
                saida.append(self._fila.get_nowait())
            except queue.Empty:
                return saida

    def enviar(self, comando: str) -> bool:
        if self._falhou or self._ser is None or not self._ser.is_open:
            return False
        try:
            with self._trava:
                self._ser.write((comando + "\n").encode("ascii"))
            return True
        except (serial.SerialException, OSError):
            if not self._falhou:
                self._falhou = True
                self._fila.put(("desconectado", None))
            return False

    def led(self, indice: int, duracao_ms: int) -> None:
        self.enviar(comando_led(indice, duracao_ms))

    def tom(self, indice: int, duracao_ms: int) -> None:
        self.enviar(comando_tom(indice, duracao_ms))

    def led_tom(self, indice: int, duracao_ms: int) -> None:
        self.enviar(comando_led(indice, duracao_ms))
        self.enviar(comando_tom(indice, duracao_ms))

    def tudo_off(self) -> None:
        self.enviar(TUDO_OFF)

    def fechar(self) -> None:
        if self._fechada:
            return
        self._fechada = True
        self._parar.set()
        if self._ser is not None:
            try:
                self._ser.close()
            except serial.SerialException:
                pass
        if self._thread is not None:
            self._thread.join(timeout=1.0)
