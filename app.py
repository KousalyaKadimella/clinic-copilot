import streamlit as st
from triage_rules import assess_risk
from gemma_client import generate_gemma_response

st.set_page_config(
    page_title="ClinicCopilot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom CSS for colorful UI polish
# -----------------------------
st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #172554 35%, #1d4ed8 100%);
        padding: 1.6rem 1.6rem;
        border-radius: 22px;
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 12px 30px rgba(29, 78, 216, 0.28);
        border: 1px solid rgba(255,255,255,0.08);
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.95;
        margin-bottom: 0.65rem;
    }

    .hero-desc {
        font-size: 0.98rem;
        opacity: 0.92;
        margin-bottom: 0.8rem;
    }

    .hero-tag {
        display: inline-block;
        background: rgba(255,255,255,0.14);
        color: #f8fafc;
        padding: 0.4rem 0.75rem;
        border-radius: 999px;
        font-size: 0.87rem;
        margin-right: 0.45rem;
        margin-top: 0.35rem;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .section-card {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border: 1px solid rgba(96, 165, 250, 0.18);
        border-radius: 18px;
        padding: 1rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.22);
    }

    .mini-label {
        font-size: 0.78rem;
        color: #93c5fd;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.35rem;
        font-weight: 800;
    }

    .value-text {
        font-size: 1rem;
        font-weight: 700;
        color: #f8fafc;
    }

    .soft-note {
        background: linear-gradient(90deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 5px solid #2563eb;
        padding: 0.95rem 1rem;
        border-radius: 12px;
        margin: 0.85rem 0 1rem 0;
        color: #0f172a;
        font-weight: 600;
    }

    .footer-note {
        color: #64748b;
        font-size: 0.92rem;
        margin-top: 1rem;
    }

    .sidebar-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.4rem;
    }

    .sidebar-section {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 0.9rem 0.9rem;
        margin-bottom: 0.9rem;
        color: #e5e7eb;
    }

    .sidebar-section h3 {
        color: #ffffff;
        margin-top: 0rem;
        margin-bottom: 0.55rem;
        font-size: 1rem;
    }

    .sidebar-link a {
        color: #93c5fd !important;
        font-weight: 700;
        text-decoration: none;
    }

    .sidebar-link a:hover {
        color: #bfdbfe !important;
        text-decoration: underline;
    }

    .stButton > button {
        border-radius: 14px !important;
        border: 1px solid rgba(96, 165, 250, 0.30) !important;
        font-weight: 700 !important;
        padding-top: 0.6rem !important;
        padding-bottom: 0.6rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.10) !important;
        background: linear-gradient(135deg, #111827 0%, #1e293b 100%) !important;
        color: #f8fafc !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(59, 130, 246, 0.8) !important;
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
        color: white !important;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.25) !important;
    }

    div[data-testid="stExpander"] {
        border-radius: 16px !important;
        border: 1px solid #cbd5e1 !important;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Session state initialization
# -----------------------------
defaults = {
    "mode": "idle",  # idle | manual | demo
    "language": "English",
    "complaint": "",
    "question_index": 0,
    "answers": [],
    "questions": [],
    "risk_result": None,
    "staff_explanation": "",
    "patient_explanation": [],
    "structured_summary": None,
    "gemma_output": None,
    "demo_hint": "",
    "demo_case_name": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def full_reset():
    keys_to_delete = []
    for key in list(st.session_state.keys()):
        if key.startswith("answer_input_") or key.startswith("answer_select_"):
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del st.session_state[key]

    st.session_state.mode = "idle"
    st.session_state.complaint = ""
    st.session_state.question_index = 0
    st.session_state.answers = []
    st.session_state.questions = []
    st.session_state.risk_result = None
    st.session_state.staff_explanation = ""
    st.session_state.patient_explanation = []
    st.session_state.structured_summary = None
    st.session_state.gemma_output = None
    st.session_state.demo_hint = ""
    st.session_state.demo_case_name = ""


def get_questions(complaint: str):
    complaint_lower = complaint.lower()

    if "fever" in complaint_lower or "cough" in complaint_lower or "cold" in complaint_lower:
        return [
            {
                "question": "How many days has the patient had these symptoms?",
                "type": "text"
            },
            {
                "question": "Does the patient have difficulty breathing?",
                "type": "select",
                "options": ["No", "Mild difficulty", "Yes"]
            },
            {
                "question": "Does the patient have a high fever or chills?",
                "type": "select",
                "options": ["No", "High fever", "Chills", "Both high fever and chills"]
            }
        ]

    elif "chest pain" in complaint_lower:
        return [
            {
                "question": "When did the chest pain start?",
                "type": "text"
            },
            {
                "question": "Does the pain spread to the arm, jaw, or back?",
                "type": "select",
                "options": ["No", "Arm", "Jaw", "Back", "Multiple areas"]
            },
            {
                "question": "Is the patient also short of breath?",
                "type": "select",
                "options": ["No", "Yes"]
            }
        ]

    else:
        return [
            {
                "question": "When did the symptoms start?",
                "type": "text"
            },
            {
                "question": "How severe are the symptoms?",
                "type": "select",
                "options": ["Mild", "Moderate", "Severe"]
            },
            {
                "question": "Are there any other associated symptoms?",
                "type": "text"
            }
        ]


def build_patient_explanation(risk_level: str, language: str):
    explanations = {
        "English": {
            "emergency": [
                "This case needs immediate medical attention.",
                "Please inform the doctor or emergency team right away.",
                "Do not delay care if symptoms become worse.",
                "Watch for breathing trouble, confusion, or severe pain.",
                "Go to emergency services immediately if needed."
            ],
            "urgent": [
                "This case should be seen by a clinician soon.",
                "Please arrange medical review as early as possible.",
                "Do not ignore worsening fever, pain, or vomiting.",
                "Return immediately if symptoms become severe.",
                "Follow clinic instructions carefully."
            ],
            "self-care": [
                "Symptoms appear mild at the moment.",
                "Home care may be enough if symptoms stay mild.",
                "Drink fluids and take rest.",
                "Come back if symptoms get worse.",
                "Seek help if new warning signs appear."
            ],
            "routine": [
                "This case appears stable based on the current answers.",
                "A routine clinical review is recommended.",
                "Monitor the symptoms carefully.",
                "Return if symptoms continue or worsen.",
                "Follow the clinic’s usual care guidance."
            ]
        },
        "Telugu": {
            "emergency": [
                "ఈ పరిస్థితికి వెంటనే వైద్య సహాయం అవసరం.",
                "దయచేసి వెంటనే డాక్టర్ లేదా అత్యవసర బృందానికి తెలియజేయండి.",
                "లక్షణాలు ఎక్కువైతే ఆలస్యం చేయకండి.",
                "శ్వాస తీసుకోవడంలో ఇబ్బంది, గందరగోళం లేదా తీవ్రమైన నొప్పి ఉంటే జాగ్రత్తగా ఉండండి.",
                "అవసరమైతే వెంటనే ఎమర్జెన్సీ సేవలకు వెళ్లండి."
            ],
            "urgent": [
                "ఈ పరిస్థితిని త్వరలోనే వైద్యుడు పరిశీలించాలి.",
                "దయచేసి వీలైనంత త్వరగా వైద్య పరీక్ష ఏర్పాటు చేయండి.",
                "జ్వరం, నొప్పి లేదా వాంతులు ఎక్కువైతే పట్టించుకోకుండా ఉండకండి.",
                "లక్షణాలు తీవ్రమైతే వెంటనే తిరిగి రండి.",
                "క్లినిక్ సూచనలను జాగ్రత్తగా పాటించండి."
            ],
            "self-care": [
                "ప్రస్తుతం లక్షణాలు తేలికగా కనిపిస్తున్నాయి.",
                "లక్షణాలు అలాగే తేలికగా ఉంటే ఇంటి దగ్గర జాగ్రత్తలు సరిపోవచ్చు.",
                "ద్రవాలు ఎక్కువగా తీసుకోండి మరియు విశ్రాంతి తీసుకోండి.",
                "లక్షణాలు ఎక్కువైతే మళ్లీ రండి.",
                "కొత్త హెచ్చరిక లక్షణాలు కనిపిస్తే సహాయం పొందండి."
            ],
            "routine": [
                "ప్రస్తుత సమాధానాల ఆధారంగా ఈ పరిస్థితి స్థిరంగా కనిపిస్తోంది.",
                "సాధారణ వైద్య సమీక్ష సిఫార్సు చేయబడింది.",
                "లక్షణాలను జాగ్రత్తగా గమనించండి.",
                "లక్షణాలు కొనసాగితే లేదా ఎక్కువైతే తిరిగి రండి.",
                "క్లినిక్ సాధారణ సూచనలను పాటించండి."
            ]
        },
        "Korean": {
            "emergency": [
                "이 상태는 즉각적인 의료 조치가 필요합니다.",
                "즉시 의사나 응급팀에 알려주세요.",
                "증상이 악화되면 지체하지 마세요.",
                "호흡 곤란, 혼란, 심한 통증이 있는지 주의하세요.",
                "필요하면 즉시 응급실로 가세요."
            ],
            "urgent": [
                "이 상태는 곧 의료진의 진료가 필요합니다.",
                "가능한 한 빨리 진료를 받도록 하세요.",
                "열, 통증, 구토가 악화되면 무시하지 마세요.",
                "증상이 심해지면 즉시 다시 오세요.",
                "병원의 지시를 잘 따라주세요."
            ],
            "self-care": [
                "현재 증상은 비교적 가벼워 보입니다.",
                "증상이 가볍게 유지되면 가정에서 관리가 가능할 수 있습니다.",
                "수분을 충분히 섭취하고 쉬세요.",
                "증상이 악화되면 다시 오세요.",
                "새로운 위험 신호가 나타나면 도움을 받으세요."
            ],
            "routine": [
                "현재 답변을 기준으로 상태는 비교적 안정적으로 보입니다.",
                "일반적인 진료 검토가 권장됩니다.",
                "증상을 주의 깊게 관찰하세요.",
                "증상이 계속되거나 악화되면 다시 오세요.",
                "병원의 일반적인 안내를 따라주세요."
            ]
        }
    }

    selected_language_data = explanations.get(language, explanations["English"])
    return selected_language_data.get(risk_level, selected_language_data["routine"])


def build_structured_summary(complaint: str, answers: list[dict], risk_level: str, reasons: list[str]) -> dict:
    return {
        "complaint": complaint,
        "answers": answers,
        "risk_level": risk_level,
        "risk_reasons": reasons
    }


def render_risk_badge(risk_level: str):
    colors = {
        "emergency": "#ef4444",
        "urgent": "#f59e0b",
        "routine": "#22c55e",
        "self-care": "#3b82f6"
    }
    color = colors.get(risk_level, "#64748b")

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}, {color});
            color: white;
            padding: 12px 18px;
            border-radius: 14px;
            display: inline-block;
            font-weight: 800;
            font-size: 18px;
            margin-bottom: 8px;
            box-shadow: 0 10px 22px rgba(0,0,0,0.16);
        ">
            Risk Level: {risk_level.upper()}
        </div>
        """,
        unsafe_allow_html=True
    )


def run_case(complaint: str, answers: list[dict], language: str):
    risk_result = assess_risk(complaint, answers)
    risk_level = risk_result["risk_level"]
    reasons = risk_result["reasons"]

    staff_explanation = (
        f"The case is classified as {risk_level.upper()} based on the reported complaint "
        f"and answers. Key reason(s): " + "; ".join(reasons)
    )

    patient_explanation = build_patient_explanation(risk_level, language)
    structured_summary = build_structured_summary(complaint, answers, risk_level, reasons)
    gemma_output = generate_gemma_response(complaint, answers, language)

    return {
        "risk_result": risk_result,
        "staff_explanation": staff_explanation,
        "patient_explanation": patient_explanation,
        "structured_summary": structured_summary,
        "gemma_output": gemma_output,
    }


def render_result_block(complaint: str, answers: list[dict], language: str, result: dict, title_prefix: str = "Triage Session"):
    gemma_output = result["gemma_output"]
    risk_level = result["risk_result"]["risk_level"]

    st.divider()
    st.markdown(f"## {title_prefix}")

    info1, info2 = st.columns(2)
    with info1:
        st.markdown(
            f'<div class="section-card"><div class="mini-label">Language</div><div class="value-text">{language}</div></div>',
            unsafe_allow_html=True
        )
    with info2:
        st.markdown(
            f'<div class="section-card"><div class="mini-label">Complaint</div><div class="value-text">{complaint}</div></div>',
            unsafe_allow_html=True
        )

    st.success("Triage processing completed.")

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown("### Risk Classification")
        render_risk_badge(risk_level)

        st.markdown("### Staff Explanation")
        if gemma_output and gemma_output.get("used_model") and gemma_output.get("staff_summary"):
            st.markdown(f'<div class="section-card">{gemma_output["staff_summary"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="section-card">{result["staff_explanation"]}</div>', unsafe_allow_html=True)

        st.markdown(f"### Patient Explanation ({language})")
        patient_lines = gemma_output["patient_bullets"] if gemma_output and gemma_output.get("used_model") and gemma_output.get("patient_bullets") else result["patient_explanation"]
        patient_html = "".join([f"<li>{line}</li>" for line in patient_lines])
        st.markdown(f'<div class="section-card"><ul>{patient_html}</ul></div>', unsafe_allow_html=True)

    with right:
        st.markdown("### Gemma Red Flags")
        if gemma_output and gemma_output.get("used_model") and gemma_output.get("red_flags"):
            flags_html = "".join([f"<li>{flag}</li>" for flag in gemma_output["red_flags"]])
            st.markdown(f'<div class="section-card"><ul>{flags_html}</ul></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-card">No model-generated red flags available.</div>', unsafe_allow_html=True)

        st.markdown("### Structured Summary")
        st.json(result["structured_summary"])

    st.markdown("### Collected Answers")
    for idx, item in enumerate(answers, start=1):
        st.markdown(
            f"""
            <div class="section-card">
                <div class="mini-label">Question {idx}</div>
                <div class="value-text" style="font-size:0.98rem; font-weight:700;">{item['question']}</div>
                <div style="margin-top:0.55rem; color:#cbd5e1;"><strong>Answer:</strong> {item['answer']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.expander("View Gemma Integration Details"):
        st.write("This section shows the model prompt and raw model output for transparency.")
        st.write(f"**Model connected:** {gemma_output.get('used_model', False) if gemma_output else False}")

        preview_text = gemma_output.get("prompt_preview", "") if gemma_output else ""
        st.text_area("Prompt Preview Sent to Gemma", preview_text, height=220)

        st.write("**Gemma Summary:**")
        st.write(gemma_output.get("staff_summary", "") if gemma_output else "No Gemma output available.")

        raw_output = gemma_output.get("raw_output", "") if gemma_output else ""
        st.text_area("Raw Model Response", raw_output, height=220)


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">About ClinicCopilot</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sidebar-section">
            ClinicCopilot is a multilingual triage support prototype that combines structured questions,
            transparent rule-based risk scoring, and Gemma-powered explanations.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-section">
            <h3>Safety</h3>
            <div>• Not a diagnosis tool</div>
            <div>• No medication recommendations</div>
            <div>• Escalation-focused guidance</div>
            <div>• Transparent reasoning</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-section">
            <h3>Demo Tips</h3>
            <div>• Use Quick Demo Cases for instant results</div>
            <div>• Use Start Triage for manual question flow</div>
            <div>• Expand the Gemma section to show explainability</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-section sidebar-link">
            <h3>Built By</h3>
            <a href="https://www.linkedin.com/in/kousalya-k-409361140/" target="_blank">Kousalya</a><br/>
            CSUDH
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🩺 ClinicCopilot</div>
        <div class="hero-subtitle">Multilingual Triage & Health Education Assistant</div>
        <div class="hero-desc">Hackathon prototype for structured, explainable, and safety-focused triage support.</div>
        <div>
            <span class="hero-tag">Rule-based risk scoring</span>
            <span class="hero-tag">Gemma explanations</span>
            <span class="hero-tag">Manual + Demo modes</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Inputs
# -----------------------------
input_left, input_right = st.columns([1, 1.65])

with input_left:
    st.markdown("### Input")
    selected_language = st.selectbox(
        "Select language",
        ["English", "Telugu", "Korean"],
        index=["English", "Telugu", "Korean"].index(st.session_state.language)
    )

with input_right:
    complaint_input = st.text_area(
        "Describe the patient's main problem",
        value=st.session_state.complaint,
        placeholder="Example: Fever for 2 days and cough",
        height=110
    )

st.markdown("###  Quick Demo Cases")
d1, d2, d3, d4 = st.columns(4)

with d1:
    if st.button(" Fever Demo", use_container_width=True):
        full_reset()
        st.session_state.language = selected_language
        st.session_state.mode = "demo"
        st.session_state.demo_case_name = "Fever Demo"
        st.session_state.demo_hint = "Direct demo result loaded."
        st.session_state.complaint = "Fever"
        st.session_state.answers = [
            {"question": "How many days has the patient had these symptoms?", "answer": "10 days"},
            {"question": "Does the patient have difficulty breathing?", "answer": "No"},
            {"question": "Does the patient have a high fever or chills?", "answer": "Both high fever and chills"},
        ]
        st.rerun()

with d2:
    if st.button(" Chest Pain Demo", use_container_width=True):
        full_reset()
        st.session_state.language = selected_language
        st.session_state.mode = "demo"
        st.session_state.demo_case_name = "Chest Pain Demo"
        st.session_state.demo_hint = "Direct demo result loaded."
        st.session_state.complaint = "Chest pain"
        st.session_state.answers = [
            {"question": "When did the chest pain start?", "answer": "Today"},
            {"question": "Does the pain spread to the arm, jaw, or back?", "answer": "Arm"},
            {"question": "Is the patient also short of breath?", "answer": "Yes"},
        ]
        st.rerun()

with d3:
    if st.button(" Mild Cold Demo", use_container_width=True):
        full_reset()
        st.session_state.language = selected_language
        st.session_state.mode = "demo"
        st.session_state.demo_case_name = "Mild Cold Demo"
        st.session_state.demo_hint = "Direct demo result loaded."
        st.session_state.complaint = "Cold"
        st.session_state.answers = [
            {"question": "How many days has the patient had these symptoms?", "answer": "2 days"},
            {"question": "Does the patient have difficulty breathing?", "answer": "No"},
            {"question": "Does the patient have a high fever or chills?", "answer": "No"},
        ]
        st.rerun()

with d4:
    if st.button("Reset Session", use_container_width=True):
        full_reset()
        st.rerun()

if st.session_state.demo_hint:
    st.markdown(f'<div class="soft-note">{st.session_state.demo_hint}</div>', unsafe_allow_html=True)

manual_col1, manual_col2 = st.columns([1, 3])

with manual_col1:
    if st.button("Start Triage", use_container_width=True):
        if complaint_input.strip() == "":
            st.warning("Please enter the patient's complaint first.")
        else:
            full_reset()
            st.session_state.mode = "manual"
            st.session_state.language = selected_language
            st.session_state.complaint = complaint_input.strip()
            st.session_state.questions = get_questions(complaint_input.strip())
            st.rerun()

# -----------------------------
# Manual mode flow
# -----------------------------
if st.session_state.mode == "manual":
    total_questions = len(st.session_state.questions)
    current_index = st.session_state.question_index

    
    if current_index < total_questions:
        st.divider()
        st.markdown("## Manual Triage Session")

        info1, info2 = st.columns(2)
        with info1:
            st.markdown(
                f'<div class="section-card"><div class="mini-label">Language</div><div class="value-text">{st.session_state.language}</div></div>',
                unsafe_allow_html=True
            )
        with info2:
            st.markdown(
                f'<div class="section-card"><div class="mini-label">Complaint</div><div class="value-text">{st.session_state.complaint}</div></div>',
                unsafe_allow_html=True
            )

        
        current_question_obj = st.session_state.questions[current_index]
        current_question = current_question_obj["question"]
        question_type = current_question_obj["type"]

        st.markdown(
            f"""
            <div class="section-card">
                <div class="mini-label">Question {current_index + 1} of {total_questions}</div>
                <div class="value-text">{current_question}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        answer_value = None

        if question_type == "text":
            answer_value = st.text_input("Enter answer", key=f"answer_input_{current_index}")
        elif question_type == "select":
            answer_value = st.selectbox(
                "Choose an answer",
                current_question_obj["options"],
                index=None,
                placeholder="Select an option",
                key=f"answer_select_{current_index}"
            )

        next_col1, next_col2 = st.columns([1, 4])
        with next_col1:
            if st.button("Next Question", use_container_width=True):
                if answer_value is None or str(answer_value).strip() == "":
                    st.warning("Please provide an answer before continuing.")
                else:
                    st.session_state.answers.append({
                        "question": current_question,
                        "answer": str(answer_value).strip()
                    })
                    st.session_state.question_index += 1
                    st.rerun()
    else:
        result = run_case(
            st.session_state.complaint,
            st.session_state.answers,
            st.session_state.language
        )
        render_result_block(
            st.session_state.complaint,
            st.session_state.answers,
            st.session_state.language,
            result,
            title_prefix="Triage Result"
        )

# -----------------------------
# Demo mode flow
# -----------------------------
elif st.session_state.mode == "demo":
    result = run_case(
        st.session_state.complaint,
        st.session_state.answers,
        st.session_state.language
    )
    render_result_block(
        st.session_state.complaint,
        st.session_state.answers,
        st.session_state.language,
        result,
        title_prefix=f"Quick Demo Result — {st.session_state.demo_case_name}"
    )

st.markdown(
    """
    <div class="footer-note">
        ClinicCopilot is a prototype built for structured, explainable, and multilingual triage support.
    </div>
    """,
    unsafe_allow_html=True
)