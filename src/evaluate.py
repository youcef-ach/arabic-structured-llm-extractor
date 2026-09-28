import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.extractor import LocalLLMExtractor
except ImportError:
    try:
        from extractor import LocalLLMExtractor
    except ImportError:
        LocalLLMExtractor = None

DEFAULT_DATASET_PATH = PROJECT_ROOT / "augmented_data" / "dataset.json"


def evaluate(dataset_path=None):
    path = Path(dataset_path) if dataset_path else DEFAULT_DATASET_PATH
    if not path.is_absolute() and not path.exists():
        fallback = PROJECT_ROOT / path
        if fallback.exists():
            path = fallback
            
    print(f"Loading dataset from {path}...")
    if not path.exists():
        print(f"Dataset not found at {path}. Please run scripts/augment_data.py first.")
        return None
        
    with open(path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    print(f"Loaded {len(dataset)} synthetic scenario samples for evaluation.")
    
    extractor = LocalLLMExtractor() if LocalLLMExtractor else None
    
    if extractor and not extractor.is_available():
        print(f"\n[Offline Demo Notice] Local LLM endpoint unreachable at {extractor.endpoint}.")
        print("Live model evaluation requires a running Ollama daemon. Skipping extraction loop.")
        print("\n" + "=" * 50)
        print("Evaluation Summary (Top-level Entity Name Exact Match)")
        print("=" * 50)
        print(f"Total scenario samples : {len(dataset)}")
        print(f"Successfully evaluated : 0")
        print(f"Skipped (LLM offline)  : {len(dataset)}")
        print("Note: Offline runs do not produce synthetic accuracy scores.")
        print("=" * 50)
        return {
            "total": len(dataset),
            "evaluated": 0,
            "matched": 0,
            "skipped": len(dataset)
        }
    
    matched = 0
    evaluated = 0
    skipped = 0
    total = len(dataset)
    
    for i, sample in enumerate(dataset):
        print(f"\n--- Evaluating Sample {i+1}/{total} ---")
        text = sample["text"]
        ground_truth = sample["ground_truth"]
        
        extracted = None
        if extractor:
            extracted = extractor.extract(text)
            
        if extracted is None:
            print("Status: SKIPPED (Local LLM unavailable at endpoint)")
            skipped += 1
            continue
            
        evaluated += 1
        # Limited check criterion: top-level entity name exact-match
        try:
            gt_forces = ground_truth.get("forces", [])
            ex_forces = extracted.get("forces", [])
            
            if (len(gt_forces) == len(ex_forces) and 
                    len(gt_forces) > 0 and 
                    gt_forces[0].get("name") == ex_forces[0].get("name")):
                print("Status: MATCH (Top-level force name matches)")
                matched += 1
            else:
                print("Status: MISMATCH")
                print(f"  Expected: {gt_forces[0].get('name') if gt_forces else 'None'}")
                print(f"  Extracted: {ex_forces[0].get('name') if ex_forces else 'None'}")
        except Exception as e:
            print(f"Status: ERROR (Failed structure comparison: {e})")
            
    print("\n" + "=" * 50)
    print("Evaluation Summary (Top-level Entity Name Exact Match)")
    print("=" * 50)
    print(f"Total scenario samples : {total}")
    print(f"Successfully evaluated : {evaluated}")
    print(f"Skipped (LLM offline)  : {skipped}")
    if evaluated > 0:
        rate = (matched / evaluated) * 100
        print(f"Top-level name match   : {matched}/{evaluated} ({rate:.1f}%)")
    else:
        print("Live model was unavailable during execution.")
        print("Note: Offline runs do not produce synthetic accuracy scores.")
    print("=" * 50)
    
    return {
        "total": total,
        "evaluated": evaluated,
        "matched": matched,
        "skipped": skipped
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    evaluate(target)
