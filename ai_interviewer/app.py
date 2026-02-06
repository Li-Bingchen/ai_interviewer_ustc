from llm_agent import llm_stream_chat
import asyncio
from audio_processor import voice_to_text
VOICE_ENABLED = True

# 配置
finance_interviewer = """您是一位专业的金融面试官，正在面试一位应聘金融分析师的候选人。
请根据金融行业的专业知识，提出相关的问题，并评估候选人的回答。
面试应包含以下方面：
1. 金融基础知识
2. 数据分析能力
3. 市场理解
4. 风险意识
5. 职业规划

请一次只问一个问题，等待候选人回答后再继续。
保持专业但友好的态度。
当面试进行到第2个问题时，可以自然结束面试。"""

history = [{'role': 'system', 'content': finance_interviewer}]
STEPFUN_API_KEY = "3ZrwQrJ6sG8i2AhNs89yejHYABzGnlT6pMpXaVxr1UDb4iSOQBeRzMwotRFXo3vP7"

# 面试状态
interview_state = {
    'in_progress': False,
    'question_count': 0,
    'max_questions': 2
}

async def simple_voice_test():
    """语音识别"""
    try:
        text = await voice_to_text(STEPFUN_API_KEY)
        
        if text:
            print(f"\n✅ 识别成功!")
            print(f"📝 您说: {text}")
            return text
        else:
            print("\n❌ 识别失败 - 未检测到语音")
            return None
            
    except KeyboardInterrupt:
        print("\n⏹️ 录音已停止")
        return None
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return None


async def chat_with_ai(user_input: str):
    """与AI对话"""
    print("\n🤖 AI面试官: ", end="", flush=True)
    
    full_response = ""
    try:
        for chunk in llm_stream_chat(history, user_input):
            if full_response:
                new_content = chunk[len(full_response):]
            else:
                new_content = chunk
            print(new_content, end="", flush=True)
            full_response = chunk
        
        # 记录对话历史
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": full_response})
        
        # 增加问题计数
        if full_response and full_response.strip().endswith('?'):
            interview_state['question_count'] += 1
            print(f"\n\n📊 问题进度: {interview_state['question_count']}/{interview_state['max_questions']}")
        
        print()
        return full_response
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return None


async def start_interview():
    """开始面试"""
    print("\n🎯 正在启动AI面试官...")
    
    # 重置状态
    interview_state['in_progress'] = True
    interview_state['question_count'] = 0
    # AI提出第一个问题
    await chat_with_ai("请开始面试，提出第一个问题。")


async def conduct_interview():
    """进行面试主循环"""
    if not interview_state['in_progress']:
        await start_interview()
    
    while interview_state['in_progress']:
        print("\n" + "-"*40)
        
        # 检查是否达到最大问题数
        if interview_state['question_count'] >= 1:
            print("\n✅ 面试问题已完成")
            await end_interview()
            break
        
        # 用户语音回答
        user_input = await simple_voice_test()
        
        if user_input is None:
            print("⚠ 未识别到语音，请重试")
            continue
        await chat_with_ai(user_input)
        
        # 简短延迟
        await asyncio.sleep(1)


async def end_interview():
    """结束面试"""
    interview_state['in_progress'] = False
    
    print("\n" + "="*50)
    print("📋 面试总结")
    print(f"总问题数: {interview_state['question_count']}")
    
    # AI提供总结
    print("\n🤖 AI面试官: ", end="", flush=True)
    
    summary_prompt = "面试已完成，请对候选人的整体表现进行简要总结，不要迎合他，批判性思维，并提供一些改进建议。"
    await chat_with_ai(summary_prompt)
    
    print("\n🎯 面试流程结束。感谢您的参与！")
    print("输入 's' 重新开始面试，'q' 退出程序")


async def main():
    """主程序"""
    while True:
        print("\n选择操作:")
        print("  [s] 开始/继续面试")
        print("  [q] 退出程序")
        
        choice = input("请选择 (s/q): ").strip().lower()
        
        if choice == 'q':
            print("\n👋 再见!")
            break
        
        if choice == 's':
            if interview_state['in_progress']:
                print("✅ 继续面试...")
            else:
                print("🎬 开始新的面试...")
            
            await conduct_interview()
      


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
