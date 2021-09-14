/* Set these parameters based on your hardware setup */
#define NUM_DEVLPRS 1
#define BAUD 2000000

int DEVLPR_PINS[] = {A0, A1, A2, A3, A4, A5};
int EMG_VALS[NUM_DEVLPRS];
/*****************************************************/

#define BASE_PIN 8
unsigned long MICROS_PER_SAMPLE = 1000L;
unsigned long lastTickMicros = 0L;
unsigned long microsSinceEMG = 0L;
byte bufOut[4];
volatile int emgValue;
volatile bool new_msg = false;

ISR(TIMER0_COMPA_vect) {  // Timer0 interrupt, 2kHz
    if (!new_msg) {
      for (int i = 0; i < NUM_DEVLPRS; i++) {
        EMG_VALS[i] = analogRead(DEVLPR_PINS[i]);
      }
      new_msg = true;
    }
}

void setup() {
    int base_pin = 8;
    for (int i = 0; i < NUM_DEVLPRS; i++) {
       pinMode(base_pin + i, OUTPUT);
    }
    
    cli();  // Stop interrupts
    //set timer0 interrupt at 2kHz
    TCCR0A = 0;// set entire TCCR2A register to 0
    TCCR0B = 0;// same for TCCR2B
    TCNT0  = 0;//initialize counter value to 0
    // set compare match register for 2khz increments
    OCR0A = 124;// = (16*10^6) / (2000*64) - 1 (must be <256)

    // OCR0A = 249;  // 8kHz
    // turn on CTC mode
    TCCR0A |= (1 << WGM01);

    // TCCR0B |= (1 << CS00);  // 8kHz
    
    // Set CS01 and CS00 bits for 64 prescaler
    TCCR0B |= (1 << CS01) | (1 << CS00);   
    // enable timer compare interrupt
    TIMSK0 |= (1 << OCIE0A);
    sei();  // Start interrupts

    Serial.begin(BAUD);
    //Serial.println();
}

/* Safety check in case the alias of A0-A5 isn't directly mapped to the number
 we expect */
byte normalizePin(int analogPin) {
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
void fillPacket(byte *buffOut, byte pin, int value) {
    // pack 16-bits for the emg value and 4 bits for the pin into
    // three bytes in the following fashion (e=emg, p=pin)
    // eeee eee0
    // eeee eee0
    // eepp pp00
    // and terminate with a 1
    // 0000 0001
    buffOut[0] = (value >> 8) & 0xFE;
    buffOut[1] = (value >> 1) & 0xFE;
    buffOut[2] = ((value << 6) & 0xC0) | ((pin << 2) & 0x3C);
    buffOut[3] = 0x01;
}

void writeEMG(int pin) {
//    emgValue = analogRead(pin);
//    fillPacket(bufOut, normalizePin(pin), emgValue);
//    Serial.write(bufOut, 4);

}

void loop() {
    if (new_msg) {
      for (int i = 0; i < NUM_DEVLPRS; i++) {
        fillPacket(bufOut, normalizePin(DEVLPR_PINS[i]), EMG_VALS[i]);
        Serial.write(bufOut, 4);
//        digitalWrite(BASE_PIN + i, HIGH);
//        digitalWrite(BASE_PIN + i, LOW);
      }
      new_msg = false;
    }
    // how much time has passed since last loop
    // unsigned long currMicros = micros();
    // unsigned long microsDelta = currMicros - lastTickMicros;
    // // accrue the micros since last
    // microsSinceEMG += microsDelta;
    // // see if enough have passed for our 1000Hz sampling
    // if (microsSinceEMG >= MICROS_PER_SAMPLE) {
    //     // read all of the pins that were indicated
    //     for (int i = 0; i < NUM_DEVLPRS; i++) {
    //         writeEMG(DEVLPR_PINS[i]);
    //     }
    //     // and update the micros since
    //     microsSinceEMG = 0L;
    // }
    // // pretend no time has passed since function start to stay on schedule
    // lastTickMicros = currMicros;
    // // delay a few micros so we're not spinning as fast as possible
    // delayMicroseconds(10);
}
