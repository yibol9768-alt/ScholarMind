from __future__ import annotations

from functools import partial

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QScrollArea, QTextEdit, QVBoxLayout, QWidget

from app.pages.base import BasePage
from app.widgets.common import LoadingWidget, make_button, make_label

PROMPT_CARDS = [
    {
        "title": "Trend Map",
        "desc": "识别近三年研究主题的演化路径与方法迁移。",
        "prompt": "请帮我梳理大语言模型在数字人文研究中的最新趋势，并标出值得继续跟进的主题。",
        "target": "trends",
    },
    {
        "title": "Literature Brief",
        "desc": "汇总代表论文、关键结论与引用脉络。",
        "prompt": "请总结数字人文方向近三年的代表性论文，并提炼核心结论与引用关系。",
        "target": "collection",
    },
    {
        "title": "Knowledge Graph",
        "desc": "抽取作者、任务、方法和数据集之间的关联。",
        "prompt": "请从现有文献中抽取作者、方法、任务与数据集，整理成知识网络视图。",
        "target": "extraction",
    },
    {
        "title": "Gap Finder",
        "desc": "定位尚未被充分验证的问题空间。",
        "prompt": "请结合当前热点与已知工作，识别值得切入的研究空白，并说明原因。",
        "target": "gaps",
    },
    {
        "title": "Idea Generator",
        "desc": "生成可执行的研究想法并评估风险。",
        "prompt": "请基于当前研究空白生成三个可执行的研究 idea，并评估创新性与风险。",
        "target": "ideas",
    },
    {
        "title": "Agent Run",
        "desc": "查看实验流程、日志和异常节点。",
        "prompt": "请展示当前 Agent 实验的运行进度，并给出下一步建议。",
        "target": "agent_run",
    },
]

INITIAL_MESSAGES = [
    {
        "role": "user",
        "content": "帮我分析一下大语言模型在数字人文领域的最新研究趋势，特别是跨学科应用的演化方向。",
    },
    {
        "role": "assistant",
        "content": "我已经汇总了趋势线索、代表性工作和后续可追踪的研究切口，下面先给你一个结构化摘要。",
    },
]

TARGET_LABELS = {
    "workflow": "工作流总览",
    "trends": "趋势分析",
    "collection": "文献获取",
    "extraction": "信息提取",
    "gaps": "研究空白",
    "ideas": "Idea 生成",
    "agent_run": "Agent 实验",
}

MARGINALIA = {
    "workflow": (
        "Recommended Reads",
        "重点回看知识图谱、证据绑定和工作流编排三条主线。",
        "Research Prompt",
        "是否可以把数字人文中的证据追踪框架迁移到多阶段 Agent 学术工作流？",
    ),
    "trends": (
        "Recommended Reads",
        "优先关注 LLMs for Digital Humanities、citation-grounded review 与 semantic mapping 方向。",
        "Research Prompt",
        "跨学科数字人文应用中，哪些任务最需要可验证引用与结构化证据绑定？",
    ),
    "collection": (
        "Recommended Reads",
        "建议先整理高被引综述，再补近 12 个月的新数据集与 benchmark。",
        "Research Prompt",
        "是否存在一套稳定的数字人文领域文献采集与去重标准流程？",
    ),
    "extraction": (
        "Recommended Reads",
        "重点抽取作者、任务、方法、数据集和评测协议五类实体。",
        "Research Prompt",
        "如何设计适用于数字人文语料的实体抽取 schema 与证据链接机制？",
    ),
    "gaps": (
        "Recommended Reads",
        "关注证据可追溯性、跨语种语料和多代理审校机制的缺口。",
        "Research Prompt",
        "数字人文中的事实核验是否可以通过句级证据绑定和 reviewer agent 联合解决？",
    ),
    "ideas": (
        "Recommended Reads",
        "优先筛选可以同时产出论文与工具化原型的题目。",
        "Research Prompt",
        "如何让一个研究 idea 同时具备方法创新、可复现流程和明确 benchmark？",
    ),
    "agent_run": (
        "Recommended Reads",
        "把日志、阶段状态和异常解释统一成一套实验轨迹视图。",
        "Research Prompt",
        "多代理科研流程中，哪些错误最适合通过审稿式 reviewer 节点来拦截？",
    ),
}


class ChatPage(BasePage):
    navigate_request = Signal(str)

    def __init__(self, navigator) -> None:
        super().__init__("chat", "主工作台", navigator)
        self.pending_target = "workflow"
        self.loading: LoadingWidget | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        stage = QWidget()
        stage_row = QHBoxLayout(stage)
        stage_row.setContentsMargins(0, 0, 0, 0)
        stage_row.setSpacing(0)

        manuscript = QWidget()
        manuscript.setObjectName("chatCanvas")
        manuscript_layout = QVBoxLayout(manuscript)
        manuscript_layout.setContentsMargins(10, 8, 10, 12)
        manuscript_layout.setSpacing(12)

        content_row = QHBoxLayout()
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(12)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("chatScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)

        self.scroll_host = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_host)
        self.scroll_layout.setContentsMargins(0, 6, 0, 14)
        self.scroll_layout.setSpacing(18)
        self.scroll.setWidget(self.scroll_host)
        left_layout.addWidget(self.scroll, 1)

        composer = self._build_composer()
        left_layout.addWidget(composer)
        left_layout.addWidget(
            make_label("AI 生成的分析结果仍需人工核验，重要结论请回看原始引文与上下文。", "footer_note")
        )

        right_panel = self._build_sidebar_rail()

        content_row.addWidget(left_panel, 7)
        content_row.addWidget(right_panel, 2)
        manuscript_layout.addLayout(content_row, 1)

        stage_row.addWidget(manuscript, 1)
        self.root.addWidget(stage, 1)

        for message in INITIAL_MESSAGES:
            self.add_message(message["role"], message["content"])
        self.add_structured_card(
            "趋势摘要",
            [
                "跨学科数字人文研究里，LLM 正从关键词抽取转向语义映射、证据归档与叙事重组。",
                "可验证引用、检索增强生成与多代理审校，正在成为研究型产品的重要基础能力。",
                "下一步最值得跟进的是跨语种语料对齐、结构化注释流程以及面向论文写作的协同工作流。",
            ],
            "trends",
        )
        QTimer.singleShot(0, self._scroll_to_bottom)

    def _build_intro(self) -> QFrame:
        hero = QFrame()
        hero.setObjectName("Card")
        hero.setProperty("variant", "editorialHero")
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        layout.addWidget(make_label("MANUSCRIPT ANALYZER", "workspace_eyebrow"))
        layout.addWidget(make_label("ScholarMind 主聊天工作台", "workspace_title"))
        layout.addWidget(
            make_label("把问题、线索、引文与下一步动作收束在同一页里，用手稿式工作流推进分析。", "workspace_subtitle")
        )

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(8)
        metrics.setVerticalSpacing(8)
        metrics.addWidget(self._build_metric_card("4.8k", "Sources"), 0, 0)
        metrics.addWidget(self._build_metric_card("12", "Steps"), 0, 1)
        metrics.addWidget(self._build_metric_card("91%", "Precision"), 1, 0)
        metrics.addWidget(self._build_metric_card("Live", "Context"), 1, 1)
        layout.addLayout(metrics)
        return hero

    def _build_metric_card(self, value: str, label: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setProperty("variant", "indicatorCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        layout.addWidget(make_label(value, "metric"))
        layout.addWidget(make_label(label, "metric_label"))
        return card

    def _build_prompt_grid(self) -> QWidget:
        host = QWidget()
        grid = QGridLayout(host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        for index, item in enumerate(PROMPT_CARDS):
            button = make_button(f"{item['title']}\n{item['desc']}", role="promptcard")
            button.clicked.connect(partial(self.run_suggestion, item))
            grid.addWidget(button, index, 0)
        return host

    def _build_prompt_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Card")
        panel.setProperty("variant", "sidebarModule")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(make_label("QUICK ACTIONS", "workspace_eyebrow"))
        layout.addWidget(make_label("快速开始", "sidebar_module_title"))
        layout.addWidget(make_label("选择一个常用分析入口，直接将问题发送到对应流程。", "sidebar_module_text"))
        layout.addWidget(self._build_prompt_grid())
        return panel

    def _build_sidebar_rail(self) -> QWidget:
        rail = QWidget()
        rail.setMinimumWidth(280)
        rail.setMaximumWidth(320)
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self._build_intro())
        layout.addWidget(self._build_prompt_panel())
        layout.addStretch(1)
        return rail

    def _build_composer(self) -> QFrame:
        box = QFrame()
        box.setObjectName("Card")
        box.setProperty("variant", "composerPanel")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(18, 18, 18, 18)
        box_layout.setSpacing(12)

        box_layout.addWidget(make_label("Ask ScholarMind", "workspace_eyebrow"))
        self.editor = QTextEdit()
        self.editor.setObjectName("composerEditor")
        self.editor.setPlaceholderText("输入研究问题，例如：请分析数字人文领域中 LLM 的趋势变化、代表方法和潜在研究空白。")
        self.editor.setMinimumHeight(116)
        self.editor.setMaximumHeight(152)
        box_layout.addWidget(self.editor)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        for text in ["附件", "语音", "图片"]:
            footer.addWidget(make_button(text, role="toolchip"))
        footer.addStretch(1)
        footer.addWidget(make_label("Send your prompt to continue the manuscript.", "composer_hint"))
        send = make_button("发送", primary=True)
        send.clicked.connect(self.submit_message)
        footer.addWidget(send)
        box_layout.addLayout(footer)

        shortcuts = QHBoxLayout()
        shortcuts.setSpacing(8)
        for text in ["History", "Browse Files", "Draft Essay"]:
            chip = make_button(text, role="utilitychip")
            shortcuts.addWidget(chip)
        shortcuts.addStretch(1)
        box_layout.addLayout(shortcuts)
        return box

    def _make_avatar(self, role: str) -> QFrame:
        avatar = QFrame()
        avatar.setObjectName("Card")
        avatar.setProperty("variant", "chatUserAvatar" if role == "user" else "chatAssistantAvatar")
        avatar.setFixedSize(42, 42)
        layout = QVBoxLayout(avatar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        text = "YOU" if role == "user" else "AI"
        label = make_label(text, "avatar_text")
        layout.addWidget(label, 0, Qt.AlignCenter)
        return avatar

    def add_message(self, role: str, text: str) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)

        bubble = QFrame()
        bubble.setObjectName("BubbleUser" if role == "user" else "BubbleAssistant")
        bubble.setMaximumWidth(760 if role == "user" else 980)
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)
        layout.addWidget(make_label("Researcher" if role == "user" else "ScholarMind", "chat_meta"))
        layout.addWidget(make_label(text, "chat_user_body" if role == "user" else "chat_body"))

        avatar = self._make_avatar(role)

        if role == "user":
            row_layout.addStretch(1)
            row_layout.addWidget(bubble, 0, Qt.AlignRight)
            row_layout.addWidget(avatar, 0, Qt.AlignTop)
        else:
            row_layout.addWidget(avatar, 0, Qt.AlignTop)
            row_layout.addWidget(bubble, 0, Qt.AlignLeft)
            row_layout.addStretch(1)

        self.scroll_layout.addWidget(row)
        QTimer.singleShot(0, self._scroll_to_bottom)

    def add_structured_card(self, title: str, lines: list[str], target: str) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(14)

        row_layout.addWidget(self._make_avatar("assistant"), 0, Qt.AlignTop)

        content = QVBoxLayout()
        content.setSpacing(12)

        card = QFrame()
        card.setObjectName("Card")
        card.setProperty("variant", "analysisCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(10)
        header.addWidget(make_label("AI Synthesis", "tertiary_badge"))
        header.addStretch(1)
        header.addWidget(make_label("Structured Review", "analysis_note"))
        card_layout.addLayout(header)

        card_layout.addWidget(make_label(title, "analysis_title"))

        for index, line in enumerate(lines, 1):
            line_row = QHBoxLayout()
            line_row.setSpacing(12)
            line_row.addWidget(make_label(f"{index:02d}.", "analysis_index"), 0, Qt.AlignTop)
            line_row.addWidget(make_label(line, "analysis_line"), 1)
            card_layout.addLayout(line_row)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        action_row.addStretch(1)
        button = make_button(f"进入{TARGET_LABELS.get(target, '下一步')}", primary=True)
        button.clicked.connect(partial(self.navigate_request.emit, target))
        action_row.addWidget(button)
        card_layout.addLayout(action_row)

        content.addWidget(card)
        content.addWidget(self._build_marginalia(target))
        row_layout.addLayout(content, 1)
        row_layout.addStretch(1)

        self.scroll_layout.addWidget(row)
        QTimer.singleShot(0, self._scroll_to_bottom)

    def _build_marginalia(self, target: str) -> QWidget:
        read_title, read_body, prompt_title, prompt_body = MARGINALIA.get(target, MARGINALIA["workflow"])
        host = QWidget()
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for title, body in [(read_title, read_body), (prompt_title, prompt_body)]:
            card = QFrame()
            card.setObjectName("Card")
            card.setProperty("variant", "marginaliaCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            card_layout.setSpacing(6)
            card_layout.addWidget(make_label(title, "marginalia_title"))
            card_layout.addWidget(make_label(body, "marginalia_body"))
            layout.addWidget(card)
        return host

    def run_suggestion(self, item: dict) -> None:
        self.editor.setPlainText(item["prompt"])
        self.submit_message(item["target"])

    def submit_message(self, auto_target: str | None = None) -> None:
        text = self.editor.toPlainText().strip()
        if not text:
            return
        self.pending_target = auto_target or "workflow"
        self.editor.clear()
        self.add_message("user", text)
        self.loading = LoadingWidget("ScholarMind 正在整理趋势、代表论文与下一步工作流建议...")
        self.scroll_layout.addWidget(self.loading, 0, Qt.AlignLeft)
        QTimer.singleShot(0, self._scroll_to_bottom)
        QTimer.singleShot(850, self.finish_reply)

    def finish_reply(self) -> None:
        if self.loading is not None:
            self.loading.deleteLater()
            self.loading = None
        self.add_message("assistant", "已完成初步分析。我整理了趋势判断、潜在空白以及推荐的后续研究动作。")
        self.add_structured_card(
            "趋势摘要",
            [
                "可信 RAG、句级证据绑定与可验证引用，正在快速成为研究型助手的基础能力。",
                "多 Agent 科研工作流已从综述整理延伸到实验执行、审校和结果回溯。",
                "建议先确认趋势分析，再进入研究空白识别与 Idea 生成，以形成完整选题链路。",
            ],
            self.pending_target,
        )

    def _scroll_to_bottom(self) -> None:
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())
