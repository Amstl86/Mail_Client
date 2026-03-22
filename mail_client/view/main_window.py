# view/main_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                             QPushButton, QStatusBar, QMenuBar, QMenu,
                             QMessageBox, QListWidget, QListWidgetItem,
                             QHBoxLayout)
from PyQt6.QtCore import Qt
from mail_client.model.account_manager import AccountManager, Account
from mail_client.view.login_dialog import LoginDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.account_manager = AccountManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mail Client")
        self.setMinimumSize(800, 600)

        # Меню
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Настройки")
        accounts_action = settings_menu.addAction("Учётные записи")
        accounts_action.triggered.connect(self.add_account)

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

        # Основная область (пока заглушка)
        self.content_label = QLabel("Выберите аккаунт для просмотра писем")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.content_label)

        # Статусная строка
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов")

        # Загружаем список аккаунтов
        self.refresh_account_list()

    def refresh_account_list(self):
        """Обновляет список аккаунтов в интерфейсе."""
        self.account_list.clear()
        for email in self.account_manager.list_emails():
            self.account_list.addItem(email)
        if self.account_list.count() == 0:
            self.content_label.setText("Нет аккаунтов. Добавьте учётную запись.")

    def add_account(self):
        """Открывает диалог добавления нового аккаунта."""
        dialog = LoginDialog(self)
        if dialog.exec():
            email, password, imap_server, imap_port, smtp_server, smtp_port = dialog.get_account_data()
            # Проверяем, нет ли уже такого аккаунта
            if self.account_manager.get_account(email):
                QMessageBox.warning(self, "Ошибка", f"Аккаунт {email} уже существует")
                return
            account = Account.create(email, password, imap_server, imap_port, smtp_server, smtp_port)
            self.account_manager.add_account(account)
            self.refresh_account_list()
            self.status_bar.showMessage(f"Аккаунт {email} добавлен")

    def on_account_selected(self, item):
        """Выбор аккаунта из списка."""
        email = item.text()
        account = self.account_manager.get_account(email)
        if account:
            self.content_label.setText(f"Выбран аккаунт: {email}\n"
                                       f"IMAP: {account.imap_server}:{account.imap_port}\n"
                                       "Здесь будет список писем")
            self.status_bar.showMessage(f"Аккаунт {email} выбран")