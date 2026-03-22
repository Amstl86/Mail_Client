"""
Управление учётными записями почтовых ящиков.
Хранит настройки (серверы, порты, логин) и зашифрованные пароли.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional
from ..utils.crypto_utils import encrypt_password, decrypt_password

CONFIG_DIR = os.path.expanduser("~/.mail_client")
ACCOUNTS_FILE = os.path.join(CONFIG_DIR, "accounts.json")

@dataclass
class Account:
    """Учётная запись почтового ящика."""
    email: str
    password_encrypted: str  # зашифрованный пароль
    imap_server: str
    imap_port: int
    smtp_server: str
    smtp_port: int
    use_ssl: bool = True  # всегда True для IMAP/SMTP over SSL
    
    def get_password(self) -> str:
        """Расшифровывает и возвращает пароль."""
        return decrypt_password(self.password_encrypted)
    
    @staticmethod
    def create(email: str, password: str, imap_server: str, imap_port: int,
               smtp_server: str, smtp_port: int) -> 'Account':
        """Создаёт новый аккаунт, шифруя пароль."""
        encrypted = encrypt_password(password)
        return Account(
            email=email,
            password_encrypted=encrypted,
            imap_server=imap_server,
            imap_port=imap_port,
            smtp_server=smtp_server,
            smtp_port=smtp_port
        )

class AccountManager:
    """Менеджер учётных записей: загрузка, сохранение, поиск."""
    
    def __init__(self):
        self.accounts: List[Account] = []
        self._ensure_config_dir()
        self.load()
    
    def _ensure_config_dir(self):
        """Создаёт папку конфигурации, если её нет."""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, mode=0o700)  # только владелец
    
    def load(self):
        """Загружает учётные записи из файла."""
        if not os.path.exists(ACCOUNTS_FILE):
            return
        try:
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.accounts = [Account(**item) for item in data]
        except Exception as e:
            print(f"Ошибка загрузки аккаунтов: {e}")
    
    def save(self):
        """Сохраняет учётные записи в файл."""
        data = [asdict(acc) for acc in self.accounts]
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Устанавливаем строгие права доступа (только владелец)
        os.chmod(ACCOUNTS_FILE, 0o600)
    
    def add_account(self, account: Account):
        """Добавляет новую учётную запись."""
        self.accounts.append(account)
        self.save()
    
    def remove_account(self, email: str):
        """Удаляет учётную запись по email."""
        self.accounts = [acc for acc in self.accounts if acc.email != email]
        self.save()
    
    def get_account(self, email: str) -> Optional[Account]:
        """Возвращает учётную запись по email или None."""
        for acc in self.accounts:
            if acc.email == email:
                return acc
        return None
    
    def list_emails(self) -> List[str]:
        """Возвращает список email-адресов всех учётных записей."""
        return [acc.email for acc in self.accounts]