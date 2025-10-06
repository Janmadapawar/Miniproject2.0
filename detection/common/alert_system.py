import pyttsx3
import time
import threading

class AlertSystem:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 160)
        self.engine.setProperty("volume", 1.0)

        # 🕒 Last alert times to prevent spamming
        self.last_alert_time = {}
        self.cooldown = 3  # seconds (minimum time between same alerts)

    def _speak(self, message):
        """Run TTS in a separate thread so it doesn’t block detection."""
        def run():
            self.engine.say(message)
            self.engine.runAndWait()
        threading.Thread(target=run, daemon=True).start()

    def play_alert(self, alert_type):
        """Trigger alert based on violation type with cooldown."""
        now = time.time()

        # Prevent repeating the same alert too frequently
        if alert_type in self.last_alert_time:
            if now - self.last_alert_time[alert_type] < self.cooldown:
                return  # skip repeating too soon

        self.last_alert_time[alert_type] = now

        # 🗣️ Define all alert messages here
        messages = {
            "no_helmet": "Warning! No helmet detected.",
            "emergency_vehicle": "Emergency vehicle detected. Changing signal to green.",
            "triple_riding": "Triple riding detected. Please follow traffic rules.",
            "wrong_way": "Wrong direction driving detected.",
            "overspeeding": "Over speeding detected. Please slow down."
        }

        # Log alert event
        print(f"[ALERT] ({alert_type}) → {messages.get(alert_type, 'Unknown alert')}")

        # Speak the alert
        self._speak(messages.get(alert_type, "Alert triggered."))

