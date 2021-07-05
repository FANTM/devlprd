#define PACK(pin, data) ((((pin) & 0x000F) << 12) | ((data) & 0x0FFF))

/* Set these parameters based on your hardware setup */
int NUM_DEVLPRS = 1; 
int DEVLPR_PINS[] = {A0};
/*****************************************************/

unsigned long lastTickMicros = 0L;
unsigned long microsSinceEMG = 0L;
const unsigned long MICROS_SCHED_EMG = 500L;  // 2k Hz

void setup() {
    Serial.begin(2000000);
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

void loop() {
    // how much time has passed since last loop
    unsigned long currMicros = micros();
    unsigned long microsDelta = currMicros - lastTickMicros;
    // accrue micros since last tick
    microsSinceEMG += microsDelta;
    // check if we need to write
    if (microsSinceEMG >= MICROS_SCHED_EMG) {
        // read and write
        for (int i = 0; i < NUM_DEVLPRS; i++) {
            uint8_t pin = normalize_pin(DEVLPR_PINS[i]);
            uint16_t emgVal = analogRead(DEVLPR_PINS[i]);
            uint8_t buffOut[4];
            fill_packet(buffOut, pin, emgVal);
            Serial.write(buffOut, 4);
        }
        // and update the micros since
        microsSinceEMG = 0L;
    }
    // pretend no time has passed for best effort timing
    lastTickMicros = currMicros;
}
