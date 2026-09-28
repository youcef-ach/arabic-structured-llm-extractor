import json
import pytest
import jsonschema
from pathlib import Path
import sys

# Ensure repository root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extractor import LocalLLMExtractor, DEFAULT_SCHEMA_PATH


def test_schema_loads_and_is_valid_draft7():
    """Verify that the repository JSON Schema exists and conforms to Draft-07."""
    assert DEFAULT_SCHEMA_PATH.exists()
    with open(DEFAULT_SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    # Draft7Validator.check_schema raises SchemaError if invalid
    jsonschema.Draft7Validator.check_schema(schema)
    assert schema.get("title") in ["Tactical State", "Military State"]


def test_synthetic_sample_conforms_to_schema():
    """Verify that the repository's synthetic training samples conform to the schema."""
    sample_path = PROJECT_ROOT / "augmented_data" / "sample_0.json"
    assert sample_path.exists()
    
    with open(sample_path, "r", encoding="utf-8") as f:
        sample = json.load(f)
        
    with open(DEFAULT_SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    # Must pass without raising jsonschema.ValidationError
    jsonschema.validate(instance=sample["ground_truth"], schema=schema)


def test_invalid_object_fails_schema_validation():
    """Verify that structurally deficient objects fail schema validation."""
    with open(DEFAULT_SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # 1. Missing required field 'affiliation'
    invalid_force = {
        "forces": [
            {
                "name": "الكتيبة الأولى",
                "level": "battalion"
                # Missing required 'affiliation'
            }
        ]
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_force, schema=schema)

    # 2. Invalid enum value for level
    invalid_level = {
        "forces": [
            {
                "name": "الكتيبة الأولى",
                "level": "non_existent_unit_level",
                "affiliation": "friendly"
            }
        ]
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_level, schema=schema)


def test_extractor_parse_and_validate_valid_mock():
    """Verify extractor successfully parses and validates compliant JSON without Ollama."""
    extractor = LocalLLMExtractor()
    valid_payload = json.dumps({
        "forces": [
            {
                "name": "السرية الصديقة الأولى",
                "level": "company",
                "affiliation": "friendly",
                "sub_units": []
            }
        ],
        "tactical_lines": [],
        "areas_of_operation": []
    })
    data = extractor.parse_and_validate(valid_payload)
    assert isinstance(data, dict)
    assert len(data["forces"]) == 1
    assert data["forces"][0]["affiliation"] == "friendly"


def test_extractor_rejects_malformed_json_syntax():
    """Verify extractor detects and rejects syntactically broken JSON strings."""
    extractor = LocalLLMExtractor()
    broken_json = "{ forces: [ 'unquoted_key': invalid ] "
    with pytest.raises(json.JSONDecodeError):
        extractor.parse_and_validate(broken_json)


def test_extractor_rejects_schema_invalid_json():
    """Verify extractor accepts valid JSON syntax but rejects schema non-compliance."""
    extractor = LocalLLMExtractor()
    # Syntactically valid JSON, but missing required 'name' and 'level'
    schema_invalid_json = json.dumps({
        "forces": [
            {
                "affiliation": "enemy"
            }
        ]
    })
    with pytest.raises(jsonschema.ValidationError):
        extractor.parse_and_validate(schema_invalid_json)


def test_prompt_construction_contains_schema_and_text():
    """Verify system prompt injects the schema and target text without live inference."""
    extractor = LocalLLMExtractor()
    sample_text = "تتمركز الكتيبة الأولى في النقطة أ"
    prompt = extractor._build_prompt(sample_text)
    
    assert "SCHEMA:" in prompt
    assert "ARABIC TEXT TO EXTRACT:" in prompt
    assert sample_text in prompt
    assert "military_unit" in prompt


def test_path_resolution_independent_of_cwd():
    """Verify that LocalLLMExtractor resolves its schema path regardless of working directory."""
    extractor = LocalLLMExtractor()
    assert extractor.schema_path.is_absolute()
    assert extractor.schema_path.exists()
    assert extractor.validator is not None
