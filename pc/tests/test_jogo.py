import random
import unittest

from genius_pc.jogo import EstadoJogo, JogoGenius


def avancar(jogo: JogoGenius, segundos: float, passo: float = 0.01):
    eventos = []
    for _ in range(int(segundos / passo)):
        eventos.extend(jogo.atualizar(passo))
    return eventos


def tipos(eventos):
    return [evento.tipo for evento in eventos]


class TesteJogo(unittest.TestCase):
    def setUp(self):
        self.jogo = JogoGenius(random.Random(7))

    def test_inicio_cria_rodada_um(self):
        eventos = self.jogo.iniciar()
        self.assertEqual(tipos(eventos), ["inicio", "nova_rodada"])
        self.assertEqual(self.jogo.estado, EstadoJogo.TOCANDO)
        self.assertEqual(self.jogo.rodada, 1)
        self.assertEqual(len(self.jogo.sequencia), 1)
        self.assertIn(self.jogo.sequencia[0], range(4))

    def test_reproduz_sequencia_e_pede_entrada(self):
        self.jogo.iniciar()
        eventos = avancar(self.jogo, 4.0)
        self.assertIn("passo_on", tipos(eventos))
        self.assertIn("passo_off", tipos(eventos))
        self.assertIn("sua_vez", tipos(eventos))
        self.assertEqual(self.jogo.estado, EstadoJogo.ENTRADA)
        self.assertEqual(tipos(eventos).count("passo_on"), 1)

    def test_acerto_completa_rodada_e_pontua(self):
        self.jogo.iniciar()
        avancar(self.jogo, 4.0)
        indice = self.jogo.sequencia[0]
        eventos = self.jogo.pressionar(indice)
        self.assertEqual(tipos(eventos), ["acerto", "rodada_completa"])
        self.assertEqual(self.jogo.estado, EstadoJogo.FIM_RODADA)
        self.assertEqual(self.jogo.pontuacao, 1 * 100 + 1 * 15)

    def test_erro_encerra_o_jogo(self):
        self.jogo.iniciar()
        avancar(self.jogo, 4.0)
        errado = (self.jogo.sequencia[0] + 1) % 4
        eventos = self.jogo.pressionar(errado)
        self.assertEqual(tipos(eventos), ["erro", "fim_de_jogo"])
        self.assertEqual(self.jogo.estado, EstadoJogo.GAME_OVER)

    def test_entrada_ignorada_durante_reproducao(self):
        self.jogo.iniciar()
        self.assertEqual(self.jogo.pressionar(self.jogo.sequencia[0]), [])
        self.assertEqual(self.jogo.estado, EstadoJogo.TOCANDO)

    def test_proxima_rodada_cresce_a_sequencia(self):
        self.jogo.iniciar()
        avancar(self.jogo, 4.0)
        self.jogo.pressionar(self.jogo.sequencia[0])
        eventos = avancar(self.jogo, 1.2)
        self.assertIn("nova_rodada", tipos(eventos))
        self.assertEqual(self.jogo.rodada, 2)
        self.assertEqual(len(self.jogo.sequencia), 2)
        self.assertEqual(self.jogo.estado, EstadoJogo.TOCANDO)

    def test_reinicio_so_depois_da_pausa_do_game_over(self):
        self.jogo.iniciar()
        avancar(self.jogo, 4.0)
        self.jogo.pressionar((self.jogo.sequencia[0] + 1) % 4)
        self.assertFalse(self.jogo.pode_reiniciar)
        avancar(self.jogo, 1.0)
        self.assertTrue(self.jogo.pode_reiniciar)
        eventos = self.jogo.iniciar()
        self.assertEqual(tipos(eventos)[0], "inicio")
        self.assertEqual(self.jogo.rodada, 1)
        self.assertEqual(self.jogo.pontuacao, 0)

    def test_reinicio_forcado_durante_a_partida(self):
        self.jogo.iniciar()
        avancar(self.jogo, 4.0)
        self.assertEqual(self.jogo.pressionar(self.jogo.sequencia[0])[0].tipo, "acerto")
        eventos = self.jogo.iniciar(forcar=True)
        self.assertEqual(tipos(eventos)[0], "inicio")
        self.assertEqual(self.jogo.estado, EstadoJogo.TOCANDO)
        self.assertEqual(self.jogo.pontuacao, 0)

    def test_sequencia_cresce_a_cada_rodada(self):
        self.jogo.iniciar()
        for _ in range(3):
            avancar(self.jogo, 4.0 if self.jogo.estado is EstadoJogo.TOCANDO else 0.01)
            if self.jogo.estado is EstadoJogo.ENTRADA:
                for indice in self.jogo.sequencia[self.jogo.indice_entrada:]:
                    self.jogo.pressionar(indice)
            avancar(self.jogo, 1.2)
        self.assertGreaterEqual(len(self.jogo.sequencia), 3)


if __name__ == "__main__":
    unittest.main()
