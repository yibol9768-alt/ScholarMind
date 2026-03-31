from __future__ import annotations

import sys
from copy import deepcopy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from components.chat_window import ChatWindow
from components.login_form import LoginForm
from components.sidebar import Sidebar


MOCK_HISTORY = [
    {
        "title": "今天",
        "items": [
            {
                "id": "today-1",
                "title": "CRISPR 新生儿伦理分析",
                "subtitle": "研究对话与文献摘要已同步",
                "messages": [
                    {"role": "assistant", "content": "欢迎回来。这个话题目前已经整理出伦理争议、政策边界和临床应用三条主线。"},
                    {"role": "user", "content": "先给我一个适合汇报的结构。"},
                    {"role": "assistant", "content": "可以按“背景问题、核心争议、支持论证、反对论证、政策建议”五部分展开。"},
                ],
            },
            {
                "id": "today-2",
                "title": "量子密码学标准综述",
                "subtitle": "近两年标准化进展与差异对比",
                "messages": [
                    {"role": "assistant", "content": "这里的重点是标准框架、协议成熟度和实现成本。"},
                    {"role": "user", "content": "帮我列出三篇代表论文的比较角度。"},
                    {"role": "assistant", "content": "建议比较安全假设、实验场景、标准兼容性三个维度。"},
                ],
            },
        ],
    },
    {
        "title": "昨天",
        "items": [
            {
                "id": "yesterday-1",
                "title": "全民基本收入与农村经济",
                "subtitle": "政策试验、就业与福利影响",
                "messages": [
                    {"role": "assistant", "content": "这个主题适合做政策实验设计和地区差异比较。"},
                    {"role": "user", "content": "先总结一下反对意见。"},
                    {"role": "assistant", "content": "常见反对意见集中在财政可持续性、劳动激励和地方执行效率。"},
                ],
            }
        ],
    },
    {
        "title": "上个月",
        "items": [
            {
                "id": "month-1",
                "title": "石墨烯导电性文献综述",
                "subtitle": "材料、温度与实验设计线索",
                "messages": [
                    {"role": "assistant", "content": "当前已整理出材料制备、温度条件和实验测量三类变量。"},
                    {"role": "user", "content": "把温度因素单独展开。"},
                    {"role": "assistant", "content": "好的，建议区分低温极限、常温稳定性和仪器误差控制。"},
                ],
            }
        ],
    },
]


class MainChatPage(QWidget):
    def __init__(self, grouped_history: list[dict]) -> None:
        super().__init__()
        self.grouped_history = grouped_history
        self.current_conversation = self.grouped_history[0]["items"][0]
        self._build_ui()
        self.sidebar.set_active_conversation(self.current_conversation["id"])
        self.chat_window.set_conversation(self.current_conversation)

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.grouped_history)
        self.sidebar.conversation_selected.connect(self.open_conversation)
        self.sidebar.new_chat_requested.connect(self.create_new_chat)
        root.addWidget(self.sidebar)

        self.chat_window = ChatWindow()
        self.chat_window.message_submitted.connect(self.handle_user_message)
        root.addWidget(self.chat_window, 1)

    def open_conversation(self, conversation: dict) -> None:
        self.current_conversation = conversation
        self.sidebar.set_active_conversation(conversation["id"])
        self.chat_window.set_conversation(conversation)

    def create_new_chat(self) -> None:
        conversation = {
            "id": "new-chat",
            "title": "新建对话",
            "subtitle": "从一个新的研究问题开始",
            "messages": [
                {"role": "assistant", "content": "新的对话已经创建。你可以直接输入研究问题、文献主题或想要整理的观点。"}
            ],
        }
        self.current_conversation = conversation
        self.sidebar.history_list.set_active("")
        self.chat_window.set_conversation(conversation)

    def handle_user_message(self, message: str) -> None:
        self.chat_window.add_message("user", message)
        reply = self._mock_reply(message)
        self.chat_window.add_message("assistant", reply)

    def _mock_reply(self, message: str) -> str:
        lowered = message.lower()
        if "综述" in message or "review" in lowered:
            return "可以。建议先按“研究背景、代表方法、关键争议、研究空白、未来方向”五段组织综述。"
        if "趋势" in message or "trend" in lowered:
            return "从 mock 数据来看，当前最适合展示的趋势模块是：主题热度、时间演进、代表作者和研究方法迁移。"
        if "图谱" in message or "网络" in message:
            return "前端层面可以先用作者、主题、论文三类节点呈现，并在右侧留出关系说明与筛选面板。"
        return "这是一个 mock 回复。当前版本只演示 Qt 前端交互，但页面结构已经为后续接入真实能力预留好了位置。"


class ScholarMindWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ScholarMind")
        self.resize(1520, 960)
        self._build_ui()
        self._apply_styles()
        self._enable_text_selection()

    def _build_ui(self) -> None:
        self.stack = QStackedWidget()
        self.login_page = LoginForm()
        self.login_page.login_requested.connect(self.enter_chat)
        self.main_page = MainChatPage(deepcopy(MOCK_HISTORY))
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.main_page)
        self.stack.setCurrentWidget(self.login_page)
        self.setCentralWidget(self.stack)

    def enter_chat(self) -> None:
        self.stack.setCurrentWidget(self.main_page)

    def _enable_text_selection(self) -> None:
        for label in self.findChildren(QLabel):
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #fbf9f5;
                color: #1b1c1a;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 13px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QPushButton {
                border: none;
            }
            QCheckBox {
                background: transparent;
            }
            QMainWindow, QScrollArea, QScrollArea > QWidget > QWidget {
                background: #fbf9f5;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 8px 4px 8px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(87, 101, 122, 0.32);
                min-height: 44px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(30, 64, 175, 0.42);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(0, 40, 142, 0.58);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
                border: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 12px;
                margin: 0 8px 4px 8px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(87, 101, 122, 0.32);
                min-width: 44px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(30, 64, 175, 0.42);
            }
            QScrollBar::handle:horizontal:pressed {
                background: rgba(0, 40, 142, 0.58);
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
                background: transparent;
                border: none;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
            }
            #loginHero {
                background: #1e40af;
            }
            #loginHeroBadge {
                background: rgba(255, 255, 255, 0.12);
                color: #dde1ff;
                border-radius: 999px;
                padding: 8px 14px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            #loginHeroTitle {
                color: white;
                font-family: "Georgia";
                font-size: 42px;
                font-weight: 700;
                line-height: 1.25;
            }
            #loginHeroText {
                color: #dde1ff;
                font-size: 15px;
                line-height: 1.8;
            }
            #loginHeroQuote {
                color: rgba(255,255,255,0.72);
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            #loginTitle, #chatPageTitle, #sidebarBrand, #cardTitle {
                font-family: "Georgia";
                font-weight: 700;
            }
            #loginTitle {
                font-size: 34px;
            }
            #loginSubtitle, #chatPageSubtitle, #sidebarSubtitle, #cardText, #bubbleText, #inputHelper {
                color: #57657a;
            }
            #loginTabActive {
                color: #00288e;
                font-weight: 700;
                border-bottom: 2px solid #00288e;
                padding-bottom: 10px;
            }
            #loginTab {
                color: #757684;
                font-weight: 600;
                padding-bottom: 10px;
            }
            #fieldLabel, #sidebarSection, #historyGroupTitle, #bubbleTitle {
                color: #757684;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            #loginField, #messageEditor {
                background: #f5f3ef;
                border: none;
                border-radius: 14px;
                padding: 14px 16px;
                color: #1b1c1a;
            }
            #rememberBox {
                color: #57657a;
            }
            #dividerText {
                color: #8a93a3;
                font-size: 12px;
            }
            #primaryButton {
                background: #00288e;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 14px 18px;
                font-weight: 700;
            }
            #secondaryButton {
                background: white;
                border: 1px solid rgba(196,197,213,0.42);
                border-radius: 14px;
                padding: 12px 16px;
                font-weight: 600;
            }
            #sidebar {
                background: #f5f3ef;
            }
            #sidebarBrand {
                font-size: 24px;
                color: #1e40af;
            }
            #sidebarSubtitle {
                font-size: 12px;
                margin-bottom: 8px;
            }
            #sidebarFooterButton {
                background: transparent;
                border: none;
                border-radius: 12px;
                padding: 10px 12px;
                text-align: left;
                color: #57657a;
                font-weight: 600;
            }
            #historyItem, #historyItemActive {
                border: none;
                text-align: left;
                border-radius: 12px;
                padding: 12px 14px;
                color: #57657a;
                background: transparent;
                font-weight: 600;
            }
            #historyItemActive {
                background: white;
                color: #1e40af;
                font-weight: 700;
            }
            #topActionButton {
                background: #f5f3ef;
                border: none;
                border-radius: 14px;
                padding: 10px 14px;
                color: #57657a;
                font-weight: 600;
            }
            #suggestionCard, #quoteCard, #metricCard, #assistantBubble, #userBubble {
                background: white;
                border: 1px solid rgba(196,197,213,0.18);
                border-radius: 18px;
            }
            #assistantBubble, #userBubble {
                max-width: 760px;
            }
            #userBubble {
                background: #dde1ff;
                border-color: rgba(30,64,175,0.18);
            }
            #iconTile {
                background: #dde1ff;
                border-radius: 12px;
            }
            #cardTitle {
                font-size: 22px;
            }
            #quoteText {
                color: #57657a;
                font-size: 20px;
                line-height: 1.7;
                font-style: italic;
            }
            #imageCard {
                background: #d8d6d1;
                border-radius: 18px;
            }
            #imagePlaceholder {
                min-height: 150px;
                color: #4b5565;
                font-size: 18px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            #metricValue {
                color: #1e40af;
                font-size: 52px;
                font-weight: 800;
            }
            #metricLabel {
                color: #57657a;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            #capsule {
                background: #d5e3fc;
                color: #57657a;
                border-radius: 999px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: 700;
            }
            #bubbleTitle {
                color: #1e40af;
            }
            #messageEditor {
                min-height: 110px;
            }
            """
        )


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("ScholarMind")
    window = ScholarMindWindow()
    window.show()
    sys.exit(app.exec())
