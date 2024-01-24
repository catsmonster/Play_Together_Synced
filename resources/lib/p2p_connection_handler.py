import requests
import socket
import xbmcgui
from playback_control import await_partner_playback
import threading


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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ip, port))
        server_socket.listen()
        xbmcgui.Dialog().notification('Connection', f"Listening on {ip}:{port}")
        server_socket.settimeout(timeout_seconds)
        try:
            client_socket, addr = server_socket.accept()
            xbmcgui.Dialog().notification('Connection', f"Connected to {addr}")
            server_socket.close()
            await_playback_start_thread = threading.Thread(target=await_partner_playback, args=[client_socket])
            await_playback_start_thread.start()
        except socket.timeout:
            xbmcgui.Dialog().notification('Connection', f"Connection timed out")

        finally:
            server_socket.close()
            xbmcgui.Dialog().notification('Connection', f"Stopped listening on {ip}:{port}")


def join_p2p_session(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((ip, port))
            xbmcgui.Dialog().notification('Connection', f"Connected to {ip}:{port}")
            await_playback_start_thread = threading.Thread(target=await_partner_playback, args=[client_socket])
            await_playback_start_thread.start()
        except ConnectionRefusedError:
            xbmcgui.Dialog().notification('Connection', f"Connection refused")
        except TimeoutError:
            xbmcgui.Dialog().notification('Connection', f"Connection timed out")
        finally:
            client_socket.close()
            xbmcgui.Dialog().notification('Connection', f"Connection closed")
