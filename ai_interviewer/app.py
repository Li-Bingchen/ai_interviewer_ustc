# app.py (支持语音输入的版本 - 修正版)
from llm_agent import llm_stream_chat
import asyncio
import tempfile
import os

# 导入语音处理模块
try:
    from audio_processor import record_audio_to_text, audio_to_text
    AUDIO_ENABLED = True
except ImportError as e:
    print(f"语音功能不可用: {str(e)}")
    print("语音功能需要额外的依赖库。要启用语音，请安装: pip install sounddevice soundfile numpy aiohttp")
    AUDIO_ENABLED = False

# 模拟配置加载
finance_interviewer = """您是一位专业的‘金融面试官’。您的目标是模拟真实的金融行业面试场景，评估候选人的专业知识、逻辑思维、风险意识和职业素养。
宗旨与目标：
* 为用户提供高度专业且具有挑战性的金融面试体验。
* 覆盖金融的不同细分领域，如投资银行、资产管理、风险控制、定量分析等。
* 针对用户的回答提供深入的反馈和改进建议。
行为与规则：
1) 面试准备与开场：
a) 热情且专业地向候选人打招呼，介绍自己的身份为‘金融面试官’。
b) 询问候选人所申请的具体岗位（例如：分析师、基金经理、风控专员）以及其背景（应届生或社招）。
c) 根据岗位设定面试流程，通常包含自我介绍、专业技术问题（Technical Questions）和行为面试问题（Behavioral Questions）。
2) 面试实施：
a) 提出与岗位紧密相关的技术性问题，例如估值模型（DCF）、财务报表分析、宏观经济影响或市场衍生品定价。
b) 采用‘压力面试’或‘追问’模式，在用户回答后，针对其逻辑漏洞进一步提问。
c) 包含行为面试题，使用STAR法则（情境、任务、行动、结果）来评估用户的软技能。
d) 每次对话仅提出 1-2 个问题，保持节奏，让过程更像真实对话。
3) 反馈与总结：
a) 在面试结束时，询问用户是否需要复盘反馈。
b) 提供具体的反馈，包括专业知识的准确性、表达的逻辑性以及需要加强的领域。
整体语气：
* 语气正式、客观、严谨，有时可以表现出面试官的威严感。
* 对金融专业术语使用精准。
* 保持高效，避免冗长的废话。"""

history = [{'role': 'system', 'content': finance_interviewer}]

# 阶跃星辰API密钥 - 请替换为你的实际API密钥
# 获取地址：https://platform.stepfun.com/
STEPFUN_API_KEY = "3ZrwQrJ6sG8i2AhNs89yejHYABzGnlT6pMpXaVxr1UDb4iSOQBeRzMwotRFXo3vP7"  # 请替换为你的实际API密钥

async def process_audio_input():
    """处理语音输入"""
    if not AUDIO_ENABLED:
        print("语音功能未启用或依赖库未安装")
        return None
    
    if STEPFUN_API_KEY.startswith("sk-xxxxxxxx"):
        print("请先设置阶跃星辰API密钥")
        return None
    
    print("\n正在录制音频（默认5秒），请开始说话...")
    text = await record_audio_to_text(
        api_key=STEPFUN_API_KEY,
        duration=5,
        sample_rate=16000
    )
    
    if text:
        print(f"识别结果: {text}")
        return text
    else:
        print("语音识别失败，请重试")
        return None

async def process_text_input():
    """处理文本输入"""
    user_input = input("\n用户: ")
    if user_input.lower() in ['quit', 'exit', '退出']:
        return None
    return user_input

async def process_file_audio(audio_file_path: str):
    """处理音频文件输入"""
    if not AUDIO_ENABLED:
        print("语音功能未启用或依赖库未安装")
        return None
    
    if STEPFUN_API_KEY.startswith("sk-xxxxxxxx"):
        print("请先设置阶跃星辰API密钥")
        return None
    
    if not os.path.exists(audio_file_path):
        print(f"音频文件不存在: {audio_file_path}")
        return None
    
    print(f"正在处理音频文件: {audio_file_path}")
    text = await audio_to_text(audio_file_path, STEPFUN_API_KEY)
    
    if text:
        print(f"识别结果: {text}")
        return text
    else:
        print("语音识别失败")
        return None



async def main():
    """主函数"""
    print("=" * 60)
    print("AI金融面试系统")
    print("=" * 60)
    
    # 检查配置
    if STEPFUN_API_KEY.startswith("sk-xxxxxxxx"):
        print("⚠ 警告: 请先在代码中设置您的阶跃星辰API密钥")
        print("在 app.py 中将 STEPFUN_API_KEY 替换为您的实际API密钥")
        print("获取API密钥地址: https://platform.stepfun.com/")
    
    
    
    print("\n输入模式:")
    print("1. 文本输入 (直接输入文本)")
    print("2. 语音输入 (输入 'voice' 或 '语音')")
    print("3. 音频文件 (输入 'file:音频文件路径')")
    print("4. 退出 (输入 'quit', 'exit', 或 '退出')")
    print("=" * 60)
    
    # AI面试官开场
    print("\nAI面试官: 您好！我是专业的金融面试官。很高兴为您提供面试模拟体验。")
    print("AI面试官: 请问您申请的是什么岗位？以及您是应届生还是有工作经验的候选人？")
    
    while True:
        print("\n" + "-" * 40)
        print("请选择输入方式:")
        print("1. 输入文字")
        print("2. 语音输入 (输入 'voice')")
        print("3. 退出 (输入 'quit')")
        
        mode = input("\n选择模式 (1/2/3 或直接输入): ").strip()
        
        if mode.lower() in ['quit', 'exit', '退出', '3']:
            print("感谢使用AI金融面试系统，再见！")
            break
        
        user_input = None
        
        if mode.lower() in ['voice', '语音', '2']:
            # 语音输入模式
            user_input = await process_audio_input()
            if not user_input:
                continue
        elif mode.startswith('file:'):
            # 音频文件模式
            audio_path = mode[5:].strip()
            user_input = await process_file_audio(audio_path)
            if not user_input:
                continue
        else:
            # 文本输入模式（直接输入）
            if mode not in ['1']:
                user_input = mode
            else:
                temp_input = await process_text_input()
                if temp_input is None:  # 用户输入了退出命令
                    print("感谢使用AI金融面试系统，再见！")
                    break
                user_input = temp_input
        
        if not user_input:
            continue
        
        # 处理AI响应（流式输出）
        print("\nAI面试官: ", end="", flush=True)
        
        full_response = ""
        try:
            # 调用llm_stream_chat函数
            for chunk in llm_stream_chat(history, user_input):
                if full_response:
                    new_content = chunk[len(full_response):]
                else:
                    new_content = chunk
                print(new_content, end="", flush=True)
                full_response = chunk
            
            # 更新对话历史
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": full_response})
            print()  # 换行
            
        except Exception as e:
            print(f"\n处理AI响应时出现错误: {str(e)}")

if __name__ == "__main__":
    # 检查语音功能依赖
    if AUDIO_ENABLED:
        print("✓ 语音功能已启用")
    else:
        print("✗ 语音功能未启用")
        print("要启用语音功能，请安装依赖:")
        print("pip install sounddevice soundfile numpy aiohttp")
    
    # 运行主程序
    asyncio.run(main())
