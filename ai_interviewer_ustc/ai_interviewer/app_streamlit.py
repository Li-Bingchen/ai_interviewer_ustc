# -*- coding: utf-8 -*-
"""
AI 面试官 - Streamlit 前端
方案：专业会客厅 - 浅灰/米白背景、深灰正文、深蓝强调，卡片式对话与留白。
"""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

import streamlit as st

# 确保项目根在 path 中（以 ai_interviewer 为运行目录）
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

from config import (
    STEPFUN_API_KEY,
    TEMP_DIR,
    AUDIO_SAMPLE_RATE,
    init_directories,
)
from modules.llm_agent import llm_stream_chat
from modules.audio_processor import (
    TTS_no_stream,
    chunking_tool,
    transcribe_file,
)

# -----------------------------------------------------------------------------
# 1. 页面配置
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI 面试官",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 确保临时目录存在
init_directories()

# -----------------------------------------------------------------------------
# 2. 自定义 CSS（专业会客厅风格）
# -----------------------------------------------------------------------------
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        .stApp {
            background-color: #f5f5f0;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e9ecef;
        }
        [data-testid="stSidebar"] .stMarkdown { font-family: 'Noto Sans SC', 'Inter', sans-serif; }
        .stApp .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 900px;
        }
        h1, h2, h3 {
            color: #2c3e50;
            font-family: 'Noto Sans SC', 'Inter', sans-serif;
        }
        p, .stMarkdown { font-size: 16px; line-height: 1.5; }
        .chat-card-user {
            background: linear-gradient(135deg, #2c5f7a 0%, #3d7a94 100%);
            color: #fff;
            border-radius: 12px;
            padding: 14px 18px;
            margin: 10px 0;
            margin-left: 15%;
            box-shadow: 0 2px 8px rgba(44,95,122,0.2);
        }
        .chat-card-assistant {
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 14px 18px;
            margin: 10px 0;
            margin-right: 15%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }
        .chat-card-assistant p { margin: 0; color: #2c3e50; }
        .chat-card-user p { margin: 0; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def run_async(coro):
    """在 Streamlit 中运行 async 函数（同步封装）"""
    return asyncio.run(coro)


# -----------------------------------------------------------------------------
# 3. Session State 初始化
# -----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """你是一位专业、友善的技术面试官。你会根据候选人的回答进行追问，并给予简洁的反馈。每次回复保持简洁，2～4句话为宜。"""
if "enable_tts" not in st.session_state:
    st.session_state.enable_tts = True
if "audio_processed_token" not in st.session_state:
    st.session_state.audio_processed_token = None
if "last_tts_path" not in st.session_state:
    st.session_state.last_tts_path = None


# -----------------------------------------------------------------------------
# 4. 侧边栏
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("面试官设置")
    st.markdown("---")
    system_prompt = st.text_area(
        "系统提示词（面试官人设）",
        value=st.session_state.system_prompt,
        height=160,
        help="设定 AI 面试官的角色与风格",
    )
    st.session_state.system_prompt = system_prompt
    enable_tts = st.checkbox("开启语音播报（TTS）", value=st.session_state.enable_tts)
    st.session_state.enable_tts = enable_tts
    st.markdown("---")
    if st.button("新对话", use_container_width=True):
        # 清理上一段 TTS 文件
        old_tts = st.session_state.get("last_tts_path")
        if old_tts and Path(old_tts).exists():
            try:
                Path(old_tts).unlink(missing_ok=True)
            except Exception:
                pass
        st.session_state.history = []
        st.session_state.audio_processed_token = None
        st.session_state.last_tts_path = None
        st.rerun()
    st.markdown("---")
    st.caption("语音输入需浏览器授权麦克风；TTS 为整段播报。")


# -----------------------------------------------------------------------------
# 5. 主区域：对话历史
# -----------------------------------------------------------------------------
st.title("AI 面试官")
st.markdown("支持**语音**或**文字**输入，与面试官对话。")

# 渲染历史消息
chat_container = st.container()
with chat_container:
    for msg in st.session_state.history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(
                f'<div class="chat-card-user"><p>{content}</p></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-card-assistant"><p>{content}</p></div>',
                unsafe_allow_html=True,
            )

# 若有当前轮 TTS 音频路径，在对话区下方展示播放器（rerun 后仍可播放）
last_tts_path = st.session_state.get("last_tts_path")
if last_tts_path and Path(last_tts_path).exists():
    st.audio(last_tts_path, format="audio/mp3")

# -----------------------------------------------------------------------------
# 6. 输入区：语音 + 文字，并执行 LLM + 可选 TTS
# -----------------------------------------------------------------------------
user_input = None

# 文字输入
chat_msg = st.chat_input("输入文字发送...")
if chat_msg and chat_msg.strip():
    user_input = chat_msg.strip()

# 语音输入（st.audio_input 返回 UploadedFile 或 None）
audio_value = st.audio_input("或点击麦克风录音", sample_rate=AUDIO_SAMPLE_RATE or 16000)
if audio_value is not None:
    # 避免同一段录音被重复处理：用唯一 token 标记当前录音
    try:
        raw = audio_value.getvalue()
        token = hash(raw) if raw else id(audio_value)
    except Exception:
        token = id(audio_value)
    if st.session_state.audio_processed_token != token:
        st.session_state.audio_processed_token = token
        temp_wav = TEMP_DIR / f"{uuid4().hex}.wav"
        temp_wav.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_wav, "wb") as f:
            f.write(audio_value.getvalue())
        with st.spinner("正在识别语音..."):
            try:
                text = run_async(transcribe_file(str(temp_wav), STEPFUN_API_KEY))
                if text and text.strip():
                    user_input = text.strip()
                else:
                    st.warning("未识别到有效内容，请重试。")
            except Exception as e:
                st.error(f"语音识别失败: {e}")
            finally:
                try:
                    temp_wav.unlink(missing_ok=True)
                except Exception:
                    pass
else:
    st.session_state.audio_processed_token = None

# 处理本轮用户输入：流式 LLM + 更新 history + 可选 TTS
if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    # 流式回复占位
    reply_placeholder = st.empty()
    full_response = ""
    with st.spinner("面试官正在思考..."):
        try:
            for partial in llm_stream_chat(
                st.session_state.history[:-1],
                user_input,
                system_prompt=st.session_state.system_prompt,
            ):
                full_response = partial
                reply_placeholder.markdown(
                    f'<div class="chat-card-assistant"><p>{full_response}</p></div>',
                    unsafe_allow_html=True,
                )
        except Exception as e:
            full_response = f"抱歉，系统出现了点小故障: {str(e)}"
            reply_placeholder.markdown(
                f'<div class="chat-card-assistant"><p>{full_response}</p></div>',
                unsafe_allow_html=True,
            )
    st.session_state.history.append({"role": "assistant", "content": full_response})

    # 可选 TTS：整段合成并播放，路径存入 session 以便 rerun 后仍可播放
    if st.session_state.enable_tts and full_response and not full_response.startswith("抱歉"):
        with st.spinner("正在生成语音..."):
            tts = TTS_no_stream(STEPFUN_API_KEY)
            temp_mp3 = TEMP_DIR / f"{uuid4().hex}.mp3"
            if tts.to_speech(full_response, str(temp_mp3)):
                # 新 TTS 前删除旧文件
                old_tts = st.session_state.get("last_tts_path")
                if old_tts and old_tts != str(temp_mp3) and Path(old_tts).exists():
                    try:
                        Path(old_tts).unlink(missing_ok=True)
                    except Exception:
                        pass
                st.session_state.last_tts_path = str(temp_mp3)
            else:
                st.error("语音生成失败，请检查网络或 API 配置。")

    st.rerun()
