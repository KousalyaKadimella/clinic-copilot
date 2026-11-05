# Clinic Copilot

A multilingual **clinic triage support prototype** built with **Python** and **Streamlit**. It asks a patient a few structured questions, sorts the case into one of **4 urgency levels** with fixed, transparent rules, and shows a short explanation in **English, Telugu or Korean**.

**Live demo:** https://kousalyak03-clinic-copilot-app-3yderz.streamlit.app/
(The free Streamlit app sleeps when unused; if you see "wake up", click it and wait about a minute.)

> **Prototype only, not medical advice.** It does not diagnose or prescribe. In the public demo the AI model call is turned off. All urgency decisions come from the rules in `triage_rules.py`.

---

## What it does

1. **Choose a language:** English, Telugu or Korean.
2. **Describe the complaint**, e.g. "fever and cough", or click a quick demo case (**Fever**, **Chest Pain**, **Mild Cold**).
3. **Answer 3 follow-up questions.** The questions depend on the complaint:
   - **Fever / cough / cold:** how many days, difficulty breathing, high fever or chills
   - **Chest pain:** when it started, whether the pain spreads to the arm, jaw or back, shortness of breath
   - **Anything else:** when it started, how severe, other symptoms
4. **See the result:**
   - A color-coded **risk level** with the reasons behind it
   - A **patient explanation** in the selected language
   - A **structured summary** (complaint, answers, risk level, reasons) for clinic staff
   - The **prompt** that would be sent to the Gemma model

## Urgency levels (rules in `triage_rules.py`)

| Level | Color | When it's assigned |
|---|---|---|
| **Emergency** | Red | Chest pain spreading to the arm, jaw or back · chest pain with shortness of breath · difficulty breathing |
| **Urgent** | Orange | High fever or chills · symptoms lasting 7+ days · severe symptoms |
| **Routine** | Green | No red flags found |
| **Self-care** | Blue | At least 2 mild signs: mild severity, no breathing difficulty, no fever, symptoms for 2 days or less |

Emergency rules are checked first. Urgent rules run only if the case isn't already an emergency, and self-care only if it's still routine.

## Why rules decide, not the AI

Urgency is a safety decision, so it's made by **fixed rules that can be read and tested**, not by a language model that could give a different answer each time. The AI's job is limited to wording: summarizing the case and writing patient-friendly guidance.

## Role of Gemma (AI model)

- `gemma_client.py` builds a prompt with the complaint, the answers and the selected language. The prompt tells the model to summarize, list red flags and write simple guidance, and **not** to diagnose or prescribe.
- **In this repository and the public demo, the model call is disabled.** The app shows the prompt preview and a note instead of a model response.
- During development, Gemma was run locally through **Ollama**.

## Tech stack

| Part | Technology |
|---|---|
| Language | Python |
| Web app | Streamlit |
| Triage logic | Plain Python rules (`triage_rules.py`) |
| AI model | Google Gemma via Ollama (local development only) |
| Hosting | Streamlit Community Cloud |

## Project structure

```text
clinic-copilot/
├── app.py              # Streamlit UI: language, complaint, questions, results, demo cases
├── triage_rules.py     # Rule-based risk levels and the reasons for each
├── gemma_client.py     # Builds the Gemma prompt (model call disabled in the demo)
├── requirements.txt    # streamlit, pydantic, ollama
└── README.md
```

## Run it locally

```bash
git clone https://github.com/KousalyaKadimella/clinic-copilot.git
cd clinic-copilot
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py              # opens http://localhost:8501
```

## Known limitations

- Only 3 question sets (fever/cough/cold, chest pain, general), matched by keywords in the complaint.
- "Mild difficulty" breathing is not treated as a red flag; only "Yes" is.
- The model call is disabled in this version, so explanations come from fixed text, not the AI.
- Not tested with clinicians or real patients.

## Possible improvements

- Unit tests for every rule in `triage_rules.py`
- More complaint types and questions
- Turn the Gemma call back on with a hosted model, and check its output before showing it

---

**Kousalya Kadimella** · M.S. Computer Science, CSU Dominguez Hills
