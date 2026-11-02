# MonitWatch: Wearable Health & Activity Monitoring

A wearable prototype that measures heart rate, SpO2, ECG and body motion, uses machine learning to flag abnormal ECG signals and recognise human activity, and sends SMS alerts through a GSM module. It started as a hackathon project (HackTrix).

Built by Team HackTrix. Original team repository: [SayakRC3/HackTrix](https://github.com/SayakRC3/HackTrix).

![Circuit diagram](health_tracking/Circuit_Diagram.png)

## Contents

- [Features](#features)
- [System overview](#system-overview)
- [Hardware](#hardware)
- [Machine learning](#machine-learning)
- [Fall detection](#fall-detection)
- [Repository structure](#repository-structure)
- [Setup](#setup)
- [Limitations](#limitations)
- [Credits](#credits)

## Features

| Feature | How it works |
|---|---|
| Heart rate and SpO2 | MAX3010x pulse oximeter read by a Raspberry Pi |
| ECG acquisition | BioAmp EXG Pill with a filtered ECG signal |
| Vital-sign alerts | SMS sent when heart rate is outside 40-110 bpm for 5 consecutive readings |
| ECG anomaly detection | Autoencoder trained on normal beats; high reconstruction error means abnormal |
| Activity recognition | LSTM classifier for 6 activity classes, **86.9% test accuracy** |
| Fall detection | Threshold-based detector on MPU6050 data (added after the hackathon) |
| Cloud upload | ESP32 publishes sensor data to AWS IoT Core |
| Alerts | SIM900 GSM module sends SMS or places a call |

## System overview

```
Sensors ──► Raspberry Pi ──► ML models / threshold logic ──► SMS or call alert (SIM900 GSM)
(pulse ox, ECG, MPU6050)

Sensors ──► ESP32 ──► AWS IoT Core
```

The Raspberry Pi handles data collection, ML and alerts. The ESP32 handles the cloud connection.

## Hardware

- Raspberry Pi 4B
- ESP32-WROOM
- MAX3010x pulse oximeter and heart-rate sensor
- MPU6050 accelerometer and gyroscope
- BioAmp EXG Pill (ECG/EEG/EMG front end)
- SIM900 GSM module

![ECG circuit](health_tracking/ECG_Biopill_Circuit.png)

## Machine learning

### ECG anomaly detection (`ML/ECG_detection/`)

- Dense autoencoder (140 → 32 → 16 → 8 → 16 → 32 → 140), trained only on normal beats for 20 epochs with MAE loss.
- A beat is flagged abnormal when its reconstruction error exceeds the training mean plus one standard deviation.
- The notebook follows the public TensorFlow/Kaggle ECG anomaly-detection tutorial. The dataset is the public ECG dataset used there and is not included in this repo.

| Normal beat | Abnormal beat |
|---|---|
| ![Normal](ML/ECG_detection/Results/normal_data%2Bprediction.png) | ![Abnormal](ML/ECG_detection/Results/Abnormal_data%2B%20prediction.png) |

### Activity recognition (`ML/activity_tracking/`)

- One LSTM layer (50 units) followed by a softmax layer for 6 classes.
- Trained for 20 epochs on `HAR_new.csv`.
- Test accuracy: **86.9%**.

## Fall detection

`activity_tracking/fall_detection.py` reads the MPU6050 at 50 Hz and reports a fall when it sees this sequence in the acceleration magnitude:

1. **Free-fall:** magnitude drops below 0.4 g.
2. **Impact:** magnitude exceeds 2.5 g within 1 second.
3. **Inactivity:** after a short settling time, the wearer stays still for 2 seconds.

On a confirmed fall it prints a message and sends an SMS through the GSM module, with a 60-second cooldown between alerts. All thresholds are constants at the top of the file.

This module was added after the hackathon. The logic has been tested on simulated motion data only, so the thresholds are starting values that need tuning on real hardware.

## Repository structure

```
health_tracking/     pulse oximeter and ECG code, SMS and call scripts, circuit files
activity_tracking/   MPU6050 reading script, fall detection, circuit diagram
ML/                  ECG autoencoder, activity LSTM, result images
Cloud/               ESP32 to AWS IoT Core firmware
```

## Setup

**Raspberry Pi scripts**
1. Install `pyserial`, `RPi.GPIO`, and the MAX30100 and MPU6050 Python libraries.
2. In the SMS, call and alert scripts, set `PHONE_NUMBER` to your own number.
3. Run `python3 health_tracking/Sp02_BPM_Alert.py` for vital-sign alerts, or `python3 activity_tracking/fall_detection.py` for fall detection.

**Cloud firmware**
1. Copy `Cloud/secrets.example.h` to `Cloud/secrets.h`.
2. Fill in your Wi-Fi details, AWS IoT endpoint and device certificates.
3. `secrets.h` is ignored by Git and must never be committed.

**ML notebooks**
1. Install `numpy`, `pandas`, `scikit-learn`, `tensorflow` and `matplotlib`.
2. Run the notebook or script in each ML folder.

## Limitations

- Prototype built during a hackathon; not a medical device.
- Alert thresholds are fixed values and are not personalised.
- The ECG model was trained on a public dataset, not on data from this device.
- Fall detection is threshold-based and has not been validated on real falls. A device dropped on a table could trigger a false alarm.

## Credits

Team HackTrix. The ECG autoencoder is based on the public TensorFlow/Kaggle tutorial. Fall detection was added later by Sayantan Panda.
