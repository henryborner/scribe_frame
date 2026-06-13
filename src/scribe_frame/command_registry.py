"""Command registry — discover CLI subcommand plugins."""
from __future__ import annotations

from importlib.metadata import entry_points

from scribe_frame.interfaces import BaseCommand


class CommandRegistry:
    _commands: dict[str, BaseCommand] = {}
    _loaded: bool = False

    @classmethod
    def discover(cls) -> None:
        if cls._loaded:
            return
        try:
            for ep in entry_points(group="scribe.commands"):
                factory = ep.load()
                instance = factory() if callable(factory) else factory
                cls._commands[instance.name] = instance
        except Exception:
            pass
        cls._loaded = True

    @classmethod
    def register(cls, command: BaseCommand) -> None:
        cls.discover()
        cls._commands[command.name] = command

    @classmethod
    def list_commands(cls) -> list[BaseCommand]:
        cls.discover()
        return list(cls._commands.values())

    @classmethod
    def get(cls, name: str) -> BaseCommand | None:
        cls.discover()
        return cls._commands.get(name)
