import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from langchain_together import ChatTogether
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def extract_game_from_question(question: str, known_games: List[str]) -> Optional[str]:
    for game in known_games:
        if game.lower() in question.lower():
            return game
    return None


def get_top_k_chunks(
    question: str,
    docs: List[Document],
    index,
    k: int,
    game: Optional[str],
    embed_model: SentenceTransformer,
) -> List[Document]:
    logger.info("Embedding question...")
    query_embedding = embed_model.encode([question])
    distances, indices = index.search(query_embedding, k * 2)
    top_docs = [docs[i] for i in indices[0]]

    if game:
        top_docs = [doc for doc in top_docs if game.lower() in doc.metadata.get("game", "").lower()]

    return top_docs[:k]


def generate_answer(question: str, retrieved_docs: List[Document], llm: ChatTogether) -> str:
    context = "\n---\n".join([doc.page_content for doc in retrieved_docs])
    prompt = f"""You are a board game rules expert. Use the context below to answer the question.
Answer the question as best you can using the context below.
If you're unsure, it's okay to infer based on the provided information.

Context:
{context}

Question: {question}
Answer:"""
    return llm.invoke(prompt).content
