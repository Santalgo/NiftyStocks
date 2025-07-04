"""Helper utilities."""

from __future__ import annotations


def printf(fmt: str, *args, flush: bool = True) -> None:
    """Print formatted message to stdout, similar to C printf."""
    print(fmt % args if args else fmt, flush=flush)
