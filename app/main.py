from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.styles.theme import build_stylesheet
from app.windows.main_window import MainWindow


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("ScholarMind")
    app.setStyleSheet(build_stylesheet("light"))
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())
