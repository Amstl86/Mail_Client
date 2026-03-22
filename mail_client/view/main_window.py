"""
Главное окно приложения.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QStatusBar
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    """Главное окно почтового клиента."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mail Client")
        self.setMinimumSize(800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Временная заглушка
        label = QLabel("Добро пожаловать в почтовый клиент!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Кнопка для проверки
        btn = QPushButton("Проверка работы")
        btn.clicked.connect(self.on_button_clicked)
        layout.addWidget(btn)
        
        # Статусная строка
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов")
    
    def on_button_clicked(self):
        """Пример обработки события."""
        self.status_bar.showMessage("Кнопка нажата")
        print("Кнопка нажата")