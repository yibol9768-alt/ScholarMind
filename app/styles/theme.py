from __future__ import annotations


def build_stylesheet(theme: str = "light") -> str:
    is_dark = theme == "dark"

    if is_dark:
        background = "#1b1f27"
        surface = "#232936"
        surface_low = "#1a202b"
        surface_high = "#2b3342"
        surface_top = "#30394b"
        text = "#edf1f7"
        muted = "#a2acbb"
        outline = "#384254"
        accent = "#8ea9ff"
        accent_strong = "#5f82ff"
        accent_soft = "#2a3657"
        tertiary = "#ffb59a"
        tertiary_soft = "#4b2b23"
        sidebar = "#171c25"
        hero_fill = "#202b44"
        hero_secondary = "#2c3f63"
    else:
        background = "#fbf9f5"
        surface = "#ffffff"
        surface_low = "#f5f3ef"
        surface_high = "#ece8e1"
        surface_top = "#faf7f1"
        text = "#1b1c1a"
        muted = "#57657a"
        outline = "#cfd5df"
        accent = "#00288e"
        accent_strong = "#1e40af"
        accent_soft = "#dde1ff"
        tertiary = "#872d00"
        tertiary_soft = "#ffede5"
        sidebar = "#f5f3ef"
        hero_fill = "#1e40af"
        hero_secondary = "#3755c3"

    return f"""
    QWidget {{
        background: {background};
        color: {text};
        font-family: "Segoe UI", "Microsoft YaHei";
        font-size: 13px;
        selection-background-color: {accent_strong};
        selection-color: white;
    }}
    QMainWindow, QScrollArea, QScrollArea > QWidget > QWidget {{
        background: {background};
        border: none;
    }}
    QLabel {{
        background: transparent;
        border: none;
    }}
    QLabel[class="title"] {{
        font-family: "Georgia";
        font-size: 25px;
        font-weight: 700;
        letter-spacing: 0.2px;
    }}
    QLabel[class="section"] {{
        font-family: "Georgia";
        font-size: 19px;
        font-weight: 700;
    }}
    QLabel[class="topbrand"] {{
        font-family: "Georgia";
        font-size: 21px;
        font-weight: 700;
        color: {accent_strong};
    }}
    QLabel[class="topnav"] {{
        color: {muted};
        font-size: 13px;
        font-weight: 600;
        padding-top: 4px;
    }}
    QLabel[class="eyebrow"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.3px;
    }}
    QLabel[class="hero"] {{
        font-family: "Georgia";
        font-size: 36px;
        font-weight: 700;
        qproperty-alignment: AlignCenter;
    }}
    QLabel[class="hero_subtitle"] {{
        color: {muted};
        font-size: 16px;
        font-weight: 600;
        qproperty-alignment: AlignCenter;
    }}
    QLabel[class="subtitle"], QLabel[class="muted"] {{
        color: {muted};
        padding-top: 1px;
        padding-bottom: 3px;
    }}
    QLabel[class="body"] {{
        color: {text};
        padding-top: 1px;
        padding-bottom: 4px;
    }}
    QLabel[class="badge"] {{
        background: {accent_soft};
        color: {accent};
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 11px;
        font-weight: 700;
    }}
    QLabel[class="source_count_badge"] {{
        background: rgba(221,225,255,0.78);
        color: {accent};
        border-radius: 12px;
        padding: 8px 12px;
        font-size: 11px;
        font-weight: 800;
    }}
    QLabel[class="source_icon_text"] {{
        color: {accent};
        font-size: 12px;
        font-weight: 800;
        qproperty-alignment: AlignCenter;
    }}
    QLabel[class="source_card_title"] {{
        font-family: "Georgia";
        font-size: 17px;
        font-weight: 700;
        padding-top: 2px;
    }}
    QLabel[class="source_card_desc"] {{
        color: {muted};
        font-size: 12px;
        line-height: 1.45;
        padding-top: 0px;
        padding-bottom: 0px;
    }}
    QLabel[class="exploration_panel_title"] {{
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 18px;
        font-weight: 700;
    }}
    QLabel[class="exploration_section_title"] {{
        font-family: "Georgia";
        font-size: 24px;
        font-weight: 700;
    }}
    QLabel[class="exploration_icon_text"] {{
        color: {accent};
        font-size: 12px;
        font-weight: 800;
        qproperty-alignment: AlignCenter;
    }}
    QLabel[class="exploration_body"] {{
        color: {muted};
        font-size: 15px;
        line-height: 1.7;
        padding-top: 0px;
        padding-bottom: 0px;
    }}
    QLabel[class="exploration_stat_label"] {{
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.1px;
    }}
    QLabel[class="exploration_stat_value"] {{
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 24px;
        font-weight: 800;
    }}
    QLabel[class="exploration_stat_note"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 600;
    }}
    QLabel[class="exploration_chart_note"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 600;
    }}
    QLabel[class="exploration_list_item"] {{
        color: {text};
        font-size: 13px;
        padding-top: 1px;
        padding-bottom: 4px;
    }}
    QLabel[class="exploration_person_name"] {{
        font-size: 13px;
        font-weight: 700;
    }}
    QLabel[class="exploration_person_meta"] {{
        color: {muted};
        font-size: 11px;
    }}
    QLabel[class="exploration_avatar_text"] {{
        color: {accent};
        font-size: 14px;
        font-weight: 800;
        qproperty-alignment: AlignCenter;
    }}
    QLabel[class="exploration_trend"] {{
        color: {accent};
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    QLabel[class="exploration_insight_body"] {{
        color: {muted};
        font-size: 12px;
        font-style: italic;
        line-height: 1.6;
        padding-top: 0px;
        padding-bottom: 0px;
    }}
    QLabel[class="tertiary_badge"] {{
        background: {tertiary_soft};
        color: {tertiary};
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 11px;
        font-weight: 700;
    }}
    QLabel[class="quote"] {{
        color: {muted};
        font-size: 15px;
        font-style: italic;
        padding-top: 6px;
        padding-bottom: 4px;
    }}
    QLabel[class="metric"] {{
        color: {accent};
        font-size: 42px;
        font-weight: 800;
    }}
    QLabel[class="metric_label"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
    }}
    QLabel[class="image_placeholder"] {{
        background: {surface_high};
        border-radius: 14px;
        min-height: 120px;
        qproperty-alignment: AlignCenter;
        color: {muted};
        font-weight: 700;
    }}
    QLabel[class="footer_note"] {{
        color: {muted};
        font-size: 10px;
        font-weight: 600;
        qproperty-alignment: AlignCenter;
        padding-top: 2px;
    }}
    QLabel[class="login_hero_brand"] {{
        color: {"#ffffff" if not is_dark else text};
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 26px;
        font-weight: 700;
    }}
    QLabel[class="login_hero_eyebrow"] {{
        color: {"rgba(221,225,255,0.82)" if not is_dark else muted};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.6px;
        text-transform: uppercase;
    }}
    QLabel[class="login_hero_title"] {{
        color: {"#ffffff" if not is_dark else text};
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 36px;
        font-weight: 700;
        padding-top: 4px;
        padding-bottom: 6px;
    }}
    QLabel[class="login_hero_text"] {{
        color: {"#dde1ff" if not is_dark else muted};
        font-size: 15px;
        padding-right: 8px;
    }}
    QLabel[class="login_hero_quote"] {{
        color: {"rgba(255,255,255,0.76)" if not is_dark else muted};
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
    }}
    QLabel[class="login_mobile_brand"] {{
        font-family: "Georgia";
        font-size: 24px;
        font-weight: 700;
        qproperty-alignment: AlignCenter;
        color: {text};
    }}
    QLabel[class="login_title"] {{
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 32px;
        font-weight: 700;
    }}
    QLabel[class="login_subtitle"] {{
        color: {muted};
        font-size: 15px;
    }}
    QLabel[class="login_tab_active"] {{
        color: {accent};
        font-size: 13px;
        font-weight: 700;
        padding-bottom: 12px;
        border-bottom: 2px solid {accent};
    }}
    QLabel[class="login_tab"] {{
        color: {muted};
        font-size: 13px;
        font-weight: 600;
        padding-bottom: 12px;
    }}
    QLabel[class="field_label"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.3px;
    }}
    QLabel[class="login_divider"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }}
    QLabel[class="login_link"] {{
        color: {accent};
        font-size: 13px;
        font-weight: 700;
    }}
    QLabel[class="login_footer_link"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 600;
    }}
    QLabel[class="workspace_eyebrow"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.6px;
    }}
    QLabel[class="workspace_title"] {{
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 30px;
        font-weight: 700;
    }}
    QLabel[class="workspace_subtitle"] {{
        color: {muted};
        font-size: 15px;
    }}
    QLabel[class="chat_meta"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }}
    QLabel[class="chat_body"] {{
        color: {text};
        font-size: 14px;
    }}
    QLabel[class="chat_user_body"] {{
        color: white;
        font-size: 14px;
    }}
    QLabel[class="analysis_title"] {{
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 22px;
        font-weight: 800;
    }}
    QLabel[class="analysis_note"] {{
        background: rgba(0,40,142,0.10);
        color: {accent};
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.1px;
    }}
    QLabel[class="analysis_index"] {{
        color: {accent_strong};
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 18px;
        font-weight: 800;
    }}
    QLabel[class="analysis_line"] {{
        color: {text};
        font-size: 14px;
    }}
    QLabel[class="marginalia_title"] {{
        color: {muted};
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
    }}
    QLabel[class="marginalia_body"] {{
        color: {text};
        font-size: 12px;
    }}
    QLabel[class="composer_hint"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 600;
    }}
    QLabel[class="sidebar_brand"] {{
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 21px;
        font-weight: 800;
        color: {text};
    }}
    QLabel[class="sidebar_caption"] {{
        color: rgba(27, 28, 26, 0.46);
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.6px;
    }}
    QLabel[class="sidebar_section"] {{
        color: {muted};
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        padding-top: 8px;
    }}
    QLabel[class="sidebar_module_title"] {{
        font-family: "Segoe UI Semibold", "Microsoft YaHei";
        font-size: 18px;
        font-weight: 700;
    }}
    QLabel[class="sidebar_module_text"] {{
        color: {muted};
        font-size: 12px;
    }}
    QLabel[class="profile_name"] {{
        font-size: 13px;
        font-weight: 700;
    }}
    QLabel[class="profile_role"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 600;
    }}
    QLabel[class="topnav_active"] {{
        color: {accent};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        border-bottom: 2px solid {accent};
        padding-bottom: 6px;
    }}
    QLabel[class="topbar_context"] {{
        color: {muted};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }}
    QLabel[class="topbar_project"] {{
        color: {muted};
        font-size: 13px;
        font-weight: 600;
    }}
    QLabel[class="avatar_text"] {{
        font-size: 11px;
        font-weight: 800;
        qproperty-alignment: AlignCenter;
    }}
    QLabel[status="completed"], QLabel[status="in_progress"], QLabel[status="not_started"], QLabel[status="risk"] {{
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.4px;
    }}
    QLabel[status="completed"] {{ background: rgba(31,139,76,0.12); color: #1f8b4c; }}
    QLabel[status="in_progress"] {{ background: rgba(0,40,142,0.12); color: {accent}; }}
    QLabel[status="not_started"] {{ background: rgba(87,101,122,0.12); color: {muted}; }}
    QLabel[status="risk"] {{ background: rgba(180,35,24,0.12); color: #b42318; }}

    QPushButton {{
        background: {surface_high};
        color: {text};
        border: none;
        border-radius: 14px;
        padding: 11px 15px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background: {surface};
    }}
    QPushButton:pressed {{
        background: {surface_high};
    }}
    QPushButton[role="primary"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {accent}, stop:1 {accent_strong});
        color: white;
        padding: 13px 18px;
        font-weight: 700;
        border-radius: 16px;
    }}
    QPushButton[role="primary"]:hover {{
        background: {accent_strong};
    }}
    QPushButton[role="ghost"] {{
        background: transparent;
        color: {accent};
        padding: 8px 10px;
    }}
    QPushButton[role="ghost"]:hover {{
        background: {surface_low};
    }}
    QPushButton[role="oidc"] {{
        background: {surface};
        border: 1px solid rgba(117,118,132,0.16);
        border-radius: 16px;
        padding: 12px 16px;
        font-weight: 700;
    }}
    QPushButton[role="oidc"]:hover {{
        background: {surface_low};
        border: 1px solid rgba(0,40,142,0.16);
    }}
    QPushButton[role="promptcard"] {{
        background: {surface};
        color: {text};
        border: none;
        border-radius: 16px;
        padding: 12px 12px;
        text-align: left;
        font-size: 12px;
        font-weight: 700;
    }}
    QPushButton[role="promptcard"]:hover {{
        background: {surface_top};
    }}
    QPushButton[role="toolchip"] {{
        background: {surface_high};
        color: {text};
        border: none;
        border-radius: 14px;
        padding: 10px 14px;
        font-size: 12px;
        font-weight: 700;
    }}
    QPushButton[role="toolchip"]:hover {{
        background: {surface};
    }}
    QPushButton[role="utilitychip"] {{
        background: transparent;
        color: {muted};
        border: none;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.1px;
    }}
    QPushButton[role="utilitychip"]:hover {{
        background: rgba(0,40,142,0.08);
        color: {accent};
    }}
    QPushButton[role="tableAction"] {{
        background: rgba(255,255,255,0.96);
        color: {accent};
        border: 1px solid rgba(0,40,142,0.16);
        border-radius: 10px;
        padding: 6px 8px;
        font-family: "Segoe UI Semibold", "Microsoft YaHei UI", "Microsoft YaHei";
        font-size: 15px;
        font-weight: 700;
        min-width: 38px;
        min-height: 30px;
    }}
    QPushButton[role="tableAction"]:hover {{
        background: rgba(0,40,142,0.10);
        border: 1px solid rgba(0,40,142,0.20);
    }}
    QPushButton[role="tableAction"]:pressed {{
        background: rgba(0,40,142,0.16);
    }}
    QPushButton[role="tableAction"]:focus {{
        border: 1px solid rgba(0,40,142,0.24);
    }}
    QPushButton[role="tableAction"]:disabled {{
        color: rgba(87,101,122,0.56);
        background: rgba(236,232,225,0.78);
        border: 1px solid rgba(196,197,213,0.16);
    }}
    QPushButton[role="keywordChip"] {{
        background: #d5e3fc;
        color: #3a485b;
        border: none;
        border-radius: 999px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 700;
    }}
    QPushButton[role="keywordChip"]:hover {{
        background: {accent};
        color: white;
    }}
    QPushButton[role="keywordChipGhost"] {{
        background: transparent;
        color: {muted};
        border: 1px dashed rgba(117,118,132,0.26);
        border-radius: 999px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 700;
    }}
    QPushButton[role="keywordChipGhost"]:hover {{
        border: 1px solid rgba(0,40,142,0.20);
        color: {accent};
        background: rgba(0,40,142,0.05);
    }}
    QPushButton[role="explorationLink"] {{
        background: rgba(0,40,142,0.05);
        color: {accent_strong};
        border: none;
        border-radius: 14px;
        padding: 10px 14px;
        font-size: 12px;
        font-weight: 700;
    }}
    QPushButton[role="explorationLink"]:hover {{
        background: rgba(0,40,142,0.10);
    }}
    QPushButton[role="task"] {{
        background: {surface};
        border: 1px solid rgba(196,197,213,0.18);
        border-radius: 18px;
        padding: 18px;
        text-align: left;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton[role="task"]:hover {{
        background: {background};
        border: 1px solid rgba(0,40,142,0.20);
    }}
    QPushButton[role="task"][active="true"] {{
        background: {accent_soft};
        border: 1px solid rgba(0,40,142,0.18);
        color: {accent};
    }}
    QPushButton[role="task"][accent="secondary"] {{
        border-color: rgba(87,101,122,0.16);
    }}
    QPushButton[role="task"][accent="tertiary"] {{
        border-color: rgba(135,45,0,0.14);
    }}
    QPushButton[role="icon"] {{
        min-width: 42px;
        max-width: 42px;
        min-height: 42px;
        max-height: 42px;
        border-radius: 12px;
        padding: 0px;
        font-size: 18px;
        font-weight: 700;
        qproperty-iconSize: 18px 18px;
    }}
    QPushButton[nav="true"] {{
        background: transparent;
        color: {muted};
        border: none;
        border-radius: 12px;
        text-align: left;
        padding: 10px 12px;
        font-weight: 600;
    }}
    QPushButton[nav="true"]:hover {{
        background: {background};
        color: {text};
    }}
    QPushButton[active="true"] {{
        background: {surface};
        color: {accent_strong};
        font-weight: 700;
    }}
    QPushButton:disabled {{
        color: {muted};
        background: {surface_high};
    }}

    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListWidget, QTreeWidget, QTableWidget {{
        background: {surface_low};
        color: {text};
        border: 1px solid rgba(117,118,132,0.16);
        border-radius: 14px;
        padding: 12px 14px;
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
        background: {surface};
        border: 1px solid rgba(0,40,142,0.18);
    }}
    QLineEdit#loginField {{
        background: {surface_low};
        border: 1px solid rgba(117,118,132,0.08);
        border-radius: 16px;
        padding: 16px 18px;
        font-size: 14px;
    }}
    QLineEdit#loginField:focus {{
        background: {surface};
        border: 1px solid rgba(0,40,142,0.18);
    }}
    QLineEdit#topSearch {{
        background: {surface_low};
        border: none;
        border-radius: 999px;
        padding: 10px 14px;
        font-size: 12px;
    }}
    QLineEdit[panel="true"], QComboBox[panel="true"] {{
        background: {surface};
        border: 1px solid rgba(117,118,132,0.10);
        border-radius: 14px;
        padding: 11px 14px;
        font-size: 13px;
    }}
    QLineEdit[panel="true"]:focus, QComboBox[panel="true"]:focus {{
        background: {surface};
        border: 1px solid rgba(0,40,142,0.18);
    }}
    QTextEdit#explorationTopic {{
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(117,118,132,0.10);
        border-radius: 16px;
        padding: 16px 18px;
        font-size: 14px;
        line-height: 1.6;
    }}
    QTextEdit#explorationTopic:focus {{
        background: {surface};
        border: 1px solid rgba(0,40,142,0.18);
    }}
    QTextEdit#composerEditor {{
        background: transparent;
        border: none;
        padding: 4px 2px;
        font-size: 14px;
    }}
    QTextEdit#composerEditor:focus {{
        background: transparent;
        border: none;
    }}
    QCheckBox#rememberBox {{
        color: {muted};
        spacing: 8px;
        font-size: 13px;
    }}
    QCheckBox#rememberBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid rgba(117,118,132,0.24);
        background: {surface};
    }}
    QCheckBox#rememberBox::indicator:checked {{
        background: {accent};
        border: 1px solid {accent};
    }}
    QCheckBox#sourceToggle {{
        spacing: 0px;
        background: transparent;
    }}
    QCheckBox#sourceToggle::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid rgba(117,118,132,0.24);
        background: rgba(255,255,255,0.92);
    }}
    QCheckBox#sourceToggle::indicator:hover {{
        border: 1px solid rgba(0,40,142,0.26);
    }}
    QCheckBox#sourceToggle::indicator:checked {{
        background: {accent};
        border: 1px solid {accent};
    }}
    QListWidget::item {{
        border-radius: 10px;
        padding: 6px 8px;
        margin: 2px 0;
    }}
    QListWidget::item:selected {{
        background: {surface};
        color: {accent_strong};
    }}
    QListWidget#sidebarHistory {{
        background: transparent;
        border: none;
        padding: 0px;
    }}
    QListWidget#sidebarHistory::item {{
        border-radius: 12px;
        padding: 8px 10px;
        margin: 1px 0;
    }}
    QListWidget#sidebarHistory::item:selected {{
        background: {surface};
        color: {accent};
    }}
    QTableWidget {{
        gridline-color: rgba(117,118,132,0.10);
    }}
    QHeaderView::section {{
        background: {surface_low};
        color: {muted};
        border: none;
        padding: 10px;
        font-size: 11px;
        font-weight: 700;
    }}

    QFrame#Card, QFrame#BubbleAssistant, QFrame#BubbleUser, QFrame#Sidebar, QFrame#TopBar, QFrame#TaskPanel {{
        background: {surface};
        border: 1px solid rgba(196,197,213,0.18);
        border-radius: 18px;
    }}
    QFrame#Card[variant="soft"], QFrame#TaskPanel {{
        background: {surface_low};
        border: none;
    }}
    QFrame#Card[variant="collectionAside"] {{
        background: {surface_low};
        border: none;
        border-radius: 20px;
    }}
    QFrame#Card[variant="collectionLive"] {{
        background: {surface};
        border: 1px solid rgba(196,197,213,0.10);
        border-radius: 20px;
    }}
    QFrame#Card[variant="explorationPrompt"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255,255,255,0.98), stop:1 rgba(245,243,239,0.98));
        border: 1px solid rgba(196,197,213,0.14);
        border-radius: 22px;
    }}
    QFrame#Card[variant="explorationDocument"] {{
        background: {surface};
        border: 1px solid rgba(196,197,213,0.12);
        border-radius: 24px;
    }}
    QFrame#Card[variant="explorationSection"] {{
        background: transparent;
        border: none;
        border-radius: 0px;
    }}
    QFrame#Card[variant="explorationMiniPanel"] {{
        background: rgba(245,243,239,0.66);
        border: 1px solid rgba(196,197,213,0.12);
        border-radius: 18px;
    }}
    QFrame#Card[variant="editorial"] {{
        background: {surface};
        border: none;
    }}
    QFrame#Card[variant="hero"] {{
        background: transparent;
        border: none;
    }}
    QFrame#Card[variant="brandMark"] {{
        background: {accent};
        border: none;
        border-radius: 10px;
    }}
    QFrame#Card[variant="loginHero"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {hero_fill}, stop:1 {hero_secondary});
        border: none;
        border-radius: 0px;
    }}
    QFrame#Card[variant="loginMark"] {{
        background: rgba(255,255,255,0.96);
        border: none;
        border-radius: 14px;
    }}
    QFrame#Card[variant="loginMobileMark"] {{
        background: {accent};
        border: none;
        border-radius: 12px;
    }}
    QFrame#Card[variant="loginPanel"] {{
        background: transparent;
        border: none;
    }}
    QWidget#loginHeroCopy {{
        background: transparent;
    }}
    QFrame#Card[variant="editorialHero"] {{
        background: {surface};
        border: none;
        border-radius: 20px;
    }}
    QFrame#Card[variant="indicatorCard"] {{
        background: {surface_top};
        border: none;
        border-radius: 16px;
    }}
    QFrame#Card[variant="analysisCard"] {{
        background: {surface};
        border: 1px solid rgba(196,197,213,0.14);
        border-radius: 20px;
    }}
    QFrame#Card[variant="marginaliaCard"] {{
        background: rgba(255,255,255,0.76);
        border: 1px solid rgba(196,197,213,0.16);
        border-radius: 16px;
    }}
    QFrame#Card[variant="composerPanel"] {{
        background: {surface};
        border: 1px solid rgba(117,118,132,0.12);
        border-radius: 20px;
    }}
    QFrame#Card[variant="sidebarModule"] {{
        background: {surface};
        border: none;
        border-radius: 20px;
    }}
    QFrame#Card[variant="chatAssistantAvatar"] {{
        background: {accent_soft};
        border: none;
        border-radius: 14px;
    }}
    QFrame#Card[variant="chatUserAvatar"] {{
        background: {surface_high};
        border: none;
        border-radius: 14px;
    }}
    QFrame#Card[variant="sidebarProfile"] {{
        background: {surface};
        border: none;
        border-radius: 18px;
    }}
    QFrame#Card[variant="topAvatar"] {{
        background: {surface_high};
        border: none;
        border-radius: 14px;
    }}
    QFrame#Card[variant="sourceCard"] {{
        background: {surface};
        border: 1px solid rgba(196,197,213,0.18);
        border-radius: 18px;
    }}
    QFrame#Card[variant="sourceCard"][selected="true"] {{
        border: 1px solid rgba(0,40,142,0.18);
    }}
    QFrame#Card[variant="sourceCard"]:hover {{
        border: 1px solid rgba(0,40,142,0.22);
        background: {surface_top};
    }}
    QFrame#Card[variant="sourceIcon"] {{
        background: {surface_low};
        border: none;
        border-radius: 14px;
    }}
    QFrame#Card[variant="sourceIcon"][selected="true"] {{
        background: {accent_soft};
    }}
    QFrame#Card[variant="explorationIcon"] {{
        background: rgba(0,40,142,0.08);
        border: none;
        border-radius: 14px;
    }}
    QFrame#Card[variant="explorationIcon"][accent="tertiary"] {{
        background: rgba(135,45,0,0.08);
    }}
    QFrame#Card[variant="explorationIcon"][accent="neutral"] {{
        background: rgba(87,101,122,0.10);
    }}
    QFrame#Card[variant="explorationStat"] {{
        background: rgba(245,243,239,0.82);
        border: none;
        border-left: 4px solid {accent};
        border-radius: 16px;
    }}
    QFrame#Card[variant="explorationStat"][accent="tertiary"] {{
        border-left: 4px solid {tertiary};
    }}
    QFrame#Card[variant="explorationStat"][accent="neutral"] {{
        border-left: 4px solid {muted};
    }}
    QFrame#Card[variant="explorationChart"] {{
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(196,197,213,0.12);
        border-radius: 20px;
    }}
    QFrame#Card[variant="explorationBar"] {{
        background: rgba(0,40,142,0.14);
        border: none;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-bottom-left-radius: 0px;
        border-bottom-right-radius: 0px;
    }}
    QFrame#Card[variant="explorationBar"]:hover {{
        background: rgba(0,40,142,0.72);
    }}
    QFrame#Card[variant="explorationPerson"] {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 16px;
    }}
    QFrame#Card[variant="explorationPerson"]:hover {{
        background: rgba(245,243,239,0.74);
        border: 1px solid rgba(196,197,213,0.12);
    }}
    QFrame#Card[variant="explorationAvatar"] {{
        background: rgba(255,255,255,0.94);
        border: 1px solid rgba(196,197,213,0.14);
        border-radius: 999px;
    }}
    QFrame#Card[variant="explorationInstitution"] {{
        background: transparent;
        border: none;
        border-radius: 14px;
    }}
    QFrame#Card[variant="explorationInstitution"]:hover {{
        background: rgba(245,243,239,0.74);
    }}
    QFrame#Card[variant="explorationInstitutionMark"] {{
        background: rgba(255,255,255,0.94);
        border: 1px solid rgba(196,197,213,0.12);
        border-radius: 12px;
    }}
    QFrame#Card[variant="explorationInsight"] {{
        background: rgba(234,232,228,0.38);
        border: 1px solid rgba(0,40,142,0.08);
        border-left: 3px solid rgba(0,40,142,0.18);
        border-radius: 18px;
    }}
    QFrame#Sidebar {{
        background: {sidebar};
        border: none;
        border-radius: 0px;
    }}
    QFrame#TopBar {{
        background: {background};
        border: none;
        border-radius: 0px;
    }}
    QFrame#BubbleAssistant {{
        background: {surface};
        border: 1px solid rgba(196,197,213,0.14);
        border-radius: 22px;
    }}
    QFrame#BubbleUser {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {accent}, stop:1 {accent_strong});
        border: none;
        border-radius: 22px;
    }}
    QFrame#Card[clickable="true"]:hover, QFrame#TaskPanel:hover {{
        background: {background};
        border: 1px solid rgba(0,40,142,0.16);
    }}
    QFrame#loginHeroLine {{
        background: {"rgba(221,225,255,0.35)" if not is_dark else "rgba(255,255,255,0.12)"};
        border: none;
    }}
    QFrame#loginHeroBar {{
        background: rgba(255,255,255,0.42);
        border: none;
        border-radius: 5px;
    }}
    QFrame#loginDividerLine {{
        background: rgba(117,118,132,0.18);
        border: none;
    }}
    QFrame#loginTabsLine {{
        background: rgba(117,118,132,0.18);
        border: none;
        margin-top: -1px;
    }}
    QFrame#explorationDivider {{
        background: rgba(196,197,213,0.18);
        border: none;
    }}
    QWidget#loginCanvas {{
        background: {surface_top};
    }}
    QWidget#chatCanvas {{
        background: transparent;
    }}

    QTextEdit {{
        line-height: 1.5;
    }}

    QProgressBar {{
        background: {surface_high};
        border: none;
        border-radius: 8px;
        height: 10px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background: {accent};
        border-radius: 8px;
    }}
    QProgressBar#collectionProgress {{
        background: {surface_high};
        border-radius: 999px;
        height: 8px;
    }}
    QProgressBar#collectionProgress::chunk {{
        background: {accent};
        border-radius: 999px;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 12px;
        margin: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(87, 101, 122, 0.32);
        border-radius: 6px;
        min-height: 36px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(30, 64, 175, 0.42);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        height: 0px;
        background: transparent;
    }}
    """
