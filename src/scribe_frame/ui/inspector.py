"""Scribe Frame plugin inspector — zero-dependency GUI for framework health."""
from __future__ import annotations

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QListWidget,
    QVBoxLayout, QWidget, QLabel, QListWidgetItem,
)
from PyQt6.QtCore import Qt

from scribe_frame.provider_registry import ProviderRegistry
from scribe_frame.formatter_registry import FormatterRegistry
from scribe_frame.chunker_registry import ChunkerRegistry


class InspectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scribe Frame — Plugin Inspector")
        self.resize(500, 400)

        tabs = QTabWidget()
        tabs.addTab(self._provider_tab(), "🔌 Providers")
        tabs.addTab(self._formatter_tab(), "📝 Formatters")
        tabs.addTab(self._chunker_tab(), "✂️ Chunkers")
        self.setCentralWidget(tabs)

    # ── provider tab ──

    def _provider_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Providers (entry_points: scribe.providers)"))
        lst = QListWidget()
        ProviderRegistry.discover()
        for name, p in ProviderRegistry._providers.items():
            engines = getattr(p, "list_engine_types", lambda: [] )()
            item = QListWidgetItem(f"{name}  →  engines: {', '.join(engines) if engines else 'N/A'}")
            lst.addItem(item)
        if lst.count() == 0:
            lst.addItem("(none found)")
        layout.addWidget(lst)
        return w

    # ── formatter tab ──

    def _formatter_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Formatters (entry_points: scribe.formatters)"))
        lst = QListWidget()
        FormatterRegistry.discover()
        for name, f in FormatterRegistry._formatters.items():
            ext = getattr(f, "file_extension", "?")
            item = QListWidgetItem(f"{name}  →  .{ext}")
            lst.addItem(item)
        if lst.count() == 0:
            lst.addItem("(none found)")
        layout.addWidget(lst)
        return w

    # ── chunker tab ──

    def _chunker_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Chunkers (entry_points: scribe.chunkers)"))
        lst = QListWidget()
        ChunkerRegistry.discover()
        for name, c in ChunkerRegistry._chunkers.items():
            item = QListWidgetItem(name)
            lst.addItem(item)
        if lst.count() == 0:
            lst.addItem("(none found)")
        layout.addWidget(lst)
        return w


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Scribe Frame Inspector")
    window = InspectorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
