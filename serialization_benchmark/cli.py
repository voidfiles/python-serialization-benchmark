from __future__ import annotations

import argparse
from collections.abc import Sequence

from serialization_benchmark.registry import encoded_adapters, primitive_adapters
from serialization_benchmark.validation import validate_all


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="serialization-benchmark")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "validate":
        validate_all()
        print(
            "validation passed: "
            f"{len(primitive_adapters())} primitive adapters, "
            f"{len(encoded_adapters())} encoded adapters"
        )
        return 0
    raise AssertionError(f"unsupported command: {args.command}")
