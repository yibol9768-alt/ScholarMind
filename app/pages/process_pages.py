from __future__ import annotations

from functools import partial

from PySide6.QtCore import QTimer, Qt, QSize, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QListWidget,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QLineEdit,
    QHeaderView,
    QFrame,
    QSizePolicy,
)

from app.mock.data import (
    AGENT_LOGS,
    AGENT_SUBTASKS,
    COLLECTION_SOURCES,
    EXPERIMENT_CONFIG,
    EXPLORATION_RESULT,
    EXTRACTION_CARDS,
    GAP_ITEMS,
    IDEAS,
    LITERATURE_RESULTS,
    REPOSITORY_TREE,
    RESULT_METRICS,
    TREND_RANKING,
    TREND_TOPICS,
    VALIDATION_TIMELINE,
    WRITING_SECTIONS,
)
from app.pages.base import BasePage
from app.widgets.common import CardWidget, LoadingWidget, SkeletonList, StatusTag, make_button, make_label
from app.widgets.layout import SearchBar


class WorkflowContentPage(BasePage):
    def nav_footer(self, previous_page: str | None, next_page: str | None, next_text: str) -> None:
        row = QHBoxLayout()
        if previous_page:
            back = make_button("上一步")
            back.clicked.connect(partial(self.navigate, previous_page))
            row.addWidget(back)
        row.addStretch(1)
        workflow = make_button("返回工作流总览")
        workflow.clicked.connect(partial(self.navigate, "workflow"))
        row.addWidget(workflow)
        home = make_button("返回主工作台")
        home.clicked.connect(partial(self.navigate, "chat"))
        row.addWidget(home)
        if next_page:
            next_button = make_button(next_text, primary=True)
            next_button.clicked.connect(partial(self.navigate, next_page))
            row.addWidget(next_button)
        self.root.addLayout(row)


class ExplorationPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("exploration", "领域探索与科研入门", navigator)
        hero = CardWidget("研究方向探索", "输入一个主题，生成领域简介、关键词、代表方向和入门论文。", variant="editorial")
        hero.layout.addWidget(make_label("Exploration Studio", "eyebrow"))
        self.topic_input = QTextEdit()
        self.topic_input.setMaximumHeight(88)
        self.topic_input.setPlainText("多模态大模型在医学文献分析中的应用")
        hero.layout.addWidget(self.topic_input)
        start = make_button("开始探索", primary=True)
        start.clicked.connect(self.start_exploration)
        hero.layout.addWidget(start)
        self.root.addWidget(hero)
        self.result_host = QVBoxLayout()
        self.root.addLayout(self.result_host)
        self.nav_footer(None, "collection", "开始文献获取")

    def start_exploration(self) -> None:
        self.clear_results()
        self.result_host.addWidget(SkeletonList(5))
        QTimer.singleShot(800, self.show_results)

    def show_results(self) -> None:
        self.clear_results()
        left, right = self.two_column()
        left.addWidget(CardWidget("领域简介", EXPLORATION_RESULT["summary"]))
        keyword = CardWidget("推荐关键词")
        for item in EXPLORATION_RESULT["keywords"]:
            keyword.layout.addWidget(make_label(item, "badge"))
        left.addWidget(keyword)
        direction = CardWidget("代表性方向")
        for item in EXPLORATION_RESULT["directions"]:
            direction.layout.addWidget(make_label(item))
        left.addWidget(direction)
        papers = CardWidget("推荐入门论文")
        for item in EXPLORATION_RESULT["papers"]:
            papers.layout.addWidget(make_label(item, "muted"))
        right.addWidget(papers)
        authors = CardWidget("热门作者 / 机构")
        authors.layout.addWidget(make_label("作者：" + "、".join(EXPLORATION_RESULT["authors"])))
        authors.layout.addWidget(make_label("机构：" + "、".join(EXPLORATION_RESULT["institutions"]), "muted"))
        right.addWidget(authors)

    def clear_results(self) -> None:
        while self.result_host.count():
            item = self.result_host.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class ExplorationPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("exploration", "领域探索与科研入门", navigator)
        self.root.setContentsMargins(18, 16, 18, 24)
        self.root.setSpacing(22)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        left_copy = QVBoxLayout()
        left_copy.setSpacing(6)
        left_copy.addWidget(make_label("知识库 / Domain Exploration", "workspace_eyebrow"))
        left_copy.addWidget(make_label("领域探索", "workspace_title"))
        left_copy.addWidget(
            make_label(
                "深入梳理学术前沿，发现交叉领域中的关键路径、潜在热点与代表性研究者。",
                "workspace_subtitle",
            )
        )
        header_layout.addLayout(left_copy, 1)

        header_actions = QHBoxLayout()
        header_actions.setSpacing(10)
        export_btn = make_button("导出报告", role="oidc")
        export_btn.clicked.connect(lambda: self._update_status_text("已准备导出当前领域探索报告。"))
        share_btn = make_button("分享研究", primary=True)
        share_btn.clicked.connect(lambda: self._update_status_text("已生成分享链接，可同步给协作者。"))
        header_actions.addWidget(export_btn)
        header_actions.addWidget(share_btn)
        header_layout.addLayout(header_actions)
        self.root.addWidget(header)

        composer = CardWidget(variant="explorationPrompt")
        composer.layout.setSpacing(14)
        composer.layout.addWidget(make_label("Exploration Studio", "eyebrow"))
        composer.layout.addWidget(make_label("输入研究主题", "exploration_panel_title"))
        composer.layout.addWidget(
            make_label(
                "围绕你的方向生成领域简介、推荐关键词、代表方向与研究者线索。",
                "muted",
            )
        )
        self.topic_input = QTextEdit()
        self.topic_input.setObjectName("explorationTopic")
        self.topic_input.setMinimumHeight(104)
        self.topic_input.setMaximumHeight(120)
        self.topic_input.setPlainText("多模态大模型在医学文献分析中的应用")
        composer.layout.addWidget(self.topic_input)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.start_exploration_btn = make_button("开始探索", primary=True)
        self.start_exploration_btn.clicked.connect(self.start_exploration)
        action_row.addWidget(self.start_exploration_btn)
        action_row.addStretch(1)
        composer.layout.addLayout(action_row)
        self.explore_status = make_label("当前结果基于最近一次主题探索生成。", "muted")
        composer.layout.addWidget(self.explore_status)
        self.root.addWidget(composer)

        self.result_host = QVBoxLayout()
        self.result_host.setContentsMargins(0, 0, 0, 0)
        self.result_host.setSpacing(0)
        self.root.addLayout(self.result_host)
        self.show_results()
        self.nav_footer(None, "collection", "下一步：文献获取")

    def start_exploration(self) -> None:
        self.clear_results()
        self.start_exploration_btn.setEnabled(False)
        self.start_exploration_btn.setText("探索中...")
        self._update_status_text("正在分析主题相关语义簇、作者网络与关键词热度...")
        self.result_host.addWidget(SkeletonList(5))
        QTimer.singleShot(800, self.show_results)

    def show_results(self) -> None:
        self.clear_results()
        document = CardWidget(variant="explorationDocument")
        document.layout.setContentsMargins(28, 28, 28, 28)
        document.layout.setSpacing(24)

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(24)

        left_col = QVBoxLayout()
        left_col.setSpacing(24)
        right_col = QVBoxLayout()
        right_col.setSpacing(24)

        left_col.addWidget(self._build_overview_section())
        left_col.addWidget(self._build_keyword_section())
        left_col.addWidget(self._build_direction_section())

        right_col.addWidget(self._build_people_section())
        right_col.addWidget(self._build_insight_section())
        right_col.addStretch(1)

        left_widget = QWidget()
        left_widget.setLayout(left_col)
        right_widget = QWidget()
        right_widget.setLayout(right_col)
        grid.addWidget(left_widget, 0, 0)
        grid.addWidget(right_widget, 0, 1)
        grid.setColumnStretch(0, 8)
        grid.setColumnStretch(1, 4)

        document.layout.addWidget(grid_host)
        self.result_host.addWidget(document)
        self.start_exploration_btn.setEnabled(True)
        self.start_exploration_btn.setText("开始探索")
        topic = self.topic_input.toPlainText().strip() or "当前主题"
        self._update_status_text(f"已完成主题“{topic}”的领域探索。")

    def _update_status_text(self, text: str) -> None:
        self.explore_status.setText(text)

    def _build_section_title(self, icon_text: str, title: str, accent: str = "primary") -> QWidget:
        host = QWidget()
        row = QHBoxLayout(host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        icon_box = QFrame()
        icon_box.setObjectName("Card")
        icon_box.setProperty("variant", "explorationIcon")
        icon_box.setProperty("accent", accent)
        icon_box.setFixedSize(40, 40)
        icon_layout = QVBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(make_label(icon_text, "exploration_icon_text"), 0, Qt.AlignCenter)

        row.addWidget(icon_box, 0, Qt.AlignTop)
        row.addWidget(make_label(title, "exploration_section_title"), 1)
        return host

    def _build_overview_section(self) -> QWidget:
        section = CardWidget(variant="explorationSection")
        section.layout.setSpacing(18)
        section.layout.addWidget(self._build_section_title("DS", "领域简介", "primary"))
        section.layout.addWidget(make_label(EXPLORATION_RESULT["summary"], "exploration_body"))
        section.layout.addWidget(
            make_label(
                "当前学术重心正从单纯提升模型指标，转向可解释性、跨模态对齐与临床或科研工作流中的可信应用。",
                "exploration_body",
            )
        )

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        stats_row.addWidget(self._build_stat_card("学术活跃度", "High", "+12% YoY", "primary"), 1)
        stats_row.addWidget(self._build_stat_card("关键研究路径", "Multi-modal", "452 篇新增文献", "tertiary"), 1)
        stats_row.addWidget(self._build_stat_card("引用峰值", "2.4k+", "月均引用增长", "neutral"), 1)
        section.layout.addLayout(stats_row)
        return section

    def _build_stat_card(self, label: str, value: str, note: str, accent: str) -> QWidget:
        card = QFrame()
        card.setObjectName("Card")
        card.setProperty("variant", "explorationStat")
        card.setProperty("accent", accent)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)
        layout.addWidget(make_label(label, "exploration_stat_label"))
        layout.addWidget(make_label(value, "exploration_stat_value"))
        layout.addWidget(make_label(note, "exploration_stat_note"))
        return card

    def _build_keyword_section(self) -> QWidget:
        section = CardWidget(variant="explorationSection")
        section.layout.setSpacing(18)
        section.layout.addWidget(self._build_section_title("KW", "推荐关键词", "tertiary"))

        chips = QWidget()
        chips_layout = QHBoxLayout(chips)
        chips_layout.setContentsMargins(0, 0, 0, 0)
        chips_layout.setSpacing(10)
        chips_layout.setAlignment(Qt.AlignLeft)
        for item in EXPLORATION_RESULT["keywords"]:
            chip = make_button(item, role="keywordChip")
            chip.clicked.connect(partial(self._update_status_text, f"已将关键词“{item}”加入当前探索语境。"))
            chips_layout.addWidget(chip)
        more_chip = make_button("更多领域", role="keywordChipGhost")
        more_chip.clicked.connect(lambda: self._update_status_text("可继续扩展相关子领域与交叉方向。"))
        chips_layout.addWidget(more_chip)
        chips_layout.addStretch(1)
        section.layout.addWidget(chips)

        chart = QFrame()
        chart.setObjectName("Card")
        chart.setProperty("variant", "explorationChart")
        chart_layout = QVBoxLayout(chart)
        chart_layout.setContentsMargins(18, 18, 18, 18)
        chart_layout.setSpacing(12)

        bars = QHBoxLayout()
        bars.setSpacing(8)
        for height in [48, 78, 56, 112, 92, 68, 104]:
            bar = QFrame()
            bar.setObjectName("Card")
            bar.setProperty("variant", "explorationBar")
            bar.setFixedWidth(34)
            bar.setMinimumHeight(height)
            bars.addWidget(bar, 0, Qt.AlignBottom)
        bars.addStretch(1)
        chart_layout.addLayout(bars)
        chart_layout.addWidget(make_label("关键词搜索热度趋势分析（过去 30 天）", "exploration_chart_note"))
        section.layout.addWidget(chart)
        return section

    def _build_direction_section(self) -> QWidget:
        section = CardWidget(variant="explorationSection")
        section.layout.setSpacing(18)
        section.layout.addWidget(self._build_section_title("RD", "代表方向与入门论文", "neutral"))

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        direction_card = CardWidget(variant="explorationMiniPanel")
        direction_card.layout.addWidget(make_label("代表方向", "exploration_panel_title"))
        for item in EXPLORATION_RESULT["directions"]:
            direction_card.layout.addWidget(make_label("• " + item, "exploration_list_item"))
        cards_row.addWidget(direction_card, 1)

        paper_card = CardWidget(variant="explorationMiniPanel")
        paper_card.layout.addWidget(make_label("入门论文", "exploration_panel_title"))
        for item in EXPLORATION_RESULT["papers"]:
            paper_card.layout.addWidget(make_label(item, "exploration_list_item"))
        cards_row.addWidget(paper_card, 1)

        section.layout.addLayout(cards_row)
        return section

    def _build_people_section(self) -> QWidget:
        section = CardWidget(variant="explorationSection")
        section.layout.setSpacing(18)
        section.layout.addWidget(self._build_section_title("AU", "热门作者与机构", "neutral"))

        for author, institution in zip(EXPLORATION_RESULT["authors"], EXPLORATION_RESULT["institutions"]):
            section.layout.addWidget(self._build_person_row(author, institution))

        divider = QFrame()
        divider.setObjectName("explorationDivider")
        divider.setFixedHeight(1)
        section.layout.addWidget(divider)

        for institution in EXPLORATION_RESULT["institutions"]:
            section.layout.addWidget(self._build_institution_row(institution))

        all_btn = make_button("查看全领域贡献排行", role="explorationLink")
        all_btn.clicked.connect(lambda: self._update_status_text("已切换到全领域作者与机构贡献视图。"))
        section.layout.addWidget(all_btn)
        return section

    def _build_person_row(self, name: str, institution: str) -> QWidget:
        row_card = QFrame()
        row_card.setObjectName("Card")
        row_card.setProperty("variant", "explorationPerson")
        layout = QHBoxLayout(row_card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        avatar = QFrame()
        avatar.setObjectName("Card")
        avatar.setProperty("variant", "explorationAvatar")
        avatar.setFixedSize(44, 44)
        avatar_layout = QVBoxLayout(avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.addWidget(make_label(name[:1], "exploration_avatar_text"), 0, Qt.AlignCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.addWidget(make_label(name, "exploration_person_name"))
        text_col.addWidget(make_label(institution, "exploration_person_meta"))

        layout.addWidget(avatar)
        layout.addLayout(text_col, 1)
        layout.addWidget(make_label("UP", "exploration_trend"), 0, Qt.AlignCenter)
        return row_card

    def _build_institution_row(self, name: str) -> QWidget:
        row_card = QFrame()
        row_card.setObjectName("Card")
        row_card.setProperty("variant", "explorationInstitution")
        layout = QHBoxLayout(row_card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        mark = QFrame()
        mark.setObjectName("Card")
        mark.setProperty("variant", "explorationInstitutionMark")
        mark.setFixedSize(40, 40)
        mark_layout = QVBoxLayout(mark)
        mark_layout.setContentsMargins(0, 0, 0, 0)
        mark_layout.addWidget(make_label(name[:1], "exploration_avatar_text"), 0, Qt.AlignCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.addWidget(make_label(name, "exploration_person_name"))
        text_col.addWidget(make_label("相关文献持续增长", "exploration_person_meta"))
        layout.addWidget(mark)
        layout.addLayout(text_col, 1)
        return row_card

    def _build_insight_section(self) -> QWidget:
        card = CardWidget(variant="explorationInsight")
        card.layout.setSpacing(12)
        card.layout.addWidget(make_label("AI 洞察", "exploration_panel_title"))
        card.layout.addWidget(
            make_label(
                "跨学科融合仍是当前最具突破潜力的方向，尤其值得关注知识图谱、可信推理与多模态检索的结合。",
                "exploration_insight_body",
            )
        )
        card.layout.addWidget(make_label("12 位同领域研究者正在持续关注这一方向", "exploration_chart_note"))
        return card

    def clear_results(self) -> None:
        while self.result_host.count():
            item = self.result_host.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class SourceOptionCard(QFrame):
    def __init__(self, icon_text: str, title: str, description: str, checked: bool) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setProperty("variant", "sourceCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName(f"{title} 数据源")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 18)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        self.icon_box = QFrame()
        self.icon_box.setObjectName("Card")
        self.icon_box.setProperty("variant", "sourceIcon")
        self.icon_box.setFixedSize(44, 44)
        icon_layout = QVBoxLayout(self.icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(make_label(icon_text, "source_icon_text"), 0, Qt.AlignCenter)
        top_row.addWidget(self.icon_box)
        top_row.addStretch(1)

        self.checkbox = QCheckBox()
        self.checkbox.setObjectName("sourceToggle")
        self.checkbox.setChecked(checked)
        self.checkbox.setAccessibleName(f"选择 {title}")
        self.checkbox.toggled.connect(self._sync_state)
        top_row.addWidget(self.checkbox, 0, Qt.AlignTop)
        layout.addLayout(top_row)

        layout.addWidget(make_label(title, "source_card_title"))
        desc_label = make_label(description, "source_card_desc")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        self._sync_state(checked)

    def _sync_state(self, checked: bool) -> None:
        selected = "true" if checked else "false"
        self.setProperty("selected", selected)
        self.icon_box.setProperty("selected", selected)
        for widget in (self, self.icon_box):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.checkbox.toggle()
            event.accept()
            return
        super().mousePressEvent(event)


class TableIconButton(QPushButton):
    def __init__(self, kind: str, accessible_name: str, tooltip: str) -> None:
        super().__init__()
        self.kind = kind
        self.setAccessibleName(accessible_name)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(32, 32)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFlat(True)
        self.setAutoDefault(False)
        self.setDefault(False)
        self.setStyleSheet("background: transparent; border: none;")

    def sizeHint(self) -> QSize:
        return QSize(32, 32)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))
        if self.isEnabled():
            border = QColor("#c8d3f0") if not self.underMouse() else QColor("#9ab0ea")
            fill = QColor("#ffffff") if not self.isDown() else QColor("#e9eefc")
            icon = QColor("#00288e")
        else:
            border = QColor(210, 214, 223)
            fill = QColor(244, 242, 238)
            icon = QColor(140, 149, 163)

        painter.setPen(QPen(border, 1))
        painter.setBrush(fill)
        painter.drawRoundedRect(rect, 9, 9)

        if self.hasFocus():
            focus_rect = rect.adjusted(1, 1, -1, -1)
            painter.setPen(QPen(QColor("#4b6fd6"), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(focus_rect, 8, 8)

        painter.setPen(QPen(icon, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)

        if self.kind == "preview":
            path = QPainterPath()
            path.moveTo(8, 16)
            path.quadTo(16, 9, 24, 16)
            path.quadTo(16, 23, 8, 16)
            painter.drawPath(path)
            painter.setBrush(icon)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(14.2, 14.2, 3.6, 3.6))
        else:
            painter.drawLine(16, 9, 16, 18)
            painter.drawLine(12.5, 15.2, 16, 18.8)
            painter.drawLine(19.5, 15.2, 16, 18.8)
            painter.setPen(QPen(icon, 1.6, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(11, 22.5, 21, 22.5)


class CollectionPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("collection", "文献获取与预处理", navigator)
        self.root.setContentsMargins(18, 16, 18, 24)
        self.root.setSpacing(22)
        self.source_cards: list[SourceOptionCard] = []
        self.preview_rows = [
            ("completed", "Attention Is All You Need: Scaling Large Language Models", "arXiv", "2023", "已获取"),
            ("completed", "Biological Neuronal Models vs Artificial Attention Mechanisms", "PubMed", "2024", "已获取"),
            ("in_progress", "Deep Reinforcement Learning in Clinical Diagnostic Support", "Crossref", "2022", "解析中"),
            ("not_started", "The Future of Scholarly Communication in the AI Era", "Semantic Scholar", "2024", "排队中"),
        ]

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        header_layout.addWidget(make_label("文献获取与预处理", "workspace_title"))
        header_layout.addWidget(make_label("选择学术数据库并设定检索参数，自动汇集候选论文并进入后续抽取流程。", "workspace_subtitle"))
        self.root.addWidget(header)

        grid_row = QHBoxLayout()
        grid_row.setSpacing(24)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)

        sources_header = QHBoxLayout()
        sources_header.addWidget(make_label("数据源", "eyebrow"))
        sources_header.addStretch(1)
        self.sources_badge = make_label("4 个可用源", "source_count_badge")
        sources_header.addWidget(self.sources_badge)
        left_layout.addLayout(sources_header)

        sources_grid = QGridLayout()
        sources_grid.setContentsMargins(0, 4, 0, 0)
        sources_grid.setSpacing(16)
        
        sources_data = [
            ("AX", "arXiv", "覆盖物理、数学、计算机科学与定量生物学。", True),
            ("PM", "PubMed", "面向生物医学与生命科学文献的 MEDLINE 检索入口。", True),
            ("CR", "Crossref", "提供 DOI 与学术元数据的全局注册与解析。", False),
            ("SS", "Semantic Scholar", "AI 驱动的学术搜索与文献发现平台。", False),
        ]
        
        for idx, (icon_text, title, desc, checked) in enumerate(sources_data):
            card = SourceOptionCard(icon_text, title, desc, checked)
            card.checkbox.toggled.connect(self._update_fetch_button_state)
            self.source_cards.append(card)
            sources_grid.addWidget(card, idx // 2, idx % 2)
            
        left_layout.addLayout(sources_grid)
        grid_row.addWidget(left_panel, 2)

        right_panel = CardWidget(variant="collectionAside")
        right_layout = right_panel.layout
        right_layout.setSpacing(12)
        right_layout.addWidget(make_label("检索参数", "eyebrow"))
        right_layout.addSpacing(16)

        right_layout.addWidget(make_label("研究领域", "eyebrow"))
        self.domain_box = QComboBox()
        self.domain_box.addItems(["人工智能", "神经科学", "分子生物学", "量子计算"])
        self._mark_panel_field(self.domain_box)
        right_layout.addWidget(self.domain_box)
        right_layout.addSpacing(8)

        right_layout.addWidget(make_label("关键词", "eyebrow"))
        self.keyword_box = QLineEdit()
        self.keyword_box.setPlaceholderText("例如：LLM、Transformer、Attention")
        self._mark_panel_field(self.keyword_box)
        right_layout.addWidget(self.keyword_box)
        right_layout.addSpacing(8)

        year_row = QHBoxLayout()
        year_row.setSpacing(12)
        year_from_layout = QVBoxLayout()
        year_from_layout.setSpacing(6)
        year_from_layout.addWidget(make_label("起始年份", "eyebrow"))
        self.year_from = QLineEdit("2020")
        self._mark_panel_field(self.year_from)
        year_from_layout.addWidget(self.year_from)
        year_row.addLayout(year_from_layout)
        
        year_to_layout = QVBoxLayout()
        year_to_layout.setSpacing(6)
        year_to_layout.addWidget(make_label("截止年份", "eyebrow"))
        self.year_to = QLineEdit("2024")
        self._mark_panel_field(self.year_to)
        year_to_layout.addWidget(self.year_to)
        year_row.addLayout(year_to_layout)
        right_layout.addLayout(year_row)
        
        right_layout.addSpacing(18)
        self.start_btn = make_button("开始抓取", primary=True)
        self.start_btn.setMinimumHeight(52)
        self.start_btn.clicked.connect(self.start_fetch)
        right_layout.addWidget(self.start_btn)
        
        grid_row.addWidget(right_panel, 1)
        self.root.addLayout(grid_row)

        live_card = CardWidget(variant="collectionLive")
        live_layout = live_card.layout
        live_layout.setSpacing(18)
        
        live_header = QHBoxLayout()
        live_titles = QVBoxLayout()
        live_titles.setSpacing(4)
        live_titles.addWidget(make_label("实时采集进度", "section"))
        self.status_msg = make_label("采集完成，可进入下一步。", "muted")
        live_titles.addWidget(self.status_msg)
        live_header.addLayout(live_titles)
        live_header.addStretch(1)
        
        pct_layout = QVBoxLayout()
        pct_layout.setSpacing(2)
        self.pct_label = make_label("0%", "metric")
        pct_layout.addWidget(self.pct_label, 0, Qt.AlignRight)
        pct_layout.addWidget(make_label("已处理", "eyebrow"), 0, Qt.AlignRight)
        live_header.addLayout(pct_layout)
        live_layout.addLayout(live_header)
        
        self.progress = QProgressBar()
        self.progress.setObjectName("collectionProgress")
        self.progress.setTextVisible(False)
        self.progress.setValue(0)
        self.progress.setFixedHeight(8)
        live_layout.addWidget(self.progress)
        live_layout.addSpacing(8)
        
        self.table = QTableWidget(0, 5)
        self.table.setObjectName("collectionTable")
        self.table.setHorizontalHeaderLabels(["状态", "文献信息", "来源", "年份", "操作"])
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 104)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setWordWrap(False)
        self.table.setMouseTracking(True)
        self.table.setMinimumHeight(320)
        self.table.setStyleSheet(
            """
            QTableWidget#collectionTable {
                outline: none;
                border: none;
                background: transparent;
            }
            QTableWidget#collectionTable::item {
                padding: 18px 16px;
                border-bottom: 1px solid rgba(117,118,132,0.10);
            }
            QTableWidget#collectionTable::item:hover {
                background: rgba(245,243,239,0.55);
            }
            QTableWidget#collectionTable::item:selected {
                background: transparent;
                color: palette(text);
            }
            QHeaderView::section {
                background: transparent;
                border: none;
                border-bottom: 1px solid rgba(117,118,132,0.12);
                padding: 0 16px 12px 16px;
                font-size: 11px;
                font-weight: 700;
            }
            """
        )
        
        live_layout.addWidget(self.table)
        self.root.addWidget(live_card)
        self._show_completed_state()
        self._update_fetch_button_state()
        self.nav_footer("exploration", "extraction", "下一步：关键信息提取")

    def _mark_panel_field(self, widget: QWidget) -> None:
        widget.setProperty("panel", "true")
        widget.setMinimumHeight(42)

    def _update_fetch_button_state(self) -> None:
        self.start_btn.setEnabled(any(card.is_checked() for card in self.source_cards))

    def _populate_table(self, rows: list[tuple[str, str, str, str, str]]) -> None:
        self.table.setRowCount(0)
        for row_idx, row in enumerate(rows):
            self._insert_table_row(row_idx, *row)

    def _insert_table_row(self, row_idx: int, status: str, title: str, source: str, year: str, status_str: str) -> None:
        self.table.insertRow(row_idx)
        can_open = status == "completed"

        tag_widget = QWidget()
        tag_widget.setObjectName("collectionStatusWrap")
        tag_layout = QHBoxLayout(tag_widget)
        tag_layout.setContentsMargins(16, 0, 0, 0)
        tag_layout.setSpacing(0)
        tag_layout.addWidget(StatusTag(status, status_str))
        tag_layout.addStretch(1)
        self.table.setCellWidget(row_idx, 0, tag_widget)
        
        title_item = QTableWidgetItem(title)
        title_item.setToolTip(title)
        self.table.setItem(row_idx, 1, title_item)
        
        src_item = QTableWidgetItem(source)
        self.table.setItem(row_idx, 2, src_item)
        
        year_item = QTableWidgetItem(year)
        year_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row_idx, 3, year_item)

        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_widget.setFixedWidth(80)
        action_widget.setFixedHeight(32)
        action_widget.setStyleSheet("background: transparent;")
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        action_layout.setAlignment(Qt.AlignCenter)
        preview_btn = make_button("预览", role="tableAction")
        preview_btn.setToolTip(f"预览 {title}")
        preview_btn.setEnabled(can_open)
        preview_btn.clicked.connect(partial(self._preview_paper, title))
        preview_btn.setText("\U0001F441")
        preview_btn.setAccessibleName("预览")
        preview_btn.setText("预览")
        preview_btn.setMinimumWidth(38)
        preview_btn.setMinimumHeight(30)
        preview_btn.setText("\U0001F441")
        download_btn = make_button("下载", role="tableAction")
        download_btn.setToolTip(f"下载 {title}")
        download_btn.setEnabled(can_open)
        download_btn.clicked.connect(partial(self._download_paper, title))
        download_btn.setText("\u2B73")
        download_btn.setAccessibleName("下载")
        download_btn.setText("下载")
        download_btn.setMinimumWidth(38)
        download_btn.setMinimumHeight(30)
        download_btn.setText("\u2B73")
        preview_btn = TableIconButton("preview", "预览", f"预览 {title}")
        preview_btn.setEnabled(can_open)
        preview_btn.clicked.connect(partial(self._preview_paper, title))
        download_btn = TableIconButton("download", "下载", f"下载 {title}")
        download_btn.setEnabled(can_open)
        download_btn.clicked.connect(partial(self._download_paper, title))
        action_layout.addWidget(preview_btn)
        action_layout.addWidget(download_btn)
        self.table.setCellWidget(row_idx, 4, action_widget)
        self.table.setRowHeight(row_idx, 62)

        title_font = QFont()
        title_font.setFamilies(["Segoe UI Variable Text", "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei"])
        title_font.setPointSize(11)
        title_font.setWeight(QFont.DemiBold)
        meta_font = QFont()
        meta_font.setFamilies(["Segoe UI Variable Text", "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei"])
        meta_font.setPointSize(10)
        meta_font.setWeight(QFont.Medium)
        title_item.setFont(title_font)
        src_item.setFont(meta_font)
        year_item.setFont(meta_font)

        if status == "completed":
            title_color = QColor("#1b1c1a")
            meta_color = QColor("#57657a")
        elif status == "in_progress":
            title_color = QColor(27, 28, 26, 150)
            meta_color = QColor(87, 101, 122, 150)
        else:
            title_color = QColor(27, 28, 26, 105)
            meta_color = QColor(87, 101, 122, 105)

        title_item.setForeground(title_color)
        src_item.setForeground(meta_color)
        year_item.setForeground(meta_color)

    def _preview_paper(self, title: str) -> None:
        self.status_msg.setText(f"正在预览：{title}")

    def _download_paper(self, title: str) -> None:
        self.status_msg.setText(f"已加入下载队列：{title}")

    def _show_completed_state(self) -> None:
        self.progress.setValue(100)
        self.pct_label.setText("100%")
        self.status_msg.setText("采集完成，可进入下一步。")
        self._populate_table(
            [
                ("completed", "Attention Is All You Need: Scaling Large Language Models", "arXiv", "2023", "已获取"),
                ("completed", "Biological Neuronal Models vs Artificial Attention Mechanisms", "PubMed", "2024", "已获取"),
                ("completed", "Deep Reinforcement Learning in Clinical Diagnostic Support", "Crossref", "2022", "已获取"),
                ("completed", "The Future of Scholarly Communication in the AI Era", "Semantic Scholar", "2024", "已获取"),
            ]
        )

    def start_fetch(self) -> None:
        self.table.setRowCount(0)
        self.start_btn.setEnabled(False)
        self.start_btn.setText("抓取中...")
        self.progress.setValue(15)
        self.pct_label.setText("15%")
        self.status_msg.setText("正在扫描已选数据源并匹配相关元数据...")
        QTimer.singleShot(600, self._step_two)

    def _step_two(self) -> None:
        self.progress.setValue(64)
        self.pct_label.setText("64%")
        self.status_msg.setText("已完成首批结果抓取，正在解析剩余文献...")
        self._populate_table(self.preview_rows)
        QTimer.singleShot(1200, self._step_three)
        
    def _step_three(self) -> None:
        self.start_btn.setText("开始抓取")
        self._show_completed_state()
        self._update_fetch_button_state()



class ExtractionPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("extraction", "关键信息提取", navigator)
        host = QWidget()
        grid = QGridLayout(host)
        grid.setSpacing(14)
        for index, (title, desc) in enumerate(EXTRACTION_CARDS):
            card = CardWidget(title, desc, clickable=True)
            card.layout.addWidget(make_button("查看详情"))
            grid.addWidget(card, index // 2, index % 2)
        self.root.addWidget(host)
        self.graph = CardWidget("知识图谱预览", "点击构建图谱后展示 mock 节点图。", variant="soft")
        build = make_button("构建图谱", primary=True)
        build.clicked.connect(self.build_graph)
        self.graph.layout.addWidget(build)
        self.root.addWidget(self.graph)
        self.nav_footer("collection", "trends", "下一步：趋势分析")

    def build_graph(self) -> None:
        self.graph.layout.addWidget(LoadingWidget("正在构建知识图谱和引用关系..."))
        QTimer.singleShot(800, lambda: self.graph.layout.addWidget(make_label("已完成：核心节点 64 个，主要关系边 284 条。")))


class TrendPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("trends", "主题建模与趋势分析", navigator)
        toolbar = CardWidget("趋势分析控制台", "切换时间范围可查看不同主题热度变化。", variant="editorial")
        self.range_box = QComboBox()
        self.range_box.addItems(["近 3 年", "近 5 年", "近 10 年"])
        self.range_box.currentIndexChanged.connect(self.refresh_data)
        toolbar.layout.addWidget(self.range_box)
        self.root.addWidget(toolbar)
        self.topic_host = QVBoxLayout()
        self.root.addLayout(self.topic_host)
        self.refresh_data()
        self.nav_footer("extraction", "gaps", "识别研究空白")

    def refresh_data(self) -> None:
        while self.topic_host.count():
            item = self.topic_host.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        chart = CardWidget("主题演化图", f"时间范围：{self.range_box.currentText()}。", variant="soft")
        for line in ["2023 ▂▃▅ 可信 RAG", "2024 ▃▅▆ 多 Agent 科研流程", "2025 ▄▆█ 医学多模态对齐"]:
            chart.layout.addWidget(make_label(line))
        self.topic_host.addWidget(chart)
        host = QWidget()
        grid = QGridLayout(host)
        for idx, (title, heat, desc) in enumerate(TREND_TOPICS):
            card = CardWidget(title, f"{heat} · {desc}", clickable=True)
            card.layout.addWidget(make_button("查看详情"))
            grid.addWidget(card, 0, idx)
        self.topic_host.addWidget(host)
        ranking = CardWidget("热门论文排行")
        for item in TREND_RANKING:
            ranking.layout.addWidget(make_label(item, "muted"))
        self.topic_host.addWidget(ranking)


class GapPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("gaps", "研究空白识别与选题开题", navigator)
        self.root.addWidget(CardWidget("当前研究热点摘要", "可信 RAG、证据绑定、多 Agent 协作和医学多模态对齐是当前最活跃方向。", variant="editorial"))
        for item in GAP_ITEMS:
            card = CardWidget(item["title"], item["reason"], clickable=True)
            row = QHBoxLayout()
            row.addWidget(StatusTag("risk", f"风险：{item['risk']}"))
            row.addStretch(1)
            for text in ["采纳", "收藏", "继续挖掘"]:
                row.addWidget(make_button(text))
            card.layout.addLayout(row)
            self.root.addWidget(card)
        score = CardWidget("选题评分", "创新性 89 / 可行性 78")
        generate = make_button("生成 Idea", primary=True)
        generate.clicked.connect(partial(self.navigate, "ideas"))
        score.layout.addWidget(generate)
        self.root.addWidget(score)
        self.nav_footer("trends", "ideas", "下一步：生成 Idea")


class IdeaPage(WorkflowContentPage):
    def __init__(self, navigator, state) -> None:
        super().__init__("ideas", "Idea 生成与打分", navigator)
        self.state = state
        row = QHBoxLayout()
        list_col = QWidget()
        list_layout = QVBoxLayout(list_col)
        self.detail = CardWidget("Idea 详情", "点击左侧候选项查看详细论证。", variant="soft")
        for idea in IDEAS:
            button = QPushButton(
                f"{idea['title']}\n创新性 {idea['innovation']} · 可行性 {idea['feasibility']} · 风险 {idea['risk']}"
            )
            button.setProperty("role", "task")
            button.clicked.connect(partial(self.show_detail, idea))
            list_layout.addWidget(button)
        list_layout.addWidget(make_button("重新生成"))
        row.addWidget(list_col, 1)
        row.addWidget(self.detail, 1)
        self.root.addLayout(row)
        self.show_detail(IDEAS[0])
        self.nav_footer("gaps", "repository", "进入代码仓库生成")

    def show_detail(self, idea: dict) -> None:
        self.state.current_idea_id = idea["id"]
        while self.detail.layout.count():
            item = self.detail.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.detail.layout.addWidget(make_label(idea["title"], "section"))
        self.detail.layout.addWidget(make_label(idea["core"]))
        self.detail.layout.addWidget(make_label(idea["detail"], "muted"))
        self.detail.layout.addWidget(make_label(f"推荐理由：{idea['reason']}"))
        choose = make_button("选择该 Idea", primary=True)
        choose.clicked.connect(partial(self.navigate, "repository"))
        self.detail.layout.addWidget(choose)


class RepositoryPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("repository", "代码仓库生成", navigator)
        row = QHBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["仓库结构"])
        for path in REPOSITORY_TREE:
            self.tree.addTopLevelItem(QTreeWidgetItem([path]))
        self.tree.itemClicked.connect(self.show_file)
        row.addWidget(self.tree, 1)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        row.addWidget(self.preview, 1)
        self.root.addLayout(row)
        action = CardWidget("操作", "仓库结构和 README 已按 Idea 自动生成。", variant="soft")
        for text in ["复制仓库结构", "导出模板", "打开实验设计"]:
            button = make_button(text, primary=text == "打开实验设计")
            if text == "打开实验设计":
                button.clicked.connect(partial(self.navigate, "experiment_design"))
            action.layout.addWidget(button)
        self.root.addWidget(action)
        self.show_file(self.tree.topLevelItem(0))
        self.nav_footer("ideas", "experiment_design", "打开实验设计")

    def show_file(self, item, _column: int = 0) -> None:
        self.preview.setPlainText(REPOSITORY_TREE.get(item.text(0), ""))


class ExperimentDesignPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("experiment_design", "实验设计与研究实施", navigator)
        for title, values in [
            ("实验计划", EXPERIMENT_CONFIG["plans"]),
            ("数据集选择", EXPERIMENT_CONFIG["datasets"]),
            ("模型配置", EXPERIMENT_CONFIG["models"]),
            ("超参数", EXPERIMENT_CONFIG["params"]),
        ]:
            card = CardWidget(title, variant="soft")
            row = QHBoxLayout()
            for value in values:
                button = QPushButton(value)
                button.setCheckable(True)
                row.addWidget(button)
            card.layout.addLayout(row)
            self.root.addWidget(card)
        timeline = CardWidget("实验步骤时间线", variant="editorial")
        for step in ["准备数据", "运行基线", "加入证据绑定", "误差分析", "汇总结论"]:
            timeline.layout.addWidget(make_label(step, "muted"))
        run = make_button("开始 Agent 实验", primary=True)
        run.clicked.connect(partial(self.navigate, "agent_run"))
        timeline.layout.addWidget(run)
        self.root.addWidget(timeline)
        self.nav_footer("repository", "agent_run", "开始 Agent 实验")


class AgentRunPage(WorkflowContentPage):
    def __init__(self, navigator, state) -> None:
        super().__init__("agent_run", "Agent 实验运行", navigator)
        self.state = state
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)
        self.log_index = 0
        overview = CardWidget("运行状态总览", "使用 QTimer 模拟自动化实验推进。", variant="editorial")
        self.progress = QProgressBar()
        self.progress.setValue(0)
        overview.layout.addWidget(self.progress)
        controls = QHBoxLayout()
        resume = make_button("继续", primary=True)
        resume.clicked.connect(self.resume_run)
        pause = make_button("暂停")
        pause.clicked.connect(self.timer.stop)
        terminate = make_button("终止")
        self.result_btn = make_button("查看结果")
        self.result_btn.setEnabled(False)
        self.result_btn.clicked.connect(partial(self.navigate, "results"))
        for button in [pause, resume, terminate, self.result_btn]:
            controls.addWidget(button)
        overview.layout.addLayout(controls)
        self.root.addWidget(overview)
        row = QHBoxLayout()
        self.log_card = QTextEdit()
        self.log_card.setReadOnly(True)
        row.addWidget(self.log_card, 2)
        subtasks = CardWidget("子任务状态", variant="soft")
        for name, status in AGENT_SUBTASKS:
            mapped = status if status in {"completed", "in_progress", "risk"} else "not_started"
            if status == "running":
                mapped = "in_progress"
            subtasks.layout.addWidget(StatusTag(mapped, name))
        subtasks.layout.addWidget(make_label("资源占用：GPU 63% / CPU 41% / 内存 22GB", "muted"))
        row.addWidget(subtasks, 1)
        self.root.addLayout(row)
        self.resume_run()
        self.nav_footer("experiment_design", "results", "查看结果")

    def resume_run(self) -> None:
        self.timer.start(500)

    def advance(self) -> None:
        value = min(100, self.progress.value() + 8)
        self.progress.setValue(value)
        if self.log_index < len(AGENT_LOGS):
            self.log_card.append(AGENT_LOGS[self.log_index])
            self.log_index += 1
        if value >= 100:
            self.timer.stop()
            self.result_btn.setEnabled(True)
            self.log_card.append("[09:13:25] 实验完成，结果分析已就绪")


class ResultsPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("results", "结果分析", navigator)
        host = QWidget()
        grid = QGridLayout(host)
        for index, (name, value, delta) in enumerate(RESULT_METRICS):
            card = CardWidget(name, f"{value} / 变化 {delta}", variant="soft")
            grid.addWidget(card, index // 2, index % 2)
        self.root.addWidget(host)
        summary = CardWidget("实验结论摘要", "证据绑定方案在引用精度和事实一致性上优于基线，但仍有延迟与数据质量风险。", variant="editorial")
        summary.layout.addWidget(make_label("优势：引用更准确、错误案例更易追溯。"))
        summary.layout.addWidget(make_label("不足：推理耗时略高，跨模态证据对齐仍有缺口。", "muted"))
        summary.layout.addWidget(StatusTag("risk", "失败原因提示：少量样本缺失影像标注"))
        self.root.addWidget(summary)
        decision = CardWidget("是否达到目标", "当前版本已满足论文初稿撰写条件。")
        iterate = make_button("继续优化")
        iterate.clicked.connect(partial(self.navigate, "experiment_design"))
        write = make_button("进入论文写作", primary=True)
        write.clicked.connect(partial(self.navigate, "writing"))
        decision.layout.addWidget(iterate)
        decision.layout.addWidget(write)
        self.root.addWidget(decision)
        self.nav_footer("agent_run", "writing", "进入论文写作")


class WritingPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("writing", "论文写作", navigator)
        row = QHBoxLayout()
        self.section_list = QListWidget()
        for name in WRITING_SECTIONS:
            self.section_list.addItem(name)
        self.section_list.currentTextChanged.connect(self.show_section)
        row.addWidget(self.section_list, 1)
        self.editor = QTextEdit()
        row.addWidget(self.editor, 3)
        self.root.addLayout(row)
        action = CardWidget("写作操作", "支持生成初稿、润色语言、检查逻辑。", variant="soft")
        draft = make_button("生成初稿")
        draft.clicked.connect(self.generate_draft)
        action.layout.addWidget(draft)
        action.layout.addWidget(make_button("润色语言"))
        action.layout.addWidget(make_button("检查逻辑"))
        next_button = make_button("进入可信验证", primary=True)
        next_button.clicked.connect(partial(self.navigate, "validation"))
        action.layout.addWidget(next_button)
        self.root.addWidget(action)
        self.section_list.setCurrentRow(0)
        self.nav_footer("results", "validation", "进入可信验证")

    def show_section(self, name: str) -> None:
        self.editor.setPlainText(WRITING_SECTIONS.get(name, ""))

    def generate_draft(self) -> None:
        self.editor.setPlainText("正在生成初稿...\n\n[段落骨架加载中]")
        QTimer.singleShot(800, lambda: self.editor.setPlainText(WRITING_SECTIONS.get(self.section_list.currentItem().text(), "")))


class ValidationPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("validation", "可信验证与可追溯", navigator)
        for item in VALIDATION_TIMELINE:
            card = CardWidget("流程审计节点", item, clickable=True)
            card.layout.addWidget(make_button("查看详情"))
            self.root.addWidget(card)
        score = CardWidget("可信评分总览", "整体可信评分 89 / 100", variant="editorial")
        score.layout.addWidget(make_label("已建立从文献 -> Idea -> 实验 -> 论文的链路追踪。"))
        score.layout.addWidget(make_button("导出报告"))
        back = make_button("返回主工作台", primary=True)
        back.clicked.connect(partial(self.navigate, "chat"))
        score.layout.addWidget(back)
        self.root.addWidget(score)
        self.nav_footer("writing", "chat", "返回主工作台")


class HistoryPage(WorkflowContentPage):
    def __init__(self, navigator) -> None:
        super().__init__("history", "历史记录", navigator)
        self.root.addWidget(SearchBar("搜索历史对话或项目"))
        for group, items in {
            "今天": ["多模态医学文献趋势分析", "RAG 高被引论文摘要"],
            "近 7 天": ["研究空白识别与选题", "实验结果对比分析"],
            "近 30 天": ["论文引言生成", "可信验证审计链"],
        }.items():
            card = CardWidget(group, variant="soft")
            for title in items:
                row = QHBoxLayout()
                row.addWidget(make_label(title))
                row.addStretch(1)
                row.addWidget(make_button("重命名"))
                row.addWidget(make_button("置顶"))
                row.addWidget(make_button("删除"))
                open_btn = make_button("打开")
                open_btn.clicked.connect(partial(self.navigate, "chat"))
                row.addWidget(open_btn)
                card.layout.addLayout(row)
            self.root.addWidget(card)
        self.nav_footer(None, None, "")


class SettingsPage(WorkflowContentPage):
    def __init__(self, navigator, current_theme: str, theme_callback) -> None:
        super().__init__("settings", "设置", navigator)
        theme_card = CardWidget("主题切换", "切换浅色 / 深色主题", variant="soft")
        row = QHBoxLayout()
        for theme in ["light", "dark"]:
            button = make_button("浅色" if theme == "light" else "深色", primary=theme == current_theme)
            button.clicked.connect(partial(theme_callback, theme))
            row.addWidget(button)
        theme_card.layout.addLayout(row)
        self.root.addWidget(theme_card)
        for title, desc in [
            ("默认研究领域", "医疗 AI / 多模态学习"),
            ("推荐偏好", "优先可信性、论文质量与实验可复现性"),
            ("数据源连接状态", "arXiv / PubMed / Crossref / Semantic Scholar 已连接"),
            ("关于产品", "ScholarMind 桌面端科研原型"),
            ("版本信息", "v0.1.0 Prototype"),
        ]:
            self.root.addWidget(CardWidget(title, desc))
        self.nav_footer(None, None, "")
