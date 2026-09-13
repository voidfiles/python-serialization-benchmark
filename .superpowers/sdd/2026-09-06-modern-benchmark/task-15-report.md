# Task 15: Documentation, CI, Docker, and Pages

## Implementation

- Rewrote `README.md` around the maintained primitive and format-partitioned encoded suites, executable local and Compose commands, benchmark methodology, result interpretation, pickle safety, and adapter requirements. Adaptix is explicitly labeled as a 3.0 beta prerelease, and format-crossing and composite comparisons are explicitly invalid.
- Extended `docker-compose.yml` with mounted primitive-handwritten and encoded-msgspec-JSON smoke services. `Dockerfile` already matched the required pinned uv 0.12.10 and Python 3.14 definition byte-for-byte, so it was verified without a no-op edit.
- Extended `.github/workflows/ci.yml` with a Python 3.14 smoke job. It runs exactly one case per tier with one process/value/warmup/loop and checks both raw files with `python -m pyperf check`; it makes no timing comparison.
- Added `.github/workflows/benchmark-pages.yml`, a manual-only one-job Python 3.14 workflow that syncs/tests/validates the locked environment, runs both rigorous suites, renders both report pairs, labels Pages output as a hardware-specific snapshot rather than a regression baseline, uploads raw/report artifacts, and deploys through the official Pages actions without secrets.
- Added trackable `results/raw` and `results/reports` anchors. Replaced obsolete root report ignores with a transient `results/site/` ignore, leaving canonical raw data and reports trackable.

## RED

Command: shell contract checks using `docker compose config --services`, `rg`, and `test -f` before implementation.

Output: Compose exposed only `tests` and `validate`; CI contained no smoke job, msgspec JSON case, or pyperf checks; `benchmark-pages.yml` and both result anchors were absent. Each expected contract check exited 1.

## GREEN

- `docker compose config --services`: `encoded`, `primitive`, `tests`, and `validate` all present.
- Real primitive-handwritten and encoded-msgspec-JSON smoke commands each wrote raw data; `python -m pyperf check` exited 0 for both. It emitted expected one-value instability warnings, with no performance threshold or comparison.
- `uv run pytest tests/test_cli.py tests/test_reporting.py`: 15 passed.
- Generated both report pairs from real pyperf data; both HTML pages contained the renderer's `index.html`/`encoded.html` navigation.
- Executed the exact embedded Pages header script against generated Markdown and HTML. All four artifacts carried `hardware-specific snapshot (not a regression baseline)`, and the script guards against unexpected renderer headings.

## Full verification

- `uv sync --locked`: resolved and audited the locked environment.
- `uv run pytest`: 50 passed on CPython 3.14.6.
- `uv run serialization-benchmark validate`: `validation passed: 10 primitive adapters, 12 encoded adapters`.
- Ruby parsed both workflow files and Compose as YAML; `docker compose config` resolved all commands, mounts, and services; `git diff --check` passed.
- The obsolete-library `rg` check returned no matches outside design history. Travis, `deploy-key.enc`, `deploy.sh`, `create_report.sh`, the misspelled discussion file, and README/workflow references to them are absent.
- `results/site` is ignored, while prospective files under `results/raw` and `results/reports` remain trackable.

## Docker validation

- `docker compose build` reached base-image metadata resolution but could not authenticate to `ghcr.io/astral-sh/uv:0.12.10`: the registry token request returned `403 Forbidden`. The first attempt also reported the Docker Hub auth transport closing for `python:3.14-slim`.
- `docker compose run --rm validate` and `docker compose run --rm tests` were attempted as required. Both exited 17 before container creation on the same external GHCR 403. No in-container assertion ran.
- The Dockerfile pin and complete Compose expansion were validated locally. Container execution must be retried where GHCR authentication succeeds.

## Self-review

- Commands match the installed CLI and pyperf separator contract. All smoke outputs have existing or mounted parent directories.
- CI remains a correctness matrix for quoted Python 3.12, 3.13, and 3.14; hosted performance is not used as a regression signal.
- The Pages workflow has only `workflow_dispatch`, one Python 3.14 job, least-necessary read/Pages/OIDC permissions, a protected `github-pages` environment, guarded hardware-snapshot headings, artifact retention, and the required official action versions.
- Published raw data and reports are not ignored. No plan, design spec, dependency, benchmark implementation, or external GitHub state was changed.

## Concerns

Container execution remains externally blocked by the repeatable GHCR 403. `actionlint` was not installed locally, so workflow validation consisted of YAML parsing, contract inspection, and execution of the local command/header/report paths; no GitHub workflow was triggered.
