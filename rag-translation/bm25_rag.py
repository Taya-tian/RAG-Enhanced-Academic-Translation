import jieba
import re
from llama_index.core import query_engine
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List

from bm25 import BM25
from rag import RagIndex

class BM25RAG(BM25):
  def __init__(self, documents) -> None:
    super().__init__(documents)

  def query(self, rag_query, top_k, similarity, use_llm=False):
    tokenized_query = self.mixed_tokenizer(rag_query)
    scores = self.query_engine.get_scores(tokenized_query)
    top_n = np.argsort(scores)[::-1][:top_k * 5]
    documents =  [self.documents[i] for i in top_n]
    self.rag = RagIndex(documents)
    self.rag.get_rag_indexing(use_llm)
    return self.rag.query(rag_query, top_k, similarity)
  def generate_references(self, nodes: List) -> str:
    return self.rag.generate_references(nodes)