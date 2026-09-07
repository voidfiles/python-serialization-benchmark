from __future__ import annotations

import argparse
import gc
import subprocess
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from importlib.metadata import version

import pyperf

from serialization_benchmark.contracts import EncodedAdapter, PrimitiveAdapter
from serialization_benchmark.fixtures import FixtureSet, make_fixtures
from serialization_benchmark.registry import encoded_adapters, primitive_adapters
from serialization_benchmark.validation import (
    validate_encoded_adapter,
    validate_primitive_adapter,
)

_UNREACHABLE_SENTINEL = object()


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    operation: Callable[[], object]
    metadata: dict[str, str | int]


def _case_metadata(
    adapter: PrimitiveAdapter | EncodedAdapter,
    *,
    tier: str,
    operation: str,
    batch_size: int,
    encoded_format: str = "",
    payload_bytes: int | None = None,
) -> dict[str, str | int]:
    metadata: dict[str, str | int] = {
        "tier": tier,
        "adapter_slug": adapter.metadata.slug,
        "adapter_name": adapter.metadata.name,
        "package": adapter.metadata.package,
        "library_version": adapter.metadata.version,
        "model_strategy": adapter.metadata.model_strategy,
        "prerelease": str(adapter.metadata.prerelease).lower(),
        "operation": operation,
        "batch_size": batch_size,
        "gc": "enabled",
    }
    if encoded_format:
        metadata["format"] = encoded_format
    if payload_bytes is not None:
        metadata["payload_bytes"] = payload_bytes
    return metadata


def _case_name(adapter: PrimitiveAdapter | EncodedAdapter, tier: str, operation: str) -> str:
    return ".".join((tier, operation, adapter.metadata.slug, adapter.metadata.model_strategy))


def build_primitive_cases(
    fixtures: FixtureSet,
    adapters: Sequence[PrimitiveAdapter] | None = None,
) -> tuple[BenchmarkCase, ...]:
    cases: list[BenchmarkCase] = []
    selected_adapters = primitive_adapters() if adapters is None else adapters
    one = fixtures.one
    many = list(fixtures.many)
    one_primitive = fixtures.one_primitive
    many_primitives = list(fixtures.many_primitives)

    for adapter in selected_adapters:
        if "dump_one" in adapter.operations:
            cases.append(
                BenchmarkCase(
                    _case_name(adapter, "primitive", "dump_one"),
                    partial(adapter.dump_one, one),
                    _case_metadata(
                        adapter,
                        tier="primitive",
                        operation="dump_one",
                        batch_size=1,
                    ),
                )
            )
        if "load_one" in adapter.operations:
            cases.append(
                BenchmarkCase(
                    _case_name(adapter, "primitive", "load_one"),
                    partial(adapter.load_one, one_primitive),
                    _case_metadata(
                        adapter,
                        tier="primitive",
                        operation="load_one",
                        batch_size=1,
                    ),
                )
            )
        if "dump_many" in adapter.operations:
            cases.append(
                BenchmarkCase(
                    _case_name(adapter, "primitive", "dump_many"),
                    partial(adapter.dump_many, many),
                    _case_metadata(
                        adapter,
                        tier="primitive",
                        operation="dump_many",
                        batch_size=len(many),
                    ),
                )
            )
        if "load_many" in adapter.operations:
            cases.append(
                BenchmarkCase(
                    _case_name(adapter, "primitive", "load_many"),
                    partial(adapter.load_many, many_primitives),
                    _case_metadata(
                        adapter,
                        tier="primitive",
                        operation="load_many",
                        batch_size=len(many_primitives),
                    ),
                )
            )
    return tuple(cases)


def build_encoded_cases(
    fixtures: FixtureSet,
    adapters: Sequence[EncodedAdapter] | None = None,
) -> tuple[BenchmarkCase, ...]:
    cases: list[BenchmarkCase] = []
    selected_adapters = encoded_adapters() if adapters is None else adapters
    one = fixtures.one
    many = list(fixtures.many)

    for adapter in selected_adapters:
        one_payload = (
            adapter.encode_one(one)
            if {"encode_one", "decode_one"} & adapter.operations
            else None
        )
        many_payload = (
            adapter.encode_many(many)
            if {"encode_many", "decode_many"} & adapter.operations
            else None
        )
        if "encode_one" in adapter.operations:
            assert one_payload is not None
            cases.append(
                BenchmarkCase(
                    _case_name(adapter, "encoded", "encode_one"),
                    partial(adapter.encode_one, one),
                    _case_metadata(
                        adapter,
                        tier="encoded",
                        operation="encode_one",
                        batch_size=1,
                        encoded_format=adapter.format,
                        payload_bytes=len(one_payload),
                    ),
                )
            )
        if "decode_one" in adapter.operations:
            assert one_payload is not None
            cases.append(
                BenchmarkCase(
                    _case_name(adapter, "encoded", "decode_one"),
                    partial(adapter.decode_one, one_payload),
                    _case_metadata(
                        adapter,
                        tier="encoded",
                        operation="decode_one",
                        batch_size=1,
                        encoded_format=adapter.format,
                        payload_bytes=len(one_payload),
                    ),
                )
            )
        if "encode_many" in adapter.operations:
            assert many_payload is not None
            cases.append(
                BenchmarkCase(
                    _case_name(adapter, "encoded", "encode_many"),
                    partial(adapter.encode_many, many),
                    _case_metadata(
                        adapter,
                        tier="encoded",
                        operation="encode_many",
                        batch_size=len(many),
                        encoded_format=adapter.format,
                        payload_bytes=len(many_payload),
                    ),
                )
            )
        if "decode_many" in adapter.operations:
            assert many_payload is not None
            cases.append(
                BenchmarkCase(
                    _case_name(adapter, "encoded", "decode_many"),
                    partial(adapter.decode_many, many_payload),
                    _case_metadata(
                        adapter,
                        tier="encoded",
                        operation="decode_many",
                        batch_size=len(many),
                        encoded_format=adapter.format,
                        payload_bytes=len(many_payload),
                    ),
                )
            )
    return tuple(cases)


def _time_operation(loops: int, operation: Callable[[], object]) -> float:
    gc.enable()
    result: object = None
    start = time.perf_counter()
    for _ in range(loops):
        result = operation()
    elapsed = time.perf_counter() - start
    if result is _UNREACHABLE_SENTINEL:
        raise AssertionError("unreachable")
    return elapsed


def _git_revision() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    revision = completed.stdout.strip()
    return revision if completed.returncode == 0 and revision else "unknown"


def _global_metadata(run_utc: str) -> dict[str, str]:
    return {
        "git_revision": _git_revision(),
        "benchmark_version": version("python-serialization-benchmark"),
        "gc": "enabled",
        "run_utc": run_utc,
    }


def _build_parser(run_utc: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m serialization_benchmark.runner")
    parser.add_argument("--tier", choices=("primitive", "encoded"), required=True)
    parser.add_argument("--adapter", action="append", default=[])
    parser.add_argument("--operation", action="append", default=[])
    parser.add_argument("--run-utc", default=run_utc, help=argparse.SUPPRESS)
    return parser


def _add_cmdline_args(command: list[str], args: argparse.Namespace) -> None:
    command.extend(("--tier", args.tier))
    for adapter in args.adapter:
        command.extend(("--adapter", adapter))
    for operation in args.operation:
        command.extend(("--operation", operation))
    command.extend(("--run-utc", args.run_utc))


def _selected_adapters(
    adapters: Sequence[PrimitiveAdapter] | Sequence[EncodedAdapter],
    slugs: Sequence[str],
) -> tuple[PrimitiveAdapter, ...] | tuple[EncodedAdapter, ...]:
    return tuple(adapter for adapter in adapters if not slugs or adapter.metadata.slug in slugs)


def _filter_cases(
    cases: Sequence[BenchmarkCase],
    adapters: Sequence[str],
    operations: Sequence[str],
) -> tuple[BenchmarkCase, ...]:
    return tuple(
        case
        for case in cases
        if (not adapters or case.metadata["adapter_slug"] in adapters)
        and (not operations or case.metadata["operation"] in operations)
    )


def main() -> int:
    run_utc = datetime.now(timezone.utc).isoformat()
    runner = pyperf.Runner(
        metadata=_global_metadata(run_utc),
        program_args=("-m", "serialization_benchmark.runner"),
        add_cmdline_args=_add_cmdline_args,
        _argparser=_build_parser(run_utc),
    )
    args = runner.parse_args()
    runner.metadata["run_utc"] = args.run_utc
    fixtures = make_fixtures()

    if args.tier == "primitive":
        adapters = _selected_adapters(primitive_adapters(), args.adapter)
        if not adapters:
            raise RuntimeError("no primitive adapters were selected")
        for adapter in adapters:
            validate_primitive_adapter(adapter, fixtures)
        cases = build_primitive_cases(fixtures, adapters)
    else:
        adapters = _selected_adapters(encoded_adapters(), args.adapter)
        if not adapters:
            raise RuntimeError("no encoded adapters were selected")
        for adapter in adapters:
            validate_encoded_adapter(adapter, fixtures)
        cases = build_encoded_cases(fixtures, adapters)

    selected_cases = _filter_cases(cases, args.adapter, args.operation)
    if not selected_cases:
        raise RuntimeError("no benchmark cases were selected")
    for case in selected_cases:
        runner.bench_time_func(
            case.name,
            _time_operation,
            case.operation,
            metadata=case.metadata,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
