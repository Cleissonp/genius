# 🎮 Genius Neon — Guia Completo de Instalação

Jogo Genius em duas camadas: firmware AVR (Arduino) + cliente pygame em Python.

---

## 📋 Pré-requisitos

- **Hardware:** Arduino Uno/Nano com CH340 (clone) ou FTDI original
- **SO:** Windows 10/11 (ou adaptar para Linux/macOS)
- **Internet:** Para baixar arduino-cli e dependências Python

---

## 🔧 Parte 1: Preparar o Arduino

### Passo 1.1: Instalar Arduino CLI

1. Acesse: https://create.arduino.cc/cli/
2. Baixe a versão para Windows (`arduino-cli_windows_amd64.zip`)
3. Extraia em: `C:\Program Files\Arduino CLI\`
4. Verifique a instalação:
   ```cmd
   "C:\Program Files\Arduino CLI\arduino-cli.exe" version
   ```
   **Saída esperada:**
   ```
   arduino-cli Version: 1.5.1
   ```

### Passo 1.2: Instalar core AVR

```cmd
"C:\Program Files\Arduino CLI\arduino-cli.exe" core install arduino:avr@1.8.8
```

Aguarde a instalação (~100 MB).

### Passo 1.3: Listar portas e testar conexão

```cmd
"C:\Program Files\Arduino CLI\arduino-cli.exe" board list
```

**Saída esperada (com Arduino conectado):**
```
Port       Type              Board Name      FQBN            Core
COM5       Serial Port (USB) Arduino Uno     arduino:avr:uno arduino:avr
```

**⚠️ Se não aparecer:**
- Verifique se o Arduino está plugado no USB
- Se for clone CH340, instale driver: https://www.wch.cn/downloads/CH341SER_EXE.html
- Tente outra porta USB
- Reinicie o PC

---

## 📝 Parte 2: Upload do Firmware

### Passo 2.1: Obter o código fonte

Copie a pasta `genius/` para seu PC. Deve conter:
```
genius/
├── genius.ino
├── pins.h (ou similar)
└── (outros arquivos do sketch)
```

### Passo 2.2: Fechar programas que usem a porta

**Feche:**
- Arduino IDE (se aberto)
- Serial Monitor
- Qualquer IDE que use COM5

### Passo 2.3: Compilar o firmware

```cmd
"C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno <caminho>\genius
```

**Saída esperada:**
```
Sketch uses 6908 bytes (21%) of program storage space. Maximum is 32256 bytes.
Global variables use 522 bytes (25%) of dynamic memory.
```

### Passo 2.4: Fazer upload

```cmd
"C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno <caminho>\genius
```

**Saída esperada:**
```
New upload port: COM5 (serial)
```

✅ **O Arduino está pronto!** Ele entrará em modo remoto e aguardará conexão do PC.

---

## 🐍 Parte 3: Instalar Cliente Python

### Passo 3.1: Verificar Python

```cmd
python --version
```

**Deve ser 3.10 ou superior.** Se não tiver:
1. Acesse: https://www.python.org/downloads/
2. Baixe **Python 3.12** (ou 3.10+)
3. Na instalação, marque **"Add Python to PATH"**
4. Reinicie o terminal

### Passo 3.2: Copiar código do cliente

Copie a pasta `pc/` para seu PC:
```
pc/
├── main.py
├── requirements.txt
├── genius_pc/
│   ├── __init__.py
│   ├── jogo.py
│   ├── app.py
│   ├── conexao.py
│   ├── audio.py
│   └── protocolo.py
└── tests/
    ├── test_jogo.py
    ├── test_protocolo.py
    └── test_conexao.py
```

### Passo 3.3: Criar ambiente virtual

```cmd
cd pc
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Nota para PowerShell:** Se der erro de permissão, execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Passo 3.4: Instalar dependências

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependências (automático):**
- pygame-ce >= 2.5.0
- pyserial >= 3.5
- numpy >= 1.26

Aguarde a instalação (~500 MB total).

---

## 🎮 Parte 4: Executar o Jogo

### Passo 4.1: Listar portas seriais

```cmd
python main.py --listar-portas
```

**Saída esperada:**
```
COM5     USB-SERIAL CH340 (COM5)  [USB VID:PID=1A86:7523 ...]
```

Anote a porta do seu Arduino.

### Passo 4.2: Jogar com Arduino

```cmd
python main.py --porta COM5
```

A janela do jogo abrirá. Controles:
- **Botões Arduino:** Escolhem cor e iniciam rodada
- **Teclado:** `1-4` ou `A-S-D-F` para cores, `Enter` para iniciar
- **Mouse:** Clique nos quadrantes
- **Pausa:** `P`
- **Som:** `M`
- **Tela cheia:** `F11`
- **Sair:** `Esc`

### Passo 4.3: Jogar sem Arduino (modo demo)

```cmd
python main.py --demo
```

Funciona só com teclado/mouse.

---

## ✅ Testes e Validação

### Rodar todos os testes

```cmd
python -m unittest discover -s tests -v
```

**Esperado:** 15 testes passando em ~0,02s

### Teste rápido (headless)

```cmd
python main.py --teste --demo
```

**Esperado:**
```
Teste concluído: estado=ENTRADA rodada=1 quadros=241 serial=não
```

---

## 📊 Protocolo Serial

O Arduino usa **115200 8N1, ASCII, uma linha por comando (`\n`).**

| Direção | Comando | Significado |
|---------|---------|-------------|
| Arduino → PC | `READY` | Firmware iniciou |
| Arduino → PC | `OK REMOTO` | Modo remoto ativado |
| Arduino → PC | `B0`–`B3` | Botão pressionado (índice) |
| PC → Arduino | `M1` | Entrar modo remoto |
| PC → Arduino | `M0` | Voltar ao standalone |
| PC → Arduino | `L<i>,<ms>` | LED `i` por `ms`ms |
| PC → Arduino | `T<i>,<ms>` | Tom `i` por `ms`ms |
| PC → Arduino | `A` | Desligar tudo |

---

## 🛠️ Troubleshooting

### ❌ "Porta ocupada" / "Acesso negado"

```
Error: cannot open port \\.\COM5: Acesso negado
```

**Solução:**
1. Feche Arduino IDE
2. Feche Serial Monitor
3. Feche qualquer IDE que use COM5
4. Aguarde 2-3 segundos
5. Tente novamente

### ❌ Arduino não encontrado

```
Arduino não encontrado; iniciando em modo demo.
```

**Checklist:**
- [ ] Arduino está plugado no USB?
- [ ] A luz LED do Arduino está acesa?
- [ ] Saiu da lista de portas em `--listar-portas`?
- [ ] É clone CH340? Instale driver: https://www.wch.cn/downloads/CH341SER_EXE.html
- [ ] Tente outra porta USB
- [ ] Reinicie o Arduino (aperte reset)

### ❌ Firmware não responde

```
Porta aberta, mas o firmware não respondeu ao M1.
```

**Solução:**
1. Verifique se fez upload do firmware correto
2. Aperte o botão RESET do Arduino
3. Aguarde 3,5 segundos
4. Rode novamente

### ❌ Sem som no jogo

**Solução:**
1. Tecle `M` para ativar/desativar som
2. Verifique o volume do Windows
3. Verifique se há dispositivo de áudio padrão

### ❌ Pygame não abre

```
Falha ao abrir a janela
```

**Solução:**
- Atualize drivers de vídeo
- Tente `python main.py --demo --teste` (modo headless)

---

## 🔌 Hardware

| Índice | Tom | LED | Botão | Freq. |
|--------|-----|-----|-------|-------|
| 0 | D12 | D2  | D3 | 880 Hz |
| 1 | D12 | D4  | D5 | 440 Hz |
| 2 | D12 | D6  | D7 | 392 Hz |
| 3 | D12 | D8  | D9 | 294 Hz |

**Requisitos:**
- Buzzer **passivo** no D12
- LEDs com resistor 220 Ω
- Botões com pull-up interno (INPUT_PULLUP, ativo em LOW)
- GND comum entre Arduino e periféricos

---

## 📦 Estrutura de Arquivos

```
Genius Neon/
├── genius/
│   ├── genius.ino              # Firmware AVR
│   └── (suporte ao sketch)
│
├── pc/
│   ├── main.py                 # CLI e ponto de entrada
│   ├── requirements.txt         # Dependências Python
│   ├── README.md               # Documentação técnica
│   ├── .venv/                  # Ambiente virtual (criado por você)
│   │
│   ├── genius_pc/
│   │   ├── __init__.py
│   │   ├── jogo.py             # Lógica pura (sem pygame)
│   │   ├── app.py              # UI, janela, efeitos
│   │   ├── conexao.py          # Serial + thread
│   │   ├── audio.py            # Síntese de som
│   │   └── protocolo.py        # Parser de comandos
│   │
│   └── tests/
│       ├── test_jogo.py
│       ├── test_protocolo.py
│       └── test_conexao.py
```

---

## 🚀 Quick Start (resumido)

```cmd
REM 1. Upload do firmware
"C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno genius
"C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno genius

REM 2. Preparar Python
cd pc
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

REM 3. Jogar
python main.py --porta COM5
```

---

## 📞 Suporte

Se algo não funcionar:

1. Rode os **testes**:
   ```cmd
   python -m unittest discover -s tests -v
   ```

2. Verifique as **portas**:
   ```cmd
   python main.py --listar-portas
   ```

3. Teste sem Arduino:
   ```cmd
   python main.py --demo
   ```

4. Leia o **README.md** e **AGENTS.md** para contexto técnico

---

## 📅 Versões Testadas

- **Arduino CLI:** 1.8.8 (core AVR)
- **Python:** 3.12.10
- **pygame-ce:** 2.5.8
- **pyserial:** 3.5
- **numpy:** 2.5.3
- **SO:** Windows 11 Pro

---

**Boa sorte! 🎮✨**
