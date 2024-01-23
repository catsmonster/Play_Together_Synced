import requests
import socket
import json
import xbmcgui


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


def start_listening(ip, port, timeout_seconds=300):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    xbmcgui.Dialog().notification('Connection', f"Listening on {ip}:{port}")
    server_socket.settimeout(timeout_seconds)
    try:
        client_socket, addr = server_socket.accept()
        xbmcgui.Dialog().notification('Connection', f"Connected to {addr}")
        # Remove the timeout after the first connection
        client_socket.settimeout(None)
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Client disconnected

            message = data.decode()
            xbmcgui.Dialog().notification('Connection', f"Received: {message}")
            if message == "STOP":
                xbmcgui.Dialog().notification('Connection', f"Stopping connection")
                break

        client_socket.close()
    except socket.timeout:
        xbmcgui.Dialog().notification('Connection', f"Connection timed out")

    finally:
        server_socket.close()
        xbmcgui.Dialog().notification('Connection', f"Stopped listening on {ip}:{port}")


def send_connection_information_to_host(host_ip, host_port, client_public_ip, client_port):
    message = {
        'client_ip': client_public_ip,
        'client_port': client_port
    }
    message_json = json.dumps(message)

    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to the server
            sock.connect((host_ip, host_port))

            # Send the message
            sock.sendall(message_json.encode())

            # Optionally, receive a response back from the server
            # response = sock.recv(1024)
            # print("Received:", response.decode())

    except Exception as e:
        print(f"Error sending message to host: {e}")