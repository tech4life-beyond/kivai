from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/intent", methods=["POST"])
def handle_intent():
    data = request.get_json()

    # If the data is a list, unwrap the first element
    if isinstance(data, list):
        data = data[0]  # Unwrap if it's a list

    print("INCOMING DATA:", data)

    command = data.get("command")
    obj = data.get("object")
    location = data.get("location")

    if command == "turn on" and obj == "light":
        response = {
            "status": "success",
            "message": f"Light turned on in {location}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "device_id": f"{location.replace(' ', '-')}-light-01",
        }
    else:
        response = {
            "status": "error",
            "message": "Unsupported command",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    return jsonify(response)


if __name__ == "__main__":
    app.run(port=5000)
