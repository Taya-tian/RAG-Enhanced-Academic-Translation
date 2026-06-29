"""
RAG knowledge base from CN–EN / EN–CN translation Excel files.
Builds an index once (or loads from data/rag_index_storage if Excel sources unchanged),
then for each source file from the command line: query and write <stem>context.txt.
Usage: python knowledge_base.py [file1.txt file2.txt ...]
       If no files given, defaults to text1.txt in data/.
"""
import sys
from prompt_generator import PromptGenerator
from rag import RagIndex
from rag_document_loader import CN_EN_PATH, EN_CN_PATH, load_rag_indexing_documents
from query_loader import get_rag_query
from common import RESULT_DIR
from datetime import datetime

# --- Retrieval settings (tune these for more accurate results) ---
# How many translation pairs to retrieve for the prompt. Higher = more context, more noise.
TOP_K = 10
# Minimum similarity score (0–1). Raise to filter out weak matches (e.g. 0.5–0.7).
SIMILARITY_CUTOFF = 0.4
# Use an LLM to rerank retrieved nodes (better order, higher cost/latency). Set to True and set Settings.llm to enable.
USE_LLM_RERANK = False

# --- What affects retrieval accuracy ---
# • Embedding model (Settings.embed_model): better CN/EN model = better similarity (e.g. BAAI/bge-m3).
# • TOP_K: larger = more references, but can add noise; tune for your glossary size.
# • SIMILARITY_CUTOFF: higher (e.g. 0.5–0.7) = stricter, fewer but more relevant results.
# • USE_LLM_RERANK: True + Settings.llm set = two-stage retrieval (embedding recall + LLM rerank) for better ordering.
# • Chunking: each row is one “chunk” here; no chunk_size/overlap effect on index, but embed model’s max length still applies.
# An LLM in this script is optional: only needed for reranking. Final translation is still done by you in ChatGPT.


def main() -> None:
    # load or build indexing from documents

    documents = load_rag_indexing_documents()
    # get the query from the user input

    rag_query_file_path = sys.argv[1:]

    rag_queries = get_rag_query(rag_query_file_path)
    rag = RagIndex(documents, (CN_EN_PATH, EN_CN_PATH))
    prompt_generator = PromptGenerator()

    top_ks = (10, 20, 40, 80, 100)
    similarities = (0.4, 0.5, 0.6)
    folder = RESULT_DIR / f"sensitive_test_prompt_{datetime.now().strftime("%Y%m%d_%H%M%S")}"
    folder.mkdir(parents=True, exist_ok=True)
    rag.get_rag_indexing()


    for top_k in top_ks:
        for similarity in similarities:
            query_engine = rag.create_query_engine(top_k, similarity)
            reference_generator = lambda rag_query: rag.generate_references(query_engine.query(rag_query).source_nodes)
            prompt_generator.generate_prompt_with_rag(reference_generator, rag_queries, lambda filename: folder /f"{filename}_top_k{top_k}similarity{similarity}_prompt.txt")

if __name__ == "__main__":
    main()