"""Abstract interfaces for plugin types."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ── reused from scribe.providers.base ──
# (will be the single source of truth; scribe depends on scribe_frame)

@dataclass
class ModelSpec:
    """Metadata for a single model."""
    id: str
    name: str
    provider: str
    engine_type: str
    role: str = ""
    display_name: str = ""
    tier: str = "medium"
    vram_estimate_mb: int = 0
    download_size_mb: int = 0
    description: str = ""
    version: str = ""
    languages: list[str] = field(default_factory=lambda: ["zh", "en"])


@dataclass
class EnginePreset:
    """A ready-to-use combination of models for an engine."""
    id: str
    name: str
    engine_type: str
    recommended_vram_mb: int
    model_selections: dict = field(default_factory=dict)
    extra_config: dict = field(default_factory=dict)


@dataclass
class HardwareInfo:
    gpu_available: bool = False
    gpu_name: str = ""
    gpu_count: int = 0
    vram_total_mb: int = 0
    vram_free_mb: int = 0
    cuda_version: str = ""
    cpu_cores: int = 0
    ram_total_mb: int = 0
    provider_hints: dict = field(default_factory=dict)

    @property
    def recommended_tier(self) -> str:
        if not self.gpu_available:
            return "mobile"
        if self.vram_total_mb >= 16000:
            return "server"
        if self.vram_total_mb >= 8000:
            return "medium"
        return "mobile"

    @property
    def supports_fp16(self) -> bool:
        return self.gpu_available and self.vram_total_mb >= 4000


class BaseProvider(ABC):
    """Each OCR backend implements this."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def list_engine_types(self) -> list[str]: ...

    @abstractmethod
    def list_models(self, engine_type: Optional[str] = None) -> list[ModelSpec]: ...

    @abstractmethod
    def list_presets(self, engine_type: Optional[str] = None) -> list[EnginePreset]: ...

    @abstractmethod
    def check_availability(self) -> bool: ...

    @abstractmethod
    def create_engine(self, engine_type: str, preset: EnginePreset, **config): ...

    @abstractmethod
    def is_model_cached(self, model: ModelSpec) -> bool: ...

    @abstractmethod
    def download_model(self, model: ModelSpec) -> bool: ...

    def recommend_preset(self, engine_type: str, hw: Optional[HardwareInfo] = None) -> EnginePreset:
        presets = self.list_presets(engine_type)
        if not presets:
            raise ValueError(f"No presets for {engine_type}")
        if hw is None:
            return presets[0]
        viable = [p for p in presets if p.recommended_vram_mb <= hw.vram_total_mb]
        return presets[0] if not viable else viable[-1]

    def refresh_remote_catalog(self) -> str:
        return ""


class BaseFormatter(ABC):
    """Each output format implements this."""

    @property
    @abstractmethod
    def format_id(self) -> str: ...

    @property
    @abstractmethod
    def label(self) -> str: ...

    @property
    @abstractmethod
    def file_extension(self) -> str: ...

    @property
    def supported_engines(self) -> list[str]:
        return ["*"]

    @abstractmethod
    def format(self, result) -> str: ...


# ── Chunker plugin interface ──────────────────────────


@dataclass
class ChunkInfo:
    """Metadata for a single image chunk."""
    path: str        # temp file path or original
    y_offset: int    # pixel offset in original image
    index: int       # 0-based chunk number
    total: int       # total chunks


class BaseChunker(ABC):
    """Pre-processing plugin: split large images into manageable chunks."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def chunk(self, image_path: str) -> list[ChunkInfo] | None:
        """Return list of chunk info, or None if no chunking needed."""
        ...


# ── CLI Command plugin interface ─────────────────────

class BaseCommand(ABC):
    """A CLI subcommand plugin."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Subcommand name, e.g. 'scan', 'parse'."""
        ...

    @property
    @abstractmethod
    def help(self) -> str:
        """One-line description."""
        ...

    @abstractmethod
    def register(self, parser) -> None:
        """Add arguments to an argparse subparser."""
        ...

    @abstractmethod
    def run(self, args) -> int:
        """Execute the command. Return exit code."""
        ...
