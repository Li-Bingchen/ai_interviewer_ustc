#这个文件的作用是只处理文字入，文字出，其他一律不管
#history 在app.py中存储，然后在app.py中调用这里的llm_stream_chat函数，实现流式输出
import os
from openai import OpenAI

try:
    from config import DASHSCOPE_API_KEY, LLM_MODEL, LLM_BASE_URL
except ImportError:
    # 提供默认值（实际应从环境变量获取）
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    LLM_MODEL = "qwen-plus"
    LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

def get_llm_client():
    """获取LLM客户端实例"""
    return OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url=LLM_BASE_URL,
    )

def llm_stream_chat(history, user_input, system_prompt=None):
    """
    history: 对话历史列表 [{"role":"user"|"assistant","content":"..."}]
    user_input: 新的用户输入字符串
    system_prompt: 可选，系统角色提示词（如面试官人设）
    """
    # 1. 准备发送给模型的消息
    messages = list(history) if history else []
    if system_prompt and system_prompt.strip():
        messages = [{"role": "system", "content": system_prompt.strip()}] + messages
    messages = messages + [{"role": "user", "content": user_input}]
    
    try:
        client = get_llm_client()
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            stream=True
        ) # type: ignore

        full_response = ""
        # 2. 流式获取内容
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:  # chunk会返回一个列表，里面可能有多轮回答，但通常是一轮
                content = chunk.choices[0].delta.content
                full_response += content
                # 重要：yield 当前累积的所有文本，Gradio 才能实时刷新界面
                yield full_response

    except Exception as e:
        yield f"抱歉，系统出现了点小故障: {str(e)}"
