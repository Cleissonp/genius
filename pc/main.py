"""Ponto de entrada do Genius Neon (pygame + Arduino)."""

from __future__ import annotations

import argparse
import os
import sys


def _argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genius Neon: jogo de memória com pygame e Arduino."
    )
    parser.add_argument(
        "--porta",
        help="porta serial do Arduino (ex.: COM5). Sem isso, tenta detectar.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="não usa Arduino; joga só com teclado/mouse.",
    )
    parser.add_argument(
        "--tela-cheia",
        action="store_true",
        help="inicia em tela cheia.",
    )
    parser.add_argument(
        "--mudo",
        action="store_true",
        help="inicia sem som.",
    )
    parser.add_argument(
        "--listar-portas",
        action="store_true",
        help="lista as portas seriais e sai.",
    )
    parser.add_argument(
        "--exigir-serial",
        action="store_true",
        help="falha se o Arduino não puder ser aberto.",
    )
    parser.add_argument(
        "--teste",
        action="store_true",
        help="executa alguns segundos sem janela (diagnóstico).",
    )
    return parser.parse_args()


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    args = _argumentos()

    if args.listar_portas:
        from genius_pc.conexao import listar_portas

        portas = listar_portas()
        if not portas:
            print("Nenhuma porta serial encontrada.")
            return 0
        for info in portas:
            print(
                f"{info['porta']:<8} {info['descricao']}"
                f"  [{info['hwid']}]"
            )
        return 0

    if args.teste:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    import pygame

    pygame.mixer.pre_init(44_100, -16, 2, 512)
    from genius_pc.app import Aplicativo
    from genius_pc.conexao import ConexaoSerial

    conexao = None
    if not args.demo and not args.teste:
        conexao = ConexaoSerial(args.porta)
        print("Procurando Arduino...")
        if conexao.abrir():
            print(f"Serial aberta: {conexao.descricao}")
            if conexao.remoto_confirmado:
                print("Modo remoto confirmado (OK REMOTO).")
            else:
                print(
                    "Porta aberta, mas o firmware não respondeu ao M1."
                    " Faça upload de genius/genius.ino e tente de novo."
                )
        else:
            print("Arduino não encontrado; iniciando em modo demo.")
            if conexao.descricao:
                detalhe = conexao.descricao.lower()
                if (
                    "permission" in detalhe
                    or "acesso negado" in detalhe
                    or "access is denied" in detalhe
                ):
                    print(
                        "A porta está ocupada. Feche o Monitor Serial da"
                        " Arduino IDE (ou outro programa) e tente de novo."
                    )
                else:
                    print(f"  detalhe: {conexao.descricao}")
            conexao = None
            if args.exigir_serial:
                return 1

    try:
        app = Aplicativo(
            conexao=conexao,
            tela_cheia=args.tela_cheia,
            mudo=args.mudo,
            teste=args.teste,
        )
    except pygame.error as erro:
        print(f"Falha ao abrir a janela: {erro}")
        if conexao is not None:
            conexao.fechar()
        return 1

    try:
        app.executar()
    except KeyboardInterrupt:
        app._encerrar()
    if args.teste:
        print(
            "Teste concluído:"
            f" estado={app.jogo.estado.name}"
            f" rodada={app.jogo.rodada}"
            f" quadros={app.quadros}"
            f" serial={'sim' if conexao else 'não'}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
