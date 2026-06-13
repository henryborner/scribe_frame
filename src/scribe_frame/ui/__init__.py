"""Scribe Frame UI — reusable dark-themed PyQt6 widgets and inspector."""

from scribe_frame.ui.theme import DARK_STYLE, DARK_GLOBAL, DARK_SCROLLBAR
from scribe_frame.ui.widgets import (
    DarkButton, PrimaryButton, OutlineButton,
    DropZone, ResultPanel, HardwarePanel, TabManager,
)
from scribe_frame.ui.inspector import InspectorWindow

__all__ = [
    "DARK_STYLE", "DARK_GLOBAL", "DARK_SCROLLBAR",
    "DarkButton", "PrimaryButton", "OutlineButton",
    "DropZone", "ResultPanel", "HardwarePanel", "TabManager",
    "InspectorWindow",
]
