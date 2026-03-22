# view/email_viewer.py

from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

class EmailViewer(QWidget):
    """
    Виджет для отображения содержимого письма.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel("Выберите письмо")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def set_email(self, email):
        """Отображает письмо."""
        if email:
            content = f"От: {email.from_}\nКому: {email.to}\nТема: {email.subject}\nДата: {email.date}\n\n"
            if email.body_text:
                content += email.body_text
            elif email.body_html:
                content += email.body_html
            else:
                content += "(нет текста)"
            self.text_edit.setPlainText(content)
            self.label.setText(f"Письмо: {email.subject}")
        else:
            self.text_edit.clear()
            self.label.setText("Выберите письмо")