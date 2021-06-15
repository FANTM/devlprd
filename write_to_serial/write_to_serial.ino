void setup() {
    Serial.begin(2000000);
}

int emgPin = A0;
unsigned long lastTickMicros = 0L;
unsigned long microsSinceEMG = 0L;
const unsigned long MICROS_SCHED_EMG = 1000L;
void loop() {
    // how much time has passed since last loop
    unsigned long currMicros = micros();
    unsigned long microsDelta = currMicros - lastTickMicros;
    // accrue micros since last tick
    microsSinceEMG += microsDelta;
    // check if we need to write
    if (microsSinceEMG >= MICROS_SCHED_EMG) {
        // read and write
        int emgVal = analogRead(emgPin);
        Serial.println(emgVal);
        // and update the micros since
        microsSinceEMG = 0L;
    }
    // pretend no time has passed for best effort timing
    lastTickMicros = currMicros;
}
