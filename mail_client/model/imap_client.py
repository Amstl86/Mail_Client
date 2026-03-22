# model/imap_client.py

import imaplib
import ssl
from typing import List, Tuple, Optional
from mail_client.model.email_parser import parse_email
from mail_client.model.email_message import EmailMessage

class IMAPClient:
    """
    Клиент для работы с IMAP-сервером.
    Поддерживает SSL/TLS, проверку сертификатов.
    """

    def __init__(self, server: str, port: int, email: str, password: str):
        self.server = server
        self.port = port
        self.email = email
        self.password = password
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        """Устанавливает SSL-соединение и аутентифицируется."""
        context = ssl.create_default_context()
        self.connection = imaplib.IMAP4_SSL(self.server, self.port, ssl_context=context)
        self.connection.login(self.email, self.password)

    def logout(self) -> None:
        """Закрывает соединение."""
        if self.connection:
            try:
                self.connection.logout()
            except Exception:
                pass
            finally:
                self.connection = None

    def select_folder(self, folder: str = "INBOX") -> None:
        """Выбирает папку (по умолчанию INBOX)."""
        if not self.connection:
            raise Exception("Not connected")
        self.connection.select(folder)

    def fetch_uids(self, limit: int = 50) -> List[str]:
        """
        Возвращает список UID писем в текущей папке (последние `limit` штук).
        """
        if not self.connection:
            raise Exception("Not connected")
        # Используем UID-режим для надёжности
        typ, data = self.connection.uid('SEARCH', None, 'ALL')
        if typ != 'OK':
            return []
        uids = data[0].split()
        # Берём последние limit
        return [uid.decode() for uid in uids[-limit:]]

    def fetch_email_by_uid(self, uid: str) -> Optional[EmailMessage]:
        """
        Загружает письмо по UID и парсит его в EmailMessage.
        """
        if not self.connection:
            raise Exception("Not connected")
        typ, data = self.connection.uid('FETCH', uid, '(RFC822)')
        if typ != 'OK' or not data or data[0] is None:
            return None
        raw_email = data[0][1]  # тело письма в байтах
        email_msg = parse_email(raw_email)
        email_msg.uid = uid
        return email_msg

    def list_folders(self) -> List[str]:
        """
        Возвращает список папок (имён).
        """
        if not self.connection:
            raise Exception("Not connected")
        typ, data = self.connection.list()
        if typ != 'OK':
            return []
        folders = []
        for line in data:
            # Пример: '(\\HasNoChildren) "/" "INBOX"'
            parts = line.decode().split(' "/" ')
            if len(parts) == 2:
                folder = parts[1].strip('"')
                folders.append(folder)
        return folders