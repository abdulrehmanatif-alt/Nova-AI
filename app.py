# =====================================
# IMPORTS
# =====================================

import os
import json
import time
import streamlit as st
from groq import Groq

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# =====================================
# LOAD SECRET (HUGGING FACE)
# =====================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Missing Hugging Face Secret: GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# =====================================
# SYSTEM PROMPT
# =====================================

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Nova AI, a futuristic helpful assistant. "
        "Always respond clearly using headings, bullet points, "
        "and short readable paragraphs."
    )
}

# =====================================
# STREAMLIT CONFIG
# =====================================

st.set_page_config(
    page_title="Nova AI",
    page_icon="🤖",
    layout="centered"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>
/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
}
/* Main title */
h1 {
    text-align: center;
    font-size: 3rem !important;
    font-weight: 800 !important;
    color: white !important;
}
/* Chat bubbles */
[data-testid="stChatMessage"] {
    border-radius: 20px;
    padding: 14px;
    margin-bottom: 12px;
}
/* User bubble */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background: rgba(59,130,246,0.18);
    border: 1px solid rgba(59,130,246,0.4);
}
/* Assistant bubble */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
}
/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(17,24,39,0.95);
}
/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: none;
    padding: 10px;
    font-weight: bold;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
}
/* Download button */
.stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    border: none;
    padding: 10px;
    font-weight: bold;
    background: linear-gradient(90deg, #10b981, #059669);
    color: white;
}
/* CHAT INPUT */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 20px;
    /* sidebar compensation */
    left: calc(50% + 140px);
    transform: translateX(-50%);
    width: min(850px, calc(100% - 350px));
    z-index: 999999;
}
/* Input container */
[data-testid="stChatInput"] > div {
    border-radius: 20px !important;
    background: rgba(17,24,39,0.96) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    box-shadow: 0 0 20px rgba(0,0,0,0.35);
}
/* Text */
[data-testid="stChatInput"] textarea {
    color: white !important;
    font-size: 16px !important;
}
/* Bottom spacing */
.main .block-container {
    padding-bottom: 140px;
}
/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# PDF EXPORT
# =====================================

def create_pdf(messages, filename="chat.pdf"):

    c = canvas.Canvas(filename, pagesize=letter)

    width, height = letter

    y = height - 40

    for msg in messages:

        text = f"{msg['role'].upper()}: {msg['content']}"

        while len(text) > 90:

            c.drawString(30, y, text[:90])

            text = text[90:]

            y -= 15

            if y < 40:
                c.showPage()
                y = height - 40

        c.drawString(30, y, text)

        y -= 20

        if y < 40:
            c.showPage()
            y = height - 40

    c.save()

# =====================================
# MEMORY
# =====================================

if "messages" not in st.session_state:

    try:
        with open("chat_history.json", "r") as f:
            st.session_state.messages = json.load(f)

    except:
        st.session_state.messages = []

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("⚙️ Settings")

    model = st.selectbox(
        "Model",
        [
            "llama-3.3-70b-versatile",
            "deepseek-r1-distill-llama-70b",
            "mixtral-8x7b-32768"
        ]
    )

    st.markdown("---")

    st.subheader("📜 History")

    if st.session_state.messages:

        for m in st.session_state.messages[-10:]:

            role = "You" if m["role"] == "user" else "Nova"

            st.write(f"**{role}:** {m['content'][:60]}...")

    st.markdown("---")

    # TXT EXPORT
    if st.session_state.messages:

        chat_text = ""

        for m in st.session_state.messages:
            chat_text += f"{m['role'].upper()}: {m['content']}\\n\\n"

        st.download_button(
            "📥 Export TXT",
            chat_text,
            file_name="chat_history.txt"
        )

    # PDF EXPORT
    if st.button("📄 Generate PDF"):

        create_pdf(st.session_state.messages)

    try:

        with open("chat.pdf", "rb") as f:

            st.download_button(
                "⬇️ Download PDF",
                f,
                file_name="chat.pdf"
            )

    except:
        pass

    # CLEAR CHAT
    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        with open("chat_history.json", "w") as f:
            json.dump([], f)

        st.rerun()

# =====================================
# TITLE
# =====================================

st.markdown(
    "<h1>🤖 Nova AI</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='text-align:center;color:#cbd5e1;font-size:18px;'>
    Your futuristic AI assistant!
    </p>
    """,
    unsafe_allow_html=True
)

# =====================================
# CHAT DISPLAY
# =====================================

for msg in st.session_state.messages:

    avatar = "👤" if msg["role"] == "user" else "🤖"

    with st.chat_message(msg["role"], avatar=avatar):

        st.markdown(msg["content"])

# =====================================
# CHAT INPUT
# =====================================

user_input = st.chat_input("Ask Nova AI anything...")

# =====================================
# RATE LIMIT
# =====================================

if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

# =====================================
# PROCESS INPUT
# =====================================

if user_input:

    current_time = time.time()

    if current_time - st.session_state.last_message_time < 1:
        st.warning("⏳ Please wait before sending another message.")
        st.stop()

    st.session_state.last_message_time = current_time

    # SAVE USER MESSAGE
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user", avatar="👤"):

        st.markdown(user_input)

    # AI RESPONSE
    with st.spinner("Thinking..."):

        try:

            messages = [SYSTEM_PROMPT] + st.session_state.messages

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )

            bot_reply = ""

            with st.chat_message("assistant", avatar="🤖"):

                placeholder = st.empty()

                for chunk in response:

                    if chunk.choices[0].delta.content:

                        bot_reply += chunk.choices[0].delta.content

                        placeholder.markdown(bot_reply + "▌")

                placeholder.markdown(bot_reply)

        except Exception as e:

            bot_reply = f"Error: {str(e)}"

            st.error(bot_reply)

    # SAVE AI MESSAGE
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })

    # SAVE HISTORY
    with open("chat_history.json", "w") as f:

        json.dump(st.session_state.messages, f)

# =====================================
# FOOTER
# =====================================

st.markdown(
    """
    <hr style="border:1px solid rgba(255,255,255,0.1)">
    <p style="text-align:center;color:gray;">
    Nova AI
    </p>
    """,
    unsafe_allow_html=True
)
