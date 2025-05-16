from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from langchain_together import ChatTogether

from config import (
    FAISS_INDEX_PATH,
    METADATA_PATH,
    EMBEDDING_MODEL_NAME,
    TOGETHER_MODEL,
    KNOWN_GAMES,
    TRACING_ENABLED,
    LANGCHAIN_PROJECT,
)
from models import QuestionRequest
from query_pipeline import extract_game_from_question, get_top_k_chunks, generate_answer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
faiss_index = None
docs = None
embedding_model = None
llm = None


@app.on_event("startup")
def on_startup():
    global faiss_index, docs, embedding_model, llm

    logger.info("Loading FAISS index...")
    faiss_index = faiss.read_index(FAISS_INDEX_PATH)

    logger.info("Loading document metadata...")
    with open(METADATA_PATH, "rb") as f:
        docs = pickle.load(f)

    logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    logger.info(f"Initializing LLM: {TOGETHER_MODEL}")
    llm = ChatTogether(model=TOGETHER_MODEL, temperature=0.7, max_tokens=512)

    if TRACING_ENABLED:
        from langsmith import Client

        Client()
        logger.info(f"LangSmith project: {LANGCHAIN_PROJECT}")

    try:
        llm.invoke("Say hello")
        logger.info("LLM warm-up complete.")
    except Exception as e:
        logger.warning(f"LLM warm-up failed: {e}")


@app.post("/ask")
async def ask_question(payload: QuestionRequest):
    try:
        start = time.time()
        game = extract_game_from_question(payload.question, KNOWN_GAMES)
        logger.info(f"Received question for game: {game}")

        top_docs = get_top_k_chunks(
            payload.question, docs, faiss_index, payload.k, game, embedding_model
        )
        answer = generate_answer(payload.question, top_docs, llm)

        logger.info(f"Answered in {time.time() - start:.2f}s")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))
