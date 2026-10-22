# 🔧 Troubleshooting — Genius Neon

Soluções para problemas comuns.

---

## 🚨 PROBLEMAS COM ARDUINO

### ❌ "Arduino não encontrado"

```
Arduino não encontrado; iniciando em modo demo.
```

**Causa:** Arduino não está conectado, desligado ou não é reconhecido.

**Solução passo a passo:**

1. **Verifique o hardware:**
   - [ ] Está o Arduino plugado no USB?
   - [ ] Tem LED vermelho aceso no Arduino?
   - [ ] Tente outra porta USB
   - [ ] Tente outro cabo USB

2. **Verifique o driver (para clones CH340):**
   ```
   Se for clone Uno/Nano barato, precise instalar driver
   ```
   - Baixe: https://www.wch.cn/downloads/CH341SER_EXE.html
   - Execute o instalador
   - Reinicie o PC
   - Tente novamente

3. **Verifique a porta:**
   ```powershell
   python main.py --listar-portas
   ```
   Deve aparecer uma linha tipo:
   ```
   COM5     USB-SERIAL CH340 (COM5)  [USB VID:PID=1A86:7523 ...]
   ```
   Se não aparecer nada, volta ao passo 1.

4. **Se a porta aparece mas não funciona:**
   - Feche Arduino IDE completamente
   - Feche Serial Monitor
   - Tente novamente após 3 segundos

5. **Último recurso:**
   - Aperte o botão RESET do Arduino
   - Aguarde 3,5 segundos
   - Rode novamente

---

### ❌ "Porta ocupada" / "Acesso negado"

```
Error: cannot open port \\.\COM5: Acesso negado
```

**Causa:** Outro programa está usando COM5.

**Solução:**

1. **Feche Arduino IDE:**
   - Menu: `File` → `Exit` (ou Ctrl+Q)
   - Ou: `taskkill /f /im "Arduino IDE.exe"`

2. **Feche Serial Monitor:**
   - Feche qualquer janela de monitor serial
   - Ou: `taskkill /f /im serial-monitor.exe`

3. **Aguarde:**
   ```powershell
   Start-Sleep -Seconds 3
   ```

4. **Tente novamente:**
   ```powershell
   python main.py --porta COM5
   ```

---

### ⚠️ "Porta aberta, mas firmware não respondeu"

```
Porta aberta, mas o firmware não respondeu ao M1.
Faça upload de genius/genius.ino e tente de novo.
```

**Causa:** O firmware antigo/errado está no Arduino.

**Solução:**

1. **Compile o firmware correto:**
   ```powershell
   & "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno "<caminho>\genius"
   ```

2. **Feche tudo que usa a porta:**
   ```powershell
   taskkill /f /im "Arduino IDE.exe"
   taskkill /f /im "serial-monitor.exe"
   Start-Sleep -Seconds 3
   ```

3. **Faça upload:**
   ```powershell
   & "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno "<caminho>\genius"
   ```

4. **Rode o jogo:**
   ```powershell
   python main.py --porta COM5
   ```

---

### 🔴 Arduino não responde a nenhum comando

**Causa:** Firmware travado ou problema na serial.

**Solução:**

1. **Aperte RESET no Arduino:**
   - Há um botão pequeno no Arduino
   - Aperte e solte rapidamente
   - Aguarde 3,5 segundos

2. **Se não resolver, reinicie o PC**

3. **Se ainda não resolver, tente reprogramar:**
   ```powershell
   & "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno "<caminho>\genius"
   ```

---

## 🐍 PROBLEMAS COM PYTHON

### ❌ "python: comando não encontrado"

```powershell
python: The term 'python' is not recognized
```

**Causa:** Python não está no PATH.

**Solução:**

1. **Reinstale Python:**
   - Acesse: https://www.python.org/downloads/
   - Baixe Python 3.12
   - ⚠️ **IMPORTANTE:** Marque "Add Python to PATH"
   - Reinicie o PowerShell

2. **Verifique:**
   ```powershell
   python --version
   ```

---

### ❌ "ModuleNotFoundError: No module named 'pygame'"

```python
ModuleNotFoundError: No module named 'pygame'
```

**Causa:** Dependências não instaladas.

**Solução:**

1. **Ative o ambiente virtual:**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   Deve aparecer `(.venv)` no prompt.

2. **Instale dependências:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Verifique:**
   ```powershell
   pip list
   ```
   Deve mostrar pygame-ce, pyserial, numpy.

---

### ❌ "No module named 'genius_pc'"

```python
ModuleNotFoundError: No module named 'genius_pc'
```

**Causa:** Está em diretório errado.

**Solução:**

```powershell
cd "<caminho>\pc"
python main.py --demo
```

Certifique-se que está dentro da pasta `pc/`.

---

### ❌ Testes falhando

```
FAILED test_jogo.py - ...
FAILED test_protocolo.py - ...
```

**Causa:** Versão errada de pygame ou numpy.

**Solução:**

```powershell
pip install --upgrade pygame-ce>=2.5.0 numpy>=1.26 pyserial>=3.5
python -m unittest discover -s tests -v
```

---

## 🎮 PROBLEMAS COM O JOGO

### ❌ "Falha ao abrir a janela"

```
Falha ao abrir a janela: ...
```

**Causa:** Problema com vídeo ou SDL.

**Solução:**

1. **Atualize drivers de vídeo:**
   - NVIDIA, AMD ou Intel (conforme seu PC)

2. **Teste em modo headless:**
   ```powershell
   python main.py --teste --demo
   ```
   Deve mostrar: `Teste concluído: estado=ENTRADA rodada=1 quadros=241`

3. **Se funciona no modo teste:**
   - Problema é visual
   - Tente atualizar drivers

4. **Último recurso:**
   - Reinstale pygame-ce:
   ```powershell
   pip uninstall pygame-ce
   pip install pygame-ce>=2.5.0
   ```

---

### 🔇 Sem som no jogo

**Solução 1: Ativar som**
- Tecle `M` durante o jogo
- Deve piscar "SOM: ON" na tela

**Solução 2: Verificar volume**
- Verifique o volume do Windows (canto inferior)
- Verifique se está mudo

**Solução 3: Escolher dispositivo de áudio**
- Clique na barra de volume do Windows
- Escolha o dispositivo correto
- Reinicie o jogo

**Solução 4: Reinstalar pygame**
```powershell
pip uninstall pygame-ce
pip install pygame-ce>=2.5.0
```

---

### ⏱️ Jogo muito lento

**Solução:**

1. **Feche outros programas pesados:**
   - Chrome, Discord, OBS, etc.

2. **Verifique a performance:**
   ```powershell
   python main.py --teste --demo
   ```
   Se mostrar < 200 quadros, problema é mesmo no seu PC.

3. **Reduza qualidade gráfica:**
   - Jogo não tem opção, mas pode
   - Reduzir resolução do monitor
   - Ou rodar em tela menor

---

### 🕹️ Botões do Arduino não funcionam

**Se usou `--demo` ao invés de `--porta COM5`:**
```powershell
REM ERRADO
python main.py --demo

REM CORRETO
python main.py --porta COM5
```

**Se os botões não são reconhecidos:**

1. **Verifique a conexão:**
   - Os botões estão conectados ao Arduino?
   - D3, D5, D7, D9 têm fios?

2. **Teste a comunicação:**
   ```powershell
   python -c "
   from genius_pc.conexao import ConexaoSerial
   conexao = ConexaoSerial('COM5')
   if conexao.abrir():
       print('Serial OK')
       # Aperte botão e verifique a saída
       import time
       time.sleep(10)
   conexao.fechar()
   "
   ```
   Aperte os botões durante 10 segundos. Se aparecer `B0`, `B1`, etc, funcionam.

3. **Se não aparecer nada:**
   - Verifique fios (solto ou invertido)
   - Verifique alimentação (GND comum)
   - Teste em modo standalone do Arduino (sem PC)

---

### 💾 Recorde não persiste

Se o recorde não é salvo em `~/.genius_neon.json`:

1. **Permissões:**
   - Verifique se tem permissão de escrita em `C:\Users\<Usuário>\`

2. **Pasta:**
   - A pasta deve existir: `C:\Users\<Usuário>\`
   - Geralmente existe

3. **Teste manualmente:**
   ```powershell
   python -c "
   from pathlib import Path
   import json
   arquivo = Path.home() / '.genius_neon.json'
   print(f'Arquivo: {arquivo}')
   print(f'Existe: {arquivo.exists()}')
   # Tente escrever
   arquivo.write_text(json.dumps({'rodada': 5, 'pontuacao': 500}))
   print('Escrito com sucesso')
   "
   ```

---

## 📊 PROBLEMAS DE COMPILAÇÃO/UPLOAD

### ❌ "Sketch uses X bytes..."

Se a mensagem disser "100% of program storage space":

**Solução:** Seu firmware é muito grande.

- Verifique se tem código desnecessário
- Remova comentários longos
- Otimize arrays/strings

### ❌ "FQBN invalid"

```
FQBN 'arduino:avr:uno' is invalid
```

**Solução:**

```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" core list
```

Procure por `arduino:avr` na saída.

Se não aparecer:
```powershell
& "C:\Program Files\Arduino CLI\arduino-cli.exe" core install arduino:avr
```

---

## 🆘 ÚLTIMA OPÇÃO: Reset Completo

Se nada funcionar:

1. **Limpar Python:**
   ```powershell
   rmdir .venv /s
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Reprogramar Arduino:**
   ```powershell
   & "C:\Program Files\Arduino CLI\arduino-cli.exe" compile --fqbn arduino:avr:uno genius
   & "C:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM5 --fqbn arduino:avr:uno genius
   ```

3. **Reiniciar PC**

4. **Tente novamente:**
   ```powershell
   python main.py --porta COM5
   ```

---

## 📞 Ainda não funciona?

1. Rode os **testes:**
   ```powershell
   python -m unittest discover -s tests -v
   ```

2. Verifique **README.md** para detalhes técnicos

3. Verifique **AGENTS.md** para padrões do projeto

4. Crie uma **note com a mensagem de erro exata** e o seu **SO/hardware**

---

**Boa sorte! 🎮**
