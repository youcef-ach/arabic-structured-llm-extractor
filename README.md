# Arabic Structured LLM Extractor (Public Portfolio Edition)

> **Portfolio Edition Notice**: This repository isolates the structured-information-extraction and local-LLM reasoning component authored by the candidate. It is a standalone, public-safe extraction from an earlier academic team project (`text-to-scene`). All proprietary domain documents, real-world operational coordinates, teammate-authored modules, and historical git ancestry have been intentionally excluded. The public demonstration and evaluation suite use newly generated synthetic scene coordinates.

---

## 1. Overview & Problem Context

In tactical decision-support and command-and-control (C2) simulation environments, field reports, commander directives, and operational updates arrive as unstructured, free-form Arabic military prose. Human operators traditionally translate these text dispatches into formal spatial objects, units, and hierarchical combat states on digital maps—a manual process vulnerable to cognitive overload, latency, and transcription errors.

This project implements an end-to-end local structured information extraction pipeline:
1. Ingests raw Arabic tactical narrative.
2. Queries a locally hosted large language model (**Qwen 2.5 7B** via **Ollama**) guided by an explicit JSON schema.
3. Parses, extracts, and strictly validates the output against a deterministic **JSON Schema (Draft-07)** specification using `jsonschema`.
4. Renders a 2D spatial plot of friendly and hostile units, boundaries, and objectives in a synthetic Cartesian scene grid.
5. Evaluates commander actions via an interactive tactical advisor module.

```
┌────────────────────────────────────────┐
│     Raw Arabic Tactical Text           │
│   (Unstructured narrative / order)     │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│       Local LLM Inference              │
│     (Ollama / Qwen 2.5 7B)             │
│    Prompt-injected JSON Schema         │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│     Markdown Fence Stripping &         │
│         JSON Syntax Parsing            │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│     Deterministic Schema Guard         │
│    (Draft-07 Validation via            │
│     `jsonschema` Validator)            │
└─────────┬────────────────────┬─────────┘
          │ Valid              │ Invalid
          ▼                    ▼
┌────────────────────┐ ┌────────────────────┐
│ Tactical State     │ │  Rejection /       │
│ - Friendly/Enemy   │ │  ValidationError   │
│ - Scene Coordinates│ └────────────────────┘
│ - Unit Hierarchy   │
└─────────┬──────────┘
          │
          ├───────────────────────────────┐
          ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ 2D Scene Visualization      │ │  Tactical Decision          │
│ (Synthetic Cartesian Grid)  │ │  Advisory Module            │
└─────────────────────────────┘ └─────────────────────────────┘
```

---

## 2. Personal Authorship & Project Boundaries

To maintain strict academic integrity and engineering transparency, the exact authorship boundaries are documented below:

| Component / Responsibility | Candidate Authorship Status | In Public Edition? | Description / Notes |
| :--- | :--- | :--- | :--- |
| **Structured LLM Extractor (`src/extractor.py`)** | **Sole Author** | **Yes** | Prompt engineering, schema injection, JSON parsing, Draft-07 runtime validation. |
| **Domain State Schema (`schema/tactical_state.json`)** | **Sole Author** | **Yes** | Draft-07 formal specification defining unit types, coordinates, combat states, and missions. |
| **Tactical Advisor (`src/advisor.py`)** | **Sole Author** | **Yes** | Rule-assisted and local LLM-driven tactical advice generator for student/commander actions. |
| **Synthetic Scenario Generator (`scripts/augment_data.py`)** | **Sole Author** | **Yes** | Generates paired Arabic text scenarios and ground-truth JSON states in synthetic Cartesian scene coordinates. |
| **2D Spatial Plotter (`scripts/visualize.py`)** | **Sole Author** | **Yes** | Matplotlib-based 2D spatial layout mapping friendly, hostile, and coordinate markers on a Cartesian grid. |
| **Deterministic Unit Tests (`tests/test_extraction.py`)** | **Sole Author** | **Yes** | Automated test suite validating schema conformance, malformed JSON handling, and path independence. |
| **Voice-to-Text / Whisper LoRA** | **Teammate Work** (`iAhmeed`) | **Excluded** | Audio transcription fine-tuning; intentionally decoupled and excluded. |
| **Backend & 3D Simulation Frontend** | **Team-Authored** | **Excluded** | Full-stack server and 3D visualization layers from the broader academic project. |
| **Original Operational Source Data** | **Proprietary / Sensitive** | **Excluded** | Original military doctrine documents and operational coordinate dumps are strictly excluded. |

---

## 3. Data Sanitization & Public Demo Safety

The original academic project was evaluated on military domain material. To ensure total confidentiality and public safety, this portfolio repository has been completely sanitized:

* **Zero Sensitive Documents**: All original proprietary military doctrine documents and raw operational extraction text files are completely omitted.
* **Synthetic Cartesian Coordinates**: All coordinates in `augmented_data/` and `demo_pipeline.py` are newly generated synthetic scene coordinates on a normalized 2D Cartesian grid $[10.0, 90.0]$. The public dataset contains newly generated synthetic scene coordinates and does not reproduce coordinates from the original source material.
* **Fresh Git History**: This repository does not contain or branch from the original academic repository's commit tree. The commit history begins with this public-edition preparation.
* **Transparent Execution Modes**:
  - **Live Mode**: Ingests Arabic text → performs local Ollama/Qwen 2.5 7B inference → parses JSON → executes Draft-07 schema validation.
  - **Offline Demo Mode**: When the local Ollama daemon is unavailable, the pipeline explicitly alerts the user and loads validated synthetic demonstration state for downstream 2D scene visualization and tactical advisor evaluation. The offline demonstration state is never described or represented as an LLM extraction result.

---

## 4. Repository Structure

```
arabic-structured-llm-extractor/
├── .gitignore                      # Hygiene rules (caches, local plots, temp states)
├── README.md                       # Architecture, authorship boundaries, and instructions
├── demo_pipeline.py                # Standalone demonstration pipeline (live/offline modes)
├── requirements.txt                # Lightweight dependencies (jsonschema, matplotlib, pytest)
├── schema/
│   └── tactical_state.json         # Draft-07 JSON Schema ontology for tactical states
├── src/
│   ├── advisor.py                  # Tactical decision advisor (Ollama / rule-based fallback)
│   ├── evaluate.py                 # Evaluation harness computing schema validation pass rates
│   └── extractor.py                # LocalLLMExtractor with programmatic Draft-07 validation
├── scripts/
│   ├── augment_data.py             # Neutral synthetic scenario & Cartesian coordinate generator
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
2. **Schema Guard**: Validates the resulting dictionary against `schema/tactical_state.json` via `jsonschema.Draft7Validator`. If any required field is missing, unit types are malformed, or coordinate arrays fail length constraints, validation fails deterministically with an explicit error.

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
To run the extraction, 2D Cartesian mapping, and advisor demo:
```bash
python demo_pipeline.py
```
*Note: In live mode (Ollama running), live LLM extraction is performed. In offline demo mode, synthetic demonstration state is loaded directly to showcase 2D scene plotting and advisor evaluation without fabricating model extraction.*

### Evaluating Extraction Performance
To run the evaluation harness across synthetic scenarios:
```bash
python src/evaluate.py
```
*Note: The evaluation harness can measure schema-constrained extraction behavior during a live Ollama run. No live model accuracy or extraction benchmark is claimed by the current offline verification.*

### Regenerating Synthetic Data
To generate fresh synthetic training/evaluation scenarios in the synthetic Cartesian scene space:
```bash
python scripts/augment_data.py
```

---

## 7. Prototype Limitations & Honest Scope

* **Academic Prototype**: This repository represents an exploratory research prototype demonstrating local LLM capabilities on low-resource Arabic structured NLP tasks. It is **not** a production military command-and-control system.
* **Local Inference Latency**: Running 7B-parameter models locally introduces noticeable execution latency compared to specialized discriminative NER models, scaling directly with host CPU/GPU compute capability.
* **Deterministic Metric Reporting**: The evaluation harness can measure schema-constrained extraction behavior during a live Ollama run. No live model accuracy or extraction benchmark is claimed by the current offline verification.
