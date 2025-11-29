# How to transform your Arduino into an Speech Emotion Recognition Device with Edge Impulse

Welcome to this tutorial of how to create your own Speech Emotion Recognition (SER) device, at the end of this tutorial you will know how to implement your own tiny machine learning model for speech emotion recognition and implement it in real life on your Arduino Nano 33 BLE sense rev2 with **Edge Impulse**. 

This tutorial is part of the **MADI PROJECT** submitted to the Edge Impulse competition of Hackearth. 

1. Required Materials
2. Database
3. Edge Impulse Steps
4. Conclusion

## Required Materials
- [Edge Impulse Account](https://edgeimpulse.com/)
- Arduino Nano 33 BLE Sense rev2
- USB A to Micro USB Cable
- (optional)  OV7675 Camera

## Database
The database utilized for training the speech emotion recognition model, is [CREMA-D](https://github.com/CheyneyComputerScience/CREMA-D) one of the most used database in the field of SER. For the porpouse of this proyect we selected the emotions of: Angry and Neutral. 

## Edge Impulse Steps

1. First, create your project and name it.

![1_a](https://github.com/user-attachments/assets/fab6a762-9ead-45da-8c09-ef6b6e25f8e7)

2. Select your Arduino BLE 33 in the target device
   
![1_b](https://github.com/user-attachments/assets/175e2e92-8468-4754-a08f-2846f3bfa369)

3.Upload 1024 excerpts from the “Angry” class of the CREMA-D database (selecting the first 1024 only) and label them as “Negative”, then upload the 1024 excerpts from the “Neutral” class and label them as “Neutral” to ensure a balanced dataset.

<img width="3104" height="1200" alt="2_a" src="https://github.com/user-attachments/assets/d930e261-cb30-4b43-b955-2301b2ad326e" alt="Wiring"/><br><br>

**Create Impulse**

4. Steps:
 - The original audio files are sampled at 48 kHz; we will resample them to 16 kHz to reduce computational cost and memory usage. This is done by the platform automatically when selecting the sample rate.
 - Emotions are detected through features that change over time. Our audio samples vary in length from 1 to 3 seconds; therefore, we selected a 1.5-second window size with a 0.5-second stride.
 - Enabled zero-padding to add zeros when the audio is shorter than the window size.
 - Click on “Add a processing block” and select MFE. The difference between MFCC and MFE is that MFCC emphasizes vocal-tract resonances that shape phonemes (better for word recognition), while MFE better captures energy and   paralinguistic cues important for emotion recognition.
 - Click on “Add a learning block”, select Classification. This model will allow us to differentiate between the “Neutral” and “Negative” classes.
   
<img width="3098" height="1302" alt="3_a" src="https://github.com/user-attachments/assets/a977a6ba-a918-4a49-b1e7-e0077feb60bc" alt="Wiring"/><br><br>

5. Check the MFE box to use them as input features and click on the "Save Impulse" button.
   
<img width="3098" height="1304" alt="3_b" src="https://github.com/user-attachments/assets/dba45ce8-e13d-40ee-80c1-645c0bda7789" alt="Wiring"/><br><br>

**MFE**

6. The platform will enable two new sections. Move to “MFE” and set the following parameters:

   - Increase the frame length to 0.032 to obtain 512 samples per frame (0.032 × 16000).

   - Set the frame stride to 0.016, which is half of the frame length.

   - Set the FFT size to 512 to match the frame length and the number of samples used in the FFT.

   - Since our sampling rate is 16 kHz, the maximum frequency analyzed will be 8 kHz, in accordance with the Nyquist theorem. This range is appropriate because emotion recognition requires more information than phoneme recognition, typically within the 400–4000 Hz range.

<img width="3004" height="1576" alt="4" src="https://github.com/user-attachments/assets/ff42858b-6724-41b5-a4c4-68711c3d48e6" alt="Wiring"/><br><br>

7. Once the parameters are saved, click on “Generate Features” and then click on the "Generate Features" button.
When the process finishes, you can view the Feature Explorer.
This is a two-dimensional mapping of the extracted features. Here, you can observe how separable your classes are, as well as the time required to generate the representation—in this case, 475 ms.

<img width="2784" height="1146" alt="4_b" src="https://github.com/user-attachments/assets/33661bcd-6257-4201-882d-92983a1fedcc" alt="Wiring"/><br><br>

**Classifier**

8. Move to “Classifier.”
Make sure to tick the Data augmentation checkbox. This will help your model generalize better to unseen data.
Click on the “Save & Train” button and wait for the training to finish.

<img width="1792" height="1726" alt="5_a" src="https://github.com/user-attachments/assets/2d9c5d10-7a97-4216-92d3-dad45ae1baec" alt="Wiring"/><br><br>

Once the training finishes, important information about the model will appear, such as the accuracy, loss, inference time, and RAM and flash usage.

<img width="1524" height="1436" alt="5_b" src="https://github.com/user-attachments/assets/bc9e77a5-4cac-4a2d-9542-1613619309e7" alt="Wiring"/><br><br>

**Live Classification**

9. For trying online your model:
   - Move to “Live Classification”
   - Click on the "Connect a development board" button
   - Click on "Connect to your computer"
   This will redirect you to a new tab.

<img width="2934" height="1060" alt="6_a" src="https://github.com/user-attachments/assets/9129d52e-39ba-4f53-9456-ea149cb703ee" alt="Wiring"/><br><br>

10. Give access to the microphone
    
<img width="1412" height="624" alt="6_b" src="https://github.com/user-attachments/assets/79ed4ecc-9956-4841-bd90-4e4b3c5b74a7" alt="Wiring"/><br><br>

11. Once in Data collection
    - Select the audio length
    - Select "Testing" for the split category
    - Click on "Start recording"
      
<img width="2136" height="532" alt="6_c" src="https://github.com/user-attachments/assets/5423f972-a906-44de-a7c4-32518055d343" alt="Wiring"/><br><br>

12. Return to the original tab. The results of each frame will be displayed.

<img width="1068" height="862" alt="6_d" src="https://github.com/user-attachments/assets/dc685b09-c6d7-412d-bed1-08c95f8406e5" alt="Wiring"/><br><br>

**Deployment**
13. Move to Deployment section
- Search the deployment option: Arduino Library
- Click on "Build"

<img width="2770" height="1204" alt="7_a" src="https://github.com/user-attachments/assets/e691c5b8-221c-4802-ae8a-4b3c4daecaca" alt="Wiring"/><br><br>

This will automatically download the library, and the next instructions will be displayed.

<img width="2730" height="1186" alt="7_b" src="https://github.com/user-attachments/assets/45969a6f-8e33-4926-bf9b-fc8109e05d93" />

Congratulations you have made your own Speech Emotion Recognition dectector! 

## Connection to the Jetson Orin Nano Super

There are two constrains to connect to the Jetson board.
1. The Jetson receive the emotional information in a Json format: {"id": "audio", "negative": "percentage_1", "neutral": "percentage_2"} where percentage_1 and percentage_2 represent the average prediction probabilities per class across all frames during the user’s speech.

2. To detect when the user starts and ends a question, a button was implemented, thus, our code must attend this interaction.

To accomplish these two constrains, we have to add the following code to the "SPEECH_EMOTION_RECOGNITION_-_MADI_PROJECT_inferencing" file downloaded in the excamples folder within the library.

Variables declaration:

```bash
const int BUTTON_PIN = 2;
bool lastPressed = false;
bool collecting = false;   // true while the button is pressed

// Accumulators for class probabilities
static float probs_sum[EI_CLASSIFIER_LABEL_COUNT];
static unsigned int sample_count = 0;
```
Whitin the setup function:

```bash
pinMode(BUTTON_PIN, INPUT);  // External pull-down
 for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        probs_sum[ix] = 0.0f;
    }

sample_count = 0;
collecting = false;
lastPressed = false;
```
Whitin the loop function:

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
















   
