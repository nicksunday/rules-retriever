import os
import logging
import argparse
from rag_utils import (
    load_rulebooks,
    embed_documents,
    build_faiss_index,
    save_index,
)

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Build FAISS index from rulebooks.")

    # CLI flags with env + default fallback
    parser.add_argument(
        "--rulebook_dir",
        default=os.getenv("RULEBOOK_DIR", "rulebooks"),
        help="Directory containing rulebook PDFs",
    )
    parser.add_argument(
        "--output_dir",
        default=os.getenv("OUTPUT_DIR", "backend"),
        help="Directory to write FAISS index and metadata",
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=int(os.getenv("CHUNK_SIZE", 300)),
        help="Character chunk size for text splitting",
    )
    parser.add_argument(
        "--chunk_overlap",
        type=int,
        default=int(os.getenv("CHUNK_OVERLAP", 150)),
        help="Character overlap between chunks",
    )
    parser.add_argument(
        "--embedding_model",
        default=os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2"),
        help="Embedding model name to use",
    )

    args = parser.parse_args()

    # Resolve paths
    os.makedirs(args.output_dir, exist_ok=True)
    index_file = os.path.join(args.output_dir, "faiss_index.idx")
    docs_file = os.path.join(args.output_dir, "doc_metadata.pkl")

    logger.info("Loading rulebooks...")
    docs = load_rulebooks(args.rulebook_dir, args.chunk_size, args.chunk_overlap)
    logger.info(f"Loaded {len(docs)} document chunks.")

    logger.info("Generating embeddings...")
    embeddings = embed_documents(docs, args.embedding_model)

    logger.info("Building FAISS index...")
    index = build_faiss_index(embeddings)

    logger.info("Saving index and metadata...")
    save_index(index, index_file, docs, docs_file)
    logger.info(f"Index saved to {index_file}")
    logger.info(f"Metadata saved to {docs_file}")


if __name__ == "__main__":
    main()
