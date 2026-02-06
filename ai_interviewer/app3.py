#这一版使用streamlit
import streamlit as st
from modules.llm_agent import llm_stream_chat
from modules.audio_processor import AudioProcessor
import time

# 1. 初始化组件
st.set_page_config(page_title="AI 实时面试官", layout="wide")
tts_processor = AudioProcessor(api_key="你的阶跃星辰API_KEY")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🚀 AI 实时模拟面试系统")

# 2. 聊天历史渲染
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. 用户输入处理
if user_input := st.chat_input("请开始你的回答..."):
    # 记录用户输入
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 回复区
    with st.chat_message("assistant"):
        response_placeholder = st.empty() # 文字显示占位符
        full_response = ""
        sentence_buffer = "" # 句子缓冲区

        # 获取 LLM 流式输出
        for chunk_text in llm_stream_chat(st.session_state.messages[:-1], user_input):
            # 这里的 chunk_text 是 llm_stream_chat yield 出来的全量文本
            # 我们需要计算出“新增”的部分
            new_chars = chunk_text[len(full_response):]
            full_response = chunk_text
            sentence_buffer += new_chars
            
            # 刷新 UI 文字
            response_placeholder.markdown(full_response + "▌")

            # 4. 实时触发 TTS 逻辑：检测标点符号
            if any(punc in new_chars for punc in ["。", "！", "？", ".", "!", "?", "\n"]):
                clean_sentence = sentence_buffer.strip()
                if len(clean_sentence) > 2: # 避免太短的词（如“嗯”）频繁调用
                    audio_content = tts_processor.text_to_speech(clean_sentence)
                    if audio_content:
                        # 在 Streamlit 中直接播放音频
                        # autoplay=True 能够实现“生成即播放”
                        st.audio(audio_content, format="audio/mp3", autoplay=True)
                    sentence_buffer = "" # 清空缓冲区处理下一句

        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})