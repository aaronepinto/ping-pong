import requests
import sys

if len(sys.argv) < 2:
    print("Usage: python pong-cli.py <command> [param]")
    sys.exit(1)

command = sys.argv[1]

base_url = "http://localhost:8001"  # Adjust as needed for your setup

if command == "start":
    if len(sys.argv) != 3:
        print("Usage: python pong-cli.py start <pong_time_ms>")
        sys.exit(1)
    pong_time_ms = int(sys.argv[2])
    response = requests.get(f"{base_url}/start/{pong_time_ms}")
elif command == "pause":
    response = requests.get(f"{base_url}/pause")
elif command == "resume":
    response = requests.get(f"{base_url}/resume")
elif command == "stop":
    response = requests.get(f"{base_url}/stop")
else:
    print("Unknown command")
    sys.exit(1)

print(response.json())
