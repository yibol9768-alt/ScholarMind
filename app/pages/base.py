from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget


class BasePage(QWidget):
    def __init__(self, page_id: str, title: str, navigator: Callable[[str], None]) -> None:
        super().__init__()
        self.page_id = page_id
        self.title = title
        self.navigate = navigator
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(12, 12, 12, 12)
        self.root.setSpacing(16)

    def two_column(self) -> tuple[QVBoxLayout, QVBoxLayout]:
        row = QHBoxLayout()
        row.setSpacing(16)
        left_widget = QWidget()
        right_widget = QWidget()
        left = QVBoxLayout(left_widget)
        right = QVBoxLayout(right_widget)
        left.setContentsMargins(0, 0, 0, 0)
        right.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(16)
        right.setSpacing(16)
        row.addWidget(left_widget, 2)
        row.addWidget(right_widget, 1)
        self.root.addLayout(row)
        return left, right
