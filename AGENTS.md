# AGENTS.md

Research code for early prediction of addictive player behavior in responsible gambling: notebooks, experiments, and model training. See `README.md` for setup, commands, and project layout.

## Environment

- Use the project's virtual environment. Run commands through `make` (run `make` alone to list targets) or call `.venv/bin/python` directly. Never use the system Python or install packages globally.
- Add dependencies to `pyproject.toml` (`dependencies` for runtime, `dev` extra for tooling), then run `make requirements`. Don't `pip install` packages ad hoc.

## Code

- Put reusable logic in the `ante` package. Notebooks should import from it rather than define it.
- Pipeline scripts in `ante/` are Typer CLIs with path options. Keep new scripts in the same shape: defaults from `ante.config`, overridable from the command line.
- Get paths from `ante.config` (`RAW_DATA_DIR`, `PROCESSED_DATA_DIR`, `MODELS_DIR`, `FIGURES_DIR`, etc.). Never hardcode absolute or cwd-relative paths.
- Log with `loguru.logger`, not `print`. Use `tqdm` for progress bars.
- Read configuration and secrets from environment variables (loaded from `.env` on import of `ante`). When adding one, also add a placeholder to `.env.example`.

## Data and Models

- Treat `data/raw` as read-only. Write derived data to `data/interim` or `data/processed`.
- Never commit anything under `data/` or `models/`. Only the `.gitkeep` files are tracked.
- Player data may be sensitive. Inspect it through schemas, shapes, and aggregates rather than printing raw rows, and don't copy real records into code, tests, or docs.

## Notebooks

- Name notebooks `<number>-<initials>-<description>.ipynb`, e.g. `1.0-db-initial-data-exploration.ipynb`.
- Start them with `%load_ext autoreload` and `%autoreload 2` so changes to `ante` are picked up.

## Before Finishing a Task

Run `make format`, `make lint`, and `make test`, and report any failures rather than hiding them.
