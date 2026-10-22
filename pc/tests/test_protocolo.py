import unittest

from genius_pc.protocolo import (
    comando_led,
    comando_tom,
    decodificar,
)


class TesteProtocolo(unittest.TestCase):
    def test_comandos(self):
        self.assertEqual(comando_led(0, 500), "L0,500")
        self.assertEqual(comando_led(3, 0), "L3,0")
        self.assertEqual(comando_tom(1, 130), "T1,130")

    def test_indice_invalido(self):
        with self.assertRaises(ValueError):
            comando_led(4, 100)
        with self.assertRaises(ValueError):
            comando_tom(-1, 100)

    def test_duracao_negativa(self):
        with self.assertRaises(ValueError):
            comando_led(0, -1)

    def test_decodifica_eventos(self):
        self.assertEqual(decodificar("READY"), ("pronto", None))
        self.assertEqual(decodificar("OK REMOTO"), ("remoto", None))
        self.assertEqual(decodificar("OK STANDALONE"), ("standalone", None))
        self.assertEqual(decodificar("B0\r\n"), ("botao", 0))
        self.assertEqual(decodificar("B3\n"), ("botao", 3))
        self.assertEqual(decodificar("R2"), ("soltar", 2))

    def test_ignora_lixo(self):
        for linha in ("", "   ", "B4", "B", "XYZ", "OK"):
            self.assertIsNone(decodificar(linha))


if __name__ == "__main__":
    unittest.main()
