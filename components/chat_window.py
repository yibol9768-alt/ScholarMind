from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from components.message_input import MessageInput


class ChatWindow(QWidget):
    message_submitted = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 24)
        root.setSpacing(18)

        topbar = QHBoxLayout()
        self.page_title = QLabel("欢迎来到研究工作台")
        self.page_title.setObjectName("chatPageTitle")
        self.page_subtitle = QLabel("让大模型成为你的科研文献分析助手")
        self.page_subtitle.setObjectName("chatPageSubtitle")
        title_block = QVBoxLayout()
        title_block.addWidget(self.page_title)
        title_block.addWidget(self.page_subtitle)
        topbar.addLayout(title_block)
        topbar.addStretch(1)

        for text in ["通知", "头像"]:
            button = QPushButton(text)
            button.setObjectName("topActionButton")
            topbar.addWidget(button)
        root.addLayout(topbar)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)
        for title, desc in [
            ("分析研究趋势", "梳理近三年的热门主题、方法路径与代表论文。"),
            ("总结 RAG 文献", "快速生成高被引论文摘要与关键结论。"),
            ("抽取知识网络", "把作者、概念和研究问题组织成关系图。"),
        ]:
            cards_row.addWidget(self._build_suggestion_card(title, desc))
        root.addLayout(cards_row)

        editorial_row = QHBoxLayout()
        editorial_row.setSpacing(14)
        quote_card = self._build_quote_card()
        image_card = self._build_image_card()
        metric_card = self._build_metric_card()
        editorial_row.addWidget(quote_card, 1)
        editorial_row.addWidget(image_card, 1)
        editorial_row.addWidget(metric_card, 1)
        root.addLayout(editorial_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.message_host = QWidget()
        self.message_layout = QVBoxLayout(self.message_host)
        self.message_layout.setContentsMargins(0, 6, 0, 6)
        self.message_layout.setSpacing(14)
        self.message_layout.addStretch(1)
        self.scroll.setWidget(self.message_host)
        root.addWidget(self.scroll, 1)

        self.input = MessageInput()
        self.input.message_submitted.connect(self.message_submitted.emit)
        root.addWidget(self.input)

    def _build_suggestion_card(self, title: str, desc: str) -> QWidget:
        card = QFrame()
        card.setObjectName("suggestionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        icon = QLabel(" ")
        icon.setFixedSize(40, 40)
        icon.setObjectName("iconTile")
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("cardText")
        layout.addWidget(icon, alignment=Qt.AlignLeft)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        return card

    def _build_quote_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("quoteCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        tag = QLabel("最新洞察")
        tag.setObjectName("capsule")
        quote = QLabel("“分散数据集的整合已经不是奢侈品，而是现代学者的基本能力。”")
        quote.setWordWrap(True)
        quote.setObjectName("quoteText")
        layout.addWidget(tag, alignment=Qt.AlignLeft)
        layout.addWidget(quote)
        return card

    def _build_image_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("imageCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("文献图像占位")
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("imagePlaceholder")
        layout.addWidget(label)
        return card

    def _build_metric_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("metricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        number = QLabel("4.8k")
        number.setObjectName("metricValue")
        label = QLabel("已收录来源")
        label.setObjectName("metricLabel")
        layout.addStretch(1)
        layout.addWidget(number)
        layout.addWidget(label)
        return card

    def set_conversation(self, conversation: dict) -> None:
        self.page_title.setText(conversation["title"])
        self.page_subtitle.setText(conversation["subtitle"])
        self.clear_messages()
        for message in conversation["messages"]:
            self.add_message(message["role"], message["content"])

    def clear_messages(self) -> None:
        while self.message_layout.count() > 1:
            item = self.message_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def add_message(self, role: str, content: str) -> None:
        bubble = QFrame()
        bubble.setObjectName("userBubble" if role == "user" else "assistantBubble")
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(18, 14, 18, 14)
        title = QLabel("我" if role == "user" else "ScholarMind")
        title.setObjectName("bubbleTitle")
        text = QLabel(content)
        text.setWordWrap(True)
        text.setObjectName("bubbleText")
        layout.addWidget(title)
        layout.addWidget(text)
        index = max(0, self.message_layout.count() - 1)
        self.message_layout.insertWidget(index, bubble, 0, Qt.AlignRight if role == "user" else Qt.AlignLeft)
