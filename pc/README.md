# Genius Neon — cliente pygame + Arduino

Jogo de memória estilo Genius com visual neon, som sintetizado e botões físicos.
O **Python é o dono do jogo** (sequência, timing, pontuação e efeitos); o Arduino
virou uma ponte de I/O: manda os botões e obedece comandos de LED/buzzer.

O sketch também continua funcionando sozinho, sem PC (veja abaixo).

## Hardware

| índice | tom | LED | botão |
|---|---|---|---|
| 0 | A5 (880 Hz) | D2 | D3 |
| 1 | A4 (440 Hz) | D4 | D5 |
| 2 | G4 (392 Hz) | D6 | D7 |
| 3 | D4 (294 Hz) | D8 | D9 |

- Buzzer no D12. Use **buzzer passivo**; buzzer ativo não reproduz as notas.
- LEDs com resistor de 220 Ω.
- Botões ligados entre o pino e o **GND** (o sketch usa `INPUT_PULLUP`, ativo em LOW).
- GND comum entre Arduino e periféricos. D0/D1 ficam reservados para a serial/USB.
- Placa alvo: Arduino Uno/Nano (AVR). O código usa `tone()` e pinos fixos.

## Firmware

Abra `genius/genius.ino` na Arduino IDE, selecione a placa e a porta e faça upload.

Pela linha de comando (arduino-cli instalado em `C:\Program Files\Arduino CLI`,
fora do PATH):

```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno genius
& "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno genius
```

Ao ligar, o firmware espera **3,5 s** por um comando `M1`. Se ninguém abrir a
serial, ele inicia o jogo standalone original. `M1` interrompe o standalone e
entra no modo remoto; `M0` volta ao standalone. Ao fechar o cliente Python, o
Arduino fica em modo remoto com as saídas desligadas — aperte **reset** para
jogar sozinho de novo.

## Cliente Python

Requisitos: Python 3.10+ (testado com 3.12 no Windows), `pygame-ce`, `pyserial`
e `numpy`.

```powershell
cd pc
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py --listar-portas
python main.py --porta COM5
```

Sem `--porta`, o programa tenta detectar Arduino/CH340/FTDI. Se não achar nada,
abre em modo demo (só teclado/mouse). Para forçar o demo:

```powershell
python main.py --demo
```

Outras opções:

```
--tela-cheia      inicia em tela cheia
--mudo            inicia sem som
--exigir-serial   falha se o Arduino não abrir
--teste           roda ~4 s sem janela (diagnóstico/CI)
```

## Controles

| ação | teclado | mouse | Arduino |
|---|---|---|---|
| escolher cor | `1`–`4` ou `A S D F` | clique no quadrante | botão físico |
| começar / reiniciar | `Enter` / `Espaço` | clique | botão |
| pausar | `P` | — | — |
| som | `M` | — | — |
| tela cheia | `F11` | — | — |
| reiniciar a qualquer momento | `R` | — | — |
| sair | `Esc` | — | — |

## Como o jogo funciona

- A cada rodada o Python sorteia mais um passo, reproduz a sequência nos LEDs,
  no buzzer e na tela, e então espera a entrada do jogador.
- A velocidade aumenta: passo de 0,55 s cai até 0,22 s; o intervalo cai de
  0,15 s até 0,07 s.
- Pontuação da rodada: `rodada * 100 + combo * 15`.
- O recorde fica em `~/.genius_neon.json` (no Windows,
  `C:\Users\<usuário>\.genius_neon.json`).
- Os quatro timbres, o jingle de início, o som de erro e o game over são
  sintetizados com numpy na inicialização — não há arquivos de áudio.
- Efeitos: brilho, ondas, partículas, tremor de tela, flash de erro, banner de
  rodada, combo e slow reveal no game over.

## Protocolo serial

ASCII, uma linha por comando (`\n`), **115200 8N1**.

| direção | comando | significado |
|---|---|---|
| Arduino → PC | `READY` | firmware iniciou |
| Arduino → PC | `OK REMOTO` / `OK STANDALONE` | modo confirmado |
| Arduino → PC | `B0`…`B3` | botão pressionado (após debounce) |
| PC → Arduino | `M1` / `M0` | entra no modo remoto / volta ao standalone |
| PC → Arduino | `L<i>,<ms>` | liga o LED `i` por `ms` (0 desliga) |
| PC → Arduino | `T<i>,<ms>` | toca o tom `i` por `ms` (0 desliga) |
| PC → Arduino | `A` | desliga LEDs e som |

O firmware usa um buffer de 32 bytes; comandos são curtos de propósito. A
leitura no PC roda em uma thread separada e alimenta uma fila — o loop do pygame
nunca fica bloqueado esperando serial.

## Testes

```powershell
cd pc
python -m unittest discover -s tests -v
python main.py --teste --demo
```

Os testes cobrem a máquina de estados (`genius_pc/jogo.py`) e o protocolo
(`genius_pc/protocolo.py`), sem precisar de pygame nem de hardware. O `--teste`
renderiza 240 quadros com drivers SDL falsos e confirma que a interface sobe.

## Estrutura

```
genius/genius.ino        firmware AVR (standalone + modo serial)
pc/main.py               CLI e ponto de entrada
pc/genius_pc/protocolo.py  comandos/linhas seriais
pc/genius_pc/jogo.py     regras puras (sem pygame)
pc/genius_pc/conexao.py  thread de leitura + fila + handshake
pc/genius_pc/audio.py    síntese dos sons
pc/genius_pc/app.py      janela, desenho e efeitos
pc/tests/                testes com unittest
```

## Problemas comuns

- **Porta ocupada**: feche o Monitor Serial da Arduino IDE antes de rodar.
- **Arduino não encontrado**: instale o driver do CH340 (clones Nano/Uno) e use
  `--listar-portas`; depois passe `--porta COMx`.
- **A placa reinicia ao conectar**: é o DTR. O cliente espera 2 s e repete `M1`
  por alguns segundos; se ainda falhar, aperte reset com o jogo já aberto.
- **Sem som**: tecle `M` (pode estar mudo); no Windows, confira o dispositivo de
  saída padrão.
- **Quero jogar sem PC**: feche o cliente, aperte reset e espere 3,5 s.
- **Placa ESP32**: não funciona sem adaptar `tone()`, `analogRead()` e os pinos.
