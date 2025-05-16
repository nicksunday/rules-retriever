import os
from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def get_bool(name: str, default: bool = False) -> bool:
    return get_env(name, str(default)).lower() == "true"


def get_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in get_env(name, default).split(",") if item.strip()]


FAISS_INDEX_PATH = get_env("FAISS_INDEX_PATH", "faiss_store/faiss_index.idx")
METADATA_PATH = get_env("METADATA_PATH", "faiss_store/doc_metadata.pkl")
EMBEDDING_MODEL_NAME = get_env("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
TOGETHER_MODEL = get_env("TOGETHER_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")
KNOWN_GAMES = get_list("KNOWN_GAMES", "Euphoria,Libertalia,Stamp Swap,Quacks")
TRACING_ENABLED = get_bool("LANGCHAIN_TRACING_V2", False)
LANGCHAIN_PROJECT = get_env("LANGCHAIN_PROJECT", "rules-retriever")
