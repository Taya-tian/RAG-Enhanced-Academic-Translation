import openai
from common import *
import sys
from pathlib import Path
import base64
from openai import APIError, BadRequestError, AuthenticationError, RateLimitError

def create_file_data(file_path: Path, file_type: str) -> str:
    with open(file_path, "rb") as f:
        encoded_content = base64.b64encode(f.read()).decode("utf-8")
    return {"type": "file", 
    "file": {"filename": file_path.name, "file_data": f"data:{file_type};base64,{encoded_content}"}}
def create_llm_response(prompt, prompt_files):

    content = []
    client = openai.OpenAI(
        api_key=load_poe_api_key(),
        base_url=POE_API_BASE,
    )

    for prompt_file in prompt_files:
            content.append(create_file_data(prompt_file["file_path"], prompt_file["content_type"]))

    content.append({
        "type": "input_text",
        "text": prompt
    })
    dump_response(str(content), Path(__file__).resolve().parent / "debug_content.json")
    try:
        response = client.chat.completions.create(
            model="Claude-Sonnet-4.6",
            messages=[{
                "role": "user",
                "content": content
            }],
        )
        print("✅ Response received:")
        dump_response(str(response), Path(__file__).resolve().parent / "response.json")

        return response

    except BadRequestError as e:
        print("❌ Bad request (your payload is invalid):")
        print(e)

    except AuthenticationError as e:
        print("❌ Auth failed (API key issue):")
        print(e)

    except RateLimitError as e:
        print("❌ Rate limited:")
        print(e)

    except APIError as e:
        print("❌ General API error:")
        print(e)

    except Exception as e:
        print("❌ Unknown error:")
        print(e)