from llama_index.core.schema import Document
from common import DATA_DIR
import pandas as pd

CN_EN_PATH = DATA_DIR / "cn-en.xlsx"
EN_CN_PATH = DATA_DIR / "en-cn.xlsx"
# --- Paths (Excel columns 6 & 7 = 0-based indices 5 & 6) ---
def load_rag_indexing_documents(lang = None) -> list[Document]:
    """Load cn-en.xlsx and en-cn.xlsx; columns 6 & 7 are source/target. Return LlamaIndex Documents."""
    documents: list[Document] = []

    print(f"Loading RAG indexing documents (lang={'both' if lang is None else ('Chinese' if lang == 'cn' else 'English')})")
    config = { CN_EN_PATH: {"COL_SOURCE": 5, "COL_TARGET": 6}, EN_CN_PATH: {"COL_SOURCE": 6, "COL_TARGET": 5} }

    for path in [CN_EN_PATH, EN_CN_PATH]:
        if path.exists():
            df_cn_en = pd.read_excel(path, header=None, engine="openpyxl")
            for i, row in df_cn_en.iterrows():
                cn = _cell_str(row, config[path]["COL_SOURCE"])
                en = _cell_str(row, config[path]["COL_TARGET"])
                if cn or en:
                    format = None if lang == None else (f"Chinese: {cn}\n" + "English: {other}" if lang == 'en' else "Chinese: {other}\n" + f"English: {en}")
                    text = f"Chinese: {cn}\nEnglish: {en}" if lang is None else (cn if lang == 'cn' else en)
                    documents.append(Document(text=text, metadata={"format": format, "source": "cn-en", "row": str(i)}, excluded_embed_metadata_keys=["format"]))

    print(f"Loaded {len(documents)} RAG indexing documents.")
    return documents


def _cell_str(row: pd.Series, col: int) -> str:
    if col >= len(row):
        return ""
    v = row.iloc[col]
    if pd.isna(v):
        return ""
    return str(v).strip()