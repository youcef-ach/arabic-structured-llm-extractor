import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extractor import LocalLLMExtractor
from src.advisor import TacticalAdvisor
from scripts.visualize import visualize_tactical_state


def run_demo():
    print("=" * 65)
    print(" STRUCTURED ARABIC INFORMATION EXTRACTION - PUBLIC DEMO")
    print("=" * 65)

    extractor = LocalLLMExtractor(model_name="qwen2.5:7b")
    advisor = TacticalAdvisor(model_name="qwen2.5:7b")

    # -----------------------------------------------------------------
    # 1. Load Synthetic Demonstration Input (Cartesian Scene Coordinates)
    # -----------------------------------------------------------------
    sample_file = PROJECT_ROOT / "augmented_data" / "sample_0.json"
    if sample_file.exists():
        with open(sample_file, "r", encoding="utf-8") as f:
            sample = json.load(f)
            text_to_extract = sample["text"]
            demo_state = sample["ground_truth"]
    else:
        text_to_extract = (
            "تتمركز الكتيبة الصديقة الأولى في موقع المشهد ذي الإحداثيات الديكارتية (25.0 , 75.0). "
            "وتتكون من عدة سرايا، منها سرية الاستطلاع المتواجدة عند نقطة المشهد (30.0 , 80.0). "
            "تقوم سرية الاستطلاع بـ استطلاع المنطقة المحددة."
        )
        demo_state = None

    print("\n[Input Text (Synthetic Scenario)]:")
    print(f"  \"{text_to_extract}\"")

    # -----------------------------------------------------------------
    # 2. Local LLM Extraction (Live Mode vs Offline Demo Mode)
    # -----------------------------------------------------------------
    print("\n[Task 1: Structured Extraction via Local LLM]")
    if extractor.is_available():
        print("  [Mode: Live LLM Extraction]")
        print("  Pipeline: Arabic text -> Ollama/Qwen 2.5 7B -> JSON parsing -> Draft-07 validation")
        print("  Sending extraction prompt to local Ollama daemon...")
        current_state = extractor.extract(text_to_extract)
        if current_state:
            print("  Extraction succeeded and passed Draft-07 schema validation.")
        else:
            print("  Extraction rejected by schema validator or model returned malformed output.")
    else:
        print("  [Mode: Offline Demonstration]")
        print(f"  Local LLM endpoint unreachable at {extractor.endpoint}.")
        print("  Live mode execution:")
        print("    Arabic text -> local Ollama/Qwen inference -> JSON parsing -> Draft-07 validation.")
        print("  In offline demo mode, synthetic demonstration state is loaded directly to showcase")
        print("  downstream 2D scene visualization and tactical advisor evaluation.")
        print("  Note: The offline demonstration state is NOT an LLM extraction result.")
        current_state = demo_state

    # -----------------------------------------------------------------
    # 3. 2D Scene Visualization (Synthetic Cartesian Grid)
    # -----------------------------------------------------------------
    print("\n[Task 2: 2D Scene Visualization (Cartesian Grid)]")
    if current_state:
        state_file = PROJECT_ROOT / "pipeline_state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(current_state, f, ensure_ascii=False, indent=2)
        try:
            visualize_tactical_state(str(state_file))
            print("  2D scene visualization generated successfully.")
        except Exception as e:
            print(f"  Visualization notice: {e}")

    # -----------------------------------------------------------------
    # 4. Domain Advisory Evaluation
    # -----------------------------------------------------------------
    print("\n[Task 3: Decision Advisory Evaluation]")
    test_command = "أمرت السرية الأولى بالتقدم السريع عبر المحور الأول للاشتباك المباشر."
    print(f"  [Student Action]: \"{test_command}\"")
    feedback = advisor.evaluate_student_decision(str(sample_file), test_command)
    print(f"  [Advisor Output]:\n  {feedback.strip()}")

    print("\n" + "=" * 65)
    print(" DEMO PIPELINE COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    run_demo()
