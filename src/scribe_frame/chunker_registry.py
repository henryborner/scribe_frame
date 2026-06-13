"""Chunker registry — discover image chunking plugins."""
from __future__ import annotations

from importlib.metadata import entry_points
from scribe_frame.interfaces import BaseChunker


class ChunkerRegistry:
    _chunkers: dict[str, BaseChunker] = {}
    _loaded: bool = False

    @classmethod
    def discover(cls) -> None:
        if cls._loaded:
            return
        try:
            for ep in entry_points(group="scribe.chunkers"):
                factory = ep.load()
                instance = factory() if callable(factory) else factory
                cls._chunkers[instance.name] = instance
        except Exception:
            pass
        cls._loaded = True

    @classmethod
    def register(cls, chunker: BaseChunker) -> None:
        cls.discover()
        cls._chunkers[chunker.name] = chunker

    @classmethod
    def get_default(cls) -> BaseChunker | None:
        cls.discover()
        return next(iter(cls._chunkers.values()), None)
