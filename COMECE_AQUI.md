# 🚀 COMECE AQUI — Genius Neon

Guia rápido para colocar o jogo funcionando em 15 minutos.

---

## ✨ O que você precisa

- Windows 10/11
- Arduino Uno/Nano (ou clone CH340)
- Cable USB para Arduino
- Internet para baixar programas

---

## 🎬 Passo 1: Arduino CLI (5 min)

### Baixar
1. Acesse: **https://create.arduino.cc/cli/**
2. Clique em **"Download"** → Windows
3. Extraia o arquivo em: **`C:\Program Files\Arduino CLI\`**

### Testar
Abra PowerShell e digite:
```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" version
```

Deve mostrar: `arduino-cli Version: 1.5.1`

### Instalar driver (se for clone)
Se seu Arduino foi muito barato, é clone CH340. Instale o driver:
- https://www.wch.cn/downloads/CH341SER_EXE.html
- Execute o instalador e reinicie o PC

---

## 🎬 Passo 2: Instalar core AVR (2 min)

```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" core install arduino:avr@1.8.8
```

Aguarde a instalação.

---

## 🎬 Passo 3: Upload do firmware (3 min)

### Encontrar a porta
```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" board list
```

Procure por uma linha como:
```
COM5       Serial Port (USB) Arduino Uno     arduino:avr:uno arduino:avr
```

Anote a porta (ex: **COM5**)

### Compilar
```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno "<caminho>\genius"
```

Troque `<caminho>` pelo caminho real da pasta `genius/`. Ex:
```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno "C:\Users\Seu Usuario\Desktop\Genius\genius"
```

### Fazer upload
```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno "<caminho>\genius"
```

**Pronto!** O Arduino está com o firmware novo.

---

## 🎬 Passo 4: Python (3 min)

### Verificar Python
```powershell
python --version
```

Se não tiver ou for versão antiga (< 3.10):
1. Baixe: **https://www.python.org/downloads/** (Python 3.12)
2. Execute o instalador
3. ⚠️ **Marque:** "Add Python to PATH"
4. Reinicie o PowerShell

### Criar ambiente
```powershell
cd "<caminho>\pc"
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Instalar dependências
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Aguarde ~5 minutos.

---

## 🎬 Passo 5: Jogar! (2 min)

### Com Arduino conectado
```powershell
python main.py --porta COM5
```

A janela do jogo abrirá! 🎮

### Controles
- **Números 1-4** = escolher cor (ou A-S-D-F)
- **Enter** = iniciar rodada
- **Botões do Arduino** = também funcionam
- **P** = pausar
- **M** = ligar/desligar som
- **Esc** = sair

---

## 🧪 Testar sem Arduino

Se não tiver Arduino ou não funcionar:

```powershell
python main.py --demo
```

Funciona com teclado/mouse só.

---

## ✅ Tudo funcionando?

```powershell
python -m unittest discover -s tests -v
```

Deve mostrar: **15 tests OK** ✨

---

## ❌ Deu problema?

### Porta ocupada
Feche Arduino IDE, aguarde 3 segundos, tente novamente.

### Arduino não encontrado
1. Verifique se está plugado
2. Se for clone, instale driver CH340
3. Tente outra porta USB
4. Reinicie o PC

### Sem som
Tecle `M` ou verifique volume do Windows.

### Pygame não abre
Rode em modo teste: `python main.py --teste --demo`

---

## 📖 Leia depois

- **INSTALACAO.md** — Guia completo e detalhado
- **CHECKLIST_SETUP.md** — Checklist de verificação
- **README.md** — Overview do projeto
- **DEPLOY.md** — Passo a passo de deploy

---

## 🎯 Resumo dos comandos

```powershell
REM Compilar firmware
& "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno genius

REM Upload
& "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno genius

REM Preparar Python
cd pc
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

REM Jogar
python main.py --porta COM5
```

---

**Divirta-se! 🎮✨**
