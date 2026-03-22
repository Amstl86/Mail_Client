"""
Модуль для безопасного хранения паролей.
Использует системное хранилище ключей (keyring) для хранения главного ключа шифрования.
Пароли шифруются с помощью Fernet (симметричное шифрование).
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring

# Идентификатор приложения для keyring
APP_NAME = "MailClient"
KEY_RING_NAME = "master_key"

def get_or_create_master_key() -> bytes:
    """
    Получает главный ключ шифрования из системного хранилища.
    Если ключа нет, генерирует новый и сохраняет.
    
    Returns:
        bytes: главный ключ (base64-encoded для Fernet)
    """
    # Пытаемся получить ключ из keyring
    key = keyring.get_password(APP_NAME, KEY_RING_NAME)
    if key is None:
        # Генерируем новый ключ
        key = Fernet.generate_key().decode('utf-8')
        keyring.set_password(APP_NAME, KEY_RING_NAME, key)
    return key.encode('utf-8')

def encrypt_password(password: str) -> str:
    """
    Шифрует пароль с использованием главного ключа.
    
    Args:
        password (str): пароль в открытом виде
        
    Returns:
        str: зашифрованный пароль (base64-строка)
    """
    key = get_or_create_master_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_password(encrypted_password: str) -> str:
    """
    Расшифровывает пароль.
    
    Args:
        encrypted_password (str): зашифрованный пароль
        
    Returns:
        str: исходный пароль
    """
    key = get_or_create_master_key()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_password.encode('utf-8'))
    return decrypted.decode('utf-8')