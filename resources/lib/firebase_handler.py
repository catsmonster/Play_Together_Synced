import time
import requests
import json
import random
import string

firebase_url = 'https://play-together-sync-default-rtdb.europe-west1.firebasedatabase.app/'


def generate_payload_json():
    """Generate a JSON payload with the current time."""
    return json.dumps({'timestamp': int(time.time())})



def generate_short_token(length=6):
    """Generate a random alphanumeric token (lowercase and digits)."""
    characters = string.ascii_lowercase + string.digits
    generated_token = ''.join(random.choice(characters) for i in range(length))
    if token_exists_in_firebase(generated_token):
        return generate_short_token(length)
    data = {'timestamp': int(time.time())}  # Current Unix time in seconds
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
