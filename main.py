import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

import theme
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PERT/CPM")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    theme.apply_theme(app, "dark")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# Распространить стартовую тему на все графики
if __name__ == "__main__":
    main()