from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class LoginForm(QWidget):
    login_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        left = QFrame()
        left.setObjectName("loginHero")
        left.setMinimumWidth(520)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(56, 56, 56, 56)
        left_layout.setSpacing(24)

        badge = QLabel("学术研究伙伴")
        badge.setObjectName("loginHeroBadge")
        title = QLabel("让大模型成为你的科研文献分析助手")
        title.setWordWrap(True)
        title.setObjectName("loginHeroTitle")
        desc = QLabel("Scholarly AI 研究工作台。把复杂的文献梳理、主题提炼与对话交互组织成更清晰的学术工作流。")
        desc.setWordWrap(True)
        desc.setObjectName("loginHeroText")
        quote = QLabel("通过神经合成，增强学术洞察。")
        quote.setObjectName("loginHeroQuote")
        left_layout.addWidget(badge, alignment=Qt.AlignLeft)
        left_layout.addStretch(1)
        left_layout.addWidget(title)
        left_layout.addWidget(desc)
        left_layout.addStretch(1)
        left_layout.addWidget(quote)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(72, 56, 72, 56)
        right_layout.setSpacing(18)
        right_layout.addStretch(1)

        welcome = QLabel("欢迎回来")
        welcome.setObjectName("loginTitle")
        sub = QLabel("继续你的精选研究手稿。")
        sub.setObjectName("loginSubtitle")

        tabs = QHBoxLayout()
        email_tab = QLabel("邮箱登录")
        email_tab.setObjectName("loginTabActive")
        code_tab = QLabel("验证码")
        code_tab.setObjectName("loginTab")
        tabs.addWidget(email_tab)
        tabs.addWidget(code_tab)
        tabs.addStretch(1)

        email_label = QLabel("机构邮箱")
        email_label.setObjectName("fieldLabel")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("name@university.edu")
        self.email_input.setObjectName("loginField")

        password_label = QLabel("安全密码")
        password_label.setObjectName("fieldLabel")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("loginField")

        self.remember = QCheckBox("保持登录状态")
        self.remember.setObjectName("rememberBox")

        login_button = QPushButton("进入工作台")
        login_button.setObjectName("primaryButton")
        login_button.clicked.connect(self.login_requested.emit)

        oidc_hint = QLabel("或使用机构账号认证")
        oidc_hint.setObjectName("dividerText")
        social_row = QHBoxLayout()
        for text in ["Google", "GitHub"]:
            button = QPushButton(text)
            button.setObjectName("secondaryButton")
            social_row.addWidget(button)

        right_layout.addWidget(welcome)
        right_layout.addWidget(sub)
        right_layout.addLayout(tabs)
        right_layout.addSpacing(8)
        right_layout.addWidget(email_label)
        right_layout.addWidget(self.email_input)
        right_layout.addWidget(password_label)
        right_layout.addWidget(self.password_input)
        right_layout.addWidget(self.remember)
        right_layout.addWidget(login_button)
        right_layout.addSpacing(18)
        right_layout.addWidget(oidc_hint, alignment=Qt.AlignCenter)
        right_layout.addLayout(social_row)
        right_layout.addStretch(1)

        root.addWidget(left, 1)
        root.addWidget(right, 1)
