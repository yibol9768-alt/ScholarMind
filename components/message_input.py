from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget


class MessageInput(QWidget):
    message_submitted = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("请输入你的问题，例如：帮我梳理这篇综述的核心观点与研究空白。")
        self.editor.setObjectName("messageEditor")
        self.editor.setMinimumHeight(110)
        root.addWidget(self.editor)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        helper = QLabel("仅为前端演示，发送后会返回 mock 回复。")
        helper.setObjectName("inputHelper")
        footer.addWidget(helper)
        footer.addStretch(1)

        self.send_button = QPushButton("发送")
        self.send_button.setObjectName("primaryButton")
        self.send_button.clicked.connect(self.submit_message)
        footer.addWidget(self.send_button)
        root.addLayout(footer)

    def submit_message(self) -> None:
        text = self.editor.toPlainText().strip()
        if not text:
            return
        self.editor.clear()
        self.message_submitted.emit(text)
