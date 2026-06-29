from pathlib import Path
from typing import List
from common import DATA_DIR
TEXT1_PATH = DATA_DIR / "text1.txt"
def read_chinese_from_txt(path: Path) -> str:
    """Read Chinese text from a .txt file (UTF-8)."""
    return path.read_text(encoding="utf-8").strip()
def validate_query_paths(args: list[str]) -> List[Path]:
    """Parse source file args and resolve them to paths under DATA_DIR."""
    # Source files: from command line, or default to text1.txt
    if args:
        source_names = [a.strip() for a in args if a.strip()]
    else:
        source_names = [TEXT1_PATH.name]

    if not source_names:
        raise ValueError("No source files given.")

    source_paths: List[Path] = []
    for name in source_names:
        p = Path(name)
        if not p.exists() and not p.is_absolute():
            p = DATA_DIR / p.name
        source_paths.append(p)
    return source_paths

def get_rag_query(query_paths: list[str]) -> dict[Path, str]:
    try:
        valid_query_paths = validate_query_paths(query_paths)
    except ValueError as exc:
        raise SystemExit(f"{exc} Usage: python knowledge_base.py [file1.txt file2.txt ...]") from exc

    rag_queries = {}
    for query_path in valid_query_paths:
        if not query_path.exists():
            print(f"Skip (not found): {query_path}")
            continue
        rag_query = read_chinese_from_txt(query_path)
        if not rag_query:
            print(f"Skip (empty): {query_path}")
            continue
        rag_queries[query_path] = rag_query
    return rag_queries