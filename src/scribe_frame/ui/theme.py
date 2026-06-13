"""Scribe Frame dark theme — reusable PyQt6 stylesheet.

Usage:
    app = QApplication([])
    app.setStyleSheet(DARK_STYLE)
"""

# ── Global widget theme ─────────────────────────────────────────

DARK_GLOBAL = """
    QMainWindow, QWidget {
        background: #0f0f1a;
        color: #c0c0d0;
    }
    QGroupBox {
        border: 1px solid #333;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 16px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        color: #aaa;
    }
    QComboBox {
        background: #1e1e2e;
        border: 1px solid #444;
        border-radius: 6px;
        padding: 6px;
        color: #e0e0e0;
    }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background: #1e1e2e;
        color: #e0e0e0;
        selection-background-color: #7c3aed;
    }
    QPushButton {
        background: #2a2a3e;
        border: 1px solid #444;
        border-radius: 6px;
        padding: 8px 16px;
        color: #e0e0e0;
    }
    QPushButton:hover { background: #3a3a4e; }
    QProgressBar {
        border: 1px solid #444;
        border-radius: 4px;
        text-align: center;
        background: #1e1e2e;
    }
    QProgressBar::chunk { background: #7c3aed; }
    QTabWidget::pane {
        border: 1px solid #333;
        background: #0f0f1a;
    }
    QTabBar::tab {
        background: #1a1a2e;
        border: 1px solid #333;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    QTabBar::tab:selected {
        background: #2a2a4e;
        border-bottom: 2px solid #7c3aed;
        color: #c0c0ff;
    }
    QTabBar::tab:hover { background: #252540; }
    QTreeWidget {
        background: #1a1a2e;
        border: 1px solid #333;
        border-radius: 6px;
        color: #c0c0d0;
    }
    QTreeWidget::item:hover {
        background: #2a2a3e;
    }
    QTreeWidget::item:selected {
        background: #7c3aed;
    }
    QHeaderView::section {
        background: #1e1e2e;
        border: 1px solid #333;
        padding: 6px;
        font-weight: bold;
    }
    QLabel {
        background: transparent;
    }
"""

# ── Custom scrollbar ───────────────────────────────────────────

DARK_SCROLLBAR = """
    QScrollBar:vertical {
        background: #1a1a2e;
        width: 12px;
        margin: 0;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background: #4a4a6e;
        min-height: 30px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #7c3aed;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    QScrollBar:horizontal {
        background: #1a1a2e;
        height: 12px;
        margin: 0;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal {
        background: #4a4a6e;
        min-width: 30px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #7c3aed;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }
"""

# ── Combined ───────────────────────────────────────────────────

DARK_STYLE = DARK_GLOBAL + DARK_SCROLLBAR
