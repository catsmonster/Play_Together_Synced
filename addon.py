import xbmcaddon
import xbmcgui
from resources.lib.firebase_handler import log_message, write_data_to_firebase, token_exists_in_firebase, \
    cleanup_expired_tokens
import random
import string
import threading
import time


def show_token_dialog(token, duration=300):
    def countdown():
        # Countdown logic in a separate thread
        for i in range(duration, 0, -1):
            time.sleep(1)
        cleanup_expired_tokens()  # Delete expired tokens after countdown

    dialog = xbmcgui.DialogProgress()
    dialog.create('Token Information')

    # Start the countdown in a separate thread
    countdown_thread = threading.Thread(target=countdown)
    countdown_thread.start()

    for i in range(duration, -1, -1):
        if dialog.iscanceled():  # Break the loop if user cancels the dialog
            break
        percent = int((duration - i) / duration * 100)
        mins, secs = divmod(i, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        message = f'Send this to the other partner: {token}\nExpires in: {time_format}'
        dialog.update(percent, message)
        time.sleep(1)

    dialog.close()


def generate_short_token(length=6):
    """Generate a random alphanumeric token (lowercase and digits)."""
    characters = string.ascii_lowercase + string.digits
    generated_token = ''.join(random.choice(characters) for i in range(length))
    return generated_token


# Generate a token
token = generate_short_token()
while token_exists_in_firebase(token):
    log_message('Token already exists in firebase, generating a new one')
    token = generate_short_token()

data = {'timestamp': int(time.time())}  # Current Unix time in seconds
write_data_to_firebase(token, data)

# Usage

addon = xbmcaddon.Addon()
show_token_dialog(token, 300)
