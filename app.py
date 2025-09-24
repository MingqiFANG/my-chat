import os
import streamlit as st
from google import genai

st.set_page_config(page_title="Stock Chat", page_icon="💬", layout="centered")

# 优先从 Streamlit Secrets 获取，其次读取环境变量
API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
if not API_KEY:
    st.error("未检测到 GEMINI_API_KEY。请在本地设置环境变量，或在 Streamlit Cloud 的 Secrets 里配置。")
    st.stop()

# 初始化 Gemini 客户端（google-genai）
client = genai.Client(api_key=API_KEY)

# --- 侧边栏设置 ---
st.sidebar.title("设置")
model = st.sidebar.selectbox("选择模型", ["gemini-2.5-flash"], index=0)
system_prompt = st.sidebar.text_area("系统提示（可选）", height=80, placeholder="你是一个中文助手...")

# --- 会话状态 ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{role:"user"|"assistant", content:str}]

st.title("Stock Chat")

# --- 展示历史消息 ---
for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"]=="user" else "assistant"):
        st.markdown(msg["content"])

# --- 输入并发送 ---
if prompt := st.chat_input("输入你的问题..."):
    # 先显示用户消息
    st.session_state.messages.append({"role":"user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 组装 contents（Gemini 的对话格式）
    contents = []
    if system_prompt:
        contents.append({"role":"user", "parts":[{"text": f"[系统提示]\n{system_prompt}"}]})
    for m in st.session_state.messages:
        contents.append({
            "role": ("user" if m["role"]=="user" else "model"),
            "parts": [{"text": m["content"]}]
        })

    # 调用模型
    with st.chat_message("assistant"):
        box = st.empty()
        try:
            r = client.models.generate_content(model=model, contents=contents)
            answer = r.text or ""
        except Exception as e:
            answer = f"请求失败：{e}"
        box.markdown(answer)
        st.session_state.messages.append({"role":"assistant", "content": answer})