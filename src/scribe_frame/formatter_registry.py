"""Formatter registry — discover and manage output formatters."""
from __future__ import annotations

from typing import Optional
from importlib.metadata import entry_points

from scribe_frame.interfaces import BaseFormatter


class FormatterRegistry:
    """Global registry for output formatters (JSON, CSV, Markdown, etc.)."""

    _formatters: dict[str, BaseFormatter] = {}
    _loaded: bool = False

    @classmethod
    def discover(cls) -> None:
        """Scan entry_points group `scribe.formatters`."""
        if cls._loaded:
            return
        try:
            for ep in entry_points():
                if ep.group == "scribe.formatters":
                    factory = ep.load()
                    instance = factory() if callable(factory) else factory
                    cls._formatters[instance.format_id] = instance
        except Exception:
            pass
        cls._loaded = True

    @classmethod
    def register(cls, formatter: BaseFormatter) -> None:
        cls.discover()  # load plugins first
        cls._formatters[formatter.format_id] = formatter

    @classmethod
    def list_all(cls) -> list[BaseFormatter]:
        cls.discover()
        return list(cls._formatters.values())

    @classmethod
    def list_for_engine(cls, engine_type: str) -> list[BaseFormatter]:
        result = []
        for f in cls.list_all():
            # Prefer supports() method if present (old API), else check supported_engines
            if hasattr(f, "supports"):
                if f.supports(engine_type):
                    result.append(f)
            else:
                engines = getattr(f, "supported_engines", ["*"])
                if "*" in engines or engine_type in engines:
                    result.append(f)
        return result

    @classmethod
    def get(cls, format_id: str) -> Optional[BaseFormatter]:
        cls.discover()
        return cls._formatters.get(format_id)
