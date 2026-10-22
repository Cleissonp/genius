# 🗺️ Fluxograma de Setup — Genius Neon

Guia visual passo a passo.

---

## 🚀 Instalação Completa (em 30-60 minutos)

```
┌─────────────────────────────────────────────┐
│  COMECE COM: Arduino CLI + Python + Jogo   │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  1️⃣  ARDUINO CLI (5 min)                    │
│  ✓ Baixar de create.arduino.cc/cli          │
│  ✓ Extrair em C:\Program Files\Arduino CLI\ │
│  ✓ Testar: arduino-cli.exe version          │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  2️⃣  DRIVER ARDUINO (3 min, se CH340)       │
│  ✓ Se clone barato: instalar driver CH340   │
│  ✓ Reiniciar PC                             │
│  ✓ Verificar em: arduino-cli.exe board list │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  3️⃣  CORE AVR (2 min)                       │
│  ✓ arduino-cli.exe core install arduino:avr │
│  ✓ Aguardar ~100MB                          │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  4️⃣  FIRMWARE (5 min)                       │
│  ✓ Compilar: arduino-cli compile ...        │
│  ✓ Fechar Arduino IDE                       │
│  ✓ Upload: arduino-cli upload ...           │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  5️⃣  PYTHON (3 min)                         │
│  ✓ Verificar: python --version (3.10+)     │
│  ✓ Venv: python -m venv .venv               │
│  ✓ Ativar: .venv\Scripts\Activate.ps1       │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  6️⃣  DEPENDÊNCIAS (5 min)                   │
│  ✓ pip install -r requirements.txt          │
│  ✓ Aguardar ~5 minutos                      │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  7️⃣  TESTES (1 min)                         │
│  ✓ python -m unittest discover -s tests -v  │
│  ✓ Esperado: 15 tests OK                    │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  8️⃣  JOGAR! (∞)                             │
│  ✓ python main.py --porta COM5              │
│  ✓ Aproveite! 🎮                            │
└─────────────────────────────────────────────┘
```

---

## ❓ Problemas? Use este fluxograma

```
┌─────────────────────┐
│ PROBLEMA ENCONTRADO │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Qual a etapa? │
    └──┬────────┬──┬──┘
       │        │  │
   Arduino    Python Jogo
       │        │    │
       ▼        ▼    ▼
   
Arduino:          Python:            Jogo:
   │                 │                  │
   ├─ Não encontra? ├─ Não instala?    ├─ Não abre?
   │  → TROUBL.#1   │  → TROUBL.#2     │  → TROUBL.#7
   │                │                  │
   ├─ Porta ocupada?├─ Sem módulos?    ├─ Sem som?
   │  → TROUBL.#2   │  → TROUBL.#3     │  → TROUBL.#8
   │                │                  │
   ├─ Upload falha? ├─ Testes falham?  ├─ Botões não
   │  → TROUBL.#3   │  → TROUBL.#4     │  funcionam?
   │                │                  │  → TROUBL.#9
   ├─ Sem resposta? │
   │  → TROUBL.#4   │
   │                │
   └─────────────────────────────────────┐
                                         │
                    ┌────────────────────▼────────┐
                    │ CONSULTÚL ARQUIVO           │
                    │ TROUBLESHOOTING.md          │
                    └─────────────────────────────┘
```

---

## 📱 Rápido? Use esta versão resumida

```bash
REM 1. Arduino CLI
"C:\Program Files\Arduino CLI\arduino-cli.exe" version

REM 2. Core AVR
"C:\Program Files\Arduino CLI\arduino-cli.exe" core install arduino:avr

REM 3. Compilar
"C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno genius

REM 4. Upload (feche Arduino IDE primeiro!)
"C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno genius

REM 5. Python
cd pc
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

REM 6. Teste
python -m unittest discover -s tests -v

REM 7. JOGAR!
python main.py --porta COM5
```

---

## 🎯 Checklist: O que fazer em cada etapa

### Arduino CLI ✓
- [ ] Baixou .zip
- [ ] Extraiu em C:\Program Files\Arduino CLI\
- [ ] Rodou: `arduino-cli.exe version`
- [ ] Saída: Version 1.5.1+

### Driver (se CH340) ✓
- [ ] Baixou driver CH340
- [ ] Executou instalador
- [ ] Reiniciou PC

### Core AVR ✓
- [ ] Rodou: `arduino-cli.exe core install arduino:avr`
- [ ] Concluiu com sucesso

### Firmware ✓
- [ ] Tem pasta `genius/` com `.ino`
- [ ] Compilou: `arduino-cli compile ...`
- [ ] Upload: `arduino-cli upload -p COM5 ...`
- [ ] Viu: `New upload port: COM5`

### Python ✓
- [ ] Tem Python 3.10+
- [ ] Criou venv
- [ ] Ativou venv (aparece `(.venv)`)
- [ ] Instalou requirements

### Testes ✓
- [ ] Rodou testes: `python -m unittest ...`
- [ ] Resultado: **15 tests OK**

### Jogo ✓
- [ ] Rodou: `python main.py --porta COM5`
- [ ] Janela abriu
- [ ] Conseguiu jogar

---

## 🔄 Precisa refazer? Reset Completo

```powershell
# Limpar tudo
rmdir .venv /s /q
taskkill /f /im "Arduino IDE.exe"
Start-Sleep -Seconds 3

# Refazer Python
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Refazer firmware
& "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno genius
& "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno genius

# Testar
python -m unittest discover -s tests -v
python main.py --porta COM5
```

---

## 📊 Tempos Estimados

| Etapa | Tempo | Notas |
|-------|-------|-------|
| Arduino CLI | 5 min | Download + extração |
| Driver CH340 | 3 min | Só se clone |
| Core AVR | 5 min | ~100MB |
| Compilar | 2 min | Primeira vez |
| Upload | 1 min | Com Arduino |
| Python | 3 min | Venv setup |
| Dependências | 5 min | pip install (~500MB) |
| Testes | 1 min | 15 testes |
| **TOTAL** | **~30 min** | |

---

## 🎮 Primeiros Passos no Jogo

```
1. Esperar a tela inicial aparecer
2. Teclar "Enter" para começar
3. Observar 4 cores piscarem em sequência
4. Repetir a sequência teclando 1-4 (ou A-S-D-F)
5. Cada rodada fica mais rápida
6. Errar = Game Over
7. Recorde salvo em ~/.genius_neon.json

Aproveite! 🎮✨
```

---

## 🆘 Se ficar preso

1. **Releia**: COMECE_AQUI.md (simples)
2. **Ou detalhado**: INSTALACAO.md (passo a passo)
3. **Procure erro**: TROUBLESHOOTING.md
4. **Verifique**: CHECKLIST_SETUP.md

---

**Você consegue! 💪**
