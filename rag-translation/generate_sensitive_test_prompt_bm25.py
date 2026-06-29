"""
RAG knowledge base from CN–EN / EN–CN translation Excel files.
Builds an index once (or loads from data/rag_index_storage if Excel sources unchanged),
then for each source file from the command line: query and write <stem>context.txt.
Usage: python knowledge_base.py [file1.txt file2.txt ...]
       If no files given, defaults to text1.txt in data/.
"""
import sys
from bm25 import BM25
from prompt_generator import PromptGenerator
from rag_document_loader import load_rag_indexing_documents
from query_loader import get_rag_query
from common import DATA_DIR

# --- Retrieval settings (tune these for more accurate results) ---
# How many translation pairs to retrieve for the prompt. Higher = more context, more noise.
TOP_K = 10
# Minimum similarity score (0–1). Raise to filter out weak matches (e.g. 0.5–0.7).
SIMILARITY_CUTOFF = 0.4


def main() -> None:
    # load or build indexing from documents

    docs = load_rag_indexing_documents()
    bm25 = BM25(docs)
    rag_query_file_path = sys.argv[1:]

    top_ks = (100,)

    rag_queries = get_rag_query(rag_query_file_path)
    generator = PromptGenerator()
    for top_k in top_ks:
        reference_generator = lambda rag_query: bm25.generate_references(bm25.query(rag_query, TOP_K))
        generator.generate_prompt_with_rag(reference_generator, rag_queries, lambda filename : DATA_DIR /f"{filename.stem}_top_k{top_k}_bm25_prompt.txt")

if __name__ == "__main__":
    main()