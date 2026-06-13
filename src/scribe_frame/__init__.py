"""Scribe Frame — Plugin framework: provider, formatter, chunker & command registries."""

from scribe_frame.interfaces import (
    BaseProvider,
    BaseFormatter,
    BaseChunker,
    BaseCommand,
    ChunkInfo,
    ModelSpec,
    EnginePreset,
    HardwareInfo,
)
from scribe_frame.provider_registry import ProviderRegistry
from scribe_frame.formatter_registry import FormatterRegistry
from scribe_frame.chunker_registry import ChunkerRegistry
from scribe_frame.command_registry import CommandRegistry

__all__ = [
    "BaseProvider",
    "BaseFormatter",
    "BaseChunker",
    "BaseCommand",
    "ChunkInfo",
    "ModelSpec",
    "EnginePreset",
    "HardwareInfo",
    "ProviderRegistry",
    "FormatterRegistry",
    "ChunkerRegistry",
    "CommandRegistry",
]
