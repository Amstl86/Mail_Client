# view/email_list_widget.py

from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtCore import pyqtSignal
from mail_client.model.email_message import EmailMessage

class EmailListWidget(QListWidget):
    """
    Виджет для отображения списка писем.
    """
    email_selected = pyqtSignal(EmailMessage)  # сигнал при выборе письма

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.itemClicked.connect(self.on_item_clicked)
        self.emails = []  # храним объекты писем

    def set_emails(self, emails: list[EmailMessage]):
        """Обновляет список писем."""
        self.clear()
        self.emails = emails
        for email in emails:
            # Формируем текст элемента: "Дата | От | Тема"
            text = f"{email.date} | {email.from_} | {email.subject}"
            item = QListWidgetItem(text)
            item.setData(1, email)  # сохраняем объект письма
            self.addItem(item)

    def on_item_clicked(self, item):
        """Обрабатывает клик по элементу."""
        email = item.data(1)
        if email:
            self.email_selected.emit(email)