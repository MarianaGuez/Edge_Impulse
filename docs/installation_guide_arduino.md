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

![2_a](https://github.com/user-attachments/assets/72a6a294-0bab-42d5-86ef-ad17519b88b9)

**Create Impulse**

4. Steps:
 - The original audio files are sampled at 48 kHz; we will resample them to 16 kHz to reduce computational cost and memory usage. This is done by the platform automatically when selecting the sample rate.
 - Emotions are detected through features that change over time. Our audio samples vary in length from 1 to 3 seconds; therefore, we selected a 1.5-second window size with a 0.5-second stride.
 - Enabled zero-padding to add zeros when the audio is shorter than the window size.
 - Click on “Add a processing block” and select MFE. The difference between MFCC and MFE is that MFCC emphasizes vocal-tract resonances that shape phonemes (better for word recognition), while MFE better captures energy and   paralinguistic cues important for emotion recognition.
 - Click on “Add a learning block”, select Classification. This model will allow us to differentiate between the “Neutral” and “Negative” classes.
   
![3_a](https://github.com/user-attachments/assets/518befa7-bfb4-4f7f-bbb7-0ac427d58e49)

5. Check the MFE box to use them as input features and click on the "Save Impulse" button.
   
![3_b](https://github.com/user-attachments/assets/870bd8be-11e5-464a-a42c-48beef1ee139)

**MFE**

6. The platform will enable two new sections. Move to “MFE” and set the following parameters:

   - Increase the frame length to 0.032 to obtain 512 samples per frame (0.032 × 16000).

   - Set the frame stride to 0.016, which is half of the frame length.

   - Set the FFT size to 512 to match the frame length and the number of samples used in the FFT.

   - Since our sampling rate is 16 kHz, the maximum frequency analyzed will be 8 kHz, in accordance with the Nyquist theorem. This range is appropriate because emotion recognition requires more information than phoneme recognition, typically within the 400–4000 Hz range.

![4_a](https://github.com/user-attachments/assets/4926d9a8-39be-4e3d-a4f2-40b1849900b8)

7. Once the parameters are saved, click on “Generate Features” and then click on the "Generate Features" button.
When the process finishes, you can view the Feature Explorer.
This is a two-dimensional mapping of the extracted features. Here, you can observe how separable your classes are, as well as the time required to generate the representation—in this case, 475 ms.

![4_b](https://github.com/user-attachments/assets/33b00006-b3fb-4bdf-8c3a-ab38742cf527)

**Classifier**

8. Move to “Classifier.”
Make sure to tick the Data augmentation checkbox. This will help your model generalize better to unseen data.
Click on the “Save & Train” button and wait for the training to finish.

![5_a](https://github.com/user-attachments/assets/104823d8-7e83-4f53-ad07-8c2b6eb062a6)

Once the training finishes, important information about the model will appear, such as the accuracy, loss, inference time, and RAM and flash usage.
![5_b](https://github.com/user-attachments/assets/5225d808-4a81-437a-960e-d0688366822a)

**Live Classification**

9. For trying online your model:
   - Move to “Live Classification”
   - Click on the "Connect a development board" button
   - Click on "Connect to your computer"
   This will redirect you to a new tab.

![6_a](https://github.com/user-attachments/assets/e4530efd-6736-4489-b394-c92aed21e3f2)

10. Give access to the microphone

![6_b](https://github.com/user-attachments/assets/0a26507b-a3d9-41ca-9e5c-a2a2f369d695) 

11. Once in Data collection
    - Select the audio length
    - Select "Testing" for the split category
    - Click on "Start recording"
      
![6_c](https://github.com/user-attachments/assets/0c5bf2d6-cbbd-4812-ab3b-ba63224c8608)

12. Return to the original tab. The results of each frame will be displayed.

![6_d](https://github.com/user-attachments/assets/5492fde7-8b19-4b30-aea6-9eb2be7f89d3)

**Deployment**
13. Move to Deployment section
- Search the deployment option: Arduino Library
- Click on "Build"

![7_a](https://github.com/user-attachments/assets/f7e67772-4b44-4994-a862-1c80a2e06b89)

This will automatically download the library, and the next instructions will be displayed.

![7_b](https://github.com/user-attachments/assets/c0d8f757-c5b3-4f03-b4fe-0e3cd54fef2c)


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
















   
