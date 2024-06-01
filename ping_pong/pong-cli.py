import sys
import requests

# Configurable URLs for the instances
INSTANCE_1_URL = "http://localhost:8001"
INSTANCE_2_URL = "http://localhost:8002"

def send_command(command, param=None):
    url = INSTANCE_1_URL  # Assuming we always control the game from instance 1
    if command == "start":
        response = requests.get(f"{url}/start/{param}")
    elif command == "pause":
        response = requests.get(f"{url}/pause")
    elif command == "resume":
        response = requests.get(f"{url}/resume")
    elif command == "stop":
        response = requests.get(f"{url}/stop")
    else:
        print("Invalid command")
        return
    
    if response.status_code == 200:
        print("Command executed successfully:", response.json())
    else:
        print("Failed to execute command:", response.status_code, response.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pong-cli.py <command> [<param>]")
        sys.exit(1)
    
    command = sys.argv[1]
    param = sys.argv[2] if len(sys.argv) > 2 else None
    send_command(command, param)
