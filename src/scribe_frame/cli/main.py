"""scribe-frame CLI — framework diagnostics + plugin command dispatcher.

Usage:
  scribe-frame list              List installed plugins
  scribe-frame info              Show framework version & paths
  scribe-frame <plugin-cmd> ...  Run a plugin-registered subcommand
"""

from __future__ import annotations

import argparse
import sys

from scribe_frame.provider_registry import ProviderRegistry
from scribe_frame.formatter_registry import FormatterRegistry
from scribe_frame.chunker_registry import ChunkerRegistry
from scribe_frame.command_registry import CommandRegistry


def cmd_list(_args) -> int:
    """Print installed plugins."""
    ProviderRegistry.discover()
    FormatterRegistry.discover()
    ChunkerRegistry.discover()
    CommandRegistry.discover()

    providers = ProviderRegistry.list_providers()
    print("Providers:")
    if providers:
        for p in providers:
            engines = p.list_engine_types()
            print(f"  {p.name}  →  {', '.join(engines)}")
    else:
        print("  (none)")

    formatters = FormatterRegistry.list_all()
    print("\nFormatters:")
    if formatters:
        for f in formatters:
            print(f"  {f.format_id}  →  .{f.file_extension}  ({f.label})")
    else:
        print("  (none)")

    chunkers = ChunkerRegistry._chunkers
    print("\nChunkers:")
    if chunkers:
        for name in chunkers:
            print(f"  {name}")
    else:
        print("  (none)")

    commands = CommandRegistry.list_commands()
    print("\nCLI Commands:")
    if commands:
        for c in commands:
            print(f"  {c.name}  —  {c.help}")
    else:
        print("  (none)")

    return 0


def cmd_info(_args) -> int:
    """Print framework information."""
    import scribe_frame
    from importlib.metadata import version

    print(f"scribe-frame version: {version('scribe-frame')}")
    print(f"Python: {sys.version}")
    print(f"Installed at: {scribe_frame.__file__}")

    ProviderRegistry.discover()
    print(f"Providers: {len(ProviderRegistry.list_providers())}")
    FormatterRegistry.discover()
    print(f"Formatters: {len(FormatterRegistry.list_all())}")
    ChunkerRegistry.discover()
    print(f"Chunkers: {len(ChunkerRegistry._chunkers)}")
    CommandRegistry.discover()
    print(f"CLI Commands: {len(CommandRegistry.list_commands())}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="scribe-frame",
        description="Scribe Frame — plugin framework diagnostics & dispatcher",
    )
    sub = parser.add_subparsers(dest="command", title="commands")

    # Built-in commands
    p_list = sub.add_parser("list", help="List installed plugins")
    p_list.set_defaults(func=cmd_list)

    p_info = sub.add_parser("info", help="Show framework info")
    p_info.set_defaults(func=cmd_info)

    # Discover and register plugin commands
    CommandRegistry.discover()
    for cmd in CommandRegistry.list_commands():
        p = sub.add_parser(cmd.name, help=cmd.help)
        cmd.register(p)
        p.set_defaults(func=cmd.run)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
