from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget


class HistoryList(QWidget):
    conversation_selected = Signal(dict)

    def __init__(self, grouped_history: list[dict]) -> None:
        super().__init__()
        self.grouped_history = grouped_history
        self.buttons: list[tuple[QPushButton, dict]] = []
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        for group in self.grouped_history:
            title = QLabel(group["title"])
            title.setObjectName("historyGroupTitle")
            layout.addWidget(title)
            for item in group["items"]:
                button = QPushButton(item["title"])
                button.setObjectName("historyItem")
                button.setCheckable(True)
                button.setCursor(Qt.PointingHandCursor)
                button.clicked.connect(lambda checked=False, data=item: self.select_item(data))
                self.buttons.append((button, item))
                layout.addWidget(button)

        layout.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll)

    def select_item(self, item: dict) -> None:
        for button, data in self.buttons:
            active = data["id"] == item["id"]
            button.setChecked(active)
            button.setObjectName("historyItemActive" if active else "historyItem")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
        self.conversation_selected.emit(item)

    def set_active(self, conversation_id: str) -> None:
        for button, data in self.buttons:
            active = data["id"] == conversation_id
            button.setChecked(active)
            button.setObjectName("historyItemActive" if active else "historyItem")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
