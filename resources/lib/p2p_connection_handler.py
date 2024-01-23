import requests
import socket


def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None


def get_dynamic_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to your host and a port of 0
    s.bind(('', 0))

    # Get the dynamically assigned port
    port = s.getsockname()[1]

    # Don't forget to close the socket
    s.close()

    return port

