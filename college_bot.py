import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MEC Bot - Muthayammal Engineering College Assistant",
    page_icon="🎓",
    layout="centered"
)

# API key check (fail fast with a clear message instead of crashing on first query)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

client = Groq(api_key=api_key)

# Known facts about the college (kept short — used as grounding context for the model)
# Note: exact figures (dept count, intake, fees) vary across sources online.
# The bot is instructed to flag these as approximate and point to the official website.
COLLEGE_INFO = """
College: Muthayammal Engineering College (MEC), also known as Muthayammal College of Engineering
Location: Kakkaveri, Rasipuram, Namakkal District, Tamil Nadu - 637408 (~25 km from Salem)
Established: 2000, under Muthayammal Educational Trust and Research Foundation
Chairman: Shri R. Kandasamy
Affiliation: Anna University, Chennai
Approvals/Accreditation: AICTE approved, NBA and NAAC accredited, Autonomous institution
Programs: UG (B.E./B.Tech), PG (M.E., MBA, MCA), and Ph.D across multiple departments
Common departments: CSE, IT, ECE, EEE, Mechanical, Civil, Mechatronics, Structural Engineering, VLSI Design
Admissions: TNEA counselling for UG, TANCET for MBA/MCA/PG
Facilities: Library, hostel (boys & girls), gym, sports complex, cafeteria, ATM, placement cell
Placements: Recruiters have included companies like Infosys, Wipro, TCS, HDFC Bank, Tech Mahindra
Website: www.muthayammalengg.ac.in
"""

# System prompt — strictly scoped to this college only
SYSTEM_PROMPT = f"""You are MEC Bot, a friendly assistant that ONLY answers questions about
Muthayammal Engineering College (MEC), Rasipuram, Namakkal.

Reference information about the college (use this, but treat exact numeric details
like department count, seat intake, and fees as approximate since they vary by year):
{COLLEGE_INFO}

STRICT RULES:
- ONLY answer questions related to Muthayammal Engineering College (courses, admissions,
  departments, facilities, placements, campus life, location, history, contact info, etc.)
- If the user asks anything unrelated to this college (general knowledge, other colleges,
  coding help, personal advice, etc.), politely decline and say you can only help with
  questions about Muthayammal Engineering College.
- For exact/current details like latest fees, cutoff marks, exact seat count, or admission
  deadlines, tell the user these can change year to year and to confirm on the official
  website (www.muthayammalengg.ac.in) or by contacting the college office directly.
- Be warm, encouraging, and concise (2-3 short paragraphs max). Use bullet points for lists.
- Do not make up specific facts (like exact fee amounts or rankings) that aren't in your
  reference information above — say you're not fully sure and point to the official source.
"""

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# App header
st.title("🎓 MEC Bot")
st.caption("Ask me anything about Muthayammal Engineering College, Rasipuram")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about courses, admissions, campus, placements..."):
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Build messages for API call (system prompt + history)
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    api_messages.extend(st.session_state.messages[-20:])  # Last 10 exchanges (20 messages)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    temperature=0.5,
                    max_tokens=500
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = "Sorry, I'm having trouble connecting right now. Please try again in a moment."
                st.error(f"API error: {e}")
            st.write(reply)

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Sidebar
with st.sidebar:
    st.header("About MEC Bot")
    st.write(
        "MEC Bot answers questions **only about Muthayammal Engineering College** — "
        "courses, admissions, departments, facilities, and placements."
    )
    st.info(
        "For the latest fees, cutoffs, and admission dates, please check the official "
        "website: www.muthayammalengg.ac.in"
    )
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Messages: {len(st.session_state.messages)}")
