import argparse
import logging
import os

from rag_utils import (
    load_index_and_docs,
    extract_game_from_question,
    get_top_k_chunks,
    build_prompt,
    generate_answer,
)

from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.panel import Panel

console = Console()
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    parser = argparse.ArgumentParser(description="Ask a board game rules question")

    parser.add_argument("--question", type=str, help="The question to ask")
    parser.add_argument("--k", type=int, default=12, help="Number of chunks to retrieve")

    parser.add_argument(
        "--index_dir",
        default=os.getenv("OUTPUT_DIR", "/app/faiss_store"),
        help="Path to FAISS index and metadata files",
    )
    parser.add_argument(
        "--embedding_model",
        default=os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2"),
        help="Embedding model to use for similarity search",
    )

    args = parser.parse_args()

    question = args.question or Prompt.ask("🎲 What rule would you like to ask about?")
    console.print(f"[bold cyan]🔍 Question:[/bold cyan] {question}")

    index, docs = load_index_and_docs(args.index_dir)
    game = extract_game_from_question(question)

    if game:
        console.print(f"[bold green]🎯 Detected game:[/bold green] {game}")
    else:
        console.print(
            "[yellow]⚠️ No specific game detected. Using all documents.[/yellow]"
        )

    top_docs = get_top_k_chunks(
        question,
        docs,
        index,
        k=args.k,
        game=game,
        model_name=args.embedding_model,
    )

    if logger.isEnabledFor(logging.DEBUG):
        console.print("\n[bold magenta]Retrieved Chunks:[/bold magenta]")
        for doc in top_docs:
            game_name = doc.metadata.get("game", "Unknown Game")
            content_preview = doc.page_content[:300].strip().replace("\n", " ")
            console.print(f"[blue][{game_name}][/blue] {content_preview}...\n")

    prompt = build_prompt(question, top_docs)

    with console.status("💭 Generating answer with LLM...", spinner="dots"):
        answer = generate_answer(prompt)

    console.print(
        Panel.fit(
            Text(answer.strip(), style="bold white"),
            title="🎓 Answer",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    main()
