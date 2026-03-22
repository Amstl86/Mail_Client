# utils/workers.py
import imaplib
import ssl

from PyQt6.QtCore import QThread, pyqtSignal

from mail_client.model.imap_client import IMAPClient

class TestConnectionThread(QThread):
    """
    Поток для проверки подключения к IMAP-серверу.
    """
    success = pyqtSignal()
    error = pyqtSignal(str)   # сообщение об ошибке

    def __init__(self, server: str, port: int, email: str, password: str):
        super().__init__()
        self.server = server
        self.port = port
        self.email = email
        self.password = password

    def run(self):
        try:
            # Создаём SSL-контекст с проверкой сертификатов
            context = ssl.create_default_context()
            imap = imaplib.IMAP4_SSL(self.server, self.port, ssl_context=context)
            imap.login(self.email, self.password)
            imap.logout()
            self.success.emit()
        except Exception as e:
            self.error.emit(str(e))
            

class FetchEmailsThread(QThread):
    """
    Поток для загрузки списка писем из папки.
    """
    finished = pyqtSignal(list)   # список EmailMessage
    error = pyqtSignal(str)

    def __init__(self, account, folder: str = "INBOX", limit: int = 50):
        super().__init__()
        self.account = account
        self.folder = folder
        self.limit = limit

    def run(self):
        try:
            client = IMAPClient(
                self.account.imap_server,
                self.account.imap_port,
                self.account.email,
                self.account.get_password()
            )
            client.connect()
            client.select_folder(self.folder)
            uids = client.fetch_uids(self.limit)
            emails = []
            for uid in uids:
                email_msg = client.fetch_email_by_uid(uid)
                if email_msg:
                    emails.append(email_msg)
            client.logout()
            self.finished.emit(emails)
        except Exception as e:
            self.error.emit(str(e))