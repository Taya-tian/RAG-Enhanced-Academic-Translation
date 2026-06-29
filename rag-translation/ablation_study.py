from sympy.polys.polyconfig import query
from bm25 import BM25
from bm25_rag import BM25RAG
from common import RESULT_DIR
from datetime import datetime
from pathlib import Path
import sys

from prompt_generator import PromptGenerator
from query_loader import get_rag_query
from rag import RagIndex
from rag_document_loader import CN_EN_PATH, EN_CN_PATH, load_rag_indexing_documents

def main():
    query_files = get_rag_query(sys.argv[1:])
    filename = f"{Path(__file__).resolve().stem}_{datetime.now().strftime("%Y%m%d_%H%M%S")}"
    folder = RESULT_DIR / filename
    folder.mkdir(parents=True, exist_ok=True)
    prompt_generator = PromptGenerator()
    # generate prompt without rag
    prompt_generator.generate_prompt_without_rag(query_files, lambda f: folder / f"{f}_prompt.txt")
    documents = load_rag_indexing_documents()
    TOP_K = 100
    SIMILARITY_CUTOFF = 0.4
    # generate prompt with rag query without llm rerank
    rag = RagIndex(documents, (CN_EN_PATH, EN_CN_PATH))
    rag.get_rag_indexing()
    reference_generator = lambda rag_query: rag.generate_references(rag.query(rag_query, TOP_K, SIMILARITY_CUTOFF))
    prompt_generator.generate_prompt_with_rag(reference_generator, query_files, lambda f: folder / f"{f}_rag_prompt.txt")

    # generate prompt with rag with llm rerank
    rag = RagIndex(documents, (CN_EN_PATH, EN_CN_PATH))
    rag.get_rag_indexing(True)
    reference_generator = lambda rag_query: rag.generate_references(rag.query(rag_query, TOP_K, SIMILARITY_CUTOFF))
    prompt_generator.generate_prompt_with_rag(reference_generator, query_files, lambda f: folder / f"{f}_rag_llm_prompt.txt")

    # generate prompt with BM25
    bm25 = BM25(documents)
    reference_generator = lambda rag_query: bm25.generate_references(bm25.query(rag_query, TOP_K))
    prompt_generator.generate_prompt_with_rag(reference_generator, query_files, lambda f: folder / f"{f}_bm25_prompt.txt")

    # generate prompt with BM25 and rag
    bm25_rag = BM25RAG(documents)
    reference_generator = lambda rag_query: bm25_rag.generate_references(bm25_rag.query(rag_query, TOP_K, SIMILARITY_CUTOFF))
    prompt_generator.generate_prompt_with_rag(reference_generator, query_files, lambda f: folder / f"{f}_bm25_rag_prompt.txt")
    
    # generate prompt with BM25 and rag
    bm25_rag = BM25RAG(documents)
    reference_generator = lambda rag_query: bm25_rag.generate_references(bm25_rag.query(rag_query, TOP_K, SIMILARITY_CUTOFF, True))
    prompt_generator.generate_prompt_with_rag(reference_generator, query_files, lambda f: folder / f"{f}_bm25_rag_llm_prompt.txt")
   
if __name__ == "__main__":
    main()