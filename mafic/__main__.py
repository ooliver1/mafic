"""Mafic CLI tools."""
# SPDX-License-Identifier: MIT

from __future__ import annotations

import platform
import sys
from argparse import ArgumentParser, Namespace

import aiohttp

import mafic

from .__libraries import library, version_info

VERSION_OUTPUT = """
- Python v{py.major}.{py.minor}.{py.micro}-{py.releaselevel}
- mafic v{mafic}
- aiohttp v{aiohttp}
- {lib} v{pkg.major}.{pkg.minor}.{pkg.micro}-{pkg.releaselevel}
- system info: {uname.system} {uname.release} {uname.version}
""".strip()


def show_version() -> None:
    """Show version information."""
    version = mafic.__version__
    uname = platform.uname()
    print(  # noqa: T201
        VERSION_OUTPUT.format(
            py=sys.version_info,
            mafic=version,
            aiohttp=aiohttp.__version__,
            uname=uname,
            lib=library,
            pkg=version_info,
        )
    )


def core(_: ArgumentParser, args: Namespace) -> None:
    """Core function for mafic CLI tools."""
    if args.version:
        show_version()


def parse_args() -> tuple[ArgumentParser, Namespace]:
    """Parse arguments from the CLI."""
    parser = ArgumentParser(prog="mafic", description="CLI tools for mafic")
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="shows mafic and other related versions",
    )
    return parser, parser.parse_args()


def main() -> None:
    """Run the parser for arguments then execute."""
    parser, args = parse_args()
    core(parser, args)


if __name__ == "__main__":
    main()
