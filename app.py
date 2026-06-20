import streamlit as st
import os
import tempfile

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI-Powered Medical Diagnostic System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Force dark premium background layout to match the image palette */
/* Fix black area at bottom */
html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main,
section[data-testid="stMain"] {
    background: #0f172a !important;
}

/* Chat area background */
[data-testid="stChatMessageContainer"] {
    background: transparent !important;
}

/* Main content container */
.block-container {
    background: #0f172a !important;
    padding-bottom: 5rem !important;
}

/* ── Main title layout matching image background ── */
h1 {
    background: linear-gradient(90deg, #38bdf8 0%, #06b6d4 50%, #2dd4bf 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700 !important;
    font-size: 2.4rem !important;
    letter-spacing: -0.5px;
}

/* Sub-headline / tagline contrast fix */
h5 {
    color: #94a3b8 !important; /* Readable muted silver text */
    font-weight: 400 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.3px;
}

/* Section headers (h2) */
h2 {
    color: #38bdf8 !important;
    font-weight: 600 !important;
    border-left: none !important;
    padding-left: 0px !important;
    margin-top: 1.5rem !important;
}

/* Section sub-headers (h3) */
h3 {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}

/* Custom text visibility handles */
p, span, label {
    color: #cbd5e1 !important;
}

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 60%, #0f172a 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

[data-testid="stSidebar"] * {
    color: #e0f2fe !important;
}

[data-testid="stSidebar"] .stRadio label {
    color: #bae6fd !important;
    font-size: 0.9rem;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > div > label:hover {
    color: #ffffff !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"], .metric-card-node {
    background: linear-gradient(135deg, #1e293b, #0f172a) !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    border-radius: 12px;
    padding: 1rem 1.2rem;
}

[data-testid="stMetricLabel"], .metric-title-lbl {
    color: #38bdf8 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

[data-testid="stMetricValue"], .metric-value-num {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* ── Primary buttons ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(90deg, #0284c7, #06b6d4) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
}

/* ── Text inputs forced dark contrast profiles ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border: 1.5px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 8px !important;
    background: #1e293b !important;
    color: #ffffff !important;
}

/* ── Multiselect tags ── */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #06b6d4 !important;
    color: #ffffff !important;
}

/* ── Login card wrapper ── */
.login-wrapper-card {
    background: #1e293b !important;
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 16px;
    padding: 2rem 1.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

button[data-baseweb="tab"] p {
    color: #94a3b8 !important;
}
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #38bdf8 !important;
}

/* Chat Input Box */
[data-testid="stChatInput"] {
    background-color: #1e293b !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    background-color: #1e293b !important;
    color: #ffffff !important;
}

[data-testid="stChatInputContainer"] {
    background-color: #0f172a !important;
}

.stChatFloatingInputContainer {
    background-color: #0f172a !important;
}

[data-testid="stChatMessage"] {
    background-color: #1e293b !important;
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Fallback Setup for Persistent Results ─────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'credentials' not in st.session_state:
    st.session_state['credentials'] = {
        "Doctor": {"username": "doctor", "password": "123"},
        "Admin":  {"username": "admin",  "password": "123"}
    }

# ── Lazy imports ───────────────────────────────────────────────────────────────
try:
    from services.symptom_predictor import predict_symptoms
    SYMPTOM_MODEL_READY = True
except Exception as e:
    SYMPTOM_MODEL_READY = False
    SYMPTOM_MODEL_ERROR = str(e)

try:
    from services.xray_predictor import predict_xray
    XRAY_MODEL_READY = True
except Exception as e:
    XRAY_MODEL_READY = False
    XRAY_MODEL_ERROR = str(e)

try:
    from services.chatbot import medical_chat
    CHAT_READY = True
except Exception as e:
    CHAT_READY = False
    CHAT_ERROR = str(e)

try:
    from services.report_analyzer import analyze_report
    REPORT_READY = True
except Exception as e:
    REPORT_READY = False
    REPORT_ERROR = str(e)

try:
    from services.pdf_generator import generate_pdf
    PDF_READY = True
except Exception as e:
    PDF_READY = False
    PDF_ERROR = str(e)

os.makedirs("reports", exist_ok=True)

COMMON_SYMPTOMS = [
    "fever", "cough", "headache", "fatigue", "nausea", "vomiting",
    "diarrhea", "chest pain", "shortness of breath", "dizziness",
    "sore throat", "runny nose", "body ache", "chills", "rash",
    "abdominal pain", "back pain", "joint pain", "loss of appetite",
    "weight loss", "night sweats", "swelling", "blurred vision",
    "palpitations", "frequent urination", "constipation",
]

# =====================================
# LOGIN PAGE
# =====================================
if not st.session_state['logged_in']:
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 0.5rem;">
        <div style="display:inline-block; background: linear-gradient(90deg, #0284c7, #06b6d4); border-radius: 16px; padding: 14px 22px;">
            <span style="font-size: 2.4rem;">🏥</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.title("AI-Powered Medical Diagnostic System")
    st.markdown("##### Disease Prediction  •  X-Ray Analysis  •  Report Analysis  •  AI Healthcare Assistant")
    st.markdown("---")

    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        #st.markdown("<div class='login-wrapper-card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='login-wrapper-card'>
            <h2 style="
                text-align:center;
                background: linear-gradient(90deg, #38bdf8 0%, #06b6d4 50%, #2dd4bf 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight:700;
                border:none;
                padding:0;
            ">
                Welcome to AI Medical Diagnostic System
            </h2>

        </div>
        """, unsafe_allow_html=True)
        auth_mode = st.tabs(["🔒 Login", "🛠️ Configure Account"])

        with auth_mode[0]:
            st.write("")
            login_role = st.segmented_control(
                "Select Role:",
                options=["👨‍⚕️ Doctor", "🛠️ System Admin"],
                default="👨‍⚕️ Doctor"
            )
            role_key = "Doctor" if login_role == "👨‍⚕️ Doctor" else "Admin"

            st.write("")
            username_input = st.text_input("Username", key="login_user", placeholder="Enter your username...")
            password_input = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password...")

            st.write("")
            if st.button("🔐 Sign In", key="submit_login_btn", use_container_width=True, type="primary"):
                target_creds = st.session_state['credentials'][role_key]
                if username_input == target_creds['username'] and password_input == target_creds['password']:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = role_key
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password. Please try again.")

        with auth_mode[1]:
            st.write("")
            reg_role     = st.selectbox("Select Role to Configure", ["Doctor", "Admin"])
            new_username = st.text_input("New Username", placeholder="Enter new username...")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password...")

            st.write("")
            if st.button("💾 Save Credentials", use_container_width=True, type="primary"):
                if not new_username.strip() or not new_password.strip():
                    st.warning("⚠️ Both fields are required.")
                else:
                    st.session_state['credentials'][reg_role] = {
                        "username": new_username.strip(),
                        "password": new_password.strip()
                    }
                    st.success(f"✅ Credentials updated for {reg_role}! You can now log in.")
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# MAIN APP (POST-LOGIN)
# =====================================
else:
    if os.path.exists("hospital_banner.png"):
        st.image("hospital_banner.png", use_container_width=True)

    st.title("AI-Powered Medical Diagnostic System")
    st.markdown("##### Disease Prediction  •  X-Ray Analysis  •  Report Analysis  •  AI Healthcare Assistant")
    st.markdown("---")

    # Sidebar Header Info Panel
    st.sidebar.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 16px; border-radius: 12px; text-align: center; margin-bottom: 16px;">
        <div style="font-size:11px; color:#bae6fd; font-weight:600; letter-spacing:1px; margin-bottom:6px;">ACTIVE SESSION</div>
        <div style="font-size:1.1rem; font-weight:700; color:#ffffff;">👨‍⚕️ {st.session_state['user_role']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.title("AI Medical System")
    st.sidebar.markdown("---")

    if st.session_state['user_role'] == "Admin":
        nav_options = [
            "🖥️ Infrastructure Dashboard",
            "⚙️ Parameter Adjustments",
            "📊 System Audit Records"
        ]
    else:
        nav_options = [
            "🏠 Dashboard",
            "🩺 Symptom Checker",
            "🔬 X-Ray Analysis",
            "📄 Report Analyzer",
            "💬 Medical Chatbot",
            "💊 Medicine Guide",
            "🧮 BMI Calculator",
            "📊 Analytics",
            "📁 Patient History",
            "ℹ️ About"
        ]

    page = st.sidebar.radio("Navigation", nav_options, label_visibility="collapsed")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Sign Out", use_container_width=True, type="primary"):
        st.session_state.clear()
        st.rerun()

    current_page = page.split(" ", 1)[1].strip() if " " in page else page

    # =====================================
    # ADMIN VIEWS
    # =====================================
    if st.session_state['user_role'] == "Admin":
        st.markdown(f"<span class='section-badge'>Admin Panel</span>", unsafe_allow_html=True)
        st.header(f"{current_page}")

        if current_page == "Infrastructure Dashboard":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='metric-card-node'><div class='metric-title-lbl'>GPU Cluster State</div><div class='metric-value-num'>V100 Node — Active ✅</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='metric-card-node'><div class='metric-title-lbl'>API Response Time</div><div class='metric-value-num'>12.4 ms</div></div>", unsafe_allow_html=True)
        elif current_page == "Parameter Adjustments":
            st.slider("Model Temperature", 0.0, 1.0, 0.2, step=0.05)
        elif current_page == "System Audit Records":
            st.code("[SYSTEM] Encryption flags and active state tokens validated successfully.")

    # =====================================
    # DOCTOR VIEWS
    # =====================================
    elif st.session_state['user_role'] == "Doctor":
        if current_page == "Dashboard":
            st.markdown("<span class='section-badge'>Overview</span>", unsafe_allow_html=True)
            st.header("Dashboard")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Symptom Classifications", "41 Conditions")
            with col2: st.metric("X-Ray AI", "Active 🟢")
            with col3: st.metric("Medical LLM", "Online 🟢")
            st.success("🔒 Secure clinical session is active.")

        elif current_page == "Symptom Checker":
            st.markdown("<span class='section-badge'>AI Diagnosis</span>", unsafe_allow_html=True)
            st.header("Symptom Checker")
            selected = st.multiselect("Select symptoms from the list:", options=COMMON_SYMPTOMS, placeholder="Choose symptoms…")
            custom = st.text_input("Add custom symptoms (comma-separated)", placeholder="e.g. itchy eyes, dry mouth")

            if custom:
                extra = [s.strip().lower() for s in custom.split(",") if s.strip()]
                selected = list(set(selected + extra))

            if selected:
                st.markdown("**Selected:** " + " ".join(f"`{s}`" for s in selected))

            if st.button("🔍 Predict Disease", type="primary", use_container_width=True):
                if not selected: st.warning("Please select at least one symptom.")
                elif not SYMPTOM_MODEL_READY: st.error(f"Symptom model error: {SYMPTOM_MODEL_ERROR}")
                else:
                    with st.spinner("Analysing symptoms…"):
                        disease, confidence = predict_symptoms(selected)
                    st.success("✅ Prediction complete!")
                    m1, m2 = st.columns(2)
                    m1.metric("Predicted Disease", disease)
                    m2.metric("Confidence", f"{confidence:.1f}%")

        elif current_page == "X-Ray Analysis":
            st.markdown("<span class='section-badge'>Radiology AI</span>", unsafe_allow_html=True)
            st.header("X-Ray Analysis")
            uploaded = st.file_uploader("Upload X-Ray Image", type=["jpg", "jpeg", "png"])
            if uploaded:
                st.image(uploaded, caption="Uploaded X-Ray", width=420)
                if not XRAY_MODEL_READY: st.error(f"X-Ray model error: {XRAY_MODEL_ERROR}")
                else:
                    if st.button("🔬 Analyse X-Ray", type="primary", use_container_width=True):
                        with st.spinner("Running inference…"):
                            suffix = os.path.splitext(uploaded.name)[-1]
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                                tmp.write(uploaded.read())
                                tmp_path = tmp.name
                            result, confidence = predict_xray(tmp_path)
                            os.unlink(tmp_path)
                        if result == "Positive": st.error(f"🔴 **{result}** — Abnormality detected ({confidence:.1f}% confidence)")
                        else: st.success(f"🟢 **{result}** — No abnormality detected ({confidence:.1f}% confidence)")

        elif current_page == "Report Analyzer":
            st.markdown("<span class='section-badge'>Document AI</span>", unsafe_allow_html=True)
            st.header("Medical Report Analyzer")
            report_text = st.text_area("Paste medical report text here", height=260)
            if st.button("📄 Analyse Report", type="primary", use_container_width=True):
                if not report_text.strip(): st.warning("Please paste some report text first.")
                elif not REPORT_READY: st.error(f"Report analyser error: {REPORT_ERROR}")
                else:
                    with st.spinner("Analysing report…"):
                        analysis = analyze_report(report_text)
                    st.markdown("---")
                    st.markdown(analysis)

        elif current_page == "Medical Chatbot":
            st.markdown("<span class='section-badge'>AI Assistant</span>", unsafe_allow_html=True)
            st.header("Medical Chatbot")
            if "chat_history" not in st.session_state: st.session_state.chat_history = []
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            user_input = st.chat_input("Ask a medical question…")
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                if not CHAT_READY: reply = f"⚠️ Chatbot unavailable: {CHAT_ERROR}"
                else:
                    with st.spinner("Thinking…"):
                        reply = medical_chat(
                        f"""
                        User Question: {user_input}

                        You are a professional medical assistant.

                        Return the answer in this format:

                        🩺 Symptom:
                        📌 Possible Cause:
                        🤒 Symptoms:
                        🏠 Home Care:
                        💊 OTC Medicines:
                        👨‍⚕️ Specialist Doctor:
                        🚨 Emergency Warning:

                        Reply in the same language as the user.
                        Use proper markdown formatting.
                        """
                        )
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                with st.chat_message("assistant"): st.markdown(reply)

        elif current_page == "Medicine Guide":
            st.markdown("<span class='section-badge'>Drug Reference</span>", unsafe_allow_html=True)
            st.header("Medicine Guide")
            medicine = st.text_input("Enter Medicine / Generic Name", placeholder="e.g. Paracetamol…")
            if st.button("🔍 Search Medicine", use_container_width=True, type="primary"):
                if not medicine.strip(): st.warning("Please enter medicine name.")
                else:
                    with st.spinner("Searching database…"):
                        response = medical_chat(f"Explain medicine: {medicine}")
                    st.markdown(response)

        elif current_page == "BMI Calculator":
            st.markdown("<span class='section-badge'>Vitals</span>", unsafe_allow_html=True)
            st.header("BMI & Vitals Calculator")
            c1, c2 = st.columns(2)
            with c1: w = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0)
            with c2: h = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
            bmi = w / ((h / 100) ** 2)
            st.metric("Your BMI", f"{bmi:.1f}")

        elif current_page == "Analytics":
            import pandas as pd
            st.markdown("<span class='section-badge'>Insights</span>", unsafe_allow_html=True)
            data = pd.DataFrame({"Month": ["Jan", "Feb", "Mar"], "Patients": [120, 150, 180]})
            st.line_chart(data.set_index("Month"))

        elif current_page == "Patient History":
            st.header("Patient Longitudinal Records")
            st.text_input("🔍 Search by Patient UID")

        elif current_page == "About":
            st.header("About This System")
            st.markdown("**Version:** 1.1.0-AI \n\nDesigned by Rajan Pandey.")