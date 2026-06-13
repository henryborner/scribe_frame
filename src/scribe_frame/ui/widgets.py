"""Reusable PyQt6 widgets with Scribe dark theme styling.

Usage:
    from scribe_frame.ui.widgets import DarkButton, DropZone, ResultPanel
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QPushButton, QGroupBox, QVBoxLayout, QLabel, QTextEdit,
    QHBoxLayout, QFileDialog, QComboBox, QProgressBar,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QWidget,
    QSplitter, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent


# ═══════════════════════════════════════════════════════════════════
# Buttons
# ═══════════════════════════════════════════════════════════════════

class DarkButton(QPushButton):
    """Standard dark-themed button."""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)


class PrimaryButton(DarkButton):
    """Accent-colored action button (purple)."""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QPushButton {
                background: #7c3aed;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background: #6d28d9; }
            QPushButton:disabled { background: #444; color: #888; }
        """)


class OutlineButton(DarkButton):
    """Bordered button (amber outline)."""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: #1a1a2e;
                color: #f59e0b;
                border: 1px solid #f59e0b;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background: #2a2a3e; }
        """)


# ═══════════════════════════════════════════════════════════════════
# Drop zone
# ═══════════════════════════════════════════════════════════════════

class DropZone(QGroupBox):
    """Drag-and-drop area for images / PDFs.  Emits file_selected(str)."""

    file_selected = pyqtSignal(str)

    def __init__(self, title: str = "Drop Image / PDF Here", parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        self._label = QLabel("Drag image or PDF here\nor click to browse")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumHeight(150)
        self._label.setStyleSheet("""
            QLabel {
                border: 2px dashed #555;
                border-radius: 12px;
                background: #1e1e2e;
                color: #888;
                font-size: 15px;
                padding: 30px;
            }
        """)
        self._label.mousePressEvent = self._on_click
        layout.addWidget(self._label)

    def _on_click(self, event):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.pdf);;All Files (*)"
        )
        if path:
            self.file_selected.emit(path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if p:
                self.file_selected.emit(p)
                break

    def set_selected_text(self, filename: str):
        """Show selected file name in drop zone."""
        self._label.setText(f"Selected:\n{filename}")
        self._label.setStyleSheet("""
            QLabel {
                border: 2px solid #7c3aed;
                border-radius: 12px;
                background: #1e1e2e;
                color: #c0c0ff;
                font-size: 15px;
                padding: 30px;
            }
        """)


# ═══════════════════════════════════════════════════════════════════
# Result panel
# ═══════════════════════════════════════════════════════════════════

class ResultPanel(QWidget):
    """Read-only text display with Copy / Save buttons."""

    copy_requested = pyqtSignal()
    save_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(QLabel("Result"))

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setFont(QFont("Consolas", 12))
        self._text.setStyleSheet("""
            QTextEdit {
                background: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        self._text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self._text)

        actions = QHBoxLayout()
        copy_btn = DarkButton("Copy")
        copy_btn.clicked.connect(self.copy_requested.emit)
        copy_btn.clicked.connect(self._on_copy)
        actions.addWidget(copy_btn)

        save_btn = DarkButton("Save to File")
        save_btn.clicked.connect(self.save_requested.emit)
        actions.addWidget(save_btn)

        layout.addLayout(actions)

    @property
    def text(self) -> str:
        return self._text.toPlainText()

    @text.setter
    def text(self, value: str):
        self._text.setPlainText(value)

    def _on_copy(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._text.toPlainText())

    def set_buttons_enabled(self, enabled: bool):
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(enabled)


# ═══════════════════════════════════════════════════════════════════
# Hardware info panel
# ═══════════════════════════════════════════════════════════════════

class HardwarePanel(QWidget):
    """Display GPU / CPU / RAM information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Property", "Value"])
        self._tree.header().setStretchLastSection(True)
        self._tree.setAlternatingRowColors(False)
        self._tree.setAnimated(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tree)

    def update_info(self, info: dict):
        """Populate tree with {label: value} dict."""
        self._tree.clear()
        for key, value in info.items():
            item = QTreeWidgetItem([str(key), str(value)])
            self._tree.addTopLevelItem(item)
        self._tree.expandAll()
        for i in range(self._tree.columnCount()):
            self._tree.resizeColumnToContents(i)


# ═══════════════════════════════════════════════════════════════════
# Tab helper
# ═══════════════════════════════════════════════════════════════════

class TabManager:
    """Lightweight wrapper around QTabWidget for registering plugin tabs."""

    def __init__(self, tab_widget):
        self._tabs = tab_widget

    def add_tab(self, widget: QWidget, label: str):
        self._tabs.addTab(widget, label)

    def on_tab_changed(self, callback):
        self._tabs.currentChanged.connect(callback)
