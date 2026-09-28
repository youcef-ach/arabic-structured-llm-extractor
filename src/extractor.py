import json
import urllib.request
import urllib.error
from pathlib import Path
import jsonschema

# Path resolution relative to repository root
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "tactical_state.json"


class LocalLLMExtractor:
    def __init__(self, model_name="qwen2.5:7b", endpoint="http://localhost:11434/api/generate", schema_path=None):
        self.model_name = model_name
        self.endpoint = endpoint
        self.schema_path = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
        
        # Load and validate schema against Draft-07
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema_dict = json.load(f)
        
        self.schema = json.dumps(self.schema_dict, ensure_ascii=False, indent=2)
        self.validator = jsonschema.Draft7Validator(self.schema_dict)

    def is_available(self, timeout=1.0):
        """Quickly probes if the local LLM endpoint is reachable."""
        try:
            req = urllib.request.Request(self.endpoint, data=b"{}", headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=timeout):
                return True
        except urllib.error.HTTPError:
            # Endpoint responded (e.g. 400 Bad Request to empty payload), so daemon is online
            return True
        except Exception:
            return False
            
    def _build_prompt(self, arabic_text):
        prompt = f"""
You are a highly capable Military Intelligence AI. Your task is to extract military entities, their hierarchies, coordinates, and tactical lines from the following Arabic text.

Return ONLY a valid JSON object that strictly adheres to the following JSON schema. Do not include any markdown formatting, explanations, or backticks.

SCHEMA:
{self.schema}

ARABIC TEXT TO EXTRACT:
{arabic_text}

JSON OUTPUT:
"""
        return prompt

    def parse_and_validate(self, raw_json_str):
        """Parses a raw JSON string and deterministically validates it against the Draft-07 schema.
        
        Raises json.JSONDecodeError if JSON syntax is malformed.
        Raises jsonschema.ValidationError if data violates schema rules.
        Returns the validated dictionary on success.
        """
        data = json.loads(raw_json_str)
        self.validator.validate(data)
        return data

    def extract(self, arabic_text, timeout=10.0):
        """Extracts structured entities from Arabic text using local LLM inference.
        
        Flow: LLM response -> JSON parsing -> JSON Schema validation -> return validated dict.
        Returns None on connection error, syntax error, or schema violation.
        """
        prompt = self._build_prompt(arabic_text)
        
        payload = json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"  # Requests JSON syntax from Ollama
        }).encode('utf-8')
        
        req = urllib.request.Request(self.endpoint, data=payload, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                extracted_json_str = result.get('response', '{}')
                
                # 1. Lexical JSON parsing
                try:
                    data = json.loads(extracted_json_str)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON syntax from LLM: {e}")
                    return None

                # 2. Deterministic JSON Schema validation
                try:
                    self.validator.validate(data)
                    return data
                except jsonschema.ValidationError as e:
                    print(f"Schema validation failed for LLM output: {e.message}")
                    return None

        except urllib.error.URLError as e:
            print(f"Error connecting to local LLM: {e}")
            print("Please ensure Ollama or your local inference engine is running at", self.endpoint)
            return None


if __name__ == "__main__":
    extractor = LocalLLMExtractor()
    sample_text = "تتمركز الكتيبة الصديقة الأولى في إحداثيات المشهد الديكارتية (25.0 , 75.0)."
    print("Testing extraction prompt on text:", sample_text)
    result = extractor.extract(sample_text)
    if result:
        print("Extraction successful and validated against schema!")
        print(json.dumps(result, ensure_ascii=False, indent=2))
