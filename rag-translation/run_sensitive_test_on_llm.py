from httpx import request
import openai
import os
import sys
import json
from datetime import datetime
from common import DATA_DIR


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

def dump_metadata(file, request_params, response, response_path, metadata_path):
    run_record = {
            "source_file": str(file),
            "output_file": str(response_path),
            "request_params": request_params,
            "response_metadata": {
                "response_id": response.id,
                "model": response.model,
                "created_at": response.created_at,
                "status": response.status,
                # Effective/runtime params echoed back by the API (implicit defaults when provided).
                "effective_params": {
                    "temperature": response.temperature,
                    "top_p": response.top_p,
                    "max_output_tokens": response.max_output_tokens,
                    "service_tier": response.service_tier,
                    "truncation": response.truncation,
                    "parallel_tool_calls": response.parallel_tool_calls,
                    "reasoning": response.reasoning.model_dump() if response.reasoning else None,
                    "text": response.text.model_dump() if response.text else None,
                },
                "usage": response.usage.model_dump() if response.usage else None,
            },
        }
    print(f"Writing metadata to {metadata_path}")

    # Write one metadata artifact for the full run.
    with open(metadata_path, "w", encoding="utf-8") as meta_file:
        json.dump(run_record, meta_file, ensure_ascii=False, indent=2)

def dump_response (response, response_path):
    print(f"Writing response to {response_path}")
    with open(response_path, "w", encoding="utf-8") as f:
        f.write(response.output_text)

client = openai.OpenAI(
    api_key=load_poe_api_key(),
    base_url="https://api.poe.com/v1",
)

def perform_llm(prompt_files):
    
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    for prompt_file in prompt_files:
        datatime = datetime.now().strftime("%Y%m%d_%H%M%S")
        RESULTS_DIR = DATA_DIR / f"{prompt_file.stem}_{datatime}"
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(prompt_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Track exactly what we send to the API.
        request_params = {
            "model": "gpt-5.5",
            "input": text,
            # Set explicit knobs if you want deterministic experiments, e.g.:
            # temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic
            # "temperature": 0.2,
            # "max_output_tokens": 2048,
        }
        response = client.responses.create(**request_params)
        response_path = RESULTS_DIR / f"{prompt_file.stem}_response.txt"
        dump_response(response, response_path)

        dump_metadata(prompt_file, request_params, response, response_path, RESULTS_DIR / f"{prompt_file.stem}_metadata.json")

def main():
    perform_llm(list(DATA_DIR.glob("sensitive_test_top_k200similarity*prompt.txt")))

if __name__ == "__main__":
    main()
