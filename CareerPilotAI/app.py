import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import plotly.graph_objects as go
import google.generativeai as genai
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ==========================================
# 0. CONFIGURATION & PAGE SETUP
# ==========================================
st.set_page_config(
    page_title="CareerPilot Pro", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
   genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    chat_model = genai.GenerativeModel('gemini-1.5-flash')
    chat_available = True
except:
    chat_available = False

# ==========================================
# 1. CUSTOM CSS (THE UI MAGIC)
# ==========================================
st.markdown("""
    <style>
    /* 1. Background Image */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1497633762265-9d179a990aa6?q=80&w=2073&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 2. Glassmorphism Containers */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* 3. Title Styling */
    h1 {
        color: #FFFFFF;
        text-shadow: 2px 2px 4px #000000;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
    }
    
    p {
        color: #1f1f1f;
        font-size: 1.1rem;
    }

    /* 4. Floating Buttons */
    div.stButton > button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        font-size: 18px;
        border-radius: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        transition: all 0.3s ease; 
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 25px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #2575fc 0%, #6a11cb 100%);
        color: white;
    }

    /* 5. Inputs & Checkboxes */
    .stNumberInput, .stSelectbox, .stSlider {
        background-color: transparent;
    }
    
    /* 6. Chat Messages */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA & MODEL (Same Logic)
# ==========================================
CAREER_DATA = {
    "Science (PCM)": {
        "roles": [
            {"title": "Software Engineer", "start": 6, "mid": 18, "senior": 35},
            {"title": "Data Scientist", "start": 8, "mid": 22, "senior": 45},
            {"title": "Civil/Mech Engineer", "start": 4.5, "mid": 12, "senior": 25},
        ],
        "colleges": [
            {"name": "IIT Bombay (CSE)", "exam": "JEE Advanced", "cutoff": "Rank < 60", "fees": "10L"},
            {"name": "NIT Trichy", "exam": "JEE Mains", "cutoff": "99.5 %ile", "fees": "6L"},
            {"name": "BITS Pilani", "exam": "BITSAT", "cutoff": "Score > 320", "fees": "24L"},
        ],
        "masters": {"degree": "M.Tech", "exam": "GATE", "top_colleges": ["IIT Madras", "IISc Bangalore"], "cutoff_note": "GATE Score > 750"}
    },
    "Science (PCB)": {
        "roles": [
            {"title": "Doctor (MBBS)", "start": 7, "mid": 18, "senior": 40},
            {"title": "Surgeon (MS/MD)", "start": 12, "mid": 35, "senior": 80},
        ],
        "colleges": [
            {"name": "AIIMS Delhi", "exam": "NEET UG", "cutoff": "Rank < 50", "fees": "5K"},
            {"name": "CMC Vellore", "exam": "NEET UG", "cutoff": "Top 1%", "fees": "2L"},
        ],
        "masters": {"degree": "MD / MS", "exam": "NEET PG", "top_colleges": ["AIIMS", "PGI Chandigarh"], "cutoff_note": "Top 500 Rank"}
    },
    "Commerce (CA Track)": {
        "roles": [
            {"title": "Chartered Accountant", "start": 9, "mid": 24, "senior": 60},
            {"title": "CFO", "start": 15, "mid": 50, "senior": 150},
        ],
        "colleges": [
            {"name": "ICAI (The Institute)", "exam": "CA Foundation", "cutoff": "Pass (>50%)", "fees": "70K (Course)"},
            {"name": "Articleship", "exam": "Interview", "cutoff": "Inter Group 1", "fees": "Earn Stipend"},
        ],
        "masters": {"degree": "CFA / CPA", "exam": "CFA Level 1-3", "top_colleges": ["CFA Institute USA"], "cutoff_note": "Global Cert"}
    },
    "Commerce (General)": {
        "roles": [
            {"title": "Investment Banker", "start": 12, "mid": 30, "senior": 80},
            {"title": "Marketing Manager", "start": 5, "mid": 15, "senior": 35},
        ],
        "colleges": [
            {"name": "SRCC Delhi", "exam": "CUET", "cutoff": "780/800", "fees": "60K"},
            {"name": "NMIMS Mumbai", "exam": "NPAT", "cutoff": "Top 500", "fees": "12L"},
        ],
        "masters": {"degree": "MBA", "exam": "CAT", "top_colleges": ["IIM Ahmedabad", "IIM Bangalore"], "cutoff_note": "CAT > 99%ile"}
    },
    "Arts/Humanities": {
        "roles": [
            {"title": "Corporate Lawyer", "start": 7, "mid": 20, "senior": 60},
            {"title": "Civil Servant (IAS)", "start": 7, "mid": 15, "senior": "Govt Scale"},
        ],
        "colleges": [
            {"name": "St. Stephens Delhi", "exam": "CUET", "cutoff": "750/800", "fees": "1L"},
            {"name": "NLSIU Bangalore", "exam": "CLAT", "cutoff": "Rank < 80", "fees": "12L"},
        ],
        "masters": {"degree": "MA / LLM", "exam": "UGC-NET", "top_colleges": ["JNU", "NALSAR"], "cutoff_note": "Entrance Based"}
    }
}

@st.cache_data
def load_model():
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        'math': np.random.randint(40, 100, n),
        'science': np.random.randint(40, 100, n),
        'history': np.random.randint(40, 100, n),
        'logic': np.random.randint(1, 10, n),
        'creative': np.random.randint(1, 10, n),
        'coding': np.random.choice([0, 1], n),
        'finance': np.random.choice([0, 1], n),
        'art': np.random.choice([0, 1], n)
    })
    conditions = [
        (df['math'] > 70) & (df['science'] > 70) & (df['coding'] == 1), 
        (df['science'] > 75) & (df['math'] > 60) & (df['coding'] == 0),
        (df['math'] > 65) & (df['finance'] == 1) & (df['logic'] > 6),
        (df['finance'] == 1) & (df['math'] < 65),
        (df['history'] > 60) & (df['art'] == 1)
    ]
    choices = ['Science (PCM)', 'Science (PCB)', 'Commerce (CA Track)', 'Commerce (General)', 'Arts/Humanities']
    df['stream'] = np.select(conditions, choices, default='Commerce (General)')
    
    X = df.drop('stream', axis=1)
    y = df['stream']
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    
    X_train, _, y_train, _ = train_test_split(X, y_enc, test_size=0.2)
    model = xgb.XGBClassifier(eval_metric='mlogloss')
    model.fit(X_train, y_train)
    return model, le

model, le = load_model()

# ==========================================
# 3. UI LAYOUT
# ==========================================

# Title Section with Shadow
st.markdown("<h1 style='text-align: center; font-size: 60px;'>🎓 CareerPilot Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; text-shadow: 1px 1px 2px black;'>AI-Powered Indian Education Roadmap & Counselor</p>", unsafe_allow_html=True)
st.write("") # Spacer

tab1, tab2 = st.tabs(["🤖 AI Stream Predictor", "📚 Career Explorer & Chatbot"])

# --- TAB 1: PREDICTOR ---
with tab1:
    st.header("Find Your Perfect Stream")
    st.write("Enter your details below to use the Machine Learning model.")
    
    # Input Cards using Columns
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.info("📚 **Academics**")
        math = st.number_input("Math Score (0-100)", 0, 100, 75)
        science = st.number_input("Science Score (0-100)", 0, 100, 75)
        history = st.number_input("Social Studies (0-100)", 0, 100, 60)
    
    with c2: 
        st.warning("🧠 **Aptitude**")
        logic = st.slider("Logical Ability (1-10)", 1, 10, 5)
        creative = st.slider("Creativity (1-10)", 1, 10, 5)
    
    with c3: 
        st.success("❤️ **Interests**")
        coding = st.checkbox("💻 Like Coding?")
        finance = st.checkbox("💰 Like Money/Accounts?")
        art = st.checkbox("🎨 Like Arts/Design?")
    
    st.markdown("---")
    
    # Center the button using columns
    col_space1, col_btn, col_space2 = st.columns([1, 2, 1])
    
    with col_btn:
        if st.button("🚀 Predict My Stream Now", type="primary"):
            input_data = pd.DataFrame([[math, science, history, logic, creative, int(coding), int(finance), int(art)]], 
                                      columns=['math', 'science', 'history', 'logic', 'creative', 'coding', 'finance', 'art'])
            pred_idx = model.predict(input_data)[0]
            pred_stream = le.inverse_transform([pred_idx])[0]
            
            # Result Card
            st.markdown(f"""
                <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745;">
                    <h2 style="color: #155724; margin:0;">🎉 Recommended: {pred_stream}</h2>
                    <p style="color: #155724;">Based on your inputs, this field aligns best with your potential.</p>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 2: EXPLORER + CHATBOT ---
with tab2:
    st.header("Explore & Ask")
    
    # Selection
    selected_stream = st.selectbox("Select a Field to Explore:", list(CAREER_DATA.keys()))
    data = CAREER_DATA[selected_stream]
    
    # Layout for data
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("🏛️ Colleges & Exams")
        st.table(pd.DataFrame(data['colleges']))
        
    with col_b:
        st.subheader("📈 Salary Growth (₹ LPA)")
        years = [0, 5, 10]
        fig = go.Figure()
        for role in data['roles']:
            salaries = [role['start'], role['mid'], role['senior']]
            fig.add_trace(go.Scatter(x=years, y=salaries, mode='lines+markers', name=role['title'], line_shape='spline'))
        
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Chatbot UI
    st.subheader("💬 AI Career Counselor")
    
    if not chat_available:
        st.error("⚠️ API Key missing. Please add your Google API Key in the code.")
    else:
        # Chat container styling
        chat_container = st.container()
        
        # Initialize
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({"role": "model", "parts": ["Hi! I'm your AI counselor. Ask me anything!"]})

        with chat_container:
            for msg in st.session_state.messages:
                role = "assistant" if msg["role"] == "model" else "user"
                with st.chat_message(role):
                    st.write(msg["parts"][0])

        if prompt := st.chat_input("Ask a question (e.g., 'Is CA tough?')"):
            st.session_state.messages.append({"role": "user", "parts": [prompt]})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        full_prompt = f"You are an expert Indian Career Counselor. Short answer for: {prompt}"
                        chat = chat_model.start_chat(history=st.session_state.messages[:-1])
                        response = chat.send_message(full_prompt)
                        st.write(response.text)
                        st.session_state.messages.append({"role": "model", "parts": [response.text]})
                    except Exception as e:
                        st.error("AI Error.")

