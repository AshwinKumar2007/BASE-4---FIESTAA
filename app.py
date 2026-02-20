import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import plotly.graph_objects as go
import json
from datetime import datetime
from PyPDF2 import PdfReader

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(prompt, system_msg="You are a biotechnology expert tutor."):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def is_biotech_related(query):
    prompt = f"""Is this question related to biotechnology? Answer ONLY 'yes' or 'no'.
Question: {query}"""
    response = call_llm(prompt, "You are a classifier. Answer only 'yes' or 'no'.")
    return "yes" in response.lower()

def extract_pdf_text(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        pages_content = []
        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            pages_content.append({"page": i+1, "text": text})
        return pages_content
    except:
        return []

def init_session():
    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    
    if not st.session_state.sessions and st.session_state.current_session_id is None:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.sessions[session_id] = {
            "name": "Study Session 1",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "learning_path": [],
            "quiz_scores": [],
            "topic_performance": {},
            "pdf_content": [],
            "pdf_full_text": "",
            "chat_history": [],
            "current_study_topic": None,
            "study_conversation": [],
            "topic_history": {},
            "quiz_data": None,
            "user_answers": {},
            "recommended_topics": []
        }
        st.session_state.current_session_id = session_id

def get_current_session():
    if st.session_state.current_session_id:
        return st.session_state.sessions.get(st.session_state.current_session_id, None)
    return None

def create_new_session():
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.sessions[session_id] = {
        "name": f"Study Session {len(st.session_state.sessions) + 1}",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "learning_path": [],
        "quiz_scores": [],
        "topic_performance": {},
        "pdf_content": [],
        "pdf_full_text": "",
        "chat_history": [],
        "current_study_topic": None,
        "study_conversation": [],
        "topic_history": {},
        "quiz_data": None,
        "user_answers": {},
        "recommended_topics": []
    }
    st.session_state.current_session_id = session_id
    return session_id

def delete_session(session_id):
    if session_id in st.session_state.sessions:
        del st.session_state.sessions[session_id]
        if st.session_state.current_session_id == session_id:
            # Switch to another session or create new one
            if st.session_state.sessions:
                st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
            else:
                create_new_session()

init_session()

st.set_page_config(page_title="Biotech Learning Platform", layout="wide")

# Dark theme with crimson/red accents
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0d0d0d;
        color: #e8e8e8;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        padding: 2rem 1rem;
    }
    
    /* Smaller title */
    h1 {
        font-size: 1.8rem !important;
        color: #dc143c !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        text-align: left !important;
    }
    
    /* Remove top padding from main container */
    .block-container {
        padding-top: 1rem !important;
    }
    
    h2 {
        font-size: 1.4rem !important;
        color: #dc143c !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
        color: #ff6b9d !important;
    }
    
    /* Top bar styling */
    .top-bar {
        background-color: #1a1a1a;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #8b0000;
    }
    
    /* Card panels */
    .card-panel {
        background-color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #2a2a2a;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #8b0000;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #a52a2a;
        transform: translateY(-1px);
    }
    
    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #dc143c;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #ff1744;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1a1a1a;
        color: #e8e8e8;
        border: 1px solid #8b0000;
        border-radius: 6px;
        padding: 0.6rem;
    }
    
    /* Select boxes */
    .stSelectbox > div > div > select {
        background-color: #1a1a1a;
        color: #e8e8e8;
        border: 1px solid #8b0000;
        border-radius: 6px;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #e8e8e8;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ff6b9d;
        font-size: 1.5rem;
    }
    [data-testid="stMetricLabel"] {
        color: #b8b8b8;
        font-size: 0.9rem;
    }
    
    /* Divider */
    hr {
        border-color: #8b0000;
        margin: 1.5rem 0;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        background-color: #1a1a1a;
        border-left: 4px solid #dc143c;
        border-radius: 6px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        color: #e8e8e8;
        border-radius: 6px;
    }
    
    /* Tabs - Enhanced */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        padding: 0.5rem;
        border-radius: 8px;
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #b8b8b8;
        padding: 0.8rem 1.5rem;
        font-weight: 500;
        border-radius: 6px;
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2a2a2a;
        color: #e8e8e8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #8b0000 !important;
        color: #ffffff !important;
        border-bottom: none !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1a1a1a;
        border: 2px dashed #8b0000;
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #dc143c;
    }
    
    /* Session button active state */
    .session-active {
        background-color: #dc143c !important;
        border: 2px solid #ff1744 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session Management Sidebar
with st.sidebar:
    st.markdown("### 📚 Session Manager")
    st.markdown("---")
    
    if st.button("➕ New Session", use_container_width=True, type="primary"):
        create_new_session()
        st.rerun()
    
    st.markdown("")
    st.markdown("**Your Sessions:**")
    
    if st.session_state.sessions:
        for session_id, session_data in st.session_state.sessions.items():
            is_active = session_id == st.session_state.current_session_id
            
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(
                    f"{session_data['name']}",
                    key=f"load_{session_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.current_session_id = session_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{session_id}", help="Delete session"):
                    delete_session(session_id)
                    st.rerun()
            
            if is_active:
                st.caption(f"✅ Active | Created: {session_data['created']}")
            else:
                st.caption(f"Created: {session_data['created']}")

# Get current session
current_session = get_current_session()
if not current_session:
    st.error("No active session. Please create one.")
    st.stop()

# Compact header
st.markdown("# 🧬 Biotech Learning Platform")

# Top bar with session info
st.markdown(f"""
<div class="top-bar">
    <strong>📋 {current_session["name"]}</strong> &nbsp;|&nbsp; 
    📚 Topics: {len(current_session["topic_history"])} &nbsp;|&nbsp; 
    📝 Quizzes: {len(current_session["quiz_scores"])}
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Ask AI", 
    "📚 Deep Study", 
    "📝 Quiz & Assessment", 
    "🎯 Learning Path", 
    "📊 Analytics", 
    "ℹ️ About"
])

with tab1:
    st.header("PDF-Grounded AI Tutor")
    
    # PDF Upload
    uploaded_file = st.file_uploader("📄 Upload PDF (Required for document-based Q&A)", type="pdf")
    if uploaded_file:
        with st.spinner("Processing PDF..."):
            pages_content = extract_pdf_text(uploaded_file)
            current_session["pdf_content"] = pages_content
            current_session["pdf_full_text"] = " ".join([p["text"] for p in pages_content])
            st.success(f"✅ PDF loaded ({len(pages_content)} pages, {len(current_session['pdf_full_text'])} characters)")
    
    # PDF Summary
    if current_session["pdf_content"]:
        if st.button("📋 Summarize PDF"):
            with st.spinner("Generating summary..."):
                prompt = f"""Summarize this biotechnology document. Include:
1. Main topics covered
2. Key concepts
3. Document structure

Document content:
{current_session['pdf_full_text'][:8000]}

Provide a clear, organized summary for study purposes."""
                summary = call_llm(prompt)
                st.markdown("### 📋 Document Summary")
                st.markdown(summary)
    
    st.divider()
    
    question = st.text_input("Ask a question about the uploaded PDF:")
    
    if st.button("Get Answer") and question:
        if not current_session["pdf_content"]:
            st.error("⚠️ Please upload a PDF first!")
        else:
            with st.spinner("Searching document..."):
                # Check if answer exists in PDF
                check_prompt = f"""Based ONLY on this document content, can you answer this question: '{question}'?

Document content:
{current_session['pdf_full_text'][:8000]}

Answer ONLY 'yes' if the information exists in the document, or 'no' if it doesn't."""
                check_response = call_llm(check_prompt, "You are a document analyzer. Answer only 'yes' or 'no'.")
                
                if "no" in check_response.lower():
                    st.error("⚠️ This topic is not covered in the uploaded material. Please use the Personalized Learning module.")
                else:
                    # Answer from document
                    answer_prompt = f"""Answer this question using ONLY information from the document below. Do not use external knowledge.

Question: {question}

Document content:
{current_session['pdf_full_text']}

Provide a clear, student-friendly explanation based strictly on the document content. If you reference specific information, mention it came from the document."""
                    answer = call_llm(answer_prompt, "You are a tutor. Answer ONLY using the provided document. Do not add external information.")
                    
                    st.markdown("### 📖 Answer from Document")
                    st.markdown(answer)
                    st.info("ℹ️ This answer is based solely on your uploaded PDF document.")
                    
                    # Try to find page references
                    page_prompt = f"""Which page(s) in the document contain information about: '{question}'?
Analyze the content and list relevant page numbers.

Document pages:
{json.dumps([{"page": p["page"], "preview": p["text"][:200]} for p in current_session['pdf_content'][:10]])}

Return only page numbers as a comma-separated list, or 'unknown' if unclear."""
                    page_response = call_llm(page_prompt, "Extract page numbers only.")
                    
                    if "unknown" not in page_response.lower():
                        st.caption(f"📄 Source: Page(s) {page_response}")
                    
                    current_session["chat_history"].append({"q": question, "a": answer})
    
    # Chat history
    if current_session["chat_history"]:
        st.divider()
        st.subheader("📜 Recent Questions")
        for i, chat in enumerate(reversed(current_session["chat_history"][-3:]), 1):
            with st.expander(f"{i}. {chat['q'][:50]}..."):
                st.write(chat['a'][:200] + "...")

with tab2:
    st.header("📚 Deep Study Mode")
    
    # Topic selection
    col1, col2 = st.columns([3, 1])
    with col1:
        new_topic = st.text_input("Enter a biotechnology topic to study:")
    with col2:
        if st.button("Start Studying"):
            if new_topic:
                with st.spinner("Validating topic..."):
                    validation_prompt = f"""Is '{new_topic}' a topic related to biotechnology?

Biotechnology includes: molecular biology, genetics, cell biology, microbiology, bioengineering, biochemistry, genetic engineering, biomedical applications, agricultural biotechnology, industrial biotechnology.

Answer ONLY 'yes' or 'no'."""
                    validation_response = call_llm(validation_prompt, "You are a biotechnology topic classifier. Answer only 'yes' or 'no'.")
                    
                    if "no" in validation_response.lower():
                        st.error("⚠️ This topic is not related to biotechnology. Please enter a biotechnology topic.")
                    else:
                        current_session["current_study_topic"] = new_topic
                        current_session["study_conversation"] = []
                        
                        if new_topic not in current_session["topic_history"]:
                            current_session["topic_history"][new_topic] = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "conversations": [],
                                "quizzes": []
                            }
                        st.rerun()
    
    # Current topic display
    if current_session["current_study_topic"]:
        topic = current_session["current_study_topic"]
        st.markdown(f"### 🎯 Current Topic: **{topic}**")
        
        # Show topic info
        if topic in current_session["topic_history"]:
            data = current_session["topic_history"][topic]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Started", data.get("timestamp", "N/A"))
            with col2:
                perf = current_session["topic_performance"].get(topic, None)
                if perf is not None:
                    if perf < 50:
                        st.metric("Performance", f"{perf:.0f}%", delta="Poor", delta_color="off")
                    elif perf < 70:
                        st.metric("Performance", f"{perf:.0f}%", delta="Average", delta_color="off")
                    else:
                        st.metric("Performance", f"{perf:.0f}%", delta="Good", delta_color="normal")
                else:
                    st.metric("Performance", "No quiz taken")
            with col3:
                quiz_count = len([q for q in current_session["quiz_scores"] if q["topic"] == topic])
                st.metric("Quizzes Taken", quiz_count)
        
        st.divider()
        
        # Detailed explanation
        st.subheader("📖 Topic Overview")
        if st.button("Generate Detailed Explanation", key="gen_explanation"):
            with st.spinner("Generating comprehensive explanation..."):
                # Double-check topic is biotech-related
                validation_prompt = f"""Is '{topic}' a topic related to biotechnology? Answer ONLY 'yes' or 'no'."""
                validation_response = call_llm(validation_prompt, "You are a biotechnology topic classifier. Answer only 'yes' or 'no'.")
                
                if "no" in validation_response.lower():
                    st.error("⚠️ This topic is not related to biotechnology. Please enter a biotechnology topic.")
                else:
                    explain_prompt = f"""Provide a comprehensive, detailed explanation of '{topic}' STRICTLY from a biotechnology perspective.

Include:
1. **Introduction**: What is {topic}? (2-3 paragraphs)
2. **Key Concepts**: Main principles and mechanisms (4-5 points with details)
3. **Biological Significance**: Why is this important in biotechnology?
4. **Real-World Applications**: Practical uses and examples in biotechnology (3-4 applications)
5. **Current Research**: Recent developments or future directions in biotechnology
6. **Common Misconceptions**: What students often get wrong

IMPORTANT: Focus ONLY on biotechnology aspects. Do not drift into unrelated subjects. Make it detailed, student-friendly, and comprehensive for deep learning."""
                    explanation = call_llm(explain_prompt, "You are a biotechnology expert. Explain ONLY biotechnology-related aspects.")
                    st.markdown(explanation)
                    
                    if topic in current_session["topic_history"]:
                        current_session["topic_history"][topic]["explanation"] = explanation
        
        if topic in current_session["topic_history"] and "explanation" in current_session["topic_history"][topic]:
            with st.expander("📚 View Saved Explanation", expanded=True):
                st.markdown(current_session["topic_history"][topic]["explanation"])
        
        st.divider()
        
        # Learning resources
        with st.expander("🔗 Additional Learning Resources", expanded=False):
            with st.spinner("Fetching resources..."):
                resource_prompt = f"""For the biotechnology topic '{topic}', suggest 5 high-quality learning resources.
Return ONLY valid JSON:
{{
  "resources": [
    {{"title": "Resource name", "url": "https://example.com", "description": "Brief description", "type": "Website/Video/Article"}}
  ]
}}
Use reputable sources: Khan Academy, Nature Education, NCBI, MIT OCW, university websites, YouTube lectures."""
                resource_response = call_llm(resource_prompt)
                
                try:
                    start = resource_response.find('{')
                    end = resource_response.rfind('}') + 1
                    resource_json = resource_response[start:end]
                    resources = json.loads(resource_json)["resources"]
                    
                    for res in resources:
                        st.markdown(f"**[{res['title']}]({res['url']})** ({res.get('type', 'Resource')})")
                        st.write(res['description'])
                        st.write("")
                except:
                    st.write("Could not load resources. Try again.")
        
        # Interactive Q&A
        st.subheader("💬 Ask Questions")
        question = st.text_input("Ask anything about this topic:", key="study_question")
        
        if st.button("Ask", key="ask_study"):
            if question:
                with st.spinner("Thinking..."):
                    context = "\n".join([f"Q: {c['q']}\nA: {c['a']}" for c in current_session["study_conversation"][-3:]])
                    prompt = f"""You are teaching about '{topic}' in biotechnology.

Previous conversation:
{context}

Student question: {question}

Provide a clear, student-friendly answer focused STRICTLY on biotechnology aspects. Assume the question is about the current topic unless specified otherwise. Do not provide general-purpose answers unrelated to biotechnology."""
                    answer = call_llm(prompt, "You are a biotechnology tutor. Answer ONLY biotechnology-related questions.")
                    current_session["study_conversation"].append({"q": question, "a": answer})
                    
                    if topic in current_session["topic_history"]:
                        current_session["topic_history"][topic]["conversations"] = current_session["study_conversation"]
                    
                    st.rerun()
        
        if current_session["study_conversation"]:
            st.divider()
            st.subheader("📝 Previous Explanations")
            for i, conv in enumerate(current_session["study_conversation"]):
                with st.expander(f"Q{i+1}: {conv['q'][:50]}..."):
                    st.markdown(f"**Question:** {conv['q']}")
                    st.markdown(f"**Answer:** {conv['a']}")
        
        st.divider()
        
        past_quizzes = [q for q in current_session["quiz_scores"] if q["topic"] == topic]
        if past_quizzes:
            st.subheader("📊 Past Quiz Results")
            for i, quiz in enumerate(past_quizzes, 1):
                perf = (quiz["score"] / quiz["total"]) * 100
                if perf < 50:
                    st.error(f"Quiz {i}: {quiz['score']}/{quiz['total']} ({perf:.0f}%) - {quiz.get('difficulty', 'N/A')} - Poor")
                elif perf < 70:
                    st.warning(f"Quiz {i}: {quiz['score']}/{quiz['total']} ({perf:.0f}%) - {quiz.get('difficulty', 'N/A')} - Average")
                else:
                    st.success(f"Quiz {i}: {quiz['score']}/{quiz['total']} ({perf:.0f}%) - {quiz.get('difficulty', 'N/A')} - Good")
        
        # Quiz section
        st.subheader("📝 Take a Quiz")
        
        col1, col2 = st.columns(2)
        with col1:
            quiz_difficulty = st.selectbox("Difficulty:", ["Easy", "Intermediate", "Hard"], key="study_quiz_diff")
        with col2:
            num_questions = st.selectbox("Number of Questions:", [3, 5, 7], index=1)
        
        if st.button("Generate Quiz", key="gen_study_quiz"):
            with st.spinner("Creating quiz..."):
                if quiz_difficulty == "Easy":
                    instructions = "Focus on basic definitions, simple facts, and foundational concepts."
                elif quiz_difficulty == "Intermediate":
                    instructions = "Focus on conceptual understanding, mechanisms, and applications."
                else:
                    instructions = "Focus on advanced concepts, analytical scenarios, and higher-order thinking."
                
                prompt = f"""Generate a {quiz_difficulty} difficulty quiz on '{topic}' with {num_questions} multiple-choice questions.
{instructions}

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct": 0,
      "explanation": "Brief explanation"
    }}
  ]
}}

Make sure questions are DIFFERENT from other difficulty levels and appropriate for {quiz_difficulty} level."""
                response = call_llm(prompt)
                quiz_generated = False
                try:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    quiz_json = response[start:end]
                    current_session["quiz_data"] = json.loads(quiz_json)
                    current_session["user_answers"] = {}
                    quiz_generated = True
                except:
                    pass
                
                if quiz_generated:
                    st.rerun()
                else:
                    st.error("Failed to generate quiz. Try again.")
        
        if current_session["quiz_data"]:
            st.divider()
            questions = current_session["quiz_data"]["questions"]
            
            for i, q in enumerate(questions):
                st.write(f"**Question {i+1}:** {q['question']}")
                answer = st.radio(
                    "Select:",
                    options=q["options"],
                    key=f"study_q_{i}",
                    index=None
                )
                if answer:
                    current_session["user_answers"][i] = q["options"].index(answer)
                st.write("")
            
            if st.button("Submit Quiz", key="submit_study_quiz"):
                if len(current_session["user_answers"]) == len(questions):
                    score = sum(1 for i, ans in current_session["user_answers"].items() if ans == questions[i]["correct"])
                    percentage = (score / len(questions)) * 100
                    
                    # Color coding
                    if percentage < 50:
                        st.error(f"Score: {score}/{len(questions)} ({percentage:.0f}%) - Poor")
                    elif percentage < 70:
                        st.warning(f"Score: {score}/{len(questions)} ({percentage:.0f}%) - Average")
                    else:
                        st.success(f"Score: {score}/{len(questions)} ({percentage:.0f}%) - Good")
                    
                    st.subheader("Results")
                    for i, q in enumerate(questions):
                        user_ans = current_session["user_answers"].get(i)
                        correct = q["correct"]
                        if user_ans == correct:
                            st.write(f"✅ Q{i+1}: Correct!")
                        else:
                            st.write(f"❌ Q{i+1}: Wrong. Correct: {q['options'][correct]}")
                        st.write(f"💡 {q['explanation']}")
                        st.write("")
                    
                    current_session["topic_performance"][topic] = percentage
                    current_session["quiz_scores"].append({
                        "topic": topic,
                        "score": score,
                        "total": len(questions),
                        "difficulty": quiz_difficulty
                    })
                    
                    if st.button("Retake Quiz"):
                        current_session["quiz_data"] = None
                        current_session["user_answers"] = {}
                        st.rerun()
                else:
                    st.warning("Please answer all questions!")
    else:
        st.info("👆 Enter a topic above to start your deep study session!")

with tab3:
    st.header("Quiz & Assessment")
    
    quiz_topic = st.text_input("Topic for quiz:", key="quiz_topic")
    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.radio("Difficulty:", ["Easy", "Medium", "Hard"], horizontal=True)
    with col2:
        quiz_type = st.selectbox("Quiz Type:", ["Multiple Choice", "True/False", "Fill in the Blank", "Mixed"])
    
    if st.button("Generate Quiz"):
        if quiz_topic:
            with st.spinner("Creating quiz..."):
                if quiz_type == "Multiple Choice":
                    prompt = f"""Generate a {difficulty} quiz on '{quiz_topic}' with 5 multiple-choice questions.
Return ONLY valid JSON:
{{
  "questions": [
    {{
      "type": "mcq",
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct": 0,
      "explanation": "Brief explanation"
    }}
  ]
}}"""
                elif quiz_type == "True/False":
                    prompt = f"""Generate a {difficulty} quiz on '{quiz_topic}' with 5 true/false questions.
Return ONLY valid JSON:
{{
  "questions": [
    {{
      "type": "tf",
      "question": "Statement here",
      "correct": "True",
      "explanation": "Brief explanation"
    }}
  ]
}}"""
                elif quiz_type == "Fill in the Blank":
                    prompt = f"""Generate a {difficulty} quiz on '{quiz_topic}' with 5 fill-in-the-blank questions.
Return ONLY valid JSON:
{{
  "questions": [
    {{
      "type": "fill",
      "question": "Question with _____ blank",
      "correct": "answer",
      "explanation": "Brief explanation"
    }}
  ]
}}"""
                else:  # Mixed
                    prompt = f"""Generate a {difficulty} mixed quiz on '{quiz_topic}' with 5 questions (mix of MCQ, True/False, Fill-in-blank).
Return ONLY valid JSON:
{{
  "questions": [
    {{
      "type": "mcq",
      "question": "Question?",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "explanation": "Explanation"
    }},
    {{
      "type": "tf",
      "question": "Statement",
      "correct": "True",
      "explanation": "Explanation"
    }},
    {{
      "type": "fill",
      "question": "Question with _____",
      "correct": "answer",
      "explanation": "Explanation"
    }}
  ]
}}"""
                
                response = call_llm(prompt)
                quiz_generated = False
                try:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    quiz_json = response[start:end]
                    current_session["quiz_data"] = json.loads(quiz_json)
                    current_session["user_answers"] = {}
                    quiz_generated = True
                except:
                    pass
                
                if quiz_generated:
                    st.rerun()
                else:
                    st.error("Failed to generate quiz. Try again.")
    
    if current_session["quiz_data"]:
        st.divider()
        questions = current_session["quiz_data"]["questions"]
        
        for i, q in enumerate(questions):
            st.subheader(f"Question {i+1}")
            
            q_type = q.get("type", "mcq")
            
            if q_type == "mcq":
                st.write(q["question"])
                answer = st.radio(
                    "Select your answer:",
                    options=q["options"],
                    key=f"q_{i}",
                    index=None
                )
                if answer:
                    current_session["user_answers"][i] = q["options"].index(answer)
            
            elif q_type == "tf":
                st.write(q["question"])
                answer = st.radio(
                    "Select:",
                    options=["True", "False"],
                    key=f"q_{i}",
                    index=None
                )
                if answer:
                    current_session["user_answers"][i] = answer
            
            elif q_type == "fill":
                st.write(q["question"])
                answer = st.text_input("Your answer:", key=f"q_{i}")
                if answer:
                    current_session["user_answers"][i] = answer.strip().lower()
        
        if st.button("Submit Quiz"):
            if len(current_session["user_answers"]) == len(questions):
                score = 0
                for i, q in enumerate(questions):
                    user_ans = current_session["user_answers"].get(i)
                    q_type = q.get("type", "mcq")
                    
                    if q_type == "mcq":
                        if user_ans == q["correct"]:
                            score += 1
                    elif q_type == "tf":
                        if user_ans == q["correct"]:
                            score += 1
                    elif q_type == "fill":
                        if user_ans == q["correct"].lower():
                            score += 1
                
                st.success(f"Score: {score}/{len(questions)}")
                
                st.subheader("Results")
                for i, q in enumerate(questions):
                    user_ans = current_session["user_answers"].get(i)
                    q_type = q.get("type", "mcq")
                    
                    if q_type == "mcq":
                        correct = q["correct"]
                        if user_ans == correct:
                            st.write(f"✅ Q{i+1}: Correct!")
                        else:
                            st.write(f"❌ Q{i+1}: Wrong. Correct answer: {q['options'][correct]}")
                    elif q_type == "tf":
                        if user_ans == q["correct"]:
                            st.write(f"✅ Q{i+1}: Correct!")
                        else:
                            st.write(f"❌ Q{i+1}: Wrong. Correct answer: {q['correct']}")
                    elif q_type == "fill":
                        if user_ans == q["correct"].lower():
                            st.write(f"✅ Q{i+1}: Correct!")
                        else:
                            st.write(f"❌ Q{i+1}: Wrong. Correct answer: {q['correct']}")
                    
                    st.write(f"💡 {q['explanation']}")
                    st.divider()
                
                current_session["quiz_scores"].append({"topic": quiz_topic, "score": score, "total": len(questions)})
                
                percentage = (score / len(questions)) * 100
                current_session["topic_performance"][quiz_topic] = percentage
                
                current_session["quiz_data"] = None
            else:
                st.warning("Please answer all questions!")

with tab4:
    st.header("Personalized Learning Path")
    
    studied_topics = list(current_session["topic_history"].keys())
    
    if studied_topics:
        st.subheader("📚 Studied in this session:")
        for i, topic in enumerate(studied_topics, 1):
            perf = current_session["topic_performance"].get(topic, None)
            if perf is not None:
                if perf >= 70:
                    st.write(f"{i}. **{topic}** - 🟢 {perf:.0f}%")
                elif perf >= 50:
                    st.write(f"{i}. **{topic}** - 🟡 {perf:.0f}%")
                else:
                    st.write(f"{i}. **{topic}** - 🔴 {perf:.0f}%")
            else:
                st.write(f"{i}. **{topic}** - ⚪ No quiz")
        
        st.divider()
        
        if st.button("🔄 Get Suggested Next Topics"):
            with st.spinner("Analyzing learning path..."):
                topics_list = ", ".join(studied_topics)
                prompt = f"""Based on these biotechnology topics studied in order: {topics_list}

Suggest 3-5 logically connected next topics based on prerequisite relationships and natural progression.

Return as a simple numbered list (e.g., 1. Topic Name).

Ensure suggestions are:
- Directly related to studied topics
- Follow logical prerequisites
- Progress in complexity
- Avoid generic unrelated topics"""
                suggestions = call_llm(prompt, "You are a biotechnology curriculum expert.")
                
                st.subheader("🎯 Suggested next topics:")
                st.markdown(suggestions)
    else:
        st.info("⚠️ No learning data available for this session. Start studying topics in the Deep Study tab to build your personalized learning path.")

with tab5:
    st.header("Feedback Analytics Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Modules Completed", len(current_session["learning_path"]))
    
    with col2:
        st.metric("Quizzes Taken", len(current_session["quiz_scores"]))
    
    with col3:
        if current_session["quiz_scores"]:
            total_questions = sum(q["total"] for q in current_session["quiz_scores"])
            total_correct = sum(q["score"] for q in current_session["quiz_scores"])
            avg_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
            st.metric("Average Score", f"{avg_percentage:.0f}%")
        else:
            st.metric("Average Score", "N/A")
    
    if current_session["quiz_scores"]:
        st.subheader("Quiz Performance")
        for q in current_session["quiz_scores"]:
            percentage = (q["score"] / q["total"]) * 100
            st.write(f"**{q['topic']}**: {q['score']}/{q['total']} ({percentage:.0f}%)")
    
    st.divider()
    
    if st.button("Get Personalized Feedback"):
        if current_session["learning_path"] or current_session["quiz_scores"]:
            with st.spinner("Analyzing your performance..."):
                data = f"""Learning path: {current_session['learning_path']}
Quiz scores: {current_session['quiz_scores']}"""
                prompt = f"""Analyze this student's biotechnology learning data:
{data}

Provide:
1. Strengths (2-3 points)
2. Areas for improvement (2-3 points)
3. Specific recommendations (3 actionable tips)"""
                feedback = call_llm(prompt)
                st.markdown(feedback)
        else:
            st.warning("Complete some modules and quizzes first!")

with tab6:
    st.header("About This Platform")
    st.markdown("""
    ### Features:
    - **💬 PDF-Grounded AI**: Ask questions strictly from uploaded documents
    - **📚 Deep Study Mode**: Topic-focused learning with resources, Q&A, and quizzes
    - **📝 Varied Quizzes**: MCQ, True/False, Fill-in-blank, Mixed types
    - **🎯 Learning Path**: Track studied topics and performance
    - **📊 Analytics**: View progress and get personalized feedback
    
    ### Deep Study Features:
    - Unlimited follow-up questions
    - Contextual conversation
    - Difficulty-based quizzes (Easy/Intermediate/Hard)
    - Performance tracking with color coding
    - Retake quizzes for improvement
    - High-quality learning resources
    """)
