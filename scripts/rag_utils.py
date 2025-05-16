import os
import faiss
import pickle
import warnings
import logging
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_together import ChatTogether
import fitz  # PyMuPDF

# Load environment variables and disable tokenizer parallelism
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", message=".*forked.*tokenizers.*")

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ---------------------------
# 📄 Index I/O
# ---------------------------
def load_index_and_docs(output_dir: str = "/app/faiss_store"):
    index_path = os.path.join(output_dir, "faiss_index.idx")
    metadata_path = os.path.join(output_dir, "doc_metadata.pkl")
    logger.info("Loading FAISS index and documents...")
    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        docs = pickle.load(f)
    return index, docs


def save_index(index, index_path: str, docs: List[Document], docs_path: str):
    faiss.write_index(index, index_path)
    with open(docs_path, "wb") as f:
        pickle.dump(docs, f)


# ---------------------------
# 📚 Rulebook Processing
# ---------------------------
def smart_split_rulebook(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    import re

    # Try numbered headings (e.g., 1., 1.2.)
    numbered = re.split(r"\n(?=\d{1,2}(?:\.\d+)*\.?\s+)", text)
    numbered = [s.strip() for s in numbered if s.strip()]
    if len(numbered) > 3:
        return numbered

    # Try all-caps headings (Stonemaier style)
    all_caps = re.split(r"\n(?=[A-Z][A-Z \-]{4,})\n", text)
    all_caps = [s.strip() for s in all_caps if len(s.strip()) > 50]
    if len(all_caps) > 3:
        return all_caps

    # Fallback: Recursive splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)


def extract_text_with_headings(doc):
    text_parts = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue
                    if span["size"] > 12 and "Bold" in span["font"]:
                        text_parts.append("\n===SECTION===\n")
                    text_parts.append(text)
    return "\n".join(text_parts)


def detect_section_type(text: str) -> str:
    section_keywords = {
        "Setup": ["setup", "game setup", "preparation"],
        "Victory": ["win", "victory", "scoring", "end of the game"],
        "Turn Order": ["turn", "phase", "actions", "player turn"],
        "Loot": ["loot", "booty", "treasure"],
        "Special Rules": ["solo", "variant", "expansion", "advanced"],
    }
    text_lower = text.lower()
    for label, keywords in section_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return label
    return "General"


def load_rulebooks(
    folder_path: str, chunk_size: int, chunk_overlap: int
) -> List[Document]:
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            path = os.path.join(folder_path, filename)
            game_name = filename.replace(".pdf", "").replace("_", " ").title()
            doc = fitz.open(path)
            logger.info(f"Parsing rulebook: {filename}")

            full_text = extract_text_with_headings(doc)
            chunks = smart_split_rulebook(full_text, chunk_size, chunk_overlap)

            for i, chunk in enumerate(chunks):
                section_type = detect_section_type(chunk)
                logger.debug(
                    f"[{game_name}] Chunk {i} ({section_type}): {chunk[:80].replace(chr(10), ' ')}..."
                )
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "game": game_name,
                            "chunk_id": i,
                            "section_type": section_type,
                        },
                    )
                )
    return documents


# ---------------------------
# 🤖 Embeddings + Search
# ---------------------------
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")


def embed_documents(docs: List[Document], model_name: str):
    model = SentenceTransformer(model_name)
    texts = [doc.page_content for doc in docs]
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings


def build_faiss_index(embeddings) -> faiss.Index:
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index


def get_top_k_chunks(
    question: str,
    docs: List[Document],
    index,
    k: int = 5,
    game: str = None,
    model_name: str = EMBEDDING_MODEL_NAME,
):
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([question])
    distances, indices = index.search(query_embedding, k * 2)
    top_docs = [docs[i] for i in indices[0]]
    if game:
        top_docs = [
            doc
            for doc in top_docs
            if game.lower() in doc.metadata.get("game", "").lower()
        ]
    return top_docs[:k]


# ---------------------------
# 🧠 Prompting + LLM
# ---------------------------
def extract_game_from_question(question: str) -> str | None:
    KNOWN_GAMES = os.getenv("KNOWN_GAMES", "").split(",")
    print("KNOWN_GAMES =", KNOWN_GAMES)
    for game in KNOWN_GAMES:
        if game.lower().strip() in question.lower().strip():
            return game
    return None


def build_prompt(question: str, retrieved_docs: list[Document]) -> str:
    context = "\n---\n".join([doc.page_content for doc in retrieved_docs])
    return f"""You are a board game rules expert. Use the context below to answer the question.
Answer the question as best you can using the context below.
If you're unsure, it's okay to infer based on the provided information.

Context:
{context}

Question: {question}
Answer:"""


# Only used in CLI/backend — pipeline does not need LLM
llm = ChatTogether(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1", temperature=0.7, max_tokens=512
)


def generate_answer(prompt: str) -> str:
    return llm.invoke(prompt).content
