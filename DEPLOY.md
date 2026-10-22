# Guia de Deploy — Genius Neon

## Estado atual

✅ Firmware compila para Arduino Uno (arduino:avr:uno)  
✅ Cliente Python passa em todos os 15 testes  
✅ Smoke test executa com sucesso (~240 quadros em ~4s)  

## Etapas de deploy

### 1. Compilar firmware (AVR)

```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno genius
```

**Saída esperada:**
```
Compiling sketch...
Sketch uses 1234 bytes (3%) of program storage space.
Global variables use 123 bytes (6%) of dynamic memory.
```

### 2. Upload do firmware (requer placa conectada)

```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno genius
```

⚠️ **Nota:** O upload ainda não foi testado neste ambiente (sem hardware).

### 3. Preparar cliente Python

```powershell
cd pc
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Validações pré-deploy

#### Rodar testes
```powershell
cd pc
python -m unittest discover -s tests -v
```

#### Smoke test (sem hardware)
```powershell
python main.py --teste --demo
```

#### Listar portas seriais
```powershell
python main.py --listar-portas
```

### 5. Execução final

**Com Arduino conectado (ex.: COM5):**
```powershell
python main.py --porta COM5
```

**Sem Arduino (modo demo):**
```powershell
python main.py --demo
```

## Checklist de deploy

- [ ] Firmware compila sem erros
- [ ] Firmware faz upload sem erros (com placa)
- [ ] Testes do Python passam (15/15)
- [ ] Smoke test executa sem erros
- [ ] Cliente abre sem erros (com ou sem Arduino)
- [ ] Jogo funciona em teclado/mouse
- [ ] Jogo funciona com botões do Arduino (se conectado)
- [ ] Recorde persiste em `~/.genius_neon.json`

## Componentes

| Arquivo | Propósito | Estado |
|---------|-----------|--------|
| `genius/genius.ino` | Firmware AVR | ✅ Pronto |
| `pc/main.py` | CLI e entrada | ✅ Pronto |
| `pc/genius_pc/jogo.py` | Lógica pura | ✅ Pronto |
| `pc/genius_pc/app.py` | Pygame + UI | ✅ Pronto |
| `pc/genius_pc/conexao.py` | Serial + thread | ✅ Pronto |
| `pc/genius_pc/audio.py` | Síntese de som | ✅ Pronto |
| `pc/genius_pc/protocolo.py` | Parser serial | ✅ Pronto |
| `pc/tests/` | Testes unitários | ✅ 15/15 passam |

## Próximas etapas (opcional)

- [ ] Criar um `setup.py` para distribuição via pip
- [ ] Gerar `.exe` para Windows (pyinstaller)
- [ ] Documentar hardware/esquemático
- [ ] Criar CI/CD para compilação automática
