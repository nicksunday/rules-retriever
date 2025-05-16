# 🧠 Rules Retriever

**Rules Retriever** is a Retrieval-Augmented Generation (RAG) system for answering natural language questions about board games. It ingests rulebook PDFs and lets you ask questions like:

> "How do you win in Libertalia?"

Built with a modular Docker-based architecture, it's designed for fast iteration, accurate answers, and clean dev experience. It also logs backend interactions to **LangSmith** for traceable prompt evaluation.

---

## 📑 Table of Contents

- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Rulebooks](#-rulebooks)
- [Quickstart](#-quickstart)
- [Justfile Commands](#-justfile-commands)
- [Example Queries](#-example-queries)
- [Future Ideas](#-future-ideas)
- [Project Structure](#-project-structure)

---

## 🎯 Features

* 🔍 Semantic search over board game rulebooks using Sentence Transformers and FAISS
* 📚 Smart PDF chunking using visual cues (bolded/large headings) or fallback text splitting
* 🧠 Context-tagging by rulebook section type ("Setup", "Victory", etc.)
* ⚡ LLM answers powered by TogetherAI's Mixtral model
* 🧪 Fully Dockerized with CLI, backend API, and frontend
* 📊 **LangSmith tracing** enabled for LLM debugging and prompt evaluation

---

## 🛠️ Tech Stack

* **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
* **Vector Index:** FAISS
* **LLM:** `Mixtral-8x7B-Instruct` via TogetherAI
* **PDF Parsing:** PyMuPDF
* **Backend API:** FastAPI
* **Frontend (optional):** Streamlit
* **Dev/CLI Tooling:** Docker, Just, Ruff
* **Tracing:** LangSmith (optional)

---

## 📥 Rulebooks

This project does not include copyrighted rulebook PDFs.
To use the system, you'll need to download them manually and place them in the `rulebooks/` directory.

Here are some links to get you started:

* [Libertalia Rules (Stonemaier Games)](https://stonemaiergames.com/games/libertalia/rules-faq/)
* [Quacks of Quedlinburg - All In Rulebook (BoardGameGeek)](https://boardgamegeek.com/file/download_redirect/7a4328fd89b46bb9b58a9f0b19e338d984020cd5c7f6632f/Quacks+All+In+how+to+play+booklet.pdf)

Once downloaded, place the PDFs in the `rulebooks/` folder. You may want to rename them to clean, recognizable names like `Libertalia.pdf` or `Quacks.pdf` for better metadata tagging during indexing.  The indexing pipeline will automatically process all `.pdf` files in that directory.

## 🚀 Quickstart

```bash
# 1. Clone and configure
just init-env  # Add your API keys to .env

# 2. Build the FAISS index from rulebooks
just build-index

# 3. Ask a question via CLI
just query "How do you win in Libertalia?"

# Or bring up the API
just up  # visit http://localhost:8501/
```

---

## 📚 Justfile Commands

### 🔧 Build Containers

```
just build            # Build all services
just build-backend    # Build backend only
just build-frontend   # Build frontend only
just build-dev        # Build dev container
just build-cli        # Build CLI container
just build-pipeline   # Build indexing pipeline
```

### 🧪 Indexing & Embeddings

```
just build-index      # Build FAISS index from PDFs using .env settings
just rebuild-index    # Clean and rebuild index
just clean-index      # Remove index files (faiss_index.idx, doc_metadata.pkl)
```

### 🔎 Query the Assistant

```
just query "your question here"  # Ask a rules question
```

### 🚀 Run Services

```
just up               # Run backend + frontend
just backend-up       # Run backend only
just backend-restart  # Rebuild and restart backend
just frontend-up      # Run frontend only
just down             # Stop all services
just logs             # Tail logs
```

### 🎨 Linting & Formatting

```
just lint             # Run Ruff linter
just lint-fix         # Auto-fix issues
just format           # Format code
just ruff-version     # Show Ruff version
```

### 🧠 Preflight Checks

```
just init-env         # Create .env from .env.example if missing
just check-env        # Fail if .env is missing
just check-index      # Fail if index files are missing
just dev-check        # Run all startup checks
```

---

## 🔍 Example Queries

```text
❓ How do you calculate essence for the Alchemists expansion in Quacks?
🎯 Detected game: Quacks
🎓 Answer: You calculate essence after brewing your potion...

❓ How do you win in Libertalia?
🎯 Detected game: Libertalia
🎓 Answer: The player with the highest reputation at the end of three voyages wins...
```

---

## 🧠 Future Ideas

* Migrate to LangChain structured retrievers with metadata filtering
* Add tie-breaking logic for chunk scoring (e.g. boost section\_type="Victory")
* UI polish + API logging tools
* Automatic enrichment from FAQ/Errata docs

---

## 📂 Project Structure

```
.
├── backend/           # FastAPI backend + config
├── scripts/           # CLI + indexing logic
├── frontend/          # Optional Streamlit UI
├── faiss_store/       # Stores index + metadata
├── rulebooks/         # Input PDFs (Quacks.pdf, etc.)
├── justfile           # All CLI and dev commands
├── docker-compose.yml
└── .env / .env.example
```
