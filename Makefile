.PHONY: install test run
install:
\tpython3 -m venv .venv || true
\t. .venv/bin/activate; pip install -r requirements.txt
test:
\t. .venv/bin/activate; PYTHONPATH=./src pytest -q
run:
\t. .venv/bin/activate; PYTHONPATH=./src uvicorn jobpulse_api.main:app --reload --port 8010
