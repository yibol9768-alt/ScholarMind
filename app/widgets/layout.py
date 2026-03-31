from __future__ import annotations

from functools import partial

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.mock.data import HISTORY_GROUPS, WORKFLOW_STEPS
from app.widgets.common import make_button, make_label

WORKSPACE_LABELS = {
    "chat": "主工作台",
    "workflow": "工作流总览",
    "history": "历史记录",
    "settings": "设置",
}

WORKFLOW_LABELS = {
    "exploration": "领域探索",
    "collection": "文献获取",
    "extraction": "信息提取",
    "trends": "趋势分析",
    "gaps": "研究空白",
    "ideas": "Idea 生成",
    "repository": "代码仓库",
    "experiment_design": "实验设计",
    "agent_run": "Agent 实验",
    "results": "结果分析",
    "writing": "论文写作",
    "validation": "可信验证",
}

HISTORY_TITLES = {
    "trends": "数字人文趋势分析",
    "collection": "RAG 文献综述整理",
    "extraction": "知识图谱与实体抽取",
    "gaps": "研究空白与选题探索",
    "results": "实验结果复盘",
    "writing": "论文段落草稿",
    "validation": "验证与审计记录",
}

HISTORY_HEADERS = ["Today", "Last 7 Days", "Last 30 Days"]


class Sidebar(QFrame):
    navigate = Signal(str)
    new_chat = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Sidebar")
        self.setMinimumWidth(272)
        self.setMaximumWidth(272)
        self.nav_buttons: dict[str, QPushButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(12)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)
        brand_mark = QFrame()
        brand_mark.setObjectName("Card")
        brand_mark.setProperty("variant", "brandMark")
        brand_mark.setFixedSize(40, 40)
        brand_row.addWidget(brand_mark, 0, Qt.AlignTop)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(2)
        brand_text.addWidget(make_label("Digital Atelier", "sidebar_brand"))
        brand_text.addWidget(make_label("Academic Manuscript", "sidebar_caption"))
        brand_row.addLayout(brand_text, 1)
        layout.addLayout(brand_row)

        new_button = make_button("新建分析", primary=True)
        new_button.clicked.connect(self.new_chat.emit)
        layout.addWidget(new_button)

        layout.addWidget(make_label("Workspace", "sidebar_section"))
        for page_id in ["chat", "workflow", "history", "settings"]:
            button = QPushButton(WORKSPACE_LABELS[page_id])
            button.setProperty("nav", "true")
            button.clicked.connect(partial(self.navigate.emit, page_id))
            self.nav_buttons[page_id] = button
            layout.addWidget(button)

        layout.addWidget(make_label("Workflow", "sidebar_section"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setMaximumHeight(300)
        host = QWidget()
        scroll_layout = QVBoxLayout(host)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(6)
        for page_id, _title in WORKFLOW_STEPS:
            button = QPushButton(WORKFLOW_LABELS.get(page_id, page_id))
            button.setProperty("nav", "true")
            button.clicked.connect(partial(self.navigate.emit, page_id))
            self.nav_buttons[page_id] = button
            scroll_layout.addWidget(button)
        scroll_layout.addStretch(1)
        scroll.setWidget(host)
        layout.addWidget(scroll)

        layout.addWidget(make_label("Recent Sessions", "sidebar_section"))
        self.history = QListWidget()
        self.history.setObjectName("sidebarHistory")
        for index, group in enumerate(HISTORY_GROUPS):
            header = QListWidgetItem(HISTORY_HEADERS[min(index, len(HISTORY_HEADERS) - 1)])
            header.setFlags(Qt.NoItemFlags)
            self.history.addItem(header)
            for item in group["items"]:
                line = QListWidgetItem(HISTORY_TITLES.get(item["page"], "研究会话"))
                line.setData(Qt.UserRole, item)
                self.history.addItem(line)
        self.history.itemClicked.connect(self._open_history)
        layout.addWidget(self.history, 1)

        profile = QFrame()
        profile.setObjectName("Card")
        profile.setProperty("variant", "sidebarProfile")
        profile_layout = QHBoxLayout(profile)
        profile_layout.setContentsMargins(14, 14, 14, 14)
        profile_layout.setSpacing(12)

        avatar = QFrame()
        avatar.setObjectName("Card")
        avatar.setProperty("variant", "topAvatar")
        avatar.setFixedSize(40, 40)
        avatar_layout = QVBoxLayout(avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.addWidget(make_label("LZ", "avatar_text"), 0, Qt.AlignCenter)

        profile_text = QVBoxLayout()
        profile_text.setSpacing(2)
        profile_text.addWidget(make_label("Lin Zhixing", "profile_name"))
        profile_text.addWidget(make_label("Computational Humanities Lab", "profile_role"))
        profile_layout.addWidget(avatar, 0, Qt.AlignTop)
        profile_layout.addLayout(profile_text, 1)
        layout.addWidget(profile)

    def _open_history(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.UserRole)
        if data:
            self.navigate.emit(data["page"])

    def set_active(self, page_id: str) -> None:
        for key, button in self.nav_buttons.items():
            button.setProperty("active", "true" if key == page_id else "false")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()


class TopBar(QFrame):
    back_requested = Signal()
    home_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("TopBar")
        self.setMinimumHeight(112)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 8)
        layout.setSpacing(18)

        left = QVBoxLayout()
        left.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(18)
        self.brand = make_label("Digital Atelier", "topbrand")
        top_row.addWidget(self.brand)
        top_row.addWidget(make_label("Dashboard", "topnav_active"))
        top_row.addWidget(make_label("Reader", "topnav"))
        top_row.addWidget(make_label("Chat", "topnav"))
        top_row.addStretch(1)
        left.addLayout(top_row)

        info_row = QHBoxLayout()
        info_row.setSpacing(10)
        self.back_button = make_button("返回", role="ghost")
        self.back_button.clicked.connect(self.back_requested.emit)
        info_row.addWidget(self.back_button, 0, Qt.AlignTop)

        info_text = QVBoxLayout()
        info_text.setSpacing(2)
        self.crumb = make_label("项目 / 主工作台", "topbar_context")
        self.title = make_label("主工作台", "section")
        self.project = make_label("ScholarMind Research Workspace", "topbar_project")
        info_text.addWidget(self.crumb)
        info_text.addWidget(self.title)
        info_text.addWidget(self.project)
        info_row.addLayout(info_text, 1)
        left.addLayout(info_row)
        layout.addLayout(left, 1)

        right = QHBoxLayout()
        right.setSpacing(10)
        self.search = QLineEdit()
        self.search.setObjectName("topSearch")
        self.search.setPlaceholderText("Search manuscript...")
        self.search.setFixedWidth(240)
        right.addWidget(self.search)

        notice = make_button("通知", role="ghost")
        history = make_button("历史", role="ghost")
        home = make_button("工作台", role="ghost")
        home.clicked.connect(self.home_requested.emit)
        right.addWidget(notice)
        right.addWidget(history)
        right.addWidget(home)

        avatar = QFrame()
        avatar.setObjectName("Card")
        avatar.setProperty("variant", "topAvatar")
        avatar.setFixedSize(36, 36)
        avatar_layout = QVBoxLayout(avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.addWidget(make_label("LZ", "avatar_text"), 0, Qt.AlignCenter)
        right.addWidget(avatar)

        layout.addLayout(right)

    def set_context(self, title: str, crumb: str, project: str) -> None:
        self.title.setText(title)
        self.crumb.setText(crumb)
        self.project.setText(project)


class SearchBar(QFrame):
    text_changed = Signal(str)

    def __init__(self, placeholder: str = "搜索...") -> None:
        super().__init__()
        self.setObjectName("Card")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(make_label("搜索", "subtitle"))
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.textChanged.connect(self.text_changed.emit)
        layout.addWidget(self.edit, 1)
