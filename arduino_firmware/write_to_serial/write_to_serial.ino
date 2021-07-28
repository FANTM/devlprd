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
const unsigned long MICROS_SCHED_EMG = 500L;  // 2k Hz
Devlpr dev(A0, FILTER_60HZ);
void printEMG(Devlpr *d);

//// ADC complete ISR
//ISR (ADC_vect)
//  {
//  if (resultNumber >= MAX_RESULTS)
//    ADCSRA = 0;  // turn off ADC
//  else
//    results [resultNumber++] = ADC;
//  }  // end of ADC_vect
//  
// EMPTY_INTERRUPT (TIMER1_COMPB_vect);

void serial_hack() {
  // reset Timer 1
  TCCR1A  = 0;
  TCCR1B  = 0;
  TCNT1   = 0;
  TCCR1B  = bit (CS11) | bit (WGM12);  // CTC, prescaler of 8
  TIMSK1  = bit (OCIE1B); 
  OCR1A   = 39;    
  OCR1B   = 39; // 20 uS - sampling frequency 50 kHz

  ADCSRA  =  bit (ADEN) | bit (ADIE) | bit (ADIF); // turn ADC on, want interrupt on completion
  ADCSRA |= bit (ADPS2);  // Prescaler of 16
  ADMUX   = bit (REFS0) | (normalize_pin(DEVLPR_PINS[0]) & 7);
  ADCSRB  = bit (ADTS0) | bit (ADTS2);  // Timer/Counter1 Compare Match B
  ADCSRA |= bit (ADSC); // bit (ADATE);   // turn on automatic triggering
}

void setup() {
    Serial.begin(115200);
    Serial.println();
    // serial_hack();
    dev.scheduleFunction(printEMG, 400);
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
//    // how much time has passed since last loop
//    unsigned long currMicros = micros();
//    unsigned long microsDelta = currMicros - lastTickMicros;
//    // accrue micros since last tick
//    microsSinceEMG += microsDelta;
//    // check if we need to write
//    if (microsSinceEMG >= MICROS_SCHED_EMG) {
//        // read and write
//        for (int i = 0; i < NUM_DEVLPRS; i++) {
//            uint8_t pin = normalize_pin(DEVLPR_PINS[i]);
//            uint16_t emgVal = analogRead(DEVLPR_PINS[i]);
//            uint8_t buffOut[4];
//            fill_packet(buffOut, pin, emgVal);
//            Serial.write(buffOut, 4);
//        }
//        // and update the micros since
//        microsSinceEMG = 0L;
//    }
//    // pretend no time has passed for best effort timing
//    lastTickMicros = currMicros;
}
