# view/main_window.py (обновлённая версия)

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                             QPushButton, QStatusBar, QMenuBar, QMenu,
                             QMessageBox, QListWidget, QListWidgetItem,
                             QHBoxLayout, QSplitter)
from PyQt6.QtCore import Qt
from ..model.account_manager import AccountManager, Account
from ..utils.workers import FetchEmailsThread
from .login_dialog import LoginDialog
from .email_list_widget import EmailListWidget
from .email_viewer import EmailViewer  # пока заглушка, создадим позже

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.account_manager = AccountManager()
        self.current_account = None
        self.fetch_thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mail Client")
        self.setMinimumSize(800, 600)

        # Меню
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Настройки")
        accounts_action = settings_menu.addAction("Учётные записи")
        accounts_action.triggered.connect(self.add_account)  # пока просто добавление

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Верхняя панель: список аккаунтов
        self.account_list = QListWidget()
        self.account_list.setMaximumHeight(80)
        self.account_list.itemClicked.connect(self.on_account_selected)
        main_layout.addWidget(QLabel("Аккаунты:"))
        main_layout.addWidget(self.account_list)

        # Кнопка "Добавить аккаунт"
        add_btn = QPushButton("Добавить аккаунт")
        add_btn.clicked.connect(self.add_account)
        main_layout.addWidget(add_btn)

        # Основная область: сплиттер со списком писем и просмотрщиком
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.email_list = EmailListWidget()
        self.email_list.email_selected.connect(self.on_email_selected)
        self.email_viewer = EmailViewer()  # заглушка, создадим в следующем этапе
        splitter.addWidget(self.email_list)
        splitter.addWidget(self.email_viewer)
        splitter.setSizes([300, 500])
        main_layout.addWidget(splitter)

        # Статусная строка
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов")

        # Загружаем список аккаунтов
        self.refresh_account_list()

    def refresh_account_list(self):
        self.account_list.clear()
        for email in self.account_manager.list_emails():
            self.account_list.addItem(email)
        if self.account_list.count() == 0:
            self.email_list.setEnabled(False)
            self.email_viewer.setEnabled(False)
        else:
            self.email_list.setEnabled(True)
            self.email_viewer.setEnabled(True)

    def add_account(self):
        dialog = LoginDialog(self)
        if dialog.exec():
            email, password, imap_server, imap_port, smtp_server, smtp_port = dialog.get_account_data()
            if self.account_manager.get_account(email):
                QMessageBox.warning(self, "Ошибка", f"Аккаунт {email} уже существует")
                return
            account = Account.create(email, password, imap_server, imap_port, smtp_server, smtp_port)
            self.account_manager.add_account(account)
            self.refresh_account_list()
            self.status_bar.showMessage(f"Аккаунт {email} добавлен")

    def on_account_selected(self, item):
        email = item.text()
        self.current_account = self.account_manager.get_account(email)
        if self.current_account:
            self.status_bar.showMessage(f"Загрузка писем для {email}...")
            self.load_emails()

    def load_emails(self):
        """Запускает поток загрузки писем для текущего аккаунта."""
        if not self.current_account:
            return
        # Если уже есть поток, останавливаем
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
        self.fetch_thread = FetchEmailsThread(self.current_account, "INBOX", limit=50)
        self.fetch_thread.finished.connect(self.on_emails_loaded)
        self.fetch_thread.error.connect(self.on_emails_error)
        self.fetch_thread.start()
        self.status_bar.showMessage("Загрузка писем...")

    def on_emails_loaded(self, emails):
        self.email_list.set_emails(emails)
        self.status_bar.showMessage(f"Загружено писем: {len(emails)}")

    def on_emails_error(self, error_msg):
        QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить письма:\n{error_msg}")
        self.status_bar.showMessage("Ошибка загрузки")

    def on_email_selected(self, email):
        """При выборе письма обновляем просмотрщик."""
        self.email_viewer.set_email(email)