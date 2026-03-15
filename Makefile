# NeuralPack — root Makefile
# All commands run from the repo root (NeuralPack/).

VENV       := .venv
PYTHON     := $(VENV)/bin/python
PIP        := $(VENV)/bin/pip
SESSIONS   := sessions
.DEFAULT_GOAL := help

# ── bootstrap ─────────────────────────────────────────────────────────────────

.PHONY: init
init: ## Pull submodules (if needed) and install packages into .venv
	git submodule update --init --recursive
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip -q
	$(PIP) install -e neuralpack-tasks -e neuralpack-comms -e neuralpack-core
	$(PIP) install pytest pytest-asyncio pytest-cov ruff mypy bandit -q
	@echo ""
	@echo "✓  Done. Activate with:  source $(VENV)/bin/activate"
	@echo "   Then run:             make run"

.PHONY: update
update: ## Pull latest for all submodules
	git submodule update --remote --merge

# ── run ───────────────────────────────────────────────────────────────────────

.PHONY: demo
demo: ## Run the end-to-end scripted demo (no stdin, no LLM)
	$(PYTHON) run_demo.py

.PHONY: run
run: ## Start the interactive CLI (no mock)
	$(VENV)/bin/np-comms

.PHONY: run-mock
run-mock: ## Start the interactive CLI with mock pipeline
	NEURALPACK_COMMS_MOCK_PIPELINE=true $(VENV)/bin/np-comms

.PHONY: run-debug
run-debug: ## Start the interactive CLI with mock pipeline + DEBUG logs
	NEURALPACK_COMMS_MOCK_PIPELINE=true \
	NEURALPACK_COMMS_LOG_LEVEL=DEBUG \
	$(VENV)/bin/np-comms

# ── inspect ───────────────────────────────────────────────────────────────────

.PHONY: inspect
inspect: ## List all sessions  (use: make inspect-session ID=a3f2)
	NEURALPACK_SESSIONS_DIR=$(SESSIONS) $(VENV)/bin/np-inspect

inspect-session: ## Inspect a specific session by ID prefix  (ID=required)
	NEURALPACK_SESSIONS_DIR=$(SESSIONS) $(VENV)/bin/np-inspect $(ID)

# ── test ──────────────────────────────────────────────────────────────────────

.PHONY: test
test: test-tasks test-comms ## Run all test suites

.PHONY: test-tasks
test-tasks: ## Run neuralpack-tasks tests
	cd neuralpack-tasks && ../$(PYTHON) -m pytest -q

.PHONY: test-comms
test-comms: ## Run neuralpack-comms tests
	cd neuralpack-comms && ../$(PYTHON) -m pytest -q

# ── lint ──────────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Lint + format check all repos
	cd neuralpack-tasks && ../$(PYTHON) -m ruff check . && ../$(PYTHON) -m ruff format --check .
	cd neuralpack-comms && ../$(PYTHON) -m ruff check . && ../$(PYTHON) -m ruff format --check .

# ── help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
