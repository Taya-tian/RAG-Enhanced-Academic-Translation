from common import *
import pandas as pd
from create_llm_response import create_llm_response

EVALUATION_DIR = Path(__file__).resolve().parent / "20260614 第一组概念翻译质量评价"
BASELINE_FOLDER = EVALUATION_DIR / "baseline"
RAG_FOLDER = EVALUATION_DIR / "rag"

def compose_prompt(rag_file, rag_file_length, baseline_file, baseline_file_length, expert_file) -> str:
    instruction = read_text(EVALUATION_DIR / "instruction.txt")
    prompt = read_text(EVALUATION_DIR / "prompt.txt")
    return instruction + "\n" + prompt.format(rag_file=rag_file, rag_file_length=rag_file_length, baseline_file=baseline_file, baseline_file_length=baseline_file_length, expert_file=expert_file)

def read_inventory() -> dict[str, dict[str, list[int, int]]]:  
    inventory = {}
    df = pd.read_csv(EVALUATION_DIR / "Translation Inventory.csv")
    for i, row in df.iterrows():
        id = row.iloc[0]
        cg = row.iloc[1].lower()
        rag = row.iloc[3]
        length = row.iloc[4]
        if id not in inventory:
            l = [0, 0]
            inventory[id] = { cg: l }
            l[0 if rag.lower() == "no" else 1] = length
        else:
            if cg not in inventory[id]:
                l = [0, 0]
                inventory[id][cg] = l
                l[0 if rag.lower() == "no" else 1] = length
            else:
                inventory[id][cg][0 if rag.lower() == "no" else 1] = length
    return inventory

def  main():
    index = 1
    inventory = read_inventory()
    prompt_files = [
        {"file_path": EVALUATION_DIR / "20260603 Translation Quality Evaluation Framework.pdf", "content_type": "application/pdf"},
        {"file_path": EVALUATION_DIR / "5.0 Codebook for Concept Group 1.xlsx", "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
    ]
    expert_file = read_text(EVALUATION_DIR / "expert_translation.txt")
    for run_folder in BASELINE_FOLDER.iterdir():
        for baseline_file_path in run_folder.iterdir():
            rag_file_path = RAG_FOLDER / run_folder.name / baseline_file_path.name
            length_list = inventory[run_folder.stem][baseline_file_path.stem]
            baseline_file_length, rag_file_length = length_list[0], length_list[1]
            rag_file = read_text(rag_file_path)
            baseline_file = read_text(baseline_file_path)
            composed_prompt = compose_prompt(rag_file, rag_file_length, baseline_file, baseline_file_length, expert_file)
            dump_response(composed_prompt, EVALUATION_DIR / f"prompt_{run_folder.name}_{baseline_file_path.name}.txt")
            index += 1

if __name__ == "__main__":
    main()