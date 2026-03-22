"""
Точка входа в приложение.
"""

import sys
from PyQt6.QtWidgets import QApplication
from view.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mail Client")
    app.setOrganizationName("Dev")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()