# ScholarMind

基于 `PySide6 + Qt Widgets` 的桌面端科研助手原型。

当前版本特性：

- 登录页
- 主工作台 / 主聊天页
- 工作流总览
- 完整科研流程页面
- 历史记录页
- 设置页
- 全局统一 QSS 风格
- 全量 mock 数据与可演示交互

## 运行

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python desktop.py
```

也可以：

```powershell
python main.py
```

## 目录

- `desktop.py` / `main.py`: 启动入口
- `app/windows/main_window.py`: 主窗口与页面路由
- `app/pages/`: 登录页、主工作台、工作流与各流程页面
- `app/widgets/`: 通用卡片、状态标签、布局组件
- `app/mock/data.py`: 所有 mock 数据
- `app/styles/theme.py`: 全局 QSS 样式
