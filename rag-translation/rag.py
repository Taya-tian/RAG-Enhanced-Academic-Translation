from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage
from llama_index.core.llms import MockLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import hashlib
import shutil
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from typing import List
from pathlib import Path
from common import load_poe_api_key, POE_API_BASE, GPT_MODEL

try:
    from llama_index.core.postprocessor import LLMRerank
except ImportError:
    LLMRerank = None  # type: ignore[misc, assignment]

try:
    from llama_index.llms.openai_like import OpenAILike
except ImportError:
    OpenAILike = None  # type: ignore[misc, assignment]

INDEX_STORAGE_DIR = Path(__file__).resolve().parent / "rag_index_storage"
INDEX_FINGERPRINT_PATH = INDEX_STORAGE_DIR / ".glossary_fingerprint"

class RagIndex:
  def __init__(self, documents) -> None:
    self.documents = documents
  def __configure(self) -> None:
    """Configure global LlamaIndex settings used by the query engine."""
    # Embedding model: BGE-M3 is multilingual (100+ languages), strong on Chinese + English
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
    if self.use_llm_rerank and OpenAILike is not None:
        poe_key = load_poe_api_key()
        if poe_key:
            Settings.llm = OpenAILike(
                model=GPT_MODEL,
                api_base=POE_API_BASE,
                api_key=poe_key,
                context_window=8192,
                is_chat_model=True,
                is_function_calling_model=False,
            )
            print(f"LLM rerank enabled (Poe API, model={GPT_MODEL}).")
        else:
            print("POE_API_KEY not set; disabling LLM rerank. Set POE_API_KEY to use Poe for reranking.")
            Settings.llm = None
    else:
        Settings.llm = None
    Settings.chunk_size = 512
    Settings.chunk_overlap = 50
    # Avoid "available context size not non-negative" when query text is long (PromptHelper default is 3900)
    Settings.context_window = 108192
    Settings.num_output = 256

  def __glossary_source_fingerprint(self) -> str:
      """Hash of glossary file paths, mtimes, and sizes so we reload the index when Excel changes."""
      if self.documents == None:
        return None
      parts: list[str] = []
      for document in self.documents:
          parts.append(document.text)
      hashCode = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
      print(f"Glossary fingerprint: {hashCode} (based on {len(self.documents)} documents)")
      return hashCode

  def __persisted_index_ready(self, folder) -> bool:
    if folder is None or not folder.exists() or not (folder / "docstore.json").exists():
        return False
    return True

  def get_rag_indexing(self, use_llm_rerank = False) -> VectorStoreIndex:
    """
    Load VectorStoreIndex from disk when storage exists and matches current Excel files;
    otherwise embed documents, persist under INDEX_STORAGE_DIR, and save a fingerprint.
    """
    self.use_llm_rerank = use_llm_rerank
    self.__configure()
    if not self.documents:
        raise ValueError("rag_documents must not be empty.")

    fp = self.__glossary_source_fingerprint()
    folder = INDEX_STORAGE_DIR / fp if fp else None
    if (
        fp != None
        and self.__persisted_index_ready(folder)
    ):
        print(f"Loaded vector index from {folder} (glossary unchanged).")
        storage_context = StorageContext.from_defaults(persist_dir=str(folder))
        self.index = load_index_from_storage(storage_context)
        if not isinstance(self.index, VectorStoreIndex):
            raise TypeError(f"Expected VectorStoreIndex, got {type(self.index).__name__}")
        return

    print(f"Built and saved vector index ({len(self.documents)} docs) to {folder}.")
    if fp != None:
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)

    storage_context = StorageContext.from_defaults()
    self.index = VectorStoreIndex.from_documents(self.documents, storage_context=storage_context)
    if fp != None:
        storage_context.persist(persist_dir=str(folder))

  def create_query_engine(self, top_k, similarity_cutoff) -> RetrieverQueryEngine:
    """Build a retriever query engine from RAG documents."""
    # Retrieve more candidates if using reranker, then cut down
    USE_LLM_RERANK = self.use_llm_rerank and LLMRerank is not None and not isinstance(Settings.llm, MockLLM)
    retriever_top_k = top_k * 3 if USE_LLM_RERANK else top_k
    retriever = VectorIndexRetriever(index=self.index, similarity_top_k=retriever_top_k)

    node_postprocessors: List[BaseNodePostprocessor] = [
        SimilarityPostprocessor(similarity_cutoff=similarity_cutoff),
    ]
    if USE_LLM_RERANK:
        node_postprocessors.append(LLMRerank(llm=Settings.llm, top_n=top_k))  # type: ignore[arg-type]

    return RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=node_postprocessors,
    )
  def query(self, rag_query, top_k, similarity_cutoff):
    query_engine = self.create_query_engine(top_k, similarity_cutoff)
    return query_engine.query(rag_query).source_nodes
  def generate_references(self, nodes: List) -> str:
    reference_block = ""
    for i, node in enumerate(nodes, 1):
        score = getattr(node, "score", None)
        score_str = f" [similarity: {float(score):.3f}]" if score is not None else ""
        text = node.metadata.get("format").format(other=node.text) if node.metadata.get("format") is not None else node.text
        reference_block += f"{i}.{score_str} {text}\n"
    return reference_block