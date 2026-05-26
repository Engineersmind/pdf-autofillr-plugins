"""
pdf-autofillr-plugins CLI

Commands:
    pdf-autofillr-plugins setup     — copy usage/ guides and create .env in working directory
    pdf-autofillr-plugins status    — check module installation and env vars
    pdf-autofillr-plugins list      — list all discovered plugins in a directory
    pdf-autofillr-plugins --version — print version
"""

from __future__ import annotations

import argparse
import importlib
import os
import shutil
import sys
from pathlib import Path

from pdf_autofillr_plugins import __version__


def _find_usage_dir() -> Path | None:
    candidates = [
        Path(__file__).parent / "usage",
        Path(__file__).parent.parent.parent / "usage",
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    return None


def _find_env_example() -> Path | None:
    candidates = [
        Path(".env.example"),
        Path(__file__).parent.parent.parent / ".env.example",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def cmd_setup(args: argparse.Namespace) -> int:
    print("\n  pdf-autofillr-plugins setup")
    print("  " + "-" * 50)

    # Step 1: create .env
    env_file = Path(".env")
    env_example = _find_env_example()
    if env_file.exists():
        print("\n  OK  .env already exists -- skipping")
    elif env_example:
        shutil.copy(env_example, env_file)
        print(f"\n  OK  Created .env from {env_example}")
        print("  --> Add your API key if your plugins require one")
    else:
        env_file.write_text(
            "# Add your API keys here if required by your plugins\n"
            "# OPENAI_API_KEY=your_key_here\n"
            "\n"
            "# Logging\n"
            "LITELLM_LOG=ERROR\n"
        )
        print("\n  OK  Created minimal .env")

    # Step 2: copy usage/ guides
    usage_src = _find_usage_dir()
    local_usage = Path("usage")
    if usage_src:
        if not local_usage.exists():
            shutil.copytree(str(usage_src), str(local_usage))
            print("\n  OK  Created usage/ directory")
            print("  --> Open usage/validator.md to get started writing your first plugin")
        else:
            print("\n  OK  usage/ already exists -- skipping")
    else:
        print("\n  Quick start:")
        print("    from pdf_autofillr_plugins import plugin, PluginManager")
        print("    from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata")

    print("\n  Run 'pdf-autofillr-plugins status' to verify everything is ready.\n")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    print("\n  pdf-autofillr-plugins status")
    print("  " + "─" * 50)

    # Check package itself
    print(f"\n  ✅  pdf-autofillr-plugins  {__version__}")

    # Check optional integrations
    print("\n  Optional integrations")
    print("  " + "─" * 50)
    optional = [
        ("pdf_autofillr_mapper", "mapper", 'pip install "pdf-autofillr[mapper]"'),
        ("chatbot", "chatbot", 'pip install "pdf-autofillr[chatbot]"'),
        (
            "pdf_autofillr_doc_upload",
            "doc-upload",
            'pip install "pdf-autofillr[doc-upload]"',
        ),
        ("ragpdf", "rag", 'pip install "pdf-autofillr[rag]"'),
    ]
    for module, name, hint in optional:
        try:
            mod = importlib.import_module(module)
            ver = getattr(mod, "__version__", "?")
            print(f"  ✅  {name:<14} {ver}")
        except ImportError:
            print(f"  ○   {name:<14} not installed  →  {hint}")

    # Check .env
    print("\n  Config")
    print("  " + "─" * 50)
    if os.path.exists(".env"):
        print("  ✅  .env file found")
    else:
        print("  ○   .env not found  →  run: pdf-autofillr-plugins setup")

    print()
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    from pdf_autofillr_plugins import PluginManager

    manager = PluginManager()
    paths = [args.path] if args.path else []

    if paths:
        discovered = manager.discover_plugins(
            paths, categories=[args.category] if args.category else None
        )
        if not discovered or all(len(v) == 0 for v in discovered.values()):
            print(f"\n  No plugins discovered in: {args.path}\n")
            return 0

        print()
        for category, names in discovered.items():
            if not names:
                continue
            print(f"  {category.upper()}")
            print(f"  {'─' * 40}")
            for name in names:
                info = manager.get_plugin_info(name, category)
                if info:
                    print(f"    • {info['name']:<30} v{info['version']}  {info['description']}")
                else:
                    print(f"    • {name}")
            print()
    else:
        print("\n  Use --path to point to a directory containing plugins.")
        print("  Example: pdf-autofillr-plugins list --path ./my_plugins/\n")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-autofillr-plugins",
        description=(
            "pdf-autofillr-plugins CLI\n\n"
            "  setup   Copy usage/ guides and create .env in working directory\n"
            "  status  Check module installation and env vars\n"
            "  list    List discovered plugins in a directory\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"pdf-autofillr-plugins {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    subparsers.add_parser(
        "setup", help="First-time setup: create .env and copy usage guides"
    ).set_defaults(func=cmd_setup)
    subparsers.add_parser("status", help="Check installation and environment").set_defaults(
        func=cmd_status
    )

    ls = subparsers.add_parser("list", help="List discovered plugins in a directory")
    ls.add_argument("--path", "-p", default=None, help="Directory to scan for plugins")
    ls.add_argument("--category", "-c", default=None, help="Filter by category")
    ls.set_defaults(func=cmd_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        sys.exit(args.func(args) or 0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
