"""Clipper - Simple clipboard text processing tool."""

import sys
import argparse
from .engine import ProcessingEngine
from .clipboard import is_clipboard_available


def main() -> None:
    """Main entry point for the clipper CLI."""
    parser = argparse.ArgumentParser(
        description="Process clipboard text (fix keyboard layout issues)",
        prog="clipper",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Show clipboard content and proposed changes without modifying clipboard",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Ask for confirmation before converting text",
    )
    parser.add_argument(
        "-u",
        "--undo",
        action="store_true",
        help="Restore previous clipboard content",
    )

    args = parser.parse_args()

    # Check clipboard availability
    if not is_clipboard_available():
        print("Error: Clipboard is not available or accessible.", file=sys.stderr)
        sys.exit(1)

    # Process clipboard
    engine = ProcessingEngine()
    if args.dry_run:
        success = engine.dry_run()
    elif args.undo:
        success = engine.undo()
    elif args.interactive:
        success = engine.process_clipboard_interactive()
    else:
        success = engine.process_clipboard()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
