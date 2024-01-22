import xbmc
import xbmcaddon
import os
import sys
import time
addon_base_path = xbmcaddon.Addon().getAddonInfo('path')
lib_path = os.path.join(addon_base_path, 'resources', 'lib')
sys.path.append(lib_path)
import requests
import json

firebase_url = 'https://play-together-sync-default-rtdb.europe-west1.firebasedatabase.app/'


def token_exists_in_firebase(token):
    cleanup_expired_tokens()
    response = requests.get(firebase_url + f'tokens/{token}.json')
    if response.status_code == 200:
        data = response.json()
        if data is not None:
            return True
    return False


def write_data_to_firebase(token, data):
    response = requests.put(firebase_url + f'tokens/{token}.json', json.dumps(data))
    if response.status_code == 200:
        return True
    return False


def cleanup_expired_tokens(expiration_seconds=300):
    current_time = int(time.time())
    response = requests.get(f'{firebase_url}/tokens.json')
    tokens = response.json()

    if tokens:
        for token, data in tokens.items():
            if current_time - data['timestamp'] > expiration_seconds:
                requests.delete(f'{firebase_url}/tokens/{token}.json')


def log_message(message, level=xbmc.LOGDEBUG):
    addon_id = xbmcaddon.Addon().getAddonInfo('id')
    xbmc.log(f'[{addon_id}] {message}', level)
