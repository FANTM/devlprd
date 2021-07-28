#include "Libdevlpr.h"

#define PACK(pin, data) ((((pin) & 0x000F) << 12) | ((data) & 0x0FFF))

/* Set these parameters based on your hardware setup */
int NUM_DEVLPRS = 1; 
int DEVLPR_PINS[] = {A0};
/*****************************************************/

const int MAX_RESULTS = 2;
volatile int results [MAX_RESULTS];
volatile int resultNumber;

unsigned long lastTickMicros = 0L;
unsigned long microsSinceEMG = 0L;
Devlpr dev(A0, FILTER_60HZ);
void printEMG(Devlpr *d);

void setup() {
    Serial.begin(2000000);
    Serial.println();
    dev.scheduleFunction(printEMG, 1);
}

/* Safety check in case the alias of A0-A5 isn't directly mapped to the number
 we expect */
uint8_t normalize_pin(int analogPin) {
    switch (analogPin)
    {
    case A0:
        return 0;
    case A1:
        return 1;
    case A2:
        return 2;
    case A3:
        return 3;
    case A4:
        return 4;
    case A5:
        return 5;
    default:
        return 0xff;
    }
}

/* Helper function for formatting data in the way that the daemon expects */
void fill_packet(uint8_t *buffOut, uint8_t pin, uint16_t data) {
    uint16_t payload = PACK(pin, data);
    buffOut[0] = ((payload & 0xFF00) >> 8) & 0x00FF;
    buffOut[1] = payload & 0xFF;
    buffOut[2] = '\r';
    buffOut[3] = '\n';
}

void printEMG(Devlpr *d) {
  int filtered = d->windowPeakToPeakAmplitude(true);
  uint8_t buffOut[4];
  fill_packet(buffOut, normalize_pin(A0), (uint16_t) filtered);
  Serial.write(buffOut, 4);
}

void loop() {
    dev.tick();
}
