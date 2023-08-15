"""CLI interface for astest."""
import argparse

import astest


class AstestArgs:
    filepath: str
    debug: bool


def cli() -> None:
    """CLI interface."""
    parser = argparse.ArgumentParser("astest")
    parser.add_argument("filepath", help="Path to python file, containing asserts.")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(namespace=AstestArgs)

    astest.run(args.filepath, args.debug)
