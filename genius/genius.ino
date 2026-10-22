/*
 * Genius — modo standalone + ponte serial para o cliente pygame.
 *
 * Protocolo (ASCII, uma linha por comando, 115200 8N1):
 *   Arduino -> PC : READY, OK REMOTO, OK STANDALONE, B0..B3
 *   PC -> Arduino : M1 (modo remoto), M0 (standalone), A (tudo off)
 *                   L<i>,<ms> (LED), T<i>,<ms> (tom); duração 0 desliga
 *
 * No boot o sketch espera 3,5 s por M1. Se ninguém falar com ele, começa
 * o jogo standalone. M1 interrompe o standalone a qualquer momento.
 */

#include <stdlib.h>
#include <string.h>

// ---------------- pinos e tons ----------------
const uint8_t PINO_AUDIO = 12;
const uint8_t PINOS_LEDS[4] = {2, 4, 6, 8};
const uint8_t PINOS_BOTOES[4] = {3, 5, 7, 9};
const int TONS[4] = {880, 440, 392, 294};

const unsigned long ESPERA_SERIAL_MS = 3500;
const unsigned long DEBOUNCE_MS = 25;

// ---------------- estado ----------------
enum Modo { MODO_AGUARDANDO, MODO_REMOTO, MODO_STANDALONE };
Modo modo = MODO_AGUARDANDO;
unsigned long inicioAguardando = 0;

// jogo standalone
int sequencia[100];
int rodada_atual = 0;
int passo_atual = 0;
bool perdeu_o_jogo = false;

// botões com debounce
bool leituraAnterior[4] = {HIGH, HIGH, HIGH, HIGH};
bool estadoBotoes[4] = {HIGH, HIGH, HIGH, HIGH};
unsigned long mudancaBotoes[4] = {0, 0, 0, 0};
int botao_evento = -1;

// saídas comandadas pelo PC
bool ledAceso[4] = {false, false, false, false};
unsigned long ledApagaEm[4] = {0, 0, 0, 0};
bool tomAtivo = false;
unsigned long tomApagaEm = 0;

// linha serial
char bufferSerial[32];
uint8_t tamanhoBuffer = 0;

// ---------------- protótipos ----------------
void atualizarBotoes();
void processarSerial();
void executarComando(char *comando);
void entrarRemoto();
void iniciarStandalone();
void desligarTudo();
void acenderLed(uint8_t indice, unsigned long duracao);
void tocarTom(uint8_t indice, unsigned long duracao);
void atualizarSaidasRemotas();
bool delayJogo(unsigned long ms);
void executarJogoStandalone();
void reiniciarJogo();
void proximaRodada();
bool reproduzirSequencia();
bool aguardarJogador();
int consumirBotao();
bool gameOver();
bool tocarSomDeInicio();

// ---------------- setup / loop ----------------
void setup() {
  for (uint8_t i = 0; i < 4; i++) {
    pinMode(PINOS_LEDS[i], OUTPUT);
    digitalWrite(PINOS_LEDS[i], LOW);
  }
  for (uint8_t i = 0; i < 4; i++) {
    pinMode(PINOS_BOTOES[i], INPUT_PULLUP);
  }
  pinMode(PINO_AUDIO, OUTPUT);
  digitalWrite(PINO_AUDIO, LOW);

  Serial.begin(115200);
  randomSeed(analogRead(0));
  inicioAguardando = millis();
  Serial.println(F("READY"));
}

void loop() {
  atualizarBotoes();
  processarSerial();

  switch (modo) {
    case MODO_AGUARDANDO:
      if (millis() - inicioAguardando >= ESPERA_SERIAL_MS) {
        iniciarStandalone();
      }
      break;

    case MODO_REMOTO:
      atualizarSaidasRemotas();
      break;

    case MODO_STANDALONE:
      executarJogoStandalone();
      break;
  }
}

// ---------------- botões e serial ----------------
void atualizarBotoes() {
  unsigned long agora = millis();
  for (uint8_t i = 0; i < 4; i++) {
    bool leitura = digitalRead(PINOS_BOTOES[i]);
    if (leitura != leituraAnterior[i]) {
      leituraAnterior[i] = leitura;
      mudancaBotoes[i] = agora;
    }
    if ((agora - mudancaBotoes[i]) >= DEBOUNCE_MS &&
        leitura != estadoBotoes[i]) {
      estadoBotoes[i] = leitura;
      if (leitura == LOW) {
        if (modo == MODO_REMOTO) {
          Serial.print(F("B"));
          Serial.println(i);
        } else if (modo == MODO_STANDALONE) {
          botao_evento = i;
        }
      }
    }
  }
}

void processarSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      bufferSerial[tamanhoBuffer] = '\0';
      if (tamanhoBuffer > 0) {
        executarComando(bufferSerial);
      }
      tamanhoBuffer = 0;
    } else if (c != '\r') {
      if (tamanhoBuffer < sizeof(bufferSerial) - 1) {
        bufferSerial[tamanhoBuffer++] = c;
      } else {
        tamanhoBuffer = 0;  // linha longa: descarta
      }
    }
  }
}

void executarComando(char *comando) {
  if (comando[0] == 'M') {
    if (comando[1] == '1') {
      if (modo != MODO_REMOTO) {
        entrarRemoto();
      } else {
        Serial.println(F("OK REMOTO"));
      }
    } else if (comando[1] == '0') {
      if (modo != MODO_STANDALONE) {
        iniciarStandalone();
      } else {
        Serial.println(F("OK STANDALONE"));
      }
    }
    return;
  }

  if (comando[0] == 'P') {
    Serial.println(F("PONG"));
    return;
  }

  if (modo != MODO_REMOTO) {
    return;
  }
  if (comando[0] == 'A') {
    desligarTudo();
    return;
  }
  if ((comando[0] == 'L' || comando[0] == 'T') && comando[2] == ',') {
    int indice = comando[1] - '0';
    if (indice < 0 || indice > 3) {
      return;
    }
    unsigned long duracao = strtoul(comando + 3, NULL, 10);
    if (comando[0] == 'L') {
      acenderLed((uint8_t)indice, duracao);
    } else {
      tocarTom((uint8_t)indice, duracao);
    }
  }
}

// ---------------- modos ----------------
void entrarRemoto() {
  desligarTudo();
  botao_evento = -1;
  modo = MODO_REMOTO;
  Serial.println(F("OK REMOTO"));
}

void iniciarStandalone() {
  desligarTudo();
  reiniciarJogo();
  modo = MODO_STANDALONE;
  Serial.println(F("OK STANDALONE"));
}

void desligarTudo() {
  for (uint8_t i = 0; i < 4; i++) {
    digitalWrite(PINOS_LEDS[i], LOW);
    ledAceso[i] = false;
  }
  noTone(PINO_AUDIO);
  tomAtivo = false;
}

void acenderLed(uint8_t indice, unsigned long duracao) {
  if (duracao == 0) {
    digitalWrite(PINOS_LEDS[indice], LOW);
    ledAceso[indice] = false;
    return;
  }
  digitalWrite(PINOS_LEDS[indice], HIGH);
  ledAceso[indice] = true;
  ledApagaEm[indice] = millis() + duracao;
}

void tocarTom(uint8_t indice, unsigned long duracao) {
  if (duracao == 0) {
    noTone(PINO_AUDIO);
    tomAtivo = false;
    return;
  }
  tone(PINO_AUDIO, TONS[indice]);
  tomAtivo = true;
  tomApagaEm = millis() + duracao;
}

void atualizarSaidasRemotas() {
  unsigned long agora = millis();
  for (uint8_t i = 0; i < 4; i++) {
    if (ledAceso[i] && (long)(agora - ledApagaEm[i]) >= 0) {
      digitalWrite(PINOS_LEDS[i], LOW);
      ledAceso[i] = false;
    }
  }
  if (tomAtivo && (long)(agora - tomApagaEm) >= 0) {
    noTone(PINO_AUDIO);
    tomAtivo = false;
  }
}

// Espera em fatias curtas para continuar ouvindo o PC (M1/M0).
bool delayJogo(unsigned long ms) {
  unsigned long inicio = millis();
  while (millis() - inicio < ms) {
    atualizarBotoes();
    processarSerial();
    if (modo != MODO_STANDALONE) {
      return false;
    }
    delay(5);
  }
  return true;
}

int consumirBotao() {
  int indice = botao_evento;
  botao_evento = -1;
  return indice;
}

// ---------------- jogo standalone ----------------
void executarJogoStandalone() {
  if (perdeu_o_jogo) {
    reiniciarJogo();
  }
  if (rodada_atual == 0) {
    if (!tocarSomDeInicio()) {
      return;
    }
  }
  proximaRodada();
  if (!reproduzirSequencia()) {
    return;
  }
  if (!aguardarJogador()) {
    return;
  }
  delayJogo(1000);
}

void reiniciarJogo() {
  memset(sequencia, 0, sizeof(sequencia));
  rodada_atual = 0;
  passo_atual = 0;
  perdeu_o_jogo = false;
  botao_evento = -1;
}

void proximaRodada() {
  if (rodada_atual >= 100) {
    reiniciarJogo();
  }
  sequencia[rodada_atual++] = random(0, 4);
}

bool reproduzirSequencia() {
  for (int i = 0; i < rodada_atual; i++) {
    int indice = sequencia[i];
    tone(PINO_AUDIO, TONS[indice]);
    digitalWrite(PINOS_LEDS[indice], HIGH);
    if (!delayJogo(500)) {
      desligarTudo();
      return false;
    }
    noTone(PINO_AUDIO);
    digitalWrite(PINOS_LEDS[indice], LOW);
    if (!delayJogo(100)) {
      desligarTudo();
      return false;
    }
  }
  noTone(PINO_AUDIO);
  return true;
}

bool aguardarJogador() {
  for (int i = 0; i < rodada_atual; i++) {
    botao_evento = -1;
    int indice = -1;
    while (indice < 0) {
      atualizarBotoes();
      processarSerial();
      if (modo != MODO_STANDALONE) {
        return false;
      }
      indice = consumirBotao();
      if (indice < 0) {
        delay(5);
      }
    }

    tone(PINO_AUDIO, TONS[indice]);
    digitalWrite(PINOS_LEDS[indice], HIGH);
    if (!delayJogo(300)) {
      desligarTudo();
      return false;
    }
    digitalWrite(PINOS_LEDS[indice], LOW);
    noTone(PINO_AUDIO);

    if (sequencia[passo_atual] != indice) {
      return gameOver();
    }
    passo_atual++;
  }
  passo_atual = 0;
  return true;
}

bool gameOver() {
  for (uint8_t i = 0; i < 4; i++) {
    tone(PINO_AUDIO, TONS[i]);
    digitalWrite(PINOS_LEDS[i], HIGH);
    if (!delayJogo(200)) {
      desligarTudo();
      return false;
    }
    digitalWrite(PINOS_LEDS[i], LOW);
    noTone(PINO_AUDIO);
  }

  tone(PINO_AUDIO, TONS[3]);
  for (uint8_t i = 0; i < 4; i++) {
    for (uint8_t p = 0; p < 4; p++) {
      digitalWrite(PINOS_LEDS[p], HIGH);
    }
    if (!delayJogo(100)) {
      desligarTudo();
      return false;
    }
    for (uint8_t p = 0; p < 4; p++) {
      digitalWrite(PINOS_LEDS[p], LOW);
    }
    if (!delayJogo(100)) {
      desligarTudo();
      return false;
    }
  }
  noTone(PINO_AUDIO);
  perdeu_o_jogo = true;
  return true;
}

bool tocarSomDeInicio() {
  tone(PINO_AUDIO, TONS[0]);
  for (uint8_t i = 0; i < 4; i++) {
    digitalWrite(PINOS_LEDS[i], HIGH);
  }
  if (!delayJogo(500)) {
    desligarTudo();
    return false;
  }
  for (uint8_t i = 0; i < 4; i++) {
    digitalWrite(PINOS_LEDS[i], LOW);
  }
  if (!delayJogo(500)) {
    desligarTudo();
    return false;
  }
  noTone(PINO_AUDIO);
  return true;
}
