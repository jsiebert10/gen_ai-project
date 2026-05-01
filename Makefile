-include .env
export ENV_NAME ?= myenv
PYTHON_VERSION = 3.12.12

.PHONY: help create install install-rag setup clean lint ingest
.PHONY: help create install install-backend setup clean lint run-backend

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

create:  ## Create conda environment
	@conda create -n $(ENV_NAME) python=$(PYTHON_VERSION) ipykernel -y -c conda-forge --override-channels
	@echo
	@echo "Run 'conda activate $(ENV_NAME)' to activate it."

install:  ## Install frontend requirements
	@conda run -n $(ENV_NAME) pip install -r requirements.txt
	@conda run -n $(ENV_NAME) pip install ruff

install-backend:  ## Install backend requirements
	@conda run -n $(ENV_NAME) pip install -r backend/requirements.txt

setup: create install install-backend  ## Create environment and install all dependencies

run-backend:  ## Start the FastAPI backend server
	@conda run -n $(ENV_NAME) uvicorn backend.main:app --reload --app-dir .

clean:  ## Remove conda environment
	@conda env remove -n $(ENV_NAME) -y
	@echo "Conda environment '$(ENV_NAME)' removed."

lint:  ## Run ruff check and format
	@conda run -n $(ENV_NAME) ruff check .
	@conda run -n $(ENV_NAME) ruff format .

install-rag:  ## Install RAG pipeline dependencies
	@conda run -n $(ENV_NAME) pip install -r requirements-rag.txt

CORPUS_DIR ?= data/corpus
INDEX_DIR  ?= indices

ingest:  ## Ingest corpus documents into the RAG vector store
	@conda run -n $(ENV_NAME) python scripts/ingest.py $(CORPUS_DIR) --output-dir $(INDEX_DIR)
	@conda run -n $(ENV_NAME) ruff format .
