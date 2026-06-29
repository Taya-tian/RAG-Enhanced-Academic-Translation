import os
from pathlib import Path
from anthropic import Anthropic
from common import *

def create_llm_response(prompt, prompt_files):

    client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    content = []

    # ❗ Claude does NOT accept raw base64 files like OpenAI/Poe
    # You must preprocess files or skip them here

    for prompt_file in prompt_files:
        file_path = prompt_file["file_path"]
        file_type = prompt_file["content_type"]

        # Example: simple workaround → read as text if possible
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_text = f.read()

            content.append({
                "type": "text",
                "text": f"[File: {Path(file_path).name}]\n{file_text}"
            })

        except Exception:
            content.append({
                "type": "text",
                "text": f"[File skipped: {Path(file_path).name} (binary or unsupported format)]"
            })

    # main prompt
    content.append({
        "type": "text",
        "text": prompt
    })

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        print("✅ Response received:")

        dump_response(
            str(response),
            Path(__file__).resolve().parent / "response.json"
        )

        return response.content[0].text

    except Exception as e:
        print("❌ Error:")
        print(e)