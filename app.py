import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from openai import OpenAI
import os

# --- 1. 頁面設定 ---
st.set_page_config(page_title="94 Line Fit", page_icon="🐻💙", layout="mobile")

# --- 2. 94 Line 專屬配色 CSS ---
st.markdown("""
    <style>
    /* 全局背景：淡淡的奶油色，很像 Seulgi 的氛圍 */
    .stApp {
        background-color: #FFFDF5;
    }
    
    /* 標題顏色：Wendy 的寶藍色 */
    h1 {
        color: #273c75 !important;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* 副標題：Seulgi 的橘色 */
    h3 {
        color: #e1b12c !important;
    }

    /* 輸入框與卡片優化 */
    .stNumberInput input {
        background-color: #FFFFFF;
        color: #273c75;
    }
    
    /* 按鈕：漸層色 (Seulgi Orange to Wendy Blue) */
    .stButton>button {
        background: linear-gradient(90deg, #fbc531 0%, #487eb0 100%);
        color: white;
        border: none;
        border-radius: 25px;
        height: 50px;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 資料處理 (自動建立 CSV) ---
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
        # 簡單邏輯：若無數據則補 0，方便繪圖處理
        new_entry = {
            "Date": str(date_input),
            "Morning_Weight": w_morning,
            "Evening_Weight": w_evening,
            "Exercise": exercise_log,
            "AI_Comment": ""
        }
        # 覆蓋同日期的舊資料
        df = df[df['Date'] != str(date_input)]
        df = pd.concat([pd.DataFrame([new_entry]), df], ignore_index=True) # 新的放最上面
        df = df.sort_values(by="Date") # 排序
        save_data(df)
        st.balloons()
        st.success("紀錄完成！Good Job!")

# --- 區塊 B: 圖表分析 ---
if not df.empty:
    st.markdown("### 📊 Trends")
    
    # 這裡只取最近 30 天，避免圖表太長
    chart_df = df.tail(30)
    
    fig = go.Figure()
    
    # Seulgi 線 (橘黃色)
    fig.add_trace(go.Scatter(
        x=chart_df['Date'], y=chart_df['Morning_Weight'],
        mode='lines+markers', name='Seulgi (早)',
        line=dict(color='#fbc531', width=3),
        marker=dict(size=8)
    ))
    
    # Wendy 線 (深藍色)
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

# --- 區塊 C: AI 教練 (Seulgi & Wendy) ---
st.markdown("### 💬 94 Line Talk")

if st.button("召喚 Seulgi & Wendy 分析"):
    if df.empty or df.iloc[-1]['Morning_Weight'] == 0:
        st.error("請先輸入今天的體重喔！")
    else:
        latest = df.iloc[-1]
        
        # 這裡需要你的 OpenAI API Key
        # 在 Streamlit Cloud 的 Secrets 設定中加入 OPENAI_API_KEY
        api_key = st.secrets["OPENAI_API_KEY"] 
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        你現在要同時扮演 Red Velvet 的 Seulgi (瑟琪) 和 Wendy (溫蒂)。
        
        **資料：**
        - 早晨體重: {latest['Morning_Weight']}
        - 晚間體重: {latest['Evening_Weight']}
        - 運動: {latest['Exercise']}
        
        **請根據以上資料，進行一場簡短的對話給我建議：**
        
        1. **Seulgi (🐻):** 語氣呆萌、慢條斯理、像熊一樣溫暖。關注我的心情和線條。用色碼 #e1b12c 代表名字。
        2. **Wendy (🐿️):** 語氣High tension、中英夾雜、專業嚴格。關注我的飲食與代謝。用色碼 #273c75 代表名字。
        
        **格式要求：**
        給一個 1-100 的綜合評分。
        然後是兩人的對話內容 (用 HTML 格式稍微美化一下)。
        """
        
        with st.spinner("Wendy 正在看你的數據... Seulgi 正在畫圖..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                advice = response.choices[0].message.content
                st.markdown(advice, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"連線錯誤: {e}")
