import json
import random
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Abstract Arabic domain vocabulary for synthetic scenario generation
BATTALION_NAMES = ["الكتيبة الصديقة الأولى", "الكتيبة المعادية الثانية", "كتيبة المشاة الثالثة", "كتيبة المدرعات الرابعة"]
COMPANY_NAMES = ["السرية الصديقة الأولى", "السرية المعادية الأولى", "سرية الاستطلاع", "سرية المشاة الميكانيكية"]
TASKS = ["الهجوم على", "الدفاع عن", "تأمين", "استطلاع"]

def generate_random_scene_coordinate():
    """Generates synthetic 2D Cartesian scene coordinates (X, Y) within a [10.0, 90.0] grid."""
    return round(random.uniform(10.0, 90.0), 1), round(random.uniform(10.0, 90.0), 1)

def generate_synthetic_scenario(index):
    """Generates a synthetic Arabic scenario text paired with ground-truth JSON in synthetic Cartesian coordinates."""
    battalion = random.choice(BATTALION_NAMES)
    company = random.choice(COMPANY_NAMES)
    task = random.choice(TASKS)
    
    b_x, b_y = generate_random_scene_coordinate()
    c_x, c_y = generate_random_scene_coordinate()
    
    affiliation = "friendly" if "الصديقة" in battalion else "enemy"
    
    text = f"تتمركز {battalion} في موقع المشهد ذي الإحداثيات الديكارتية ({b_x} , {b_y}). "
    text += f"وتتكون من عدة سرايا، منها {company} المتواجدة عند نقطة المشهد ({c_x} , {c_y}). "
    text += f"تقوم {company} بـ {task} المنطقة المحددة."
    
    json_ground_truth = {
        "forces": [
            {
                "name": battalion,
                "level": "battalion",
                "affiliation": affiliation,
                "location": {
                    "description": "موقع المشهد",
                    "coordinate": [b_x, b_y]
                },
                "sub_units": [
                    {
                        "name": company,
                        "level": "company",
                        "affiliation": affiliation,
                        "task": f"{task} المنطقة المحددة",
                        "location": {
                            "description": "نقطة المشهد",
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
    print(f"Generating {num_samples} synthetic Cartesian scene scenario samples...")
    
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
        
    print(f"Successfully generated {num_samples} synthetic samples in '{output_dir}/'")

if __name__ == "__main__":
    main()
