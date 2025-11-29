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
   
<img width="3096" height="1408" alt="1_a" src="https://github.com/user-attachments/assets/bfe51983-f8fe-4dd5-86a2-584541357873" alt="Wiring"/><br><br>

2. Select your Arduino BLE 33 in the target device
   
<img width="3098" height="1164" alt="1_b" src="https://github.com/user-attachments/assets/2bd55bec-579f-4729-8bf5-4ea9a906d691" alt="Wiring"/><br><br>

3.Upload 1024 excerpts from the “Angry” class of the CREMA-D database (selecting the first 1024 only) and label them as “Negative”, then upload the 1024 excerpts from the “Neutral” class and label them as “Neutral” to ensure a balanced dataset.

<img width="3104" height="1200" alt="2_a" src="https://github.com/user-attachments/assets/d930e261-cb30-4b43-b955-2301b2ad326e" alt="Wiring"/><br><br>

4. Create Impulse:
 - The original audio files are sampled at 48 kHz; we will resample them to 16 kHz to reduce computational cost and memory usage.
 - Emotions are detected through features that change over time. Our audio samples vary in length from 1 to 3 seconds; therefore, we selected a 1.5-second window size with a 0.5-second stride.
 - Enabled zero-padding to add zeros when the audio is shorter than the window size.
 - Click “Add a processing block” and select MFE. The difference between MFCC and MFE is that MFCC emphasizes vocal-tract resonances that shape phonemes (better for word recognition), while MFE better captures energy and   paralinguistic cues important for emotion recognition.
 - Click “Add a learning block”, select Classification. This model will allow us to differentiate between the “Neutral” and “Negative” classes.
   
<img width="3098" height="1302" alt="3_a" src="https://github.com/user-attachments/assets/a977a6ba-a918-4a49-b1e7-e0077feb60bc" alt="Wiring"/><br><br>

5. Check the MFE box to use them as input features and press the "Save Impulse" button.
   
<img width="3098" height="1304" alt="3_b" src="https://github.com/user-attachments/assets/dba45ce8-e13d-40ee-80c1-645c0bda7789" alt="Wiring"/><br><br>






















   
