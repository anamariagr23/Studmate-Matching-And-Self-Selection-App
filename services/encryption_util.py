from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=dotenv_path)

# Get the encryption key from the environment variables
key = os.getenv('ENCRYPTION_KEY')
if not key:
    raise ValueError(f"No encryption key found in environment variables. Looking in: {dotenv_path}")

cipher_suite = Fernet(key.encode())

def encrypt_message(message: str) -> str:
    encrypted_text = cipher_suite.encrypt(message.encode('utf-8'))
    return encrypted_text.decode('utf-8')

def decrypt_message(encrypted_message: str) -> str:
    decrypted_text = cipher_suite.decrypt(encrypted_message.encode('utf-8'))
    return decrypted_text.decode('utf-8')
