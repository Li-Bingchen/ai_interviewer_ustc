#这一版是尝试流式输出并用gradio做前端做了一个聊天框
import gradio as gr
import time
from modules.llm_agent import llm_stream_chat

# 这里的 predict 函数是 Gradio 和你的 LLM 模块之间的“桥梁”
def predict(message, history):
    """
    message: 当前用户输入的内容
    history: 之前的对话记录，格式为 [[user_msg1, bot_msg1], [user_msg2, bot_msg2]...]
    """
    
    # 1. 将 Gradio 的 history 格式转换为 OpenAI 期望的 messages 格式
    formatted_history = []
    for user, assistant in history:
        formatted_history.append({"role": "user", "content": user})
        formatted_history.append({"role": "assistant", "content": assistant})
    
    # 2. 调用你的流式生成器
    # Gradio 会自动迭代这个 generator，并实时更新 UI
    for response in llm_stream_chat(formatted_history, message):
        yield response

# 3. 构建极简但功能强大的界面
demo = gr.ChatInterface(
    fn=predict,
    title="AI 实时模拟面试系统",
    description="欢迎参加金融/CS 模拟面试。请开始你的自我介绍。",
    examples=["你好，我来面试量化分析师。", "请针对 DCF 模型考考我。"],
    #theme="soft" # 选一个舒服的主题
)

if __name__ == "__main__":
    demo.launch()