import time
import requests
import json
import random
import string
from resources.lib.p2p_connection_handler import get_public_ip, get_dynamic_port

firebase_url = 'https://play-together-sync-default-rtdb.europe-west1.firebasedatabase.app/'


def generate_connection_details_payload():
    """Generate a JSON payload with the current time."""
    public_ip = get_public_ip()
    if public_ip is None:
        return None
    dynamic_port = get_dynamic_port()
    if dynamic_port is None:
        return None
    return {'public_ip': public_ip,
            'port': dynamic_port}


def generate_token_and_send_to_firebase(length=6, connection_payload=None):
    """Generate a random alphanumeric token (lowercase and digits)."""
    characters = string.ascii_lowercase + string.digits
    generated_token = ''.join(random.choice(characters) for i in range(length))
    if token_exists_in_firebase(generated_token):
        return generate_token_and_send_to_firebase(length, connection_payload)
    encrypted_payload = xor_encrypt_decrypt(json.dumps(connection_payload), generated_token)
    data = {'timestamp': int(time.time()),  # Current Unix time in seconds',
            'payload': encrypted_payload}  # Current Unix time in seconds
    write_data_to_firebase(generated_token, data)
    return generated_token


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


def xor_encrypt_decrypt(data, key):
    key = str(key)
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))


def get_token_payload(token):
    response = requests.get(f'{firebase_url}/tokens/{token}.json')
    data = response.json()

    # Check if the response contains the 'payload' key
    if 'payload' in data:
        return json.loads(xor_encrypt_decrypt(data['payload'], token))
    else:
        return None  # or handle the missing 'payload' case as needed

#
# # Example usage
# json_data = {
#     "key1": "value1",
#     "key2": "value2"
# }
#
# # Convert JSON to string
# json_str = json.dumps(json_data)
#
# # Encrypt
# encrypted = xor_encrypt_decrypt(json_str, key)
#
# # Decrypt
# decrypted = xor_encrypt_decrypt(encrypted, key)
#
# # Convert string back to JSON
# json_decrypted = json.loads(decrypted)
