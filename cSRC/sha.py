import hashlib
import os
import binascii


def generate_salt():
    return os.urandom(16)


def encrypt(password, salt=None, iterations=100000, key_length=32):
    if salt is None:
        salt = generate_salt()
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, key_length
    )
    return {
        "salt": binascii.hexlify(salt).decode("utf-8"),
        "encription": binascii.hexlify(key).decode("utf-8"),
    }


# Function to verify a password against the stored hash
def verify(stored_salt_hex, stored_key_hex, password, iterations=100000, key_length=32):
    stored_salt = binascii.unhexlify(stored_salt_hex.encode("utf-8"))
    stored_key = binascii.unhexlify(stored_key_hex.encode("utf-8"))
    key_to_check = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), stored_salt, iterations, key_length
    )
    return key_to_check == stored_key
