import xbmc
import xbmcaddon
import os
import sys
addon_base_path = xbmcaddon.Addon().getAddonInfo('path')
lib_path = os.path.join(addon_base_path, 'resources', 'lib')
sys.path.append(lib_path)
import requests
import json

firebase_url = 'https://play-together-sync-default-rtdb.europe-west1.firebasedatabase.app/'
# Writing Data to Firebase
data = {'name': 'John Doe', 'location': 'City'}
response = requests.put(firebase_url + 'users/john_doe.json', json.dumps(data))
if response.status_code == 200:
    xbmc.log("Data written successfully")
else:
    xbmc.log("Failed to write data")

# Reading Data from Firebase
response = requests.get(firebase_url + 'users/john_doe.json')
if response.status_code == 200:
    data = response.json()
    xbmc.log(f'The added data is:\n{data}')
else:
    xbmc.log("Failed to read data")




def log_message(message, level=xbmc.LOGDEBUG):
    addon_id = xbmcaddon.Addon().getAddonInfo('id')
    xbmc.log(f'[{addon_id}] {message}', level)

