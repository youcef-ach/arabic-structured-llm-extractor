# Arabic Structured LLM Extractor (Public Portfolio Edition)

> **Portfolio Edition Notice**: This repository isolates the structured-information-extraction and local-LLM reasoning component authored by the candidate. It is a standalone, public-safe extraction from an earlier academic team project (`text-to-scene`). All proprietary domain documents, real-world operational coordinates, teammate-authored modules, and historical git ancestry have been intentionally excluded. All included scenarios and coordinates are purely synthetic.

---

## 1. Overview & Problem Context

In tactical decision-support and command-and-control (C2) simulation environments, field reports, commander directives, and operational updates arrive as unstructured, free-form Arabic military prose. Human operators traditionally translate these text dispatches into formal spatial objects, units, and hierarchical combat states on digital maps—a manual process vulnerable to cognitive overload, latency, and transcription errors.

This project implements an end-to-end local structured information extraction pipeline:
1. Ingests raw Arabic tactical narrative.
2. Queries a locally hosted large language model (**Qwen 2.5 7B** via **Ollama**) guided by an explicit JSON schema.
3. Parses, extracts, and strictly validates the output against a deterministic **JSON Schema (Draft-07)** specification using `jsonschema`.
4. Renders a 2D spatial plot of friendly and hostile units, boundaries, and objectives.
5. Evaluates commander actions via an interactive tactical advisor module.

```
┌─────────────────────────────────┐
│   Raw Arabic Tactical Text      │
│  (Unstructured narrative/order) │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│     Local LLM Inference         │
│   (Ollama / Qwen 2.5 7B)        │
│   Prompt-injected JSON Schema   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   Markdown Fence Stripping &    │
│       JSON Syntax Parsing       │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   Deterministic Schema Guard    │
│  (Draft-07 Validation via       │
│   `jsonschema` Validator)       │
└───────┬─────────────────┬───────┘
        │ Valid           │ Invalid
        ▼                 ▼
┌──────────────────┐ ┌──────────────────┐
│  State Schema    │ │  Rejection /     │
│  - Friendly/Host │ │  ValidationError │
│  - Coordinates   │ └──────────────────┘
│  - Unit Hierarchy│
└───────┬──────────┘
        │
        ├─────────────────────────────┐
        ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│  2D Spatial Visualization │ │  Tactical Decision        │
│  (Matplotlib map layout)  │ │  Advisory Module          │
└───────────────────────────┘ └───────────────────────────┘
```

---

## 2. Personal Authorship & Project Boundaries

To maintain strict academic integrity and engineering transparency, the exact authorship boundaries are documented below:

| Component / Responsibility | Candidate Authorship Status | In Public Edition? | Description / Notes |
| :--- | :--- | :--- | :--- |
| **Structured LLM Extractor (`src/extractor.py`)** | **Sole Author** | **Yes** | Prompt engineering, schema injection, JSON parsing, Draft-07 runtime validation. |
| **Domain State Schema (`schema/military_state.json`)** | **Sole Author** | **Yes** | Draft-07 formal specification defining unit types, coordinates, combat states, and missions. |
| **Tactical Advisor (`src/advisor.py`)** | **Sole Author** | **Yes** | Rule-assisted and local LLM-driven tactical advice generator for student/commander actions. |
| **Synthetic Scenario Generator (`scripts/augment_data.py`)** | **Sole Author** | **Yes** | Generates paired Arabic text scenarios and ground-truth JSON states in neutral coordinate space. |
| **2D Spatial Plotter (`scripts/visualize.py`)** | **Sole Author** | **Yes** | Matplotlib-based 2D spatial layout mapping friendly, hostile, and coordinate markers. |
| **Deterministic Unit Tests (`tests/test_extraction.py`)** | **Sole Author** | **Yes** | Automated test suite validating schema conformance, malformed JSON handling, and path independence. |
| **Voice-to-Text / Whisper LoRA** | **Teammate Work** (`iAhmeed`) | **Excluded** | Audio transcription fine-tuning; intentionally decoupled and excluded. |
| **Backend & 3D Simulation Frontend** | **Team-Authored** | **Excluded** | Full-stack server and 3D visualization layers from the broader academic project. |
| **Original Operational Source Data** | **Proprietary / Sensitive** | **Excluded** | Original military doctrine documents and operational coordinate dumps are strictly excluded. |

---

## 3. Data Sanitization & Public Demo Safety

The original academic project was evaluated on military domain material. To ensure total confidentiality and public safety, this portfolio repository has been completely sanitized:

* **Zero Sensitive Documents**: All original proprietary military doctrine documents and raw operational extraction text files are completely omitted.
* **Neutral Synthetic Coordinate Space**: All coordinates across `augmented_data/` and `demo_pipeline.py` have been synthetically generated inside an arbitrary neutral grid space $[10.0, 50.0]$. No coordinates correspond to any real-world operational terrain, borders, or tactical facilities.
* **Fresh Git History**: This repository does not contain or branch from the original academic repository's commit tree. The commit history reflects only the public-edition preparation work.
* **Offline Transparency**: When the local Ollama daemon is offline, scripts explicitly state that the LLM is unreachable and use validated synthetic ground-truth states for downstream visualization rather than fabricating successful inference results.

---

## 4. Repository Structure

```
arabic-structured-llm-extractor/
├── .gitignore                      # Hygiene rules (caches, local plots, temp states)
├── README.md                       # Architecture, authorship boundaries, and instructions
├── demo_pipeline.py                # Standalone demonstration pipeline (offline-safe)
├── requirements.txt                # Lightweight dependencies (jsonschema, matplotlib, pytest)
├── schema/
│   └── military_state.json         # Draft-07 JSON Schema ontology for tactical states
├── src/
│   ├── advisor.py                  # Tactical decision advisor (Ollama / rule-based fallback)
│   ├── evaluate.py                 # Evaluation harness computing schema validation pass rates
│   └── extractor.py                # LocalLLMExtractor with programmatic Draft-07 validation
├── scripts/
│   ├── augment_data.py             # Neutral synthetic scenario and coordinate generator
│   └── visualize.py                # 2D spatial layout visualization tool
├── augmented_data/                 # 10 regenerated synthetic scenario pairs + dataset.json
│   ├── dataset.json
│   ├── sample_0.json
│   └── ...
└── tests/
    └── test_extraction.py         # 8 deterministic unit tests
```

---

## 5. Technical Mechanics

### A. Schema-Constrained Prompting
The extractor constructs a prompt that directly injects the formal JSON schema definition into the LLM system context. The model is instructed to output strictly valid JSON matching the schema, with no preamble or conversational filler:

```python
from src.extractor import LocalLLMExtractor

extractor = LocalLLMExtractor(model_name="qwen2.5:7b")
result = extractor.extract(arabic_tactical_text)

if result["success"]:
    state = result["data"]
    print("Extracted unit count:", len(state["units"]["friendly"]))
else:
    print("Extraction rejected:", result["error"])
```

### B. Two-Stage Deterministic Validation Guard
1. **Syntax Guard**: Strips potential markdown code blocks (` ```json ... ``` `) and parses via `json.loads`.
2. **Schema Guard**: Validates the resulting dictionary against `schema/military_state.json` via `jsonschema.Draft7Validator`. If any required field is missing, unit types are malformed, or coordinate arrays fail length constraints, validation fails deterministically with an explicit error.

---

## 6. Setup & Verification

### Prerequisites
* Python 3.10+ (tested on Python 3.13)
* (Optional for live inference) [Ollama](https://ollama.com/) with Qwen 2.5 7B:
  ```bash
  ollama pull qwen2.5:7b
  ```

### Installation
Clone this repository and install dependencies:
```bash
git clone https://github.com/<your-username>/arabic-structured-llm-extractor.git
cd arabic-structured-llm-extractor
pip install -r requirements.txt
```

### Running the Test Suite
The unit test suite runs completely offline, requiring no live LLM instance:
```bash
python -m pytest tests -v -W error
```
*Expected output: 8 passed.*

### Running the Demonstration Pipeline
To run the full extraction, 2D mapping, and advisor demo:
```bash
python demo_pipeline.py
```
*Note: If Ollama is running, live inference is performed. If Ollama is offline, the script informs the user and uses the validated synthetic ground-truth state to demonstrate downstream spatial rendering and advisory evaluation without fabricating inference.*

### Regenerating Synthetic Data
To generate fresh synthetic training/evaluation scenarios in the neutral coordinate space:
```bash
python scripts/augment_data.py
```

---

## 7. Prototype Limitations & Honest Scope

* **Academic Prototype**: This repository represents an exploratory research prototype demonstrating local LLM capabilities on low-resource Arabic structured NLP tasks. It is **not** a production military command-and-control system.
* **Inference Latency**: Running 7B-parameter models locally on CPU or consumer GPU introduces noticeable latency (2–8 seconds per dispatch) compared to specialized discriminative NER models.
* **Deterministic Metric Reporting**: No synthetic or inflated F1/BLEU benchmarks are claimed. Pass rates represent exact Draft-07 schema compliance under local Qwen 2.5 7B generation.
