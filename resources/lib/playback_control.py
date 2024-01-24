import socket
import time
import xbmc
import json


class SynchronizedPlayer(xbmc.Player):
    def __init__(self, client_socket):
        super(SynchronizedPlayer, self).__init__()
        self.client_socket = client_socket
        self.playback_started = False

    def pause(self, send_message=True):
        # Overloaded pause function
        super(SynchronizedPlayer, self).pause()  # Call the original pause function
        if send_message:
            # Send a message to the other client only if send_message is True
            self.send_message_to_client({"event": "pause"})

    def onPlayBackStarted(self):
        self.pause(send_message=False)  # Pause playback without sending a message
        # Get the current playback time
        start_time = self.getTime()
        self.playback_started = True
        message = {"event": "playback_started", "start_time": start_time}
        self.send_message_to_client(message)
        xbmc.log(f"Playback started at {start_time} seconds.", xbmc.LOGINFO)

    def send_message_to_client(self, message):
        try:
            # Convert the dictionary to a JSON string and then encode it
            message_json = json.dumps(message)
            self.client_socket.sendall(message_json.encode())
        except Exception as e:
            xbmc.log(f"Error sending message to client: {e}", xbmc.LOGERROR)


def await_partner_playback(client_socket):
    partner_started_playing = False
    player = SynchronizedPlayer(client_socket)
    message = None
    while not partner_started_playing or not player.playback_started:
        try:
            client_socket.settimeout(1.0)  # Adjust timeout as needed
            message = client_socket.recv(1024).decode()
            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                xbmc.log(f"Error decoding message: {message}", xbmc.LOGERROR)
                continue
            if message.event == "playback_started":
                partner_started_playing = True
                xbmc.log("Partner playback has started.", xbmc.LOGINFO)
        except socket.timeout:
            continue  # Continue waiting
        except Exception as e:
            xbmc.log(f"Error receiving playback start message: {e}", xbmc.LOGERROR)
            break
    if partner_started_playing and player.playback_started:
        synced_start_time = min(message.start_time, player.getTime())
        player.seekTime(synced_start_time)
        time.sleep(1)  # Wait for the seek to finish
