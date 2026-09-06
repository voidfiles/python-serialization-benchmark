from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from serialization_benchmark.registry import encoded_adapters, primitive_adapters
from serialization_benchmark.reporting import ReportError, load_report, render_html, render_markdown
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
    report = subcommands.add_parser("report")
    report.add_argument("raw_json", type=Path)
    report.add_argument("--markdown", type=Path, required=True)
    report.add_argument("--html", type=Path, required=True)
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
    if args.command == "report":
        if pyperf_args:
            parser.error("unrecognized arguments: " + " ".join(pyperf_args))
        try:
            report = load_report(args.raw_json)
            _write_text_atomically(args.markdown, render_markdown(report))
            _write_text_atomically(args.html, render_html(report))
        except ReportError as error:
            print(f"report failed: {error}", file=sys.stderr)
            return 1
        return 0
    if pyperf_args:
        parser.error("unrecognized arguments: " + " ".join(pyperf_args))
    raise AssertionError(f"unsupported command: {args.command}")


def _write_text_atomically(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(contents)
            temporary_path = Path(temporary_file.name)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
