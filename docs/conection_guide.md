# Connection to the Jetson Orin Nano Super

To establish communication between the Arduino and the Jetson Orin Nano Super, we must consider three key factors. First, the Jetson Orin Nano receives emotional information in a JSON format: {"id": "audio", "negative": "percentage_1", "neutral": "percentage_2"}, where percentage_1 and percentage_2 represent the average prediction probabilities for each class across all frames during the user’s speech. Second, a button has been integrated to trigger audio capture when the user speaks. Finally, while full error handling will be implemented in future work, for now all unused commands must be commented out to prevent the transmission of unsupported messages to the Jetson.

For addressing these two points, we must make some modifications in the "SPEECH_EMOTION_RECOGNITION_-_MADI_PROJECT_inferencing" file downloaded whitin the examples folder of the library created in the [arduino guide](./installation_guide_arduino.md).

## Code 

**Variables declaration:**

```bash
const int BUTTON_PIN = 2;
bool lastPressed = false;
bool collecting = false;   // true while the button is pressed

// Accumulators for class probabilities
static float probs_sum[EI_CLASSIFIER_LABEL_COUNT];
static unsigned int sample_count = 0;
```
**Whitin the setup function:**

```bash
pinMode(BUTTON_PIN, INPUT);  // External pull-down
 for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        probs_sum[ix] = 0.0f;
    }

sample_count = 0;
collecting = false;
lastPressed = false;
```
**Whitin the loop function:**

```bash
// -----------------------------
    // 1) Read button and manage states
    // -----------------------------
    bool pressed = (digitalRead(BUTTON_PIN) == HIGH);

    // Rising edge: NOT pressed -> PRESSED
    if (pressed && !lastPressed) {
        collecting = true;
        sample_count = 0;

        for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
            probs_sum[ix] = 0.0f;
        }

        // ei_printf(">> START window (button PRESSED)\n");
    }

    // Falling edge: PRESSED -> NOT pressed
    if (!pressed && lastPressed) {
        if (collecting && sample_count > 0) {

            // Compute and send final JSON result 

            Serial.print("{\"id\":\"audio\"");

            // Compute per-class average and print JSON
            for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {

                // Average probability for this specific class
                float avg = probs_sum[ix] / (float)sample_count;

                Serial.print(",\"");
                Serial.print(ei_classifier_inferencing_categories[ix]); // class name
                Serial.print("\":");
                Serial.print(avg, 4);  // 4 decimal precision
            }

            Serial.println("}");
        }

        // Reset state when button is released
        collecting = false;
    }

    lastPressed = pressed;

    // ALWAYS-ON inference

if (collecting) {
        sample_count++;
        for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
            probs_sum[ix] += result.classification[ix].value;
        }
    }

```

## Physical Connections:
![schematic](https://github.com/user-attachments/assets/216a378f-1113-4a4d-a70b-579feef916ed)
