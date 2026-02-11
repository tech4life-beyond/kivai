import argparse
import requests
import json

# Define the endpoint and headers
url = "http://127.0.0.1:5000/intent"  # Update the URL if needed
headers = {"Content-Type": "application/json"}


# Function to send a request to the /intent endpoint
def send_request(command, obj, location, temperature=None):
    data = {
        "command": command,
        "object": obj,
        "location": location,
    }
    if command == "set temperature" and obj == "thermostat":
        data["temperature"] = temperature

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Setting up the argument parser for CLI
def main():
    parser = argparse.ArgumentParser(description="Kivai Protocol CLI Demo")

    parser.add_argument(
        "command",
        choices=["set temperature", "turn on", "turn off"],
        help="The command to execute",
    )
    parser.add_argument(
        "object",
        choices=["thermostat", "light", "motion"],
        help="The object to control",
    )
    parser.add_argument(
        "location", help="The location of the device (e.g., kitchen, living room)"
    )
    parser.add_argument(
        "--temperature",
        type=int,
        help="The temperature for the thermostat (only for 'set temperature' command)",
    )

    args = parser.parse_args()

    send_request(args.command, args.object, args.location, args.temperature)


if __name__ == "__main__":
    main()
