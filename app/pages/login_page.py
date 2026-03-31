from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from app.widgets.common import make_button, make_label


class LoginPage(QWidget):
    login_success = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        hero = QFrame()
        hero.setObjectName("Card")
        hero.setProperty("variant", "loginHero")
        hero.setMinimumWidth(520)
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(48, 52, 44, 52)
        hero_layout.setSpacing(24)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(14)
        brand_mark = QFrame()
        brand_mark.setObjectName("Card")
        brand_mark.setProperty("variant", "loginMark")
        brand_mark.setFixedSize(44, 44)
        brand_row.addWidget(brand_mark, 0, Qt.AlignTop)

        brand_copy = QVBoxLayout()
        brand_copy.setSpacing(2)
        brand_copy.addWidget(make_label("ScholarMind", "login_hero_brand"))
        brand_copy.addWidget(make_label("Academic Research Studio", "login_hero_eyebrow"))
        brand_row.addLayout(brand_copy)
        brand_row.addStretch(1)
        hero_layout.addLayout(brand_row)

        hero_layout.addStretch(1)
        hero_copy = QWidget()
        hero_copy.setObjectName("loginHeroCopy")
        hero_copy_layout = QVBoxLayout(hero_copy)
        hero_copy_layout.setContentsMargins(0, 0, 0, 0)
        hero_copy_layout.setSpacing(12)
        hero_copy_layout.addWidget(make_label("让大模型成为你的科研文献分析助手", "login_hero_title"))
        hero_copy_layout.addWidget(
            make_label(
                "聚合检索、综述梳理、实验启发与论文写作支持，把复杂研究流程整理成清晰、稳定、可执行的学术工作台。",
                "login_hero_text",
            )
        )
        hero_copy.setMaximumWidth(500)
        hero_layout.addWidget(hero_copy)
        hero_layout.addStretch(1)

        footer_row = QHBoxLayout()
        footer_row.setSpacing(14)
        footer_line = QFrame()
        footer_line.setObjectName("loginHeroLine")
        footer_line.setFixedHeight(1)
        footer_line.setMinimumWidth(56)
        footer_row.addWidget(footer_line, 0, Qt.AlignVCenter)
        footer_row.addWidget(make_label("Empowering Academia through Neural Synthesis", "login_hero_quote"))
        footer_row.addStretch(1)
        hero_layout.addLayout(footer_row)

        bars = QHBoxLayout()
        bars.setSpacing(10)
        bars.addStretch(1)
        for height in [92, 148, 72, 126]:
            bar = QFrame()
            bar.setObjectName("loginHeroBar")
            bar.setFixedSize(10, height)
            bars.addWidget(bar, 0, Qt.AlignBottom)
        hero_layout.addLayout(bars)

        canvas = QWidget()
        canvas.setObjectName("loginCanvas")
        canvas_layout = QVBoxLayout(canvas)
        canvas_layout.setContentsMargins(56, 52, 56, 40)
        canvas_layout.setSpacing(20)
        canvas_layout.addStretch(1)

        form_host = QFrame()
        form_host.setObjectName("Card")
        form_host.setProperty("variant", "loginPanel")
        form_host.setMaximumWidth(560)
        form_host.setMinimumWidth(440)
        form = QVBoxLayout(form_host)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(18)

        header = QVBoxLayout()
        header.setSpacing(6)
        header.addWidget(make_label("欢迎回来", "login_title"))
        header.addWidget(make_label("继续进入你的 ScholarMind 学术工作台。", "login_subtitle"))
        form.addLayout(header)

        tabs = QHBoxLayout()
        tabs.setSpacing(28)
        tabs.addWidget(make_label("邮箱登录", "login_tab_active"))
        tabs.addWidget(make_label("验证码登录", "login_tab"))
        tabs.addStretch(1)
        form.addLayout(tabs)

        tab_line = QFrame()
        tab_line.setObjectName("loginTabsLine")
        tab_line.setFixedHeight(1)
        form.addWidget(tab_line)

        email_group = QVBoxLayout()
        email_group.setSpacing(8)
        email_group.addWidget(make_label("机构邮箱", "field_label"))
        self.email = QLineEdit()
        self.email.setObjectName("loginField")
        self.email.setPlaceholderText("name@university.edu")
        self.email.setMinimumHeight(56)
        email_group.addWidget(self.email)
        form.addLayout(email_group)

        password_group = QVBoxLayout()
        password_group.setSpacing(8)
        password_top = QHBoxLayout()
        password_top.setSpacing(8)
        password_top.addWidget(make_label("安全密码", "field_label"))
        password_top.addStretch(1)
        forgot_button = make_button("忘记密码？", role="ghost")
        password_top.addWidget(forgot_button)
        password_group.addLayout(password_top)

        self.password = QLineEdit()
        self.password.setObjectName("loginField")
        self.password.setPlaceholderText("请输入密码")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(56)
        password_group.addWidget(self.password)
        form.addLayout(password_group)

        self.remember = QCheckBox("保持登录状态")
        self.remember.setObjectName("rememberBox")
        form.addWidget(self.remember)

        login = make_button("进入工作台", primary=True)
        login.setMinimumHeight(52)
        login.clicked.connect(self.login_success.emit)
        form.addWidget(login)

        divider = QHBoxLayout()
        divider.setSpacing(12)
        left_line = QFrame()
        left_line.setObjectName("loginDividerLine")
        left_line.setFixedHeight(1)
        right_line = QFrame()
        right_line.setObjectName("loginDividerLine")
        right_line.setFixedHeight(1)
        divider.addWidget(left_line, 1)
        divider.addWidget(make_label("或使用以下方式登录", "login_divider"))
        divider.addWidget(right_line, 1)
        form.addLayout(divider)

        oidc = QHBoxLayout()
        oidc.setSpacing(12)
        google_button = make_button("Google", role="oidc")
        github_button = make_button("GitHub", role="oidc")
        oidc.addWidget(google_button)
        oidc.addWidget(github_button)
        form.addLayout(oidc)

        request = QHBoxLayout()
        request.setSpacing(6)
        request.addStretch(1)
        request.addWidget(make_label("还没有账号？", "login_subtitle"))
        request.addWidget(make_label("申请邀请", "login_link"))
        request.addStretch(1)
        form.addLayout(request)

        canvas_layout.addWidget(form_host, 0, Qt.AlignHCenter)
        canvas_layout.addStretch(1)

        support = QHBoxLayout()
        support.setSpacing(18)
        support.addStretch(1)
        for text in ["隐私政策", "服务条款", "联系支持"]:
            support.addWidget(make_label(text, "login_footer_link"))
        support.addStretch(1)
        canvas_layout.addLayout(support)

        root.addWidget(hero, 8)
        root.addWidget(canvas, 12)
