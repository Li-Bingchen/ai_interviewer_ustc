#这个文件的作用是只处理文字入，文字出，其他一律不管
#history 在app.py中存储，然后在app.py中调用这里的llm_stream_chat函数，实现流式输出
import os
from openai import OpenAI
import re

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key="sk-97cc56de88184ad1913987c3005a8c93",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
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
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            stream=True
        )

        full_response = ""
        # 2. 流式获取内容
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:#chunk会返回一个列表，里面可能有多轮回答，但通常是一轮,所以下面会用chunk.choixes[0],delta为增量
                content = chunk.choices[0].delta.content
                full_response += content
                # 重要：yield 当前累积的所有文本，Gradio 才能实时刷新界面
                yield full_response 

    except Exception as e:
        yield f"抱歉，系统出现了点小故障: {str(e)}"
        #鲁棒性这一块
