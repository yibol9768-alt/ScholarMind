from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QScrollArea, QStackedWidget, QVBoxLayout, QWidget

from app.models.state import AppState
from app.pages.chat_page import ChatPage
from app.pages.login_page import LoginPage
from app.pages.process_pages import (
    AgentRunPage,
    CollectionPage,
    ExperimentDesignPage,
    ExplorationPage,
    ExtractionPage,
    GapPage,
    HistoryPage,
    IdeaPage,
    RepositoryPage,
    ResultsPage,
    SettingsPage,
    TrendPage,
    ValidationPage,
    WritingPage,
)
from app.pages.workflow_page import WorkflowPage
from app.styles.theme import build_stylesheet
from app.widgets.layout import Sidebar, TopBar

PAGE_TITLES = {
    "chat": "主工作台",
    "workflow": "工作流总览",
    "exploration": "领域探索",
    "collection": "文献获取与预处理",
    "extraction": "关键信息提取",
    "trends": "主题建模与趋势分析",
    "gaps": "研究空白识别",
    "ideas": "Idea 生成与筛选",
    "repository": "代码仓库生成",
    "experiment_design": "实验设计与实施",
    "agent_run": "Agent 实验运行",
    "results": "结果分析",
    "writing": "论文写作",
    "validation": "可信验证与追溯",
    "history": "历史记录",
    "settings": "设置",
}


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.state = AppState()
        self.history: list[str] = []
        self.pages: dict[str, QWidget] = {}
        self.setWindowTitle("ScholarMind")
        self.resize(1560, 980)

        self.stack = QStackedWidget()
        self.login_page = LoginPage()
        self.login_page.login_success.connect(self.enter_workspace)
        self.workspace = self.build_workspace()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.workspace)
        self.stack.setCurrentWidget(self.login_page)
        self.setCentralWidget(self.stack)

    def build_workspace(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigate.connect(self.navigate)
        self.sidebar.new_chat.connect(lambda: self.navigate("chat"))
        layout.addWidget(self.sidebar)

        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(14, 12, 18, 18)
        shell_layout.setSpacing(12)

        self.topbar = TopBar()
        self.topbar.back_requested.connect(self.go_back)
        self.topbar.home_requested.connect(lambda: self.navigate("chat"))
        shell_layout.addWidget(self.topbar)

        self.page_stack = QStackedWidget()
        shell_layout.addWidget(self.page_stack, 1)
        layout.addWidget(shell, 1)

        self.register_pages()
        return container

    def register_pages(self) -> None:
        chat = ChatPage(self.navigate)
        chat.navigate_request.connect(self.navigate)
        self.add_page("chat", chat)
        self.add_page("workflow", WorkflowPage(self.navigate, self.state))
        self.add_page("exploration", ExplorationPage(self.navigate))
        self.add_page("collection", CollectionPage(self.navigate))
        self.add_page("extraction", ExtractionPage(self.navigate))
        self.add_page("trends", TrendPage(self.navigate))
        self.add_page("gaps", GapPage(self.navigate))
        self.add_page("ideas", IdeaPage(self.navigate, self.state))
        self.add_page("repository", RepositoryPage(self.navigate))
        self.add_page("experiment_design", ExperimentDesignPage(self.navigate))
        self.add_page("agent_run", AgentRunPage(self.navigate, self.state))
        self.add_page("results", ResultsPage(self.navigate))
        self.add_page("writing", WritingPage(self.navigate))
        self.add_page("validation", ValidationPage(self.navigate))
        self.add_page("history", HistoryPage(self.navigate))
        self.add_page("settings", SettingsPage(self.navigate, self.state.theme, self.apply_theme))

    def add_page(self, page_id: str, page: QWidget) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidget(page)
        self.page_stack.addWidget(scroll)
        self.pages[page_id] = scroll

    def enter_workspace(self) -> None:
        self.stack.setCurrentWidget(self.workspace)
        self.navigate("chat")

    def navigate(self, page_id: str) -> None:
        if page_id not in self.pages:
            return
        if not self.history or self.history[-1] != page_id:
            self.history.append(page_id)

        self.state.current_page = page_id
        self.page_stack.setCurrentWidget(self.pages[page_id])
        self.sidebar.set_active(page_id)

        title = PAGE_TITLES.get(page_id, "ScholarMind")
        self.topbar.set_context(title, f"项目 / {title}", self.state.current_project)
        self.animate_current_page()

    def go_back(self) -> None:
        if len(self.history) <= 1:
            self.navigate("chat")
            return
        self.history.pop()
        self.navigate(self.history.pop())

    def apply_theme(self, theme: str) -> None:
        self.state.theme = theme
        self.app.setStyleSheet(build_stylesheet(theme))
        self.navigate(self.state.current_page)

    def animate_current_page(self) -> None:
        widget = self.page_stack.currentWidget()
        if widget is None:
            return
        end_pos = widget.pos()
        start_pos = end_pos + QPoint(24, 0)
        widget.move(start_pos)
        animation = QPropertyAnimation(widget, b"pos", self)
        animation.setDuration(180)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        self._animation = animation
