# AGENTS.md

## Repositório

- Projeto Arduino + cliente Python. **Não é repositório git**; não há CI, Makefile nem `pyproject`.
- `genius/genius.ino`: firmware AVR (jogo standalone + ponte serial).
- `pc/`: cliente pygame (dono do jogo), testes e `pc/README.md` para o usuário.
- Comentários, identificadores e textos de UI em pt-BR. Mantenha esse padrão.
- Ambiente atual: Python 3.12, pygame-ce 2.5.8, pyserial 3.5, numpy 2.5.3.
- `arduino-cli` 1.5.1 está em `C:\Program Files\Arduino CLI\arduino-cli.exe` (fora do PATH), com core `arduino:avr@1.8.8`.

## Comandos

Sempre rode os comandos Python a partir de `pc/` (os imports usam `genius_pc`):

```powershell
cd pc
python -m unittest discover -s tests -v      # 14 testes, sem hardware
python main.py --teste --demo                # smoke test headless, ~4 s
python main.py --listar-portas
python main.py --porta COM5                  # ou --demo
```

Firmware (a pasta e o arquivo devem continuar `genius`):

```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno genius
& "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno genius
```

O upload nunca foi testado neste ambiente (sem placa). O compile para Uno foi verificado.

## Firmware

- Pinos: buzzer D12; LEDs D2/D4/D6/D8; botões D3/D5/D7/D9 (`INPUT_PULLUP`, **ativo em LOW**). D0/D1 são a serial/USB.
- `tons`, `pinosLeds` e `pinosBotoes` são paralelos por índice; reordenar um sem os outros quebra o jogo.
- Use buzzer **passivo**; o sketch depende de `tone()`.
- Modos: `MODO_AGUARDANDO` (3,5 s por `M1`), `MODO_REMOTO` e `MODO_STANDALONE`.
- No standalone o timing é bloqueante, mas `delayJogo()` fatia as esperas e processa a serial; é assim que `M1` interrompe a partida. Não troque esses `delay()` por `delay()` puro.
- No modo remoto as saídas expiram por `millis()` (sem bloquear): `L<i>,<ms>`, `T<i>,<ms>`, `A`, `M1`/`M0`.
- Botões têm debounce de 25 ms e emitem `B<0-3>` só no modo remoto.
- Buffer serial de 32 bytes, 115200 8N1. Mantenha comandos curtos; não mande rajadas por frame.
- O standalone limita a sequência a 100 passos. O Python não tem esse limite.
- Não é portável para ESP32 sem trocar `tone()`, `analogRead()` e pinagem.

## Cliente Python

- `genius_pc/jogo.py` é lógica pura: **não importe pygame nem serial nele**; os testes dependem disso.
- `genius_pc/app.py` desenha e converte eventos em efeitos/ comandos. `conexao.py` lê serial em thread e entrega `queue.Queue`; nunca faça `readline()`/`sleep()` no loop do pygame.
- `genius_pc/audio.py` sintetiza todos os sons com numpy; não há assets para adicionar.
- Handshake: o cliente espera 2 s pelo bootloader (DTR), repete `M1` por 3,5 s e lê em thread. Ao sair, manda `A` e fecha; o Arduino fica em modo remoto até um reset.
- Fluxo: menu → `iniciar()` (0,75 s de jingle) → reprodução → entrada → fim de rodada (0,9 s) → próxima. Pontos = `rodada*100 + combo*15`; passo de 0,55 s até 0,22 s.
- Recorde persistido em `~/.genius_neon.json`.
- `main.py --teste` define drivers SDL dummy antes de importar o app; use para validar render/áudio sem janela.
- Mudou o protocolo? Atualize `genius/genius.ino`, `pc/genius_pc/protocolo.py`, `pc/tests/test_protocolo.py` e a tabela do `pc/README.md` juntos.
