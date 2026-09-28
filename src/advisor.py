import json
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TacticalAdvisor:
    def __init__(self, model_name="qwen2.5:7b", endpoint="http://localhost:11434/api/generate"):
        # Default local LLM configuration
        self.model_name = model_name
        self.endpoint = endpoint
        
    def _build_prompt(self, military_state_json, student_input):
        prompt = f"""
أنت مستشار تكتيكي عسكري ذكي وخبير في العقيدة العسكرية.
مهمتك هي مساعدة طالب عسكري في تدريب المحاكاة، وتقييم قراراته بناءً على حالة المعركة الحالية.

حالة المعركة الحالية (مستخرجة من مستندات الاستطلاع):
{military_state_json}

طالب المحاكاة يقول/يأمر:
"{student_input}"

قم بتقييم هذا القرار بناءً على حالة المعركة أعلاه. إذا كان القرار خطيراً أو خاطئاً (مثل التقدم في منطقة عدو أو تجاهل خطوط الزج)، قم بتنبيه الطالب واقترح بديلاً تكتيكياً أفضل. تحدث باللغة العربية العسكرية الاحترافية.
"""
        return prompt

    def evaluate_student_decision(self, state_file_path, student_input):
        # Load the extracted state with robust path resolution
        try:
            path = Path(state_file_path)
            if not path.is_absolute() and not path.exists():
                fallback = PROJECT_ROOT / path
                if fallback.exists():
                    path = fallback
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # If wrapped in sample format
                state = data.get("ground_truth", data)
        except Exception as e:
            return f"Error loading state file: {e}"

        state_json_str = json.dumps(state, ensure_ascii=False, indent=2)
        prompt = self._build_prompt(state_json_str, student_input)
        
        payload = json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(self.endpoint, data=payload, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
        except urllib.error.URLError as e:
            print(f"[Offline Demo Mode] Could not connect to Local LLM at {self.endpoint}")
            # Mocking a response for demonstration purposes if Ollama is not running
            if "المحور الأول" in student_input:
                return "تقييم المستشار: قرار محفوف بالمخاطر. المحور الأول يقع ضمن نطاق الكتيبة المعادية الأولى. يُنصح بطلب دعم مدفعي قبل التقدم أو استخدام المحور الثالث للتطويق."
            else:
                return "تقييم المستشار: قرار سليم تكتيكياً. يمكنك المضي قدماً في التنفيذ."


if __name__ == "__main__":
    advisor = TacticalAdvisor()
    print("=========================================")
    print("Military Simulation - Tactical Advisor")
    print("=========================================")
    
    sample_state_file = "augmented_data/sample_0.json"
    student_command = "أمرت السرية الأولى بالتقدم السريع عبر المحور الأول للاشتباك المباشر."
    print(f"\n[الطالب]: {student_command}")
    print("\n[جاري تحليل الحالة التكتيكية...]")
    feedback = advisor.evaluate_student_decision(sample_state_file, student_command)
    print(f"\n[المستشار العسكري]:\n{feedback}")
