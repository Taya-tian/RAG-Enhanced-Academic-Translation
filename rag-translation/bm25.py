import jieba
import re
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List

class BM25:
  @staticmethod
  def mixed_tokenizer(text):
    # Use jieba.cut to segment Chinese; it preserves English words as-is
    tokens = list(jieba.cut(text))
    # Standardize: lowercase English and filter out single punctuation marks
    return [t.lower() for t in tokens if re.match(r'\w+', t)]
  def __init__(self, documents) -> None:
    self.documents = documents
    tokenized_corpus = [self.mixed_tokenizer(doc.text) for doc in documents]
    self.query_engine = BM25Okapi(tokenized_corpus)

  def query(self, rag_query, top_k):
    tokenized_query = self.mixed_tokenizer(rag_query)
    scores = self.query_engine.get_scores(tokenized_query)
    top_n = np.argsort(scores)[::-1][:top_k]
    return [{"text": self.documents[i].text, "score": scores[i]} for i in top_n]
  def generate_references(self, nodes: List) -> str:
    reference_block = ""
    for i, node in enumerate(nodes, 1):
        score = node["score"]
        score_str = f" [similarity: {float(score):.3f}]" if score is not None else ""
        reference_block += f"{i}.{score_str} {node["text"]}\n"
    return reference_block