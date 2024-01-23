import threading
import time
from resources.lib import firebase_handler


def show_token_dialog(token, duration=300):
    def countdown():
        # Countdown logic in a separate thread
        for i in range(duration, 0, -1):
            time.sleep(1)
        firebase_handler.cleanup_expired_tokens(duration-1)  # Delete expired tokens after countdown

    # Start the countdown in a separate thread
    countdown_thread = threading.Thread(target=countdown)
    countdown_thread.start()

    countdown_thread.join()  # Wait for the countdown thread to finish


def test_token_dialog():
    generate_token = firebase_handler.generate_token_and_send_to_firebase()
    show_token_dialog(generate_token, 5)
