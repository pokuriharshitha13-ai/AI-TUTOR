Adaptive AI Tutor

it is a high-throughput, personalized AI tutoring framework designed
to provide specialized instruction in technical domains such as
**Python, Machine Learning, and Deep Learning**.

By leveraging **Groq LPU (Language Processing Unit)** and **LangChain's
orchestration layer**, Lumina dynamically adapts its pedagogical style,
complexity, and feedback loops based on a real-time user profile.

------------------------------------------------------------------------

## 🧠 System Architecture

Lumina is built as a **state-managed monolithic application**, carefully
separating conversational intelligence from the technical assessment
module.

### 🔹 1. Orchestration Layer

-   Built using **LangChain**
-   Uses **LLMChain**
-   Maintains cross-turn context via **ConversationBufferMemory**
-   Ensures persona and instructional consistency across sessions

### 🔹 2. Inference Engine

-   Powered by **Groq's `openai/gpt-oss-120b`**
-   Optimized for ultra-low latency
-   Enables near real-time, human-like tutoring interaction

### 🔹 3. Dynamic Context Injection

-   Injects user skill level *(Beginner / Intermediate / Advanced)*
-   Injects preferred teaching style *(Mathematical / Code-first /
    Conceptual)*
-   Reinforces contextual signals at every inference call

### 🔹 4. Code Execution Sandbox

-   Uses Python's `exec()` for execution
-   Captures output via `io.StringIO`
-   Safely renders real-time execution results in the UI
-   Enables interactive, experimentation-driven learning

------------------------------------------------------------------------

## 🧩 Tech Stack

  Layer                Technology
  -------------------- ------------------------------------
  Frontend             Streamlit (Stateful Web Interface)
  LLM Orchestration    LangChain
  Inference Hardware   Groq LPU (via langchain-groq)
  Memory               ConversationBufferMemory
  Runtime              Python 3.10+

------------------------------------------------------------------------

## 🚀 Key Features

### ✅ Adaptive Pedagogical Scaling

-   Beginners → High-level analogies\
-   Intermediate → Structured explanations with examples\
-   Advanced → Mathematical derivations and LaTeX-style breakdowns

### ✅ Integrated Code Sandbox

-   Modify tutor-generated Python code\
-   Execute instantly within the browser\
-   Observe real-time execution output

### ✅ Structured Technical Quizzes (Examiner Mode)

-   Generates targeted assessment questions\
-   Uses low-temperature LLM inference for objective grading\
-   Provides structured scoring with detailed feedback

### ✅ Context-Aware Memory

-   Remembers previous topics\
-   Tracks user mistakes\
-   Maintains cohesive, progressive learning journeys

------------------------------------------------------------------------

## 🛠️ Installation & Setup


### Install Dependencies

``` bash
pip install streamlit langchain langchain-groq python-dotenv
```

### Set Up Groq API Key

#### Option A -- Environment Variable

``` bash
export GROQ_API_KEY='your_api_key_here'
```

#### Option B -- Sidebar Input

-   Launch the application
-   Enter the API key manually in the Streamlit sidebar

### Run the Application

``` bash
streamlit run app.py
```

------------------------------------------------------------------------

## 📖 Usage Guide

### 🏠 Home

-   View personalized learning dashboard\
-   Check current learner profile\
-   Monitor progress

### 💬 Tutor Chat

Ask technical questions such as:

-   Explain the Attention Mechanism in Transformers\
-   How does backpropagation work?\
-   Write a Python implementation of Gradient Descent

The tutor dynamically adapts explanations based on your selected profile
(subject, level, and style).

### 📝 Quiz Room

1.  Enter a topic (e.g., Neural Networks, Pandas, CNNs)\
2.  Click Generate Quiz\
3.  Submit your answers\
4.  Receive:
    -   Technical grade\
    -   Detailed evaluation\
    -   Improvement suggestions


