from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from components.history_list import HistoryList


class Sidebar(QWidget):
    new_chat_requested = Signal()
    conversation_selected = Signal(dict)

    def __init__(self, grouped_history: list[dict]) -> None:
        super().__init__()
        self._build_ui(grouped_history)

    def _build_ui(self, grouped_history: list[dict]) -> None:
        self.setObjectName("sidebar")
        self.setFixedWidth(286)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        brand = QLabel("研究工作室")
        brand.setObjectName("sidebarBrand")
        subtitle = QLabel("精选手稿")
        subtitle.setObjectName("sidebarSubtitle")
        layout.addWidget(brand)
        layout.addWidget(subtitle)

        new_chat = QPushButton("+ 新建对话")
        new_chat.setObjectName("primaryButton")
        new_chat.clicked.connect(self.new_chat_requested.emit)
        layout.addWidget(new_chat)

        history_title = QLabel("历史记录")
        history_title.setObjectName("sidebarSection")
        layout.addWidget(history_title)

        self.history_list = HistoryList(grouped_history)
        self.history_list.conversation_selected.connect(self.conversation_selected.emit)
        layout.addWidget(self.history_list, 1)

        footer_title = QLabel("设置与帮助")
        footer_title.setObjectName("sidebarSection")
        layout.addWidget(footer_title)

        for text in ["设置", "帮助"]:
            button = QPushButton(text)
            button.setCursor(Qt.PointingHandCursor)
            button.setObjectName("sidebarFooterButton")
            layout.addWidget(button)

    def set_active_conversation(self, conversation_id: str) -> None:
        self.history_list.set_active(conversation_id)
