import json
import random
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Abstract Arabic domain vocabulary for synthetic augmentation
BATTALION_NAMES = ["الكتيبة الصديقة الأولى", "الكتيبة المعادية الثانية", "كتيبة المشاة الثالثة", "كتيبة الدروع الرابعة"]
COMPANY_NAMES = ["السرية الصديقة الأولى", "السرية المعادية الأولى", "سرية الاستطلاع", "سرية المشاة الميكانيكية"]
PLATOON_NAMES = ["الفصيلة الأولى", "الفصيلة الثانية", "الفصيلة الثالثة"]
TASKS = ["الهجوم على", "الدفاع عن", "تأمين", "استطلاع"]

def generate_random_coordinate():
    """Generates arbitrary normalized coordinates on an abstract synthetic grid [10.0, 50.0]."""
    return round(random.uniform(10.0, 50.0), 3), round(random.uniform(10.0, 50.0), 3)

def generate_synthetic_scenario(index):
    """Generates a synthetic Arabic domain scenario text and its paired ground-truth JSON."""
    battalion = random.choice(BATTALION_NAMES)
    company = random.choice(COMPANY_NAMES)
    platoon = random.choice(PLATOON_NAMES)
    task = random.choice(TASKS)
    
    b_x, b_y = generate_random_coordinate()
    c_x, c_y = generate_random_coordinate()
    
    affiliation = "friendly" if "صديقة" in battalion else "enemy"
    
    text = f"تتمركز {battalion} في مقر القيادة علامة ({b_x} , {b_y}). "
    text += f"وتتكون من عدة سرايا، منها {company} التي تتواجد في العلامة ({c_x} , {c_y}). "
    text += f"تقوم {company} بـ {task} المنطقة المحددة."
    
    json_ground_truth = {
        "forces": [
            {
                "name": battalion,
                "level": "battalion",
                "affiliation": affiliation,
                "location": {
                    "description": "مقر القيادة",
                    "coordinate": [b_x, b_y]
                },
                "sub_units": [
                    {
                        "name": company,
                        "level": "company",
                        "affiliation": affiliation,
                        "task": f"{task} المنطقة المحددة",
                        "location": {
                            "description": "تتواجد في",
                            "coordinate": [c_x, c_y]
                        },
                        "sub_units": []
                    }
                ]
            }
        ],
        "tactical_lines": [],
        "areas_of_operation": []
    }
    
    return text, json_ground_truth

def main():
    random.seed(42)  # Deterministic reproducibility
    output_dir = PROJECT_ROOT / "augmented_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    num_samples = 10
    print(f"Generating {num_samples} neutral synthetic scenario samples...")
    
    dataset = []
    for i in range(num_samples):
        text, truth = generate_synthetic_scenario(i)
        dataset.append({
            "id": i,
            "text": text,
            "ground_truth": truth
        })
        
        # Save individually
        with open(output_dir / f"sample_{i}.json", "w", encoding="utf-8") as f:
            json.dump({"text": text, "ground_truth": truth}, f, ensure_ascii=False, indent=2)
            
    # Save combined dataset
    with open(output_dir / "dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated {num_samples} samples in '{output_dir}/'")

if __name__ == "__main__":
    main()
