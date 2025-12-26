import streamlit as st
import google.generativeai as genai
import sqlite3

# --- CONFIGURATION ---
# Replace with your actual API Key from Google AI Studio
API_KEY = "AIzaSyBceVPdVbAQ7BC5VdGnU_1Qzpux3Jf1OJ4"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-flash-latest")

# --- DATABASE FUNCTIONS ---
def get_financials(stream_name):
    conn = sqlite3.connect('career.db')
    c = conn.cursor()
    c.execute("SELECT * FROM financials WHERE stream_name=?", (stream_name,))
    data = c.fetchone()
    conn.close()
    return data

def get_jobs(stream_name):
    conn = sqlite3.connect('career.db')
    c = conn.cursor()
    c.execute("SELECT role, avg_salary FROM jobs WHERE stream_name=?", (stream_name,))
    data = c.fetchall()
    conn.close()
    return data

# --- UI SETUP ---
st.set_page_config(page_title="CareerPath AI", page_icon="🎓")

st.title("🎓 CareerPath AI")
st.subheader("Find your perfect stream after 10th")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial greeting from the bot
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hi! I'm here to help you choose your stream. Tell me about your favorite subjects, hobbies, and what you hate studying!"
    })

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User Input
user_input = st.chat_input("Type here (e.g., 'I love math but hate history...')")

if user_input:
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. AI Processing (The "Brain")
    # We ask Gemini to analyze the chat and decide if it has enough info to recommend a stream.
    conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    
    prompt = f"""
    You are a career counselor. Read this conversation:
    {conversation_history}
    
    If the user has provided enough info (interests, dislikes), recommend ONE stream from: ['Science (PCM)', 'Commerce', 'Arts'].
    If not, ask a follow-up question.
    
    FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
    Status: [RECOMMEND or ASK]
    Content: [Your response text to the user]
    Stream: [Stream Name if Status is RECOMMEND, else None]
    """

    response = model.generate_content(prompt)
    text_response = response.text
    
    # Parse the AI response
    status = "ASK"
    reply_content = "I didn't understand that."
    recommended_stream = None

    try:
        lines = text_response.split('\n')
        for line in lines:
            if line.startswith("Status:"): status = line.split(":")[1].strip()
            if line.startswith("Content:"): reply_content = line.split("Content:")[1].strip()
            if line.startswith("Stream:"): recommended_stream = line.split(":")[1].strip()
    except:
        reply_content = response.text # Fallback

    # 3. Show AI Response
    st.session_state.messages.append({"role": "assistant", "content": reply_content})
    with st.chat_message("assistant"):
        st.write(reply_content)

    # 4. IF RECOMMENDATION IS MADE -> SHOW DASHBOARD
    if status == "RECOMMEND" and recommended_stream in ['Science (PCM)', 'Commerce', 'Arts']:
        st.divider()
        st.success(f"🎉 Final Recommendation: {recommended_stream}")
        
        # Fetch Data from SQLite
        fin_data = get_financials(recommended_stream)
        job_data = get_jobs(recommended_stream)

        if fin_data:
            # Create Columns for Layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("💰 Estimated Expenses")
                st.write(f"**11th-12th Coaching:** ₹{fin_data[1]:,}")
                st.write(f"**College (Total):** ₹{fin_data[2]:,} - ₹{fin_data[3]:,}")
                total_min = fin_data[1] + fin_data[2]
                st.metric(label="Min Investment Required", value=f"₹{total_min:,}")

            with col2:
                st.info("🚀 Career & Salary")
                for role, salary in job_data:
                    st.write(f"**{role}:** ~₹{salary:,}/year")
            
            st.warning("⚠️ Note: Fees vary by city and college rank.")