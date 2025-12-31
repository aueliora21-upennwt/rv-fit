import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from openai import OpenAI
import os

# --- 1. 頁面設定 (這裡絕對是 centered) ---
st.set_page_config(page_title="94 Line Fit", page_icon="🐻💙", layout="centered")

# --- 2. 94 Line 專屬配色 CSS ---
st.markdown("""
    <style>
    /* 全局背景 */
    .stApp {
        background-color: #FFFDF5;
    }
    
    /* 標題顏色 */
    h1 {
        color: #273c75 !important;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* 輸入框優化 */
    .stNumberInput input {
        background-color: #FFFFFF;
        color: #273c75;
    }
    
    /* 按鈕漸層色 */
    .stButton>button {
        background: linear-gradient(90deg, #fbc531 0%, #487eb0 100%);
        color: white;
        border: none;
        border-radius: 25px;
        height: 50px;
        font-weight: bold;
        font-size: 18px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 資料處理 ---
DATA_FILE = 'rv_log.csv'

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Date", "Morning_Weight", "Evening_Weight", "Exercise", "AI_Comment"])
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --- 4. 介面開始 ---
st.title("🐻 94 Line Fit 🐿️")

# --- 區塊 A: 輸入資料 ---
with st.container():
    st.markdown("### 📝 Log Today")
    date_input = st.date_input("日期", datetime.now())
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**☀️ Morning (Seulgi)**")
        w_morning = st.number_input("早晨空腹 (kg)", min_value=0.0, step=0.1, key="morning")
    with col2:
        st.markdown("**🌙 Evening (Wendy)**")
        w_evening = st.number_input("晚間睡前 (kg)", min_value=0.0, step=0.1, key="evening")
    
    exercise_log = st.text_area("🏃‍♀️ Workout", placeholder="Wendy: 今天動了沒？Let's burn it!")
    
    if st.button("Save Record"):
        new_entry = {
            "Date": str(date_input),
            "Morning_Weight": w_morning,
            "Evening_Weight": w_evening,
            "Exercise": exercise_log,
            "AI_Comment": ""
        }
        df = df[df['Date'] != str(date_input)]
        df = pd.concat([pd.DataFrame([new_entry]), df], ignore_index=True)
        df = df.sort_values(by="Date")
        save_data(df)
        st.balloons()
        st.success("紀錄完成！Happiness!")

# --- 區塊 B: 圖表分析 ---
if not df.empty:
    st.markdown("### 📊 Trends")
    chart_df = df.tail(30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_df['Date'], y=chart_df['Morning_Weight'],
        mode='lines+markers', name='Seulgi (早)',
        line=dict(color='#fbc531', width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=chart_df['Date'], y=chart_df['Evening_Weight'],
        mode='lines+markers', name='Wendy (晚)',
        line=dict(color='#487eb0', width=3, dash='dot'),
        marker=dict(size=6, symbol='diamond')
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.5)',
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 區塊 C: AI 教練 ---
st.markdown("### 💬 94 Line Talk")

if st.button("召喚 Seulgi & Wendy"):
    if df.empty or df.iloc[-1]['Morning_Weight'] == 0:
        st.error("請先輸入今天的數據喔！")
    else:
        # 檢查是否有 API Key
        if "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            client = OpenAI(api_key=api_key)
            
            latest = df.iloc[-1]
            prompt = f"""
            你現在要同時扮演 Red Velvet 的 Seulgi (瑟琪) 和 Wendy (溫蒂)。
            資料：早晨 {latest['Morning_Weight']}kg, 晚間 {latest['Evening_Weight']}kg, 運動: {latest['Exercise']}
            
            請給一個 1-100 的評分，並讓兩人進行簡短對話建議。
            Seulgi (🐻): 語氣呆萌溫暖 (#e1b12c)。
            Wendy (🐿️): 語氣High tension嚴格 (#273c75)。
            """
            
            with st.spinner("Seulgi 正在畫畫... Wendy 正在熱身..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"AI 連線錯誤: {e}")
        else:
            st.warning("⚠️ 請記得在 Streamlit 設定 Secrets 輸入 OPENAI_API_KEY")
