# Ante Research

Notebooks, experiments, and model training for early prediction of addictive player behavior in responsible gambling.

## Prerequisites

You need the following installed on your system:

- Python 3.11+
- GNU Make
- Git

## Getting Started

```sh
git clone https://github.com/ante-rg/ante-research
cd ante-research

make requirements        # creates .venv and installs all dependencies
cp .env.example .env     # on Windows cmd: copy .env.example .env
```

Run `make` with no arguments to list all available commands.

Every `make` command uses the project's `.venv` directly. Activate it explicitly when you want to run `python`, `jupyter`, etc. yourself:

| Shell              | Command                      |
| ------------------ | ---------------------------- |
| macOS/Linux        | `source .venv/bin/activate`  |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows cmd        | `.venv\Scripts\activate.bat` |

## Common Commands

| Command                   | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| `make requirements`       | Create `.venv` (if missing) and install dependencies |
| `make create_environment` | Only create `.venv`                                  |
| `make lint`               | Check formatting and lint errors with ruff           |
| `make format`             | Auto-fix lint errors and format code with ruff       |
| `make test`               | Run tests with pytest                                |
| `make clean`              | Delete `__pycache__` directories                     |
| `make data`               | Run `ante/dataset.py`                                |
| `make features`           | Run `ante/features.py`                               |
| `make train`              | Run `ante/modeling/train.py`                         |
| `make predict`            | Run `ante/modeling/predict.py`                       |

## Working on the Project

### Pipeline scripts

The scripts in `ante/` are small CLIs built with [Typer](https://typer.tiangolo.com/). Input and output paths have defaults but can be overridden:

```sh
python -m ante.modeling.train --help
python -m ante.modeling.train --model-path models/payment_review_model.json
```

Use `loguru.logger` for logging and `tqdm` for progress bars. `ante/config.py` sets them up to work together.

### Notebooks

- Name notebooks `<number>-<initials>-<description>.ipynb`, e.g. `1.0-db-initial-data-exploration.ipynb`.
- Put reusable code in the `ante` package and import it, rather than copying it between notebooks.
- `ante` is installed in editable mode, so code changes apply without reinstalling. Enable autoreload to pick them up without restarting the kernel:

  ```python
  %load_ext autoreload
  %autoreload 2

  from ante.config import RAW_DATA_DIR
  ```

Start Jupyter with `jupyter lab` from the activated venv, or select `.venv` as the kernel in your editor.

### Paths and configuration

- Use the paths from `ante.config` (`RAW_DATA_DIR`, `MODELS_DIR`, etc.) instead of hardcoding them. They resolve relative to the project root, so they work from scripts and notebooks alike.
- Put secrets and machine-specific settings in `.env`. Importing `ante` loads it into `os.environ`.
- When you add a new variable, also add it with a placeholder value to `.env.example`.

### Data and models

- Contents of `data/` and `models/` are not committed to Git. Only the folder structure is.
- Treat `data/raw` as read-only. Write transformed data to `data/interim` or `data/processed`.

### Dependencies

Add packages to `pyproject.toml`, then run `make requirements`:

- `dependencies` for anything the code or notebooks use.
- `[project.optional-dependencies] dev` for development tools (testing, linting).

### Before committing

```sh
make format
make lint
make test
```

## Research Documentation

- [TSI-100-v1 Data Description](docs/data-description.md)
- [Literature-to-Data Comparison](docs/literature-to-data-comparison.md)
- [Feature Readiness and Exploratory Analysis Plan](docs/feature-readiness-and-exploratory-analysis-plan.md)

## Project Organization

The layout follows [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) (v2) as a reference.

```txt
├── ante               <- Source code for use in this project.
│   ├── modeling
│   │   ├── __init__.py
│   │   ├── predict.py <- Code to run model inference with trained models.
│   │   └── train.py   <- Code to train models.
│   ├── __init__.py    <- Makes ante a Python module.
│   ├── config.py      <- Store useful variables and configuration.
│   ├── dataset.py     <- Scripts to download or generate data.
│   ├── features.py    <- Code to create features for modeling.
│   └── plots.py       <- Code to create visualizations.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
├── docs               <- Project documentation.
├── models             <- Trained and serialized models, model predictions, or model summaries.
├── notebooks          <- Jupyter notebooks (see naming convention above).
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting.
├── tests              <- Unit tests for the project code.
├── .env.example       <- Template for the local .env file.
├── LICENSE
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`.
├── pyproject.toml     <- Project metadata, dependencies, and tool configuration.
└── README.md
```

## License

[MIT](LICENSE)
