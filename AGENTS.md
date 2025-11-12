# Repository Guidelines

## Project Structure & Module Organization
`src/epftools` houses the Python package, with modules scoped to specific workflows (e.g., `anomaly_detector.py` for claims analytics, `pdf_tools.py` for PDF utilities, `gui.py` for the desktop launcher). Shared helpers belong in `validation_utils.py` to avoid duplication. Tests live in `tests/`, mirroring module names; use `tests/todo/` for placeholders that still need assertions. Project metadata and packaging live in `setup.py`, `pyproject.toml`, and `MANIFEST.in`; update them whenever you add public modules. Reference `.editorconfig` for workspace defaults.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: create and enter a clean dev environment.
- `pip install -e .[dev,ocr,ml]`: install the package with extras needed for OCR and ML paths plus manifest checks.
- `pytest tests`: run the focused test suite locally; add `-k name` when iterating on a single module.
- `tox -e py311`: execute the CI-equivalent pipeline (manifest checks, packaging sanity, full tests) against Python 3.11.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation for Python files (enforced via `.editorconfig`). Modules stay lowercase with underscores; classes use `CamelCase`; functions and variables use `snake_case`. Prefer explicit imports from within `epftools` to keep dependency graphs clear. Align formatting with the existing codebase—avoid introducing new tooling without discussion and let the editor maintain spacing and newline rules defined in `.editorconfig`.

## Testing Guidelines
Pytest is the primary framework. Name new test files `test_<module>.py` and test functions `test_<behavior>`. Provide fixtures for heavy I/O objects so test runs stay fast. When adding analytics or reporting features, assert both the resulting DataFrame schema and key values. Ensure GUI changes have smoke coverage through `tests/test_gui.py` and guard optional dependencies with `pytest.importorskip`.

## Commit & Pull Request Guidelines
Write concise, imperative commit subjects (e.g., `gui: block duplicate exports`). Group related fixes into a single commit and include brief body context when touching data pipelines. Pull requests should summarize motivation, link any GitHub issues, and list manual verification steps or screenshots for GUI or reporting changes. Always mention new dependencies and confirm that `pytest` and `tox` pass before requesting review.

## Security & Configuration Tips
Never commit credentials; use `vscode.env` or user-specific env files for secrets. Sanitise sample data before adding it to `tests/` or documentation. When scraping or automating external sites (`website_scraper.py`), respect rate limits and wrap configuration in environment variables so credentials remain out of the codebase.
