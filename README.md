# Genius

Jogo Genius em duas camadas:

- `genius/genius.ino` — firmware Arduino Uno/Nano que funciona sozinho (standalone) ou como ponte serial para o PC.
- `pc/` — cliente pygame com visual neon, sons sintetizados, efeitos e botões físicos. O Python controla a sequência, o timing e a pontuação.

## Começar rápido

1. Abra `genius/genius.ino` na Arduino IDE e faça upload para a placa.
2. Instale as dependências e rode o cliente:

```powershell
cd pc
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --listar-portas
python main.py --porta COM5
```

Sem Arduino, use `python main.py --demo`. Instruções completas de hardware, protocolo, controles e solução de problemas estão em [`pc/README.md`](pc/README.md).

## Verificação

```powershell
cd pc
python -m unittest discover -s tests -v
python main.py --teste --demo
```

O firmware compila para `arduino:avr:uno`. O upload precisa de uma placa conectada; a porta serial não pode estar em uso pela Arduino IDE.
