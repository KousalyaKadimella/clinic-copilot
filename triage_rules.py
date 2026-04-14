def normalize_text(text: str) -> str:
    return text.lower().strip()


def extract_answer_map(answers: list[dict]) -> dict:
    answer_map = {}

    for item in answers:
        q = normalize_text(item["question"])
        a = normalize_text(item["answer"])
        answer_map[q] = a

    return answer_map


def extract_number_from_text(text: str):
    words_to_numbers = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14
    }

    for token in text.split():
        if token.isdigit():
            return int(token)
        if token in words_to_numbers:
            return words_to_numbers[token]

    return None


def assess_risk(complaint: str, answers: list[dict]) -> dict:
    complaint_text = normalize_text(complaint)
    answer_map = extract_answer_map(answers)

    risk_level = "routine"
    reasons = []

    breathing = answer_map.get(
        "does the patient have difficulty breathing?", ""
    )

    chest_breathing = answer_map.get(
        "is the patient also short of breath?", ""
    )

    fever = answer_map.get(
        "does the patient have a high fever or chills?", ""
    )

    days = answer_map.get(
        "how many days has the patient had these symptoms?", ""
    )

    spread = answer_map.get(
        "does the pain spread to the arm, jaw, or back?", ""
    )

    severity = answer_map.get(
        "how severe are the symptoms?", ""
    )

    days_number = extract_number_from_text(days)

    # -------------------------
    # EMERGENCY RULES
    # -------------------------
    if "chest pain" in complaint_text:
        if spread in ["arm", "jaw", "back", "multiple areas"]:
            risk_level = "emergency"
            reasons.append("Chest pain spreading to critical areas")

        if chest_breathing == "yes":
            risk_level = "emergency"
            reasons.append("Chest pain with shortness of breath")

    if breathing == "yes":
        risk_level = "emergency"
        reasons.append("Difficulty breathing reported")

    # -------------------------
    # URGENT RULES
    # -------------------------
    if risk_level != "emergency":
        if fever in ["high fever", "both high fever and chills", "chills"]:
            risk_level = "urgent"
            reasons.append("High fever or chills detected")

        if days_number is not None and days_number >= 7:
            risk_level = "urgent"
            reasons.append(f"Symptoms lasting {days_number} days")

        if severity == "severe":
            risk_level = "urgent"
            reasons.append("Severe symptoms reported")

    # -------------------------
    # SELF-CARE RULES
    # -------------------------
    if risk_level == "routine":
        mild_score = 0

        if severity == "mild":
            mild_score += 1

        if breathing == "no":
            mild_score += 1

        if fever == "no":
            mild_score += 1

        if days_number is not None and days_number <= 2:
            mild_score += 1

        if mild_score >= 2:
            risk_level = "self-care"
            reasons.append("Symptoms appear mild")

    if not reasons:
        reasons.append("No major red-flag symptoms detected")

    return {
        "risk_level": risk_level,
        "reasons": reasons
    }


def get_risk_color(risk_level: str) -> str:
    mapping = {
        "emergency": "red",
        "urgent": "orange",
        "routine": "green",
        "self-care": "blue"
    }
    return mapping.get(risk_level, "gray")