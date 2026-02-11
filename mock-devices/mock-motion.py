import requests
from datetime import datetime


# Simulated motion detection in the kitchen
def send_context():
    context = {
        "intent": {"command": "turn on", "object": "light", "location": "kitchen"},
        "user": {"id": "abc123", "preferences": {"language": "en"}},
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "handoff": {
            "from_device": "kitchen-motion-01",
            "to_device": "kitchen-light-01",
        },
    }

    print("📡 Sending context to light...")
    res = requests.post("http://127.0.0.1:5000/intent", json=context["intent"])
    print(f"💡 Light responded: {res.status_code}")
    print(res.json())


if __name__ == "__main__":
    send_context()
