# utils/workers.py

from PyQt6.QtCore import QThread, pyqtSignal
import imaplib
import ssl

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