# app.py
from modules.llm_agent import llm_stream_chat, get_summary, evaluate_answer
from typing import Dict
import time

# 系统提示词模板 - 添加时间控制指令
SYSTEM_PROMPTS = {
    "finance": """你是专业的金融面试官，正在进行一场15分钟的结构化面试。
你的任务：
1. 先热情打招呼并说明面试时长约15分钟
2. 根据候选人的回答动态生成问题（不要用预制问题）
3. 在回答简短或模糊时适当追问
4. 面试进行到14分钟时开始自然收尾
5. 15分钟时主动、自然地结束面试
6. 全程不要透露AI身份，只提出问题并追问

请保持专业但友好的语气，把握好时间节奏。""",
    
    "tech": """你是技术面试官，正在进行一场15分钟的结构化面试。
你的任务：
1. 先热情打招呼并说明面试时长约15分钟
2. 根据候选人的回答动态生成技术问题
3. 在回答简短或模糊时适当追问技术细节
4. 面试进行到14分钟时开始自然收尾
5. 15分钟时主动、自然地结束面试
6. 全程不要透露AI身份，只提出问题并追问

请保持专业但友好的语气，把握好时间节奏。""",
    
    "pm": """你是产品经理面试官，正在进行一场15分钟的结构化面试。
你的任务：
1. 先热情打招呼并说明面试时长约15分钟
2. 根据候选人的回答动态生成产品相关问题
3. 在回答简短或模糊时适当追问
4. 面试进行到14分钟时开始自然收尾
5. 15分钟时主动、自然地结束面试
6. 全程不要透露AI身份，只提出问题并追问

请保持专业但友好的语气，把握好时间节奏。""",
    
    "default": """你是专业的面试官，正在进行一场15分钟的结构化面试。
你的任务：
1. 先热情打招呼并说明面试时长约15分钟
2. 根据候选人的回答动态生成问题
3. 在回答简短或模糊时适当追问
4. 面试进行到14分钟时开始自然收尾
5. 15分钟时主动、自然地结束面试
6. 全程不要透露AI身份，只提出问题并追问

请保持专业但友好的语气，把握好时间节奏。"""
}

# 模型配置字典
MODEL_CONFIGS = {
    "default": {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.9
    },
    "structured": {
        "model": "deepseek-chat",
        "temperature": 0.6,  # 适合结构化面试
        "max_tokens": 1800,
        "top_p": 0.85
    }
}

# 全局时间状态
interview_start_time = None
TOTAL_INTERVIEW_SECONDS = 15 * 60  # 15分钟
time_warnings_sent = []

def start_interview_timer():
    """开始面试计时"""
    global interview_start_time, time_warnings_sent
    interview_start_time = time.time()
    time_warnings_sent = []  # 重置警告记录
    print(f"⏰ 面试计时开始！总时长：{TOTAL_INTERVIEW_SECONDS//60}分钟")
    return interview_start_time

def get_interview_time_status():
    """获取面试时间状态"""
    if interview_start_time is None:
        return {"elapsed": 0, "remaining": TOTAL_INTERVIEW_SECONDS, "progress": 0}
    
    elapsed = time.time() - interview_start_time
    remaining = max(0, TOTAL_INTERVIEW_SECONDS - elapsed)
    progress = min(100, (elapsed / TOTAL_INTERVIEW_SECONDS) * 100)
    
    return {
        "elapsed": int(elapsed),
        "remaining": int(remaining),
        "progress": progress,
        "minutes_left": remaining // 60,
        "seconds_left": int(remaining % 60),
        "is_time_up": remaining <= 0
    }



def should_end_interview() -> bool:
    """判断是否应该结束面试"""
    status = get_interview_time_status()
    return status["is_time_up"]


def get_system_prompt(position_type: str) -> str:
    """根据岗位类型获取系统提示词"""
    return SYSTEM_PROMPTS.get(position_type, SYSTEM_PROMPTS["default"])

def get_model_config(config_name: str) -> Dict:
    """获取模型配置"""
    return MODEL_CONFIGS.get(config_name, MODEL_CONFIGS["default"])

def show_menu():
    """显示主菜单"""
    print("╔════════════════════════════════════╗")
    print("║       🤖 智能面试系统 v3.0        ║")
    print("║    (15分钟结构化面试-动态问题)    ║")
    print("╚════════════════════════════════════╝")
    print()
    print("请选择面试模式：")
    print("  1️⃣  15分钟结构化面试")
    print("  0️⃣  退出系统")
    print()

def show_position_menu():
    """显示岗位选择菜单"""
    print("\n请选择面试岗位类型：")
    print("  1. 金融类 (投资、银行、风控)")
    print("  2. 技术类 (开发、算法、运维)")
    print("  3. 产品类 (产品经理、运营)")
    print("  4. 自定义 (其他岗位)")
    print()

def fifteen_minute_interview(position_name: str, system_prompt: str, model_config: Dict):
    """
    15分钟结构化面试
    AI动态生成问题，主动控制时间
    """
    # 1. 开始计时
    start_interview_timer()
    
    # 2. 初始化历史记录
    history = [{"role": "system", "content": system_prompt}]
    scores = []
    question_count = 0
    
    print(f"\n🎯 {position_name} 面试开始！")
    print("⏰ 时长：15分钟")
    print("🤖 AI将动态生成问题并控制时间节奏")
    print("-" * 50)
    
    # 3. AI生成开场白（不固定）
    print("🤖 面试官: ", end="", flush=True)
    
    opening_response = ""
    for chunk in llm_stream_chat(
        history=history,
        user_input="请开始面试，先打招呼并说明面试时长。",
        system_prompt="",
        model_name=model_config["model"],
        temperature=model_config["temperature"],
        max_tokens=model_config["max_tokens"],
        top_p=model_config["top_p"]
    ):
        print(chunk, end="", flush=True)
        opening_response += chunk
    
    print()  # 换行
    history.append({"role": "assistant", "content": opening_response})
    
    # 4. 主对话循环
    while True:
        try:
            # 检查时间
            time_status = get_interview_time_status()
            
            # 时间到了，主动结束
            if time_status["is_time_up"]:
                print("\n" + "="*50)
                print("⏰ 时间到！")
                print("="*50)
                
                # AI生成结束语
                print("🤖 面试官: ", end="", flush=True)
                ending_response = ""
                for chunk in llm_stream_chat(
                    history=history,
                    user_input="面试时间已到，请自然地结束面试，感谢候选人并适当总结他刚刚的表现。",
                    system_prompt="",
                    model_name=model_config["model"],
                    temperature=model_config["temperature"],
                    max_tokens=800,  # 结束语短一点
                    top_p=model_config["top_p"]
                ):
                    print(chunk, end="", flush=True)
                    ending_response += chunk
                
                print()
                break
            
            
            
            
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()
            
            # 退出检查
            if user_input.lower() in ['quit', 'exit', '退出', '结束']:
                print("\n⏹️ 面试提前结束")
                break
            
            # 评估命令
            if user_input.lower() == '评估':
                if scores:
                    avg = sum(scores) / len(scores)
                    print(f"📊 当前平均分: {avg:.1f}/5.0 (共{len(scores)}个评分)")
                else:
                    print("📊 暂无评分数据")
                continue
            
            # 准备给AI的上下文（包含剩余时间信息）
            remaining_minutes = time_status["minutes_left"]
            remaining_seconds = time_status["seconds_left"]
            
            # 根据剩余时间调整提示
            time_hint = ""
            if remaining_minutes == 14:
                time_hint = "（刚开始）"
            elif remaining_minutes <= 10 and remaining_minutes > 5:
                time_hint = "（进行中）"
            elif remaining_minutes <= 5 and remaining_minutes > 2:
                time_hint = "（深入讨论）"
            elif remaining_minutes <= 2:
                time_hint = "（准备收尾）"
            
            # 组合输入
            enhanced_input = user_input
            if time_hint:
                enhanced_input = f"{user_input} {time_hint}"
            
            # AI生成回应
            print("🤖 面试官: ", end="", flush=True)
            
            full_response = ""
            for chunk in llm_stream_chat(
                history=history,
                user_input=enhanced_input,
                system_prompt="",
                model_name=model_config["model"],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"],
                top_p=model_config["top_p"]
            ):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print()  # 换行
            
            # 更新历史记录
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": full_response})
            
            # 自动评估回答
            if len(history) > 3:
                # 找到最近的问题
                recent_question = ""
                for msg in reversed(history[:-2]):
                    if msg["role"] == "assistant":
                        recent_question = msg["content"]
                        break
                
                if recent_question and len(user_input) > 15:
                    evaluation = evaluate_answer(recent_question, user_input)
                    scores.append(evaluation["score"])
            
            question_count += 1
            
            # 控制历史长度
            if len(history) > 12:
                history = [history[0]] + history[-10:]
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 面试中断")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            continue
    
    # 5. 面试结束
    print("\n" + "="*50)
    print("🎯 面试结束")
    
    # 计算实际用时
    actual_seconds = time.time() - interview_start_time if interview_start_time else 0
    minutes = int(actual_seconds // 60)
    seconds = int(actual_seconds % 60)
    
    print(f"⏱️ 实际用时: {minutes}分{seconds}秒")
    print(f"📊 总问题数: {question_count}")
    
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"⭐ 平均评分: {avg_score:.1f}/5.0")
    
    print("="*50)
    
    return question_count, scores

def main():
    """主函数：控制整个面试流程"""
    
    while True:
        show_menu()
        choice = input("请输入选择 (0-1): ").strip()
        
        if choice == '0':
            print("👋 感谢使用，再见！")
            break
        
        elif choice == '1':
            # 15分钟结构化面试
            
            # 1. 选择岗位类型
            show_position_menu()
            pos_choice = input("请选择岗位类型 (1-4): ").strip()
            
            if pos_choice == '1':
                position_type = "finance"
                default_name = "金融分析师"
            elif pos_choice == '2':
                position_type = "tech"
                default_name = "软件工程师"
            elif pos_choice == '3':
                position_type = "pm"
                default_name = "产品经理"
            elif pos_choice == '4':
                position_type = "default"
                default_name = "候选人"
            else:
                print("❌ 无效选择，使用默认设置")
                position_type = "default"
                default_name = "候选人"
            
            # 输入具体岗位名称
            position_name = input(f"请输入具体岗位名称 (回车使用 '{default_name}'): ").strip()
            if not position_name:
                position_name = default_name
            
            # 2. 使用结构化面试专用配置
            model_config = get_model_config("structured")
            
            # 3. 获取系统提示词
            system_prompt = get_system_prompt(position_type)
            
            # 4. 开始15分钟面试
            question_count, scores = fifteen_minute_interview(position_name, system_prompt, model_config)
            
            # 5. 生成总结
            if question_count > 0:
                summary = get_summary(position_name, question_count, scores)
                print("\n" + "="*50)
                print("📝 面试总结报告")
                print("="*50)
                print(summary)
                print("="*50)
            
            input("\n按回车键返回主菜单...")
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
