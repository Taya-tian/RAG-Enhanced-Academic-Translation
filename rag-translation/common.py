from pathlib import Path
import os

DATA_DIR = Path(__file__).resolve().parent / "data"
RESULT_DIR = Path(__file__).resolve().parent / "result"
POE_API_BASE = "https://api.poe.com/v1"
GPT_MODEL = "gpt-5.5"
def load_poe_api_key() -> str:
    """Load and validate POE_API_KEY for HTTP header safety (ASCII only)."""
    api_key = os.getenv("POE_API_KEY")
    if not api_key:
        raise SystemExit("Missing POE_API_KEY environment variable.")

    api_key = api_key.strip()
    try:
        api_key.encode("ascii")
    except UnicodeEncodeError as exc:
        raise SystemExit(
            "POE_API_KEY contains non-ASCII characters. Re-copy your key from Poe and "
            "set it again without extra characters/spaces/newlines."
        ) from exc
    return api_key

def read_text(file_path: Path) -> str:
    """Read text content from a file, ensuring UTF-8 encoding."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        raise SystemExit(f"Error reading file {file_path}: {exc}") from exc

def dump_response (response, response_path):
    print(f"Writing response to {response_path}")
    with open(response_path, "w", encoding="utf-8") as f:
        f.write(response if isinstance(response, str) else response.output_text)