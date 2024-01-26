import time
import requests
import json
import random
import string
from resources.lib.p2p_connection_handler import get_nat_type_and_external_address
import pyscrypt
import pyaes
import os
import base64

firebase_url = 'https://play-together-sync-default-rtdb.europe-west1.firebasedatabase.app/'


def generate_connection_details_payload():
    """Generate a JSON payload with the current time."""
    NAT_type, public_ip, external_port = get_nat_type_and_external_address()
    if public_ip is None:
        return None
    return {'public_ip': public_ip,
            'port': external_port}


def generate_token_and_send_to_firebase(length=6, connection_payload=None):
    """Generate a random alphanumeric token (lowercase and digits)."""
    characters = string.ascii_lowercase + string.digits
    generated_token = ''.join(random.choice(characters) for i in range(length))
    if token_exists_in_firebase(generated_token):
        return generate_token_and_send_to_firebase(length, connection_payload)
    encrypted_payload, salt = encrypt_with_salt(json.dumps(connection_payload), generated_token)
    encoded_data = base64.b64encode(encrypted_payload).decode('utf-8')
    encoded_salt = base64.b64encode(salt).decode('utf-8')
    data = {'timestamp': int(time.time()),  # Current Unix time in seconds',
            'payload': encoded_data,
            'secret_sauce': encoded_salt}  # Current Unix time in seconds
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


def derive_key(passphrase, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Generate a new 16-byte salt
    # Derive a 256-bit key using scrypt
    key = pyscrypt.hash(password=passphrase.encode('utf-8'), salt=salt, N=1024, r=1, p=1, dkLen=32)
    return key, salt


def encrypt_data(data, key):
    aes = pyaes.AESModeOfOperationCTR(key)
    encrypted_data = aes.encrypt(data)
    return encrypted_data


def decrypt_data(encrypted_data, key):
    aes = pyaes.AESModeOfOperationCTR(key)
    decrypted_data = aes.decrypt(encrypted_data)
    return decrypted_data.decode('utf-8')


def encrypt_with_salt(data, passphrase):
    key, salt = derive_key(passphrase)
    encrypted_data = encrypt_data(data, key)
    return encrypted_data, salt


def decrypt_with_salt(encrypted_data, passphrase, salt):
    key, _ = derive_key(passphrase, salt)
    decrypted_data = decrypt_data(encrypted_data, key)
    return decrypted_data


def get_token_payload(token):
    response = requests.get(f'{firebase_url}/tokens/{token}.json')
    data = response.json()

    # Check if the response contains the 'payload' key
    if 'payload' in data:
        salt = data['secret_sauce']
        salt_bytes = base64.b64decode(salt)
        encrypted_data_bytes = base64.b64decode(data['payload'])
        return json.loads(decrypt_with_salt(encrypted_data_bytes, token, salt_bytes))
    else:
        return None  # or handle the missing 'payload' case as needed
