"""
RAG knowledge base from CN–EN / EN–CN translation Excel files.
Builds an index once (or loads from data/rag_index_storage if Excel sources unchanged),
then for each source file from the command line: query and write <stem>context.txt.
Usage: python knowledge_base.py [file1.txt file2.txt ...]
       If no files given, defaults to text1.txt in data/.
"""
import sys
from common import DATA_DIR
from prompt_generator import PromptGenerator
from rag import RagIndex
from rag_document_loader import CN_EN_PATH, EN_CN_PATH, load_rag_indexing_documents
from query_loader import get_rag_query

# --- Retrieval settings (tune these for more accurate results) ---
# How many translation pairs to retrieve for the prompt. Higher = more context, more noise.
TOP_K = 30
# Minimum similarity score (0–1). Raise to filter out weak matches (e.g. 0.5–0.7).
SIMILARITY_CUTOFF = 0.4

# --- What affects retrieval accuracy ---
# • Embedding model (Settings.embed_model): better CN/EN model = better similarity (e.g. BAAI/bge-m3).
# • TOP_K: larger = more references, but can add noise; tune for your glossary size.
# • SIMILARITY_CUTOFF: higher (e.g. 0.5–0.7) = stricter, fewer but more relevant results.
# • USE_LLM_RERANK: True + Settings.llm set = two-stage retrieval (embedding recall + LLM rerank) for better ordering.
# • Chunking: each row is one “chunk” here; no chunk_size/overlap effect on index, but embed model’s max length still applies.
# An LLM in this script is optional: only needed for reranking. Final translation is still done by you in ChatGPT.


def main() -> None:
    # load or build indexing from documents
    lang = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ["cn", "en"] else None

    documents = load_rag_indexing_documents(lang)
    rag = RagIndex(documents)
    rag.get_rag_indexing()

    # get the query from the user input

    rag_query_file_path = sys.argv[1:] if lang is None else sys.argv[2:]

    rag_queries = get_rag_query(rag_query_file_path)

    prompt_generator = PromptGenerator()
    prompt_generator.generate_prompt_without_rag(rag_queries)
    reference_generator = lambda rag_query: rag.generate_references(rag.query(rag_query, TOP_K, SIMILARITY_CUTOFF))
    prompt_generator.generate_prompt_with_rag(reference_generator, rag_queries, lambda filename: DATA_DIR / (f"{filename}_rag_prompt.txt" if lang is None else f"{filename}_{lang}_rag_prompt.txt"))

if __name__ == "__main__":
    main()