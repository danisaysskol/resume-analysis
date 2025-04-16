# Makefile for Skill Gap Analysis Project

.PHONY: help setup venv install lint format test seed clean export

help:
	@echo "Available targets:"
	@echo "  setup     - Install dependencies in a venv (resume-analysis-venv)"
	@echo "  venv      - Create a Python virtual environment"
	@echo "  install   - Install Python dependencies from requirements.txt"
	@echo "  lint      - Run black and flake8 on codebase"
	@echo "  format    - Auto-format code with black"
	@echo "  test      - Run demo seed to check DB & JSON export"
	@echo "  seed      - Populate DB and export JSON (demo_seed.py)"
	@echo "  export    - Export DB tables to JSON (demo_seed.py)"
	@echo "  clean     - Remove DB, JSON, and __pycache__ files"

venv:
	python3 -m venv resume-analysis-venv

setup: venv
	. resume-analysis-venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

install:
	. resume-analysis-venv/bin/activate && pip install -r requirements.txt

lint:
	. resume-analysis-venv/bin/activate && black resume_analysis scripts && flake8 resume_analysis scripts

format:
	. resume-analysis-venv/bin/activate && black resume_analysis scripts

test:
	PYTHONPATH=. resume-analysis-venv/bin/python scripts/demo_seed.py

seed: test

export: test

clean:
	rm -f db/resume_analysis.db
	rm -f data/*.json
	rm -rf __pycache__ resume_analysis/__pycache__ scripts/__pycache__
