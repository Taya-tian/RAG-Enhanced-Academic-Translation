from pathlib import Path
from common import DATA_DIR
class PromptGenerator:
  def build_rag_prompt(self, rag_query: str, reference: str) -> str:
    """Build the ChatGPT prompt from retrieved nodes and Chinese text."""
    reference_block = "Reference translations (from glossary):\n"
    reference_block += reference
    return f"""{reference_block}
Chinese text to translate:
---
{rag_query}
---
Using the reference translations above for terminology and style, provide the best English translation of the Chinese text.
"""

  def build_prompt(self, rag_query: str) -> str:
      """Build the ChatGPT prompt from retrieved nodes and Chinese text."""
      return f"""
Chinese text to translate:
---
{rag_query}
---

Using the terminology and style befitting the translation of academic text, provide the best English translation of the Chinese text.
"""
    
  def generate_prompt_without_rag(self, rag_queries: dict[Path, str], get_path= lambda filename:  DATA_DIR / f"{filename}_prompt.txt"):
    self.generate_prompt(rag_queries, self.build_prompt, get_path)

  def generate_prompt_with_rag(self, reference_generator, rag_queries:dict[Path, str], get_path):
    self.generate_prompt(rag_queries, lambda rag_query: self.build_rag_prompt(rag_query, reference_generator(rag_query)), get_path)

  def generate_prompt(self, rag_queries:dict[Path, str], get_prompt, get_output_path):
    for query_path, rag_query in rag_queries.items():
        prompt = get_prompt(rag_query)
        output_path = get_output_path(query_path.stem)
        output_path.write_text(prompt, encoding="utf-8")