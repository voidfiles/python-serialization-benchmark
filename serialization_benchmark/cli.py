from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from serialization_benchmark.registry import encoded_adapters, primitive_adapters
from serialization_benchmark.validation import validate_all


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="serialization-benchmark")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate")
    run = subcommands.add_parser("run")
    run.add_argument("tier", choices=("primitive", "encoded"))
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--adapter", action="append", default=[])
    run.add_argument("--operation", action="append", default=[])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args, pyperf_args = parser.parse_known_args(argv)
    if args.command == "validate":
        validate_all()
        print(
            "validation passed: "
            f"{len(primitive_adapters())} primitive adapters, "
            f"{len(encoded_adapters())} encoded adapters"
        )
        return 0
    if args.command == "run":
        if pyperf_args and pyperf_args[0] != "--":
            parser.error("pyperf arguments must follow '--'")
        command = [
            sys.executable,
            "-m",
            "serialization_benchmark.runner",
            "--tier",
            args.tier,
            "-o",
            str(args.output),
        ]
        for adapter in args.adapter:
            command.extend(("--adapter", adapter))
        for operation in args.operation:
            command.extend(("--operation", operation))
        command.extend(pyperf_args[1:])
        completed = subprocess.run(command, check=False)
        return completed.returncode
    if pyperf_args:
        parser.error("unrecognized arguments: " + " ".join(pyperf_args))
    raise AssertionError(f"unsupported command: {args.command}")
