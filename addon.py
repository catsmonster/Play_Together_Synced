import xbmc
import xbmcaddon
import xbmcgui
import os
import sys
addon_base_path = xbmcaddon.Addon().getAddonInfo('path')
lib_path = os.path.join(addon_base_path, 'resources', 'lib')
sys.path.append(lib_path)
from resources.lib.firebase_handler import cleanup_expired_tokens, generate_short_token
import threading
import time


def log_message(message, level=xbmc.LOGDEBUG):
    addon_id = xbmcaddon.Addon().getAddonInfo('id')
    xbmc.log(f'[{addon_id}] {message}', level)


def show_token_dialog(token, duration=300):
    def countdown():
        # Countdown logic in a separate thread
        for i in range(duration, 0, -1):
            time.sleep(1)
        cleanup_expired_tokens(duration-1)  # Delete expired tokens after countdown

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
    countdown_thread.join()  # Wait for the countdown thread to finish


# Usage

addon = xbmcaddon.Addon()
token = generate_short_token()
show_token_dialog(token, 300)
