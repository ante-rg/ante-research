# ANTE research: indicators of gambling-related harm

This is a research prototype for **human review** of potential gambling-related harm. It does not diagnose addiction, make account decisions, or claim to reduce harm. Payment-event summaries are descriptive; predictive evaluation requires permitted, defensible outcome labels.

## Portfolio contents and evidence status

This public README is the annotated contents page for the group portfolio. Jurijs has confirmed the five team members and their planned roles below. The course team number and contribution shares are **pending**; no individual contribution is attributed here yet. Evidence links will be added as work is completed.

| Area | Evidence and purpose | Current status |
| --- | --- | --- |
| Proposal | Group proposal, problem, initial research, scope, plan | Independently reviewed local draft; team number and submission pending |
| Research protocol | [Question, data gate, point-in-time features and evaluation rules](docs/research_protocol.md) | Draft; no outcome labels confirmed |
| Work plan | [Milestones, Gantt and risk register](docs/project_plan.md) | Draft; team and Moodle dates pending |
| Roadmap | [Five planned work packages and adaptation of the teaching example](docs/roadmap.md), [live GitHub timeline](https://github.com/orgs/ante-rg/projects/1/views/3) | Planned dates through 15 Dec; not completion evidence |
| Project charter | [Purpose, scope, roles, acceptance and decision gates](docs/project_charter.md) | Working draft; data and course confirmation pending |
| Data management | [Access, provenance, privacy and publication plan](docs/data_management_plan.md) | Draft; private data access not confirmed |
| Data pipeline | [`ante/dataset.py`](ante/dataset.py), [`ante/payment_schema.py`](ante/payment_schema.py), [synthetic tests](tests/test_data.py) | Prototype; validates a prepared canonical CSV |
| Feature pipeline | [`ante/features.py`](ante/features.py), [boundary tests](tests/test_features.py) | Prototype; 7/30-day payment counts and amounts |
| Model and evaluation | [`ante/modeling`](ante/modeling), [synthetic tests](tests/test_modeling.py) | Working prototype; empirical evaluation pending permitted labels |
| API and app | [Single local API endpoint](ante/api.py), [synthetic API tests](tests/test_api.py), [ante-app](https://github.com/ante-rg/ante-app) | API prototype works locally; separate UI pending |
| Team process | [Kanban board](https://github.com/orgs/ante-rg/projects/1/views/1), [iteration log](docs/iteration_log.md), [meeting notes and template](docs/meetings/README.md), review notes and feedback | All 18 cards have descriptions; no actual meeting note or contribution log yet |
| Final analysis | Results, failure cases, limitations and recommendations | Pending data and tests |

**Team metadata:** team number `TBC`; verified contribution shares `TBC`. The planned roles reported by Jurijs are: Jurijs Kaminskis — product owner; Arturs Greķe — data engineer; Volodymyr Stishkovskyi — software developer and ML engineer; Andrejs Fjodorovs and Daniils Buts — data scientists. The reported course approval for a five-member team needs a course record. The team should record dated reviews and actual work before filling contribution shares. No private player row, individual prediction, credential or unapproved operator data belongs in this repository.

## Reproducible prototype

The canonical input is a prepared CSV with `event_id,player_id,event_time,event_type,amount,currency`. Timestamps must carry a UTC offset; `event_type` is `deposit` or `withdrawal`; amounts are positive. The source-specific mapping and permission decision must precede import of any external dataset.

```sh
make requirements
.venv/bin/python -m ante.dataset --input-path data/raw/payment_events.csv --output-path data/processed/payment_events.csv
.venv/bin/python -m ante.features --input-path data/processed/payment_events.csv --output-path data/processed/payment_features.csv --as-of 2026-10-15T00:00:00Z
make lint
make test
```

Individual-level outputs stay in ignored local `data/` paths. The current model prototype requires a **single-currency cohort** and independently supplied labels; a mixed-currency feature file must be split before training or prediction. See the [research protocol](docs/research_protocol.md) for the exact time-window boundary and limitations.

The model CLI requires separately prepared labeled training and holdout CSVs. Both have the 13 base columns (`player_id`, `currency`, `as_of_utc`, plus ten documented features) and `label`, `label_available_at_utc`. These labels must come from an independently documented source. Training refuses shared players, late training labels and nonchronological cohorts. Its JSON report contains aggregate proxy metrics only. See the [research protocol](docs/research_protocol.md) for the full validation boundary.

After an approved model artifact exists, the local API runs with `ANTE_MODEL_PATH=models/payment_review_model.json .venv/bin/uvicorn ante.api:app --host 127.0.0.1 --port 8000`. It exposes one business endpoint, `POST /assess`, accepting a timezone-aware `as_of` and canonical payment `events`. It returns per-player **relative review scores**, not diagnoses, calibrated risk probabilities or automatic decisions. The API has no authentication and must remain local until access control, threat review and deployment controls are designed.

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
