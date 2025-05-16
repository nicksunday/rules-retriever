# --------------------------------------------
# 📌 Default task: show summary of all commands
# --------------------------------------------
default:
	@echo "🧠 Justfile for Rules Retriever: Available Commands"
	@just --summary


# ---------------------------
# 🔧 Build Docker Images
# ---------------------------

# Build all services (backend, frontend, dev, pipeline)
build:
	docker compose build

# Build individual services
build-backend:
	docker compose build backend

build-frontend:
	docker compose build frontend

build-dev:
	docker compose build dev

build-cli:
	docker compose build cli

build-pipeline:
	docker compose build pipeline

# ---------------------------
# 🧪 Indexing & Embeddings
# ---------------------------

# Uses values from .env: CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME, etc.
build-index:
	just check-env
	@echo "📚 Building FAISS index using .env values..."
	docker compose run --rm pipeline

# Full rebuild: recompile container, delete old index, and regenerate
rebuild-index:
	just clean-index
	just build-index

# Delete previously generated FAISS index files
clean-index:
	rm -f faiss_store/faiss_index.idx faiss_store/doc_metadata.pkl

# ---------------------------
# 🔎 Query the Assistant
# ---------------------------

# Ask a question via CLI (requires FAISS index)
query question:
	docker compose run --rm cli --question "{{question}}"


# ---------------------------
# 🚀 Run Services
# ---------------------------

# Start backend + frontend with fresh build
up:
	docker compose up --build

# Start only backend (useful for API testing)
backend-up:
	docker compose up --build backend

# Rebuild and restart backend (shortcut for dev)
backend-restart:
	docker compose build backend && docker compose up backend

# Start only frontend (useful for UI testing)
frontend-up:
	docker compose up --build frontend

# Stop all services and clean up orphans
down:
	docker compose down --remove-orphans

# Tail logs from all services
logs:
	docker compose logs -f


# ---------------------------
# 🎨 Linting & Formatting
# ---------------------------

# Run Ruff linter on scripts, backend, frontend
lint:
	docker compose run --rm dev "ruff check scripts backend frontend"

# Auto-fix lint issues with Ruff
lint-fix:
	docker compose run --rm dev "ruff check --fix scripts backend frontend"

# Format code using Ruff formatter
format:
	docker compose run --rm dev "ruff format scripts backend frontend"

# Show installed Ruff version
ruff-version:
	docker compose run --rm dev "ruff --version"


# ---------------------------
# 🧠 Preflight Checks
# ---------------------------

# Initialize local .env file from example, but don't overwrite existing config
init-env:
	@if [ -f .env ]; then \
		echo "⚠️  .env already exists. Skipping creation."; \
	else \
		cp .env.example .env && echo "✅ .env created from .env.example"; \
	fi

# Fail if .env file is missing
check-env:
	@if [ ! -f .env ]; then echo "❌ .env file is missing!"; exit 1; fi

# Fail if index files are missing
check-index:
	@if [ ! -f faiss_store/faiss_index.idx ] || [ ! -f faiss_store/doc_metadata.pkl ]; then \
		echo "❌ Index files missing! Run 'just build-index' first."; exit 1; fi

# Run both env and index checks together
dev-check:
	just check-env
	just check-index

