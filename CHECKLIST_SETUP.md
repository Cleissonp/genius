# ✅ Checklist de Setup — Genius Neon

Marque cada item conforme concluir.

---

## 🔧 Arduino Setup

### Arduino CLI
- [ ] Baixou arduino-cli para Windows
- [ ] Extraiu em `C:\Program Files\Arduino CLI\`
- [ ] Testou: `arduino-cli.exe version` (output: 1.5.1+)
- [ ] Instalou core: `arduino:avr@1.8.8`

### Hardware
- [ ] Arduino Uno/Nano está plugado no USB
- [ ] LED vermelho do Arduino está aceso
- [ ] Identificou a porta em `--listar-portas` (COMx)
- [ ] Se CH340, instalou driver: https://www.wch.cn/downloads/CH341SER_EXE.html

### Firmware
- [ ] Copiou pasta `genius/` para seu PC
- [ ] Fechou Arduino IDE e Serial Monitor
- [ ] Compilou: `arduino-cli.exe compile --fqbn arduino:avr:uno genius`
- [ ] Upload: `arduino-cli.exe upload -p COM5 --fqbn arduino:avr:uno genius`
- [ ] Viu: `New upload port: COM5 (serial)` ✅

---

## 🐍 Python Setup

### Ambiente
- [ ] Tem Python 3.10+ instalado
- [ ] Testou: `python --version` (output: Python 3.10+)
- [ ] Python está no PATH
- [ ] Criou venv: `python -m venv .venv`
- [ ] Ativou venv: `.venv\Scripts\Activate.ps1`

### Dependências
- [ ] Instalou pip: `pip install --upgrade pip`
- [ ] Instalou requirements: `pip install -r requirements.txt`
- [ ] Testou: `pip list` (mostra pygame-ce, pyserial, numpy)

### Testes
- [ ] Rodar: `python -m unittest discover -s tests -v`
- [ ] Resultado: **15 tests OK** ✅
- [ ] Smoke test: `python main.py --teste --demo`
- [ ] Resultado: **~241 quadros em ~4s** ✅

---

## 🎮 Jogo Funcional

### Conexão
- [ ] Testou: `python main.py --listar-portas`
- [ ] Viu a porta do Arduino (COM5, CH340, etc)
- [ ] Testou: `python main.py --demo` (só teclado/mouse)
- [ ] Funcionou: Janela abriu, jogo rodou

### Com Arduino
- [ ] Plugou Arduino antes de rodar Python
- [ ] Rodou: `python main.py --porta COM5`
- [ ] Viu: `Serial aberta: COM5`
- [ ] Viu: `Modo remoto confirmado (OK REMOTO)`
- [ ] Janela pygame abriu
- [ ] Teclou `1-4` ou clicou nos quadrantes
- [ ] Som funcionou (ou tecle `M` se mudo)
- [ ] Botões do Arduino funcionaram (se conectados)

---

## 🔌 Hardware Conectado (Opcional)

Se montou os LEDs e botões:

### LEDs
- [ ] LED 0 (D2) acende em verde
- [ ] LED 1 (D4) acende em rosa
- [ ] LED 2 (D6) acende em azul
- [ ] LED 3 (D8) acende em amarelo

### Botões
- [ ] Botão 0 (D3) escolhe cor 0
- [ ] Botão 1 (D5) escolhe cor 1
- [ ] Botão 2 (D7) escolhe cor 2
- [ ] Botão 3 (D9) escolhe cor 3

### Som
- [ ] Buzzer (D12) toca as 4 notas: A5, A4, G4, D4
- [ ] Som inicial (jingle) toca ao começar rodada
- [ ] Som de erro toca ao errar

---

## 📊 Validação Final

- [ ] Compilação: ✅ (firmware)
- [ ] Upload: ✅ (no Arduino)
- [ ] Testes: ✅ (15/15 Python)
- [ ] Jogo demo: ✅ (sem Arduino)
- [ ] Jogo serial: ✅ (com Arduino)
- [ ] Hardware: ✅ (LEDs, botões, som)

---

## 🆘 Se algo falhar

| Problema | Solução |
|----------|---------|
| Porta ocupada | Feche Arduino IDE, aguarde 3s, tente novamente |
| Arduino não encontrado | Instale driver CH340, tente outra porta USB |
| Firmware não responde | Aperte RESET no Arduino, aguarde 3,5s |
| Sem som | Tecle `M`, verifique volume Windows |
| Pygame não abre | Rodoo em modo headless: `--teste --demo` |
| Testes falhando | Verifique se pygame-ce 2.5.8 está instalado |

---

## 🎯 Próximos passos

- [ ] Otimizar a velocidade do jogo
- [ ] Adicionar mais efeitos visuais
- [ ] Criar versão `.exe` com PyInstaller
- [ ] Documentar hardware/esquemático
- [ ] Criar CI/CD automático

---

**Status:** ✅ **PRONTO PARA JOGAR**

Data: _____________  
Responsável: _____________  
Notas: _____________________________________________

