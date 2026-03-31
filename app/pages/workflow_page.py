from __future__ import annotations

from functools import partial

from PySide6.QtWidgets import QHBoxLayout

from app.mock.data import WORKFLOW_STEPS
from app.pages.base import BasePage
from app.widgets.common import CardWidget, StatusTag, make_button, make_label


class WorkflowPage(BasePage):
    def __init__(self, navigator, state) -> None:
        super().__init__("workflow", "工作流总览", navigator)
        self.state = state
        self._build_ui()

    def _build_ui(self) -> None:
        top = CardWidget("科研闭环总览", "从领域探索到可信验证，所有步骤都可以直接进入并继续推进。")
        row = QHBoxLayout()
        row.addWidget(make_label("当前项目进度 42%", "badge"))
        row.addStretch(1)
        back = make_button("返回主工作台")
        back.clicked.connect(partial(self.navigate, "chat"))
        row.addWidget(back)
        top.layout.addLayout(row)
        self.root.addWidget(top)

        for page_id, title in WORKFLOW_STEPS:
            card = CardWidget(title, f"点击进入 {title} 页面")
            action = QHBoxLayout()
            action.addWidget(StatusTag(self.state.workflow_status.get(page_id, "not_started")))
            action.addStretch(1)
            button = make_button("进入该步骤", primary=page_id in {"exploration", "collection", "trends", "results"})
            button.clicked.connect(partial(self.navigate, page_id))
            action.addWidget(button)
            card.layout.addLayout(action)
            self.root.addWidget(card)
