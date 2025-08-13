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

    parser.parse_args()  # Parse arguments but don't need to use them yet

    # Check clipboard availability
    if not is_clipboard_available():
        print("Error: Clipboard is not available or accessible.", file=sys.stderr)
        sys.exit(1)

    # Process clipboard
    engine = ProcessingEngine()
    success = engine.process_clipboard()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
