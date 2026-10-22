# 📚 Índice de Documentação — Genius Neon

Todos os documentos do projeto em um só lugar.

---

## 🚀 COMECE AQUI

### 📄 [COMECE_AQUI.md](COMECE_AQUI.md)
**Para:** Quem quer instalar em 15 minutos  
**Contém:** Passos simples e diretos para Arduino + Python + jogo  
**Tempo:** ~15 minutos

---

## 📖 INSTALAÇÃO COMPLETA

### 📄 [INSTALACAO.md](INSTALACAO.md)
**Para:** Instalação detalhada passo a passo  
**Contém:**
- Arduino CLI (com driver CH340)
- Core AVR
- Python e dependências
- Upload do firmware
- Testes e validação
- Hardware e pinagem
- Protocolo serial

**Tempo:** ~1 hora

---

## ✅ CHECKLISTS

### 📄 [CHECKLIST_SETUP.md](CHECKLIST_SETUP.md)
**Para:** Verificar se tudo foi instalado corretamente  
**Contém:**
- Arduino Setup (CLI, hardware, firmware)
- Python Setup (ambiente, dependências)
- Testes
- Hardware conectado
- Validação final

**Uso:** Marque itens conforme completar

---

## 🎯 DEPLOY

### 📄 [DEPLOY.md](DEPLOY.md)
**Para:** Fazer deploy do projeto completo  
**Contém:**
- Estado atual
- Compilação do firmware
- Upload no Arduino
- Preparação do cliente Python
- Validações pré-deploy
- Checklist de deploy

**Tempo:** ~30 minutos

---

## 🔧 PROBLEMAS?

### 📄 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
**Para:** Resolver problemas comuns  
**Contém:**
- Arduino não encontrado
- Porta ocupada
- Firmware não responde
- Sem som
- Testes falhando
- Hardware não funciona
- Reset completo

**Uso:** Procure seu problema no índice

---

## 📚 TÉCNICA E REFERÊNCIA

### 📄 [README.md](README.md)
**Para:** Overview do projeto  
**Contém:**
- Estrutura do projeto
- Como começar rápido
- Verificação

### 📄 [pc/README.md](pc/README.md)
**Para:** Documentação técnica do cliente pygame  
**Contém:**
- Hardware (pinagem)
- Firmware (modos, comandos)
- Cliente Python (requisitos, opções CLI)
- Controles
- Funcionamento do jogo
- Protocolo serial
- Testes
- Estrutura de código
- Troubleshooting específico

### 📄 [AGENTS.md](AGENTS.md)
**Para:** Padrões e regras do projeto  
**Contém:**
- Estrutura do repositório
- Comandos essenciais
- Firmware (pinos, timings, protocolo)
- Cliente Python (arquitetura, regras)

---

## 🗂️ ESTRUTURA DO PROJETO

```
Genius Neon/
│
├── 📄 COMECE_AQUI.md              ← START HERE (15 min)
├── 📄 INSTALACAO.md               ← Instalação detalhada (1h)
├── 📄 CHECKLIST_SETUP.md          ← Validação
├── 📄 DEPLOY.md                   ← Passo a passo de deploy (30 min)
├── 📄 TROUBLESHOOTING.md          ← Resolver problemas
├── 📄 DOCUMENTACAO.md             ← Este arquivo
│
├── 📄 README.md                   ← Overview
├── 📄 AGENTS.md                   ← Padrões do projeto
│
├── genius/
│   └── genius.ino                 ← Firmware (Arduino)
│
├── pc/
│   ├── 📄 README.md               ← Docs técnicas do Python
│   ├── main.py                    ← CLI
│   ├── requirements.txt           ← Dependências
│   ├── genius_pc/
│   │   ├── jogo.py               ← Lógica pura
│   │   ├── app.py                ← UI/pygame
│   │   ├── conexao.py            ← Serial
│   │   ├── audio.py              ← Som
│   │   └── protocolo.py          ← Parser
│   └── tests/
│       ├── test_jogo.py
│       ├── test_protocolo.py
│       └── test_conexao.py
```

---

## 🎯 Roteiros Rápidos

### Instalação (novo PC)
1. Leia: **COMECE_AQUI.md**
2. Ou detalhado: **INSTALACAO.md**
3. Verifique: **CHECKLIST_SETUP.md**

### Problema durante setup
1. Procure em: **TROUBLESHOOTING.md**
2. Ou leia: **INSTALACAO.md** (seção correspondente)

### Fazer deploy novo
1. Siga: **DEPLOY.md**
2. Valide: **CHECKLIST_SETUP.md**

### Entender o código
1. Leia: **README.md** (overview)
2. Depois: **pc/README.md** (técnica)
3. Depois: **AGENTS.md** (padrões)

### Programar/modificar
1. Firmware: **AGENTS.md** (seção Firmware)
2. Python: **pc/README.md** (estrutura)
3. Testes: **AGENTS.md** (comandos)

---

## 📊 Comparação de Documentos

| Doc | Nível | Tempo | Para | Detalhe |
|-----|-------|-------|------|---------|
| COMECE_AQUI | Iniciante | 15 min | Instalação rápida | ⭐⭐⭐ |
| INSTALACAO | Intermediário | 1h | Passo a passo completo | ⭐⭐⭐⭐ |
| CHECKLIST | Iniciante | 10 min | Validação | ⭐⭐⭐ |
| DEPLOY | Intermediário | 30 min | Fazer deploy | ⭐⭐⭐⭐ |
| TROUBLESHOOTING | Intermediário | 5 min/problema | Resolver erros | ⭐⭐⭐⭐⭐ |
| README | Intermediário | 10 min | Overview | ⭐⭐⭐ |
| pc/README | Avançado | 30 min | Técnica Python | ⭐⭐⭐⭐⭐ |
| AGENTS | Avançado | 20 min | Padrões/desenvolvimento | ⭐⭐⭐⭐ |

---

## 🎓 Curva de Aprendizado

### Apenas Jogar
- Leia: **COMECE_AQUI.md**
- Tempo: 15-30 min

### Instalar + Jogar
- Leia: **COMECE_AQUI.md** ou **INSTALACAO.md**
- Use: **CHECKLIST_SETUP.md**
- Tempo: 30 min - 2h

### Modificar o jogo
- Leia: **pc/README.md**
- Leia: **AGENTS.md**
- Tempo: 2-4h

### Desenvolver features
- Leia: **AGENTS.md** (tudo)
- Leia: **pc/README.md** (tudo)
- Entenda: Cada arquivo em `pc/genius_pc/`
- Tempo: 4-8h

---

## 🆘 Matriz de Troubleshooting

| Problema | Documento | Seção |
|----------|-----------|-------|
| Arduino não encontrado | TROUBLESHOOTING | ❌ Arduino não encontrado |
| Porta ocupada | TROUBLESHOOTING | ❌ Porta ocupada |
| Firmware não responde | TROUBLESHOOTING | ⚠️ Firmware não responde |
| Sem som | TROUBLESHOOTING | 🔇 Sem som |
| Python não funciona | TROUBLESHOOTING | 🐍 Problemas com Python |
| Teste falhando | TROUBLESHOOTING | Testes falhando |
| Upload não funciona | INSTALACAO | Passo 2.4 |
| Pygame não abre | TROUBLESHOOTING | ❌ Falha ao abrir janela |

---

## 📞 Como Usar Esta Documentação

### Se você é...

**Iniciante:**
1. Comece: **COMECE_AQUI.md**
2. Se der erro: **TROUBLESHOOTING.md**
3. Dúvidas técnicas: **INSTALACAO.md**

**Intermediário:**
1. Leia: **INSTALACAO.md** (completo)
2. Use: **CHECKLIST_SETUP.md** (validar)
3. Se erro: **TROUBLESHOOTING.md**

**Desenvolvedor:**
1. Leia: **README.md** + **AGENTS.md**
2. Estude: **pc/README.md**
3. Explore: código em `pc/genius_pc/`

**Mantedor:**
1. Leia: **AGENTS.md** (padrões)
2. Use: **DEPLOY.md** (para deploy)
3. Consulte: **pc/README.md** (técnica)

---

## 🔄 Versionamento

Última atualização: **22 de outubro de 2026**

### Versões dos Softwares Testados:
- Arduino CLI: **1.5.1**
- Arduino AVR core: **1.8.8**
- Python: **3.12.10**
- pygame-ce: **2.5.8**
- pyserial: **3.5**
- numpy: **2.5.3**

---

## 🎯 Checklist Final

- [ ] Li **COMECE_AQUI.md**
- [ ] Arduino CLI está instalado
- [ ] Firmware foi feito upload
- [ ] Python e dependências instaladas
- [ ] Jogo abre e funciona
- [ ] Testes passam (15/15)
- [ ] Hardware (LEDs, botões, som) funciona

**Status:** ✅ **PRONTO PARA JOGAR**

---

**Divirta-se! 🎮✨**
