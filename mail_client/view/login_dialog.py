# view/login_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QHBoxLayout, QMessageBox, QSpinBox,
                             QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from ..utils.workers import TestConnectionThread
from ..model.account_manager import Account

class LoginDialog(QDialog):
    """
    Диалог для добавления/редактирования учётной записи.
    """
    account_saved = pyqtSignal()  # сигнал после сохранения

    def __init__(self, parent=None, account: Account = None):
        super().__init__(parent)
        self.account = account  # если передан, то режим редактирования
        self.test_thread = None
        self.init_ui()
        if account:
            self.load_account_data()
        self.setWindowTitle("Учётная запись" if account is None else "Редактирование")

    def init_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Поля
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.imap_server_edit = QLineEdit()
        self.imap_port_edit = QSpinBox()
        self.imap_port_edit.setRange(1, 65535)
        self.imap_port_edit.setValue(993)
        self.smtp_server_edit = QLineEdit()
        self.smtp_port_edit = QSpinBox()
        self.smtp_port_edit.setRange(1, 65535)
        self.smtp_port_edit.setValue(465)

        # Автозаполнение для популярных сервисов (можно позже)
        self.imap_server_edit.setPlaceholderText("например, imap.gmail.com")
        self.smtp_server_edit.setPlaceholderText("например, smtp.gmail.com")

        form.addRow("Email:", self.email_edit)
        form.addRow("Пароль:", self.password_edit)
        form.addRow("IMAP сервер:", self.imap_server_edit)
        form.addRow("IMAP порт:", self.imap_port_edit)
        form.addRow("SMTP сервер:", self.smtp_server_edit)
        form.addRow("SMTP порт:", self.smtp_port_edit)

        layout.addLayout(form)

        # Кнопка проверки соединения
        self.test_btn = QPushButton("Проверить соединение")
        self.test_btn.clicked.connect(self.test_connection)
        layout.addWidget(self.test_btn)

        # Кнопки OK/Cancel
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn.setEnabled(False)  # доступна только после успешной проверки
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def load_account_data(self):
        """Загружает данные существующего аккаунта в поля (пароль не загружается)"""
        self.email_edit.setText(self.account.email)
        self.imap_server_edit.setText(self.account.imap_server)
        self.imap_port_edit.setValue(self.account.imap_port)
        self.smtp_server_edit.setText(self.account.smtp_server)
        self.smtp_port_edit.setValue(self.account.smtp_port)
        # Пароль не заполняем, пользователь вводит заново

    def test_connection(self):
        """Запускает проверку IMAP-соединения в отдельном потоке"""
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        imap_server = self.imap_server_edit.text().strip()
        imap_port = self.imap_port_edit.value()

        if not email or not password or not imap_server:
            QMessageBox.warning(self, "Ошибка", "Заполните email, пароль и IMAP сервер")
            return

        # Блокируем кнопку на время проверки
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Проверка...")

        self.test_thread = TestConnectionThread(imap_server, imap_port, email, password)
        self.test_thread.success.connect(self.on_test_success)
        self.test_thread.error.connect(self.on_test_error)
        self.test_thread.finished.connect(self.on_test_finished)
        self.test_thread.start()

    def on_test_success(self):
        QMessageBox.information(self, "Успешно", "Соединение с сервером установлено")
        self.ok_btn.setEnabled(True)

    def on_test_error(self, error_msg):
        QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться:\n{error_msg}")
        self.ok_btn.setEnabled(False)

    def on_test_finished(self):
        self.test_btn.setEnabled(True)
        self.test_btn.setText("Проверить соединение")
        self.test_thread.deleteLater()
        self.test_thread = None

    def get_account_data(self):
        """
        Возвращает кортеж (email, password, imap_server, imap_port, smtp_server, smtp_port)
        для создания объекта Account.
        """
        return (
            self.email_edit.text().strip(),
            self.password_edit.text(),
            self.imap_server_edit.text().strip(),
            self.imap_port_edit.value(),
            self.smtp_server_edit.text().strip(),
            self.smtp_port_edit.value()
        )