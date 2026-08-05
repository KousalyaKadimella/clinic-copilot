# Clinic Copilot: Intelligent Clinical Triage Assistant

An AI-powered medical assistant utilizing the Google Gemma LLM client alongside a rule-based expert system for automated response evaluation and patient triage.

---

## Project Overview

**Clinic Copilot** is a Python-based intelligent decision support tool designed to streamline patient intake and clinical triage. The platform combines deterministic clinical triage rules with generative AI (Google Gemma LLM) to analyze patient symptoms, evaluate severity, and suggest safe, structured healthcare routing pathways (e.g., Immediate Care, Scheduled Appointment, or Home Care).

### Key Technical Achievements
* **Hybrid Architecture:** Blends programmatic safety-rule logic with LLM flexibility to prevent hallucinations in critical medical paths.
* **Intelligent Evaluation:** Evaluates response quality and matches conversational symptom inputs against strict triage parameters.
* **Modular Engineering:** Decoupled architecture allows effortless client swapping or rules customization.

---

## Tech Stack

* **Language:** Python 3.10+
* **AI/LLM Engine:** Google Gemma LLM via API client execution
* **Libraries:** Python environment abstractions, `requests` / standard HTTP tooling

---

## Repository Structure

```text
clinic-copilot/
├── app.py              # Main application workflow engine
├── gemma_client.py     # Interface wrapper for Google Gemma LLM API interactions
├── triage_rules.py     # Expert system rules & severity mapping parameters
├── requirements.txt    # Declared project dependencies
└── README.md           # Technical documentation
```

---

## Architecture & Data Flow

1. **Input Intake:** The application receives patient symptom declarations and demographic contexts.
2. **Deterministic Triage (`triage_rules.py`):** High-risk keywords, symptoms, or combinations are evaluated by hardcoded guidelines to instantly catch emergency baselines.
3. **AI Evaluation Context (`gemma_client.py`):** The context passes down to the Google Gemma model with explicit, zero-shot system prompts instructing it to safely gauge clinical priority.
4. **Output Synthesis (`app.py`):** System displays clear triage recommendations, reasoning protocols, and next-step actions.

---

## Local Installation & Setup

Follow these steps to deploy and explore the repository environment locally:

### 1. Prerequisite Environments
Ensure your machine runs Python 3.10 or higher. Verify your local installation via:
```bash
python --version
```

### 2. Clone the Repository
```bash
git clone https://github.com/KousalyaKadimella/clinic-copilot.git
cd clinic-copilot
```

### 3. Initialize a Virtual Environment
Isolate your dependency trees using an explicit Python virtual environment:
```bash
# Create the environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Running the Tool
Execute the root system processor via terminal:
```bash
python app.py
```

---

## Medical & Architecture Safeguards

* **Rule Fallbacks:** When LLMs take too long to resolve or find ambiguous terminology, `triage_rules.py` implements structured logic trees to safely default to high-severity precautions.
* **Sanitized Evaluation Prompts:** Prompts are restricted from giving actionable single-drug prescriptions, focusing instead on diagnostic category suggestion and priority processing.

---

## Author

**Kousalya Kadimella**  
*MS in Computer Science*  
California State University, Dominguez Hills

---
*Disclaimer: This tool is built as an educational research asset exploring hybrid NLP automation pipelines. It does not replace professional medical advice, clinical diagnoses, or urgent emergency interventions.*
