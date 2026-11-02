# MonitWatch: Wearable Health & Activity Monitoring

A hackathon project (HackTrix) building a wearable that measures heart rate, SpO2, ECG and motion, and uses machine learning to flag abnormal ECG signals and recognise human activity. Alerts are sent by SMS or call through a GSM module.

Built by Team HackTrix. Original team repository: [SayakRC3/HackTrix](https://github.com/SayakRC3/HackTrix).

![Circuit diagram](health_tracking/Circuit_Diagram.png)

## What it does

- **Vital signs:** heart rate and SpO2 from a pulse oximeter; ECG from a BioAmp EXG Pill.
- **Alerts:** if the heart rate is outside 40-110 bpm for 5 consecutive readings, an SMS alert is sent through a SIM900 GSM module. A separate script can place a call.
- **Motion sensing:** an MPU6050 accelerometer and gyroscope reads body movement.
- **ECG anomaly detection:** an autoencoder is trained on normal heartbeats, and beats with a high reconstruction error are flagged as abnormal.
- **Activity recognition:** an LSTM classifies 6 activity classes from accelerometer and gyroscope features. Test accuracy: **86.9%**.
- **Cloud upload:** an ESP32 publishes sensor data to AWS IoT Core.

## Hardware

- Raspberry Pi 4B (data collection and ML)
- ESP32-WROOM (cloud connection)
- MAX3010x pulse oximeter and heart-rate sensor
- MPU6050 accelerometer and gyroscope
- BioAmp EXG Pill (ECG/EEG/EMG front end)
- SIM900 GSM module

![ECG circuit](health_tracking/ECG_Biopill_Circuit.png)

## Machine learning

**ECG anomaly detection** (`ML/ECG_detection/`)
- Dense autoencoder (140 → 32 → 16 → 8 → 16 → 32 → 140), trained on normal ECG beats only, 20 epochs, MAE loss.
- A beat is flagged abnormal when its reconstruction error exceeds the training mean plus one standard deviation.
- The notebook follows the public TensorFlow/Kaggle ECG anomaly-detection tutorial. The dataset is the public ECG dataset used there, and it is not included in this repo.

| Normal beat | Abnormal beat |
|---|---|
| ![Normal](ML/ECG_detection/Results/normal_data%2Bprediction.png) | ![Abnormal](ML/ECG_detection/Results/Abnormal_data%2B%20prediction.png) |

**Activity recognition** (`ML/activity_tracking/`)
- Single LSTM layer (50 units) followed by a softmax layer for 6 classes, trained for 20 epochs on `HAR_new.csv`.
- Test accuracy: 86.9%.

## Repository structure

- `health_tracking/` - pulse oximeter and ECG code, SMS/call scripts, Fritzing and circuit files
- `activity_tracking/` - MPU6050 reading script and circuit diagram
- `ML/` - ECG autoencoder and activity LSTM, with result images
- `Cloud/` - ESP32 to AWS IoT Core firmware

## Setup

1. **Raspberry Pi scripts:** install `pyserial`, `RPi.GPIO` and the MAX30100 and MPU6050 libraries. In the SMS and call scripts, set `PHONE_NUMBER` to your number.
2. **Cloud firmware:** copy `Cloud/secrets.example.h` to `Cloud/secrets.h` and fill in your Wi-Fi details, AWS IoT endpoint and device certificates. `secrets.h` is ignored by Git and must never be committed.
3. **ML notebooks:** install `numpy`, `pandas`, `scikit-learn`, `tensorflow` and `matplotlib`, then run the notebook or script in each ML folder.

## Limitations

- Prototype built during a hackathon, not a medical device.
- Alert thresholds are fixed values and not personalised.
- The ECG model was trained on a public dataset, not on data from this device.
- The motion script prints raw readings; fall detection is not implemented in this repo.

## Credits

Team HackTrix. ECG autoencoder based on the public TensorFlow/Kaggle tutorial.
