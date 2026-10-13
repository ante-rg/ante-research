#################################################################################
# GLOBALS                                                                       #
#################################################################################

MODULE_NAME = ante
VENV_DIR = .venv

# Interpreter used only to create the virtual environment. Override if needed,
# e.g. `make create_environment SYSTEM_PYTHON=python3.12`.
ifeq ($(OS),Windows_NT)
SYSTEM_PYTHON ?= py
VENV_PYTHON = $(VENV_DIR)/Scripts/python.exe
else
SYSTEM_PYTHON ?= python3
VENV_PYTHON = $(VENV_DIR)/bin/python
endif

# Quoted so that forward-slash paths also work when make runs recipes in cmd.exe
PYTHON = "$(VENV_PYTHON)"

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Create the virtual environment
.PHONY: create_environment
create_environment: $(VENV_PYTHON)

$(VENV_PYTHON):
	$(SYSTEM_PYTHON) -m venv $(VENV_DIR)

## Install Python dependencies into the virtual environment
.PHONY: requirements
requirements: $(VENV_PYTHON)
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e ".[dev]"

## Delete all __pycache__ directories
.PHONY: clean
clean:
	$(SYSTEM_PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in list(pathlib.Path().rglob('__pycache__')) if '$(VENV_DIR)' not in p.parts]"

## Lint using ruff
.PHONY: lint
lint:
	$(PYTHON) -m ruff format --check $(MODULE_NAME)
	$(PYTHON) -m ruff check $(MODULE_NAME)

## Format source code with ruff
.PHONY: format
format:
	$(PYTHON) -m ruff check --fix $(MODULE_NAME)
	$(PYTHON) -m ruff format $(MODULE_NAME)

## Run tests
.PHONY: test
test:
	$(PYTHON) -m pytest tests

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## Make dataset
.PHONY: data
data:
	$(PYTHON) -m $(MODULE_NAME).dataset

## Generate features
.PHONY: features
features:
	$(PYTHON) -m $(MODULE_NAME).features

## Train models
.PHONY: train
train:
	$(PYTHON) -m $(MODULE_NAME).modeling.train

## Run model inference
.PHONY: predict
predict:
	$(PYTHON) -m $(MODULE_NAME).modeling.predict

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

## Show available commands
.PHONY: help
help:
	@$(SYSTEM_PYTHON) -c "import re; [print(f'{t:<20}{d}') for d, t in re.findall(r'^## (.*)\n(?:\.PHONY: .*\n)?([\w-]+):', open('$(firstword $(MAKEFILE_LIST))').read(), re.M)]"
