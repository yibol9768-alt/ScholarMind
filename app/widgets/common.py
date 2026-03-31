from __future__ import annotations

from PySide6.QtCore import QMargins, QRect, QSize, QTimer, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton, QSizePolicy, QVBoxLayout, QWidget


class WrapLabel(QLabel):
    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self.setWordWrap(True)
        self.setTextFormat(Qt.PlainText)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        if width <= 0:
            width = 240
        margins: QMargins = self.contentsMargins()
        inner_width = max(1, width - margins.left() - margins.right())
        metrics = QFontMetrics(self.font())
        rect = metrics.boundingRect(QRect(0, 0, inner_width, 10000), Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop, self.text())
        return rect.height() + margins.top() + margins.bottom() + 2

    def sizeHint(self) -> QSize:
        hint = super().sizeHint()
        if self.wordWrap():
            return QSize(hint.width(), self.heightForWidth(max(240, self.width())))
        return hint


def make_label(text: str, css_class: str = "") -> QLabel:
    label = WrapLabel(text)
    if css_class:
        label.setProperty("class", css_class)
    else:
        label.setProperty("class", "body")
    label.setContentsMargins(0, 0, 0, 2)
    return label


def make_button(text: str, primary: bool = False, role: str | None = None) -> QPushButton:
    button = QPushButton(text)
    if role:
        button.setProperty("role", role)
    elif primary:
        button.setProperty("role", "primary")
    return button


class CardWidget(QFrame):
    def __init__(self, title: str = "", subtitle: str = "", clickable: bool = False, variant: str = "") -> None:
        super().__init__()
        self.setObjectName("Card")
        if clickable:
            self.setProperty("clickable", "true")
        if variant:
            self.setProperty("variant", variant)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(14)
        if title:
            self.layout.addWidget(make_label(title, "section"))
        if subtitle:
            self.layout.addWidget(make_label(subtitle, "muted"))


class StatusTag(QLabel):
    def __init__(self, status: str, text: str | None = None) -> None:
        super().__init__(text or status)
        self.setProperty("status", status)


class LoadingWidget(QFrame):
    def __init__(self, text: str = "正在处理...") -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setProperty("variant", "soft")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(make_label("AI Synthesis Active", "tertiary_badge"))
        layout.addWidget(make_label(text))
        progress = QProgressBar()
        progress.setRange(0, 0)
        layout.addWidget(progress)


class SkeletonList(QFrame):
    def __init__(self, rows: int = 4) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setProperty("variant", "soft")
        self.rows: list[QFrame] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        for idx in range(rows):
            row = QFrame()
            row.setStyleSheet(f"background: rgba(120,120,120,{0.10 + idx * 0.03}); min-height: 14px; border-radius: 7px;")
            self.rows.append(row)
            layout.addWidget(row)
        self.phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.pulse)
        self.timer.start(240)

    def pulse(self) -> None:
        self.phase = (self.phase + 1) % 4
        for idx, row in enumerate(self.rows):
            alpha = 0.10 + ((self.phase + idx) % 4) * 0.04
            row.setStyleSheet(f"background: rgba(120,120,120,{alpha:.2f}); min-height: 14px; border-radius: 7px;")
