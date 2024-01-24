import xbmc
import xbmcaddon
import xbmcgui
import os
import sys
addon_base_path = xbmcaddon.Addon().getAddonInfo('path')
lib_path = os.path.join(addon_base_path, 'resources', 'lib')
sys.path.append(lib_path)
from resources.lib.firebase_handler import cleanup_expired_tokens, generate_token_and_send_to_firebase, \
    get_token_payload, generate_connection_details_payload
import threading
import time
import pyxbmct
from resources.lib.p2p_connection_handler import start_listening, join_p2p_session


def show_join_dialog():
    # Create an instance of the Dialog class
    dialog = xbmcgui.Dialog()

    # Show an input box and get the user input
    # The input type xbmcgui.INPUT_ALPHANUM allows alphanumeric input
    user_input = dialog.input("Enter Join Information", type=xbmcgui.INPUT_ALPHANUM)

    # Check if the user canceled the dialog
    if user_input:
        # User clicked OK and entered some text
        connection_information_json = get_token_payload(user_input)
        if connection_information_json is None:
            xbmcgui.Dialog().notification('Join Info', 'Invalid token')
        else:
            ip_address = connection_information_json['public_ip']
            port = connection_information_json['port']
            if ip_address is None or port is None:
                xbmcgui.Dialog().notification('Join Info', 'Error loading connection information')
            else:
                xbmcgui.Dialog().notification('Join Info', f'IP: {ip_address}, Port: {port}')
                join_p2p_session(ip_address, port)
    else:
        # User clicked Cancel
        xbmcgui.Dialog().notification('Join Info', 'Canceled')


class JoinOrCreateDialog(pyxbmct.AddonDialogWindow):
    def __init__(self, title="Choose to join or create a session"):
        super(JoinOrCreateDialog, self).__init__(title)
        self.setGeometry(400, 200, 4, 2)
        self.set_controls()
        self.set_navigation()

    def set_controls(self):
        self.button_join = pyxbmct.Button("Join")
        self.placeControl(self.button_join, 1, 0)
        self.button_create = pyxbmct.Button("Create")
        self.placeControl(self.button_create, 1, 1)
        self.connect(self.button_join, self.on_join_clicked)
        self.connect(self.button_create, self.on_create_clicked)

    def set_navigation(self):
        # Set up navigation between controls
        self.button_join.setNavigation(self.button_create, self.button_create, self.button_create, self.button_create)
        self.button_create.setNavigation(self.button_join, self.button_join, self.button_join, self.button_join)

        # Set the initial focus
        self.setFocus(self.button_create)

    def on_join_clicked(self):
        # Handle Join button click
        show_join_dialog()
        self.close()

    def on_create_clicked(self):
        # Handle Create button click
        timeout = 60
        connection_payload = generate_connection_details_payload()
        public_ip = connection_payload['public_ip']
        port = connection_payload['port']
        token = generate_token_and_send_to_firebase(6, connection_payload)
        listen_thread = threading.Thread(target=start_listening, args=("0.0.0.0", port, timeout))
        listen_thread.start()
        token_dialog_thread = threading.Thread(target=show_token_dialog, args=(token, timeout))
        token_dialog_thread.start()
        self.close()


def log_message(message, level=xbmc.LOGDEBUG):
    addon_id = xbmcaddon.Addon().getAddonInfo('id')
    xbmc.log(f'[{addon_id}] {message}', level)


def show_token_dialog(token, duration=300):
    def countdown():
        # Countdown logic in a separate thread
        for i in range(duration, 0, -1):
            time.sleep(1)
        cleanup_expired_tokens(duration - 1)  # Delete expired tokens after countdown

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
# Create and show the dialog
my_dialog = JoinOrCreateDialog()
my_dialog.doModal()
del my_dialog
