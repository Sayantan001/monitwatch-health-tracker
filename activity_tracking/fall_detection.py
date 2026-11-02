"""
Threshold-based fall detection for MonitWatch (MPU6050 + optional SIM900 SMS alert).

Added after the hackathon as an extension of the motion-sensing module.

A fall is reported when this sequence is seen in the acceleration magnitude:
    1. free-fall   : magnitude drops below FREE_FALL_G
    2. impact      : magnitude exceeds IMPACT_G within IMPACT_WINDOW_S
    3. inactivity  : after a short settling time, the wearer stays still for STILL_TIME_S

Thresholds are starting values and should be tuned on real data.
"""
import math
import time

# ---- Tunable settings -------------------------------------------------------
SAMPLE_HZ = 50            # readings per second
FREE_FALL_G = 0.4         # magnitude below this = free-fall (in g)
IMPACT_G = 2.5            # magnitude above this = impact (in g)
IMPACT_WINDOW_S = 1.0     # max time between free-fall and impact
SETTLE_S = 0.5            # ignore the bounce right after the impact
STILL_TIME_S = 2.0        # how long the wearer must stay still after impact
STILL_STD_G = 0.15        # max variation (std dev) counted as "still"
STILL_MEAN_MIN_G = 0.8    # still = magnitude close to 1 g (device at rest)
STILL_MEAN_MAX_G = 1.3
ALERT_COOLDOWN_S = 60     # minimum time between two alerts
PHONE_NUMBER = "+00XXXXXXXXXX"  # set the number to text
# -----------------------------------------------------------------------------


def magnitude(ax, ay, az):
    """Length of the acceleration vector (in g when inputs are in g)."""
    return math.sqrt(ax * ax + ay * ay + az * az)


class FallDetector:
    IDLE, FREE_FALL, IMPACT = "IDLE", "FREE_FALL", "IMPACT"

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = self.IDLE
        self.t_state = 0.0
        self.still_samples = []

    def update(self, ax, ay, az, t):
        """Feed one reading (in g) with timestamp t (seconds).
        Returns True when a fall is confirmed."""
        mag = magnitude(ax, ay, az)

        if self.state == self.IDLE:
            if mag < FREE_FALL_G:
                self.state = self.FREE_FALL
                self.t_state = t

        elif self.state == self.FREE_FALL:
            if mag > IMPACT_G:
                self.state = self.IMPACT
                self.t_state = t
                self.still_samples = []
            elif t - self.t_state > IMPACT_WINDOW_S:
                self.reset()  # free-fall without an impact

        elif self.state == self.IMPACT:
            if t - self.t_state < SETTLE_S:
                return False  # still bouncing, do not judge yet
            self.still_samples.append(mag)
            if t - self.t_state >= SETTLE_S + STILL_TIME_S:
                n = len(self.still_samples)
                mean = sum(self.still_samples) / n
                std = math.sqrt(sum((m - mean) ** 2 for m in self.still_samples) / n)
                fell = std < STILL_STD_G and STILL_MEAN_MIN_G < mean < STILL_MEAN_MAX_G
                self.reset()
                return fell
        return False


def send_sms(port, message):
    """Send an SMS through the SIM900 GSM module (same commands as health_tracking/SMS.py)."""
    port.write(b"AT+CMGF=1\r")
    time.sleep(3)
    port.write(f'AT+CMGS="{PHONE_NUMBER}"\r'.encode())
    time.sleep(3)
    port.reset_output_buffer()
    time.sleep(1)
    port.write(str.encode(message + chr(26)))
    time.sleep(3)


def main():
    from mpu6050 import mpu6050  # needs the MPU6050 library on the Raspberry Pi

    mpu = mpu6050(0x68)
    detector = FallDetector()

    port = None
    try:
        import serial
        port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
    except Exception as err:
        print("GSM module not available, alerts will only be printed:", err)

    last_alert = 0.0
    print("Fall detection running. Press Ctrl+C to stop.")
    while True:
        a = mpu.get_accel_data(g=True)
        now = time.time()
        if detector.update(a["x"], a["y"], a["z"], now):
            print("Fall detected!")
            if now - last_alert > ALERT_COOLDOWN_S:
                last_alert = now
                if port is not None:
                    send_sms(port, "Fall detected by MonitWatch")
        time.sleep(1.0 / SAMPLE_HZ)


if __name__ == "__main__":
    main()
