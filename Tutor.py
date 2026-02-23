import streamlit as st
import re
import sys
from io import StringIO
from langchain_groq import ChatGroq
from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.output_parsers import BaseOutputParser

class MathFormattingParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        return text

def render_safe_markdown(text):
    import re

    pattern = r'\$\$(.*?)\$\$'
    matches = list(re.finditer(pattern, text, re.DOTALL))

    last_end = 0

    for match in matches:
        # Render normal text before math
        if match.start() > last_end:
            st.markdown(text[last_end:match.start()])

        # Render math safely
        math_content = match.group(1).strip()
        try:
            st.latex(math_content)
        except Exception:
            st.code(math_content)

        last_end = match.end()

    # Render remaining text
    if last_end < len(text):
        st.markdown(text[last_end:])

# ================== EDUCATIONAL-ONLY PROMPT ==================
EDUCATIONAL_ONLY_PROMPT = """
You are an AI Tutor limited strictly to EDUCATIONAL purposes.

You may allow minimal greetings (hi, hello, how are you).

GENERAL RULES:
- If a question is not educational, politely refuse.
- Do not provide partial or indirect answers to non-educational questions.
- Clearly state that you can help only with academic topics.
- Ask the user to rephrase in a learning-oriented way if needed.
- Maintain a supportive and encouraging tone.
- Suggest next topics when appropriate.

MATHEMATICS RULES:
- Ignore any provided style.
- Respond strictly using definitions, formulas, derivations, and worked examples.
- Wrap every formula inside $$ and $$.
- Do not output standalone LaTeX.
- Ensure formulas render correctly in Markdown.
- Explain formulas in simple terms with examples and applications.

ADVANCED LEARNER RULES:
- Provide deeper explanations.
- Provide example code when relevant.
- Do NOT provide interactive or step-by-step guided coding
  for Python, Machine Learning, or Deep Learning.

RESOURCE MODE:
When asked for learning resources:
- Provide 4–6 high-quality resources.
- Include:
  • 1 structured course platform
  • 1 university/academic source
  • 2 video resource (YouTube allowed)
  • 1 interactive tool (if applicable)
  • Optional: 1 practice resource
- Adapt to Beginner / Intermediate / Advanced level.
- Use Markdown bullet points.
- Make titles clickable (no raw URLs).
- Avoid random blogs or unverified sources.
- Avoid repeating the same platform in consecutive responses.
- Suggest next topics when appropriate

User Question:
{question}

Educational Answer:
"""
# --- 1. CONFIGURATION & STATE ---
st.set_page_config(page_title="Adaptive AI Tutor", layout="wide")
# ================== BACKGROUND IMAGE FUNCTION ==================
import os
import base64

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return None
    
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# ---- Call the function OUTSIDE ----
try:
    img_base64 = get_base64_image("img1.jpeg")
except Exception:
    img_base64 = None

# ---------- SAFE BACKGROUND HANDLING ----------
background_css = "background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);" 
if img_base64:
    background_css = f""" background: linear-gradient(rgba(15,23,42,0.75),
    rgba(15,23,42,0.75)), url("data:image/jpeg;base64,{img_base64}");
    background-size: cover; 
    background-position: center; 
    background-attachment: fixed;
    background-repeat: no-repeat; """


st.markdown(f"""
<style>

/* ======================================================
   GLOBAL BACKGROUND
====================================================== */
html, body, #root, [data-testid="stApp"] {{
    height: 100%;
    {background_css}
}}

[data-testid="stAppViewContainer"],
.main {{
    background: transparent !important;
}}

/* ======================================================
   HEADER + TOOLBAR + FOOTER (SAME BACKGROUND EFFECT)
====================================================== */

header[data-testid="stHeader"],
[data-testid="stToolbar"],
footer {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
}}

/* Footer layout */
footer {{
    text-align: center;
    padding: 10px 0;
}}

/* Footer text styling */
footer * {{
    color: transparent !important;
    opacity: 0.9;
    font-size: 0.9rem;
}}
/* ======================================================
   SIDEBAR
====================================================== */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}}

section[data-testid="stSidebar"] * {{
    color: #ffffff !important;
}}

section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select {{
    background-color: #ffffff !important;
    color: #0f172a !important;
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
}}
/* ===== REDUCE FOOTER HEIGHT ===== */
[data-testid="stBottomBlockContainer"] {{
    padding-top: 5px !important;
    padding-bottom: 5px !important;
    margin-top: 0px !important;
}}

/* Remove extra spacing inside footer */
[data-testid="stChatInputContainer"] {{
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    margin: 0px !important;
}}

/* Reduce chat input outer spacing */
div[data-testid="stChatInput"] {{
    margin-top: 0px !important;
    margin-bottom: 0px !important;
}}

/* ======================================================
   MAIN CONTENT TEXT
====================================================== */
[data-testid="stMarkdownContainer"] *,
h1, h2, h3, h4, h5, h6 {{
    color: #ffffff !important;
}}

/* ======================================================
   CHAT BUBBLES
====================================================== */
[data-testid="stChatMessage"] {{
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 14px;
}}

/* USER MESSAGE */
[data-testid="stChatMessage"]:has(div[aria-label="user"]) {{
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
}}

[data-testid="stChatMessage"]:has(div[aria-label="user"]) * {{
    color: #ffffff !important;
}}

/* ASSISTANT MESSAGE */
[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) {{
    background: rgba(30,41,59,0.95);
    border: 1px solid rgba(255,255,255,0.05);
}}

/* ==========================================
   ASSISTANT MESSAGE STYLING (SAFE)
========================================== */

/* Assistant message container */
[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) {{
    background-color: #1e293b;
    border-radius: 12px;
    padding: 12px;
}}

/* Assistant text only */
[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) p,
[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) span,
[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) li,
[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) strong {{
    color: #f8fafc;
}}

/* ==========================================
   USER MESSAGE STYLING
========================================== */

[data-testid="stChatMessage"]:has(div[aria-label="user"]) {{
    background-color: #0f172a;
    border-radius: 12px;
    padding: 12px;
}}

[data-testid="stChatMessage"]:has(div[aria-label="user"]) p,
[data-testid="stChatMessage"]:has(div[aria-label="user"]) span,
[data-testid="stChatMessage"]:has(div[aria-label="user"]) li,
[data-testid="stChatMessage"]:has(div[aria-label="user"]) strong {{
    color: #ffffff;
}}

/* ==========================================
   CODE BLOCK PROTECTION (CRITICAL)
========================================== */

/* Markdown code blocks */
[data-testid="stChatMessage"] pre {{
    background-color: #0b1220;
    color: #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    overflow-x: auto;
}}

/* Inline code */
[data-testid="stChatMessage"] code {{    
    background-color: #1e293b;
    color: #38bdf8;
    padding: 3px 6px;
    border-radius: 6px;
}}

/* st.code() block */
[data-testid="stCodeBlock"] {{
    background-color: #0b1220;
    color: #e2e8f0;
    border-radius: 8px;
}}
/* ======================================================
   BUTTONS
====================================================== */
.stButton > button {{
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: #ffffff !important;
    border-radius: 10px;
    border: none;
    padding: 0.55rem 1.2rem;
    font-weight: 600;
    transition: all 0.25s ease;
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(59,130,246,0.35);
}}

/* ======================================================
   MAIN INPUTS
====================================================== */
.stTextInput input,
.stTextArea textarea {{
    background-color: #8E93AE!important;
    color: #0f172a !important;
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
}}

/* ======================================================
   EXPANDER
====================================================== */
[data-testid="stExpander"] {{
    background: rgba(15,23,42,0.95);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.05);
}}


/* ======================================================
   SCROLLBAR
====================================================== */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: transparent;
}}

::-webkit-scrollbar-thumb {{
    background: #334155;
    border-radius: 10px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: #475569;
}}

</style>
""", unsafe_allow_html=True)



if "messages" not in st.session_state: st.session_state.messages = []
if "memory" not in st.session_state: st.session_state.memory = ConversationBufferMemory(memory_key="history", input_key="input")
if "quiz_data" not in st.session_state: st.session_state.quiz_data = None

# --- 2. SIDEBAR NAVIGATION & PROFILE ---
with st.sidebar:
    st.title("🚀 Navigation")
    page = st.radio("Go to:", ["🏠 Home", "🎓 Tutor Chat", "📝 Quiz Room"])
    
    st.divider()
    st.header("🔑 Settings")
    api_key = st.text_input("Groq API Key", type="password",help=r'https://console.groq.com/keys')

    model="openai/gpt-oss-120b"
    
    st.header("👤 Profile")
    subject = st.text_input(label="Subject")
    level = st.select_slider("Level", ["Beginner", "Intermediate", "Advanced"])
    style = st.radio("Style", ["Code-first", "Mathematical", "Conceptual"])
    
    if st.button("Clear History"):
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.rerun()

# --- 3. HELPER FUNCTIONS ---
def get_response(prompt_text, use_memory=True):
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar.")
        return None
    llm = ChatGroq(model=model, groq_api_key=api_key, temperature=0.3)
    if use_memory:
        template = PromptTemplate.from_template(EDUCATIONAL_ONLY_PROMPT +"\nTutor in {subject} for {level}. Style: {style}. History: {history}. Input: {input}")
        parser = MathFormattingParser()
        chain = LLMChain(llm=llm, prompt=template, output_parser=parser, memory=st.session_state.memory)

        res = chain.invoke({"subject": subject,"level": level,"style": style,"history": "","input": prompt_text,"question": prompt_text})
        return res["text"] if isinstance(res, dict) else res.content
    else:
        res = llm.invoke(prompt_text)
        return res.content


def render_sandbox(text, idx):
    """
    Silent, output-aware Python sandbox for Streamlit AI Tutor.
    - Supports standard imports
    - Persists execution state
    - Never shows Python errors
    - Guides learners when no output is produced
    """

    if "sandbox_globals" not in st.session_state:
        st.session_state.sandbox_globals = {
            "__name__": "__sandbox__",
            "__builtins__": __builtins__,
            "sys": sys,
            "re": re,
        }

    blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)

    for i, code in enumerate(blocks):
        with st.expander(f"🧪 Interactive Code {i + 1}"):

            edited = st.text_area(
                "Edit and run the code below:",
                value=code,
                height=220,
                key=f"sandbox_code_{idx}_{i}",
            )

            if st.button("▶ Run Code", key=f"sandbox_run_{idx}_{i}"):

                buffer = StringIO()
                old_stdout = sys.stdout
                sys.stdout = buffer

                try:
                    exec(edited, st.session_state.sandbox_globals)
                    output = buffer.getvalue()

                    if output.strip():
                        st.code(output)
                    else:
                        st.info(
                            "ℹ️ The code ran successfully but did not produce any visible output.\n\n"
                            "If this code is expected to show results, try running it in your own IDE "
                            "or in **VS Code**, or add `print()` statements."
                        )

                except Exception:
                    st.info(
                        "⚠️ This code may use advanced logic or environment-specific features.\n\n"
                        "**Please try running it in your own IDE or in VS Code for full support.**"
                    )

                finally:
                    sys.stdout = old_stdout


# --- 4. PAGE LOGIC ---

link=r'https://console.groq.com/keys'
if page == "🏠 Home":

    st.title("👋 Welcome to your AI Personalized Tutor")
    st.markdown(f"""
    Hello **{level}** learner! This application is your dedicated space for mastering in your Eduction**
    
    ### 🌟 Core Features
    - **🎓 Tutor Chat:** Engage in a deep technical conversation. The AI adapts to your skill level and preferred style.
    - **📝 Quiz Room:** Test your knowledge! Generate custom quizzes and get them evaluated instantly by the AI.
    - **🛠️ Code Sandbox:** Run and edit Python code snippets directly within the chat.
    
    **How to start?**
    1. Enter your **Groq API Key** in the sidebar.{link}
    2. Choose a page from the navigation menu above to begin your journey.
    """)

elif page == "🎓 Tutor Chat":
    st.title("🎓 Adaptive Tutor Chat")

    for idx, m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"] == "assistant": render_sandbox(m["content"], idx)

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            final_prompt = prompt
            response = get_response(final_prompt)
            if response:
                render_safe_markdown(response)   # ✅ FIXED
                render_sandbox(response, len(st.session_state.messages))
                st.session_state.messages.append({"role": "assistant", "content": response})
elif page == "📝 Quiz Room":
    st.title("📝 Technical Quiz Module")

    quiz_type = st.selectbox(
        "Choose Your Quiz Mode",
        options=["Multiple-Choice Questions", "Open Ended"]
    )

    topic = st.text_input("Enter topic for your quiz:")

    if st.button("Generate Quiz") and topic:
        with st.spinner("Creating your quiz..."):

            if quiz_type == "Multiple-Choice Questions":
                quiz_prompt = (
                    f"Generate a new set of 5 multiple-choice questions on {topic} "
                    f"for a {level} learner in {subject}. "
                    f"Each question should have 4 options labeled A, B, C, and D. "
                    f"Do not provide answers."
                )
            else:
                quiz_prompt = (
                    f"Generate a new set of 5 fill in the blank questions on {topic} "
                    f"for a {level} learner in {subject}. "
                    f"Do not provide answers."
                )

            st.session_state.quiz_data = get_response(quiz_prompt, use_memory=False)
            st.session_state.last_topic = topic

    if st.session_state.quiz_data:
        st.info(st.session_state.quiz_data)

        ans = st.text_area("Write your answers / code here:",height=150)

        if st.button("Submit Answers"):
            with st.spinner("Evaluating..."):
                eval_prompt = (
                    f"Topic: {st.session_state.last_topic}. "
                    f"Quiz: {st.session_state.quiz_data}. "
                    f"User Answers: {ans}. "
                    f"Evaluate technical accuracy and provide a score out of 10. "
                    f"If answers are incorrect, explain the correct answer. "
                    f"If the score is below 6, encourage the learner to revise and retry."
                )

                evaluation = get_response(eval_prompt, use_memory=False)
                st.success("### Evaluation Results")

                st.markdown(evaluation)
