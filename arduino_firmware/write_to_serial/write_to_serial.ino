/* Set these parameters based on your hardware setup */
int NUM_DEVLPRS = 1; 
int DEVLPR_PINS[] = {A0};
/*****************************************************/

unsigned long MICROS_PER_SAMPLE = 1000L;
unsigned long lastTickMicros = 0L;
unsigned long microsSinceEMG = 0L;
byte bufOut[4];
int emgValue;

void setup() {
    Serial.begin(2000000);
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
    emgValue = analogRead(pin);
    fillPacket(bufOut, normalizePin(pin), emgValue);
    Serial.write(bufOut, 4);
}
/*
void loop() {
    // how much time has passed since last loop
    unsigned long currMicros = micros();
    unsigned long microsDelta = currMicros - lastTickMicros;
    // accrue the micros since last
    microsSinceEMG += microsDelta;
    // see if enough have passed for our 1000Hz sampling
    if (microsSinceEMG >= MICROS_PER_SAMPLE) {
        // read all of the pins that were indicated
        for (int i = 0; i < NUM_DEVLPRS; i++) {
            writeEMG(DEVLPR_PINS[i]);
        }
        // and update the micros since
        microsSinceEMG = 0L;
    }
    // pretend no time has passed since function start to stay on schedule
    lastTickMicros = currMicros;
    // delay a few micros so we're not spinning as fast as possible
    delayMicroseconds(10);
}
*/

void loop() {
    for (byte p = 0; p < 6; p++) {
        for (int v = -1024; v < 1025; v++) {
            fillPacket(bufOut, p, v);
            Serial.write(bufOut, 4);
            delayMicroseconds(50);
        }
    }
    
}
