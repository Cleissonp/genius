import time
import unittest
from unittest import mock

from genius_pc import conexao as modulo

_sleep_real = time.sleep


class SerialFalsa:
    instancias: list["SerialFalsa"] = []

    def __init__(self, porta: str, baud: int, **kwargs) -> None:
        self.porta = porta
        self.is_open = True
        self.entrada = bytearray()
        self.escritas: list[bytes] = []
        SerialFalsa.instancias.append(self)

    def read(self, tamanho: int) -> bytes:
        if self.entrada:
            dados = bytes(self.entrada[:tamanho])
            del self.entrada[:tamanho]
            return dados
        time.sleep(0.001)
        return b""

    def write(self, dados: bytes) -> int:
        self.escritas.append(dados)
        if dados == b"M1\n":
            self.entrada.extend(b"OK REMOTO\n")
        return len(dados)

    def reset_input_buffer(self) -> None:
        self.entrada.clear()

    def close(self) -> None:
        self.is_open = False


def dormir(segundos: float) -> None:
    # pula só a espera longa do bootloader; mantém a pausa curta do leitor
    if segundos < 0.5:
        _sleep_real(segundos)


class TesteConexao(unittest.TestCase):
    def setUp(self):
        SerialFalsa.instancias.clear()

    def test_handshake_comandos_e_botao(self):
        with mock.patch.object(modulo.serial, "Serial", SerialFalsa), mock.patch.object(
            modulo.time, "sleep", dormir
        ):
            link = modulo.ConexaoSerial("COMX")
            self.assertTrue(link.abrir())
            self.assertTrue(link.remoto_confirmado)
            self.assertTrue(link.conectado)

            link.led(2, 300)
            link.tom(1, 0)
            link.led_tom(3, 120)
            link.tudo_off()
            self.assertEqual(
                SerialFalsa.instancias[0].escritas[-5:],
                [
                    b"L2,300\n",
                    b"T1,0\n",
                    b"L3,120\n",
                    b"T3,120\n",
                    b"A\n",
                ],
            )

            SerialFalsa.instancias[0].entrada.extend(b"B2\n")
            recebido = []
            limite = time.monotonic() + 1.0
            while time.monotonic() < limite:
                recebido.extend(link.eventos())
                if ("botao", 2) in recebido:
                    break
                time.sleep(0.005)
            self.assertIn(("botao", 2), recebido)

            link.fechar()
            self.assertFalse(link.conectado)


if __name__ == "__main__":
    unittest.main()
