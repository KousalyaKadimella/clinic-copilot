def build_triage_prompt(complaint: str, answers: list[dict], language: str) -> str:
    answers_text = "\n".join(
        [f"Q: {item['question']}\nA: {item['answer']}" for item in answers]
    )

    prompt = f"""
You are ClinicCopilot, a multilingual triage support assistant.

Language selected: {language}

Patient complaint:
{complaint}

Collected triage answers:
{answers_text}

Your task:
1. Summarize the complaint and answers.
2. Identify possible red flags.
3. Explain the likely risk level in simple terms.
4. Generate patient-friendly guidance in the selected language.

Important:
- This is triage support only.
- Do not give a diagnosis.
- Do not prescribe medication.
- Escalate clearly if red-flag symptoms are present.
""".strip()

    return prompt


def generate_gemma_response(complaint: str, answers: list[dict], language: str) -> dict:
    prompt = build_triage_prompt(complaint, answers, language)

    return {
        "used_model": False,
        "prompt_preview": prompt,
        "raw_output": "",
        "staff_summary": "Gemma cloud inference is disabled in this deployed demo. Local Ollama-based Gemma was used during development.",
        "patient_bullets": [],
        "red_flags": [],
    }