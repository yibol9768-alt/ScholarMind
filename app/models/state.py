from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AppState:
    theme: str = "light"
    current_project: str = "ScholarMind Research Workspace"
    current_topic: str = "大语言模型在数字人文文献分析中的研究趋势"
    current_page: str = "chat"
    current_conversation_id: str = "conv-1"
    current_idea_id: str = "idea-1"
    workflow_status: dict[str, str] = field(
        default_factory=lambda: {
            "exploration": "completed",
            "collection": "completed",
            "extraction": "completed",
            "trends": "in_progress",
            "gaps": "not_started",
            "ideas": "not_started",
            "repository": "not_started",
            "experiment_design": "not_started",
            "agent_run": "not_started",
            "results": "not_started",
            "writing": "not_started",
            "validation": "not_started",
        }
    )
