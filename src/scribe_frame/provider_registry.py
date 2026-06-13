"""Provider registry — discover and manage OCR backends."""
from __future__ import annotations

from typing import Optional
from importlib.metadata import entry_points

from scribe_frame.interfaces import BaseProvider, EnginePreset, ModelSpec, HardwareInfo


class ProviderRegistry:
    """Global registry for OCR providers (PaddleOCR, Tesseract, etc.)."""

    _providers: dict[str, BaseProvider] = {}
    _loaded: bool = False

    @classmethod
    def discover(cls) -> None:
        """Scan entry_points group `scribe.providers` for installed plugins."""
        if cls._loaded:
            return
        try:
            for ep in entry_points(group="scribe.providers"):
                factory = ep.load()
                instance = factory() if callable(factory) else factory
                cls._providers[ep.name] = instance
        except Exception:
            pass
        cls._loaded = True

    @classmethod
    def register(cls, provider: BaseProvider) -> None:
        """Manually register a provider (for built-ins or testing)."""
        cls.discover()  # load plugins first
        cls._providers[provider.name] = provider

    @classmethod
    def list_providers(cls) -> list[BaseProvider]:
        cls.discover()
        return list(cls._providers.values())

    @classmethod
    def get_provider(cls, name: str) -> Optional[BaseProvider]:
        cls.discover()
        return cls._providers.get(name)

    @classmethod
    def get_default(cls) -> Optional[BaseProvider]:
        """Return the first registered provider, or None."""
        cls.discover()
        return next(iter(cls._providers.values()), None)
