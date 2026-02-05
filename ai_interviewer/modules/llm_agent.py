import os
import re
from openai import OpenAI

import json

api_key = os.getenv("API_KEY", "sk-7040bb4394684465b0f62f3063dbe9cc")

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


#岗位输入检查
def clean_position_input(position_input):
    if not position_input or not position_input.strip():
        return False, "", "岗位名称不能为空"
    
    position = position_input.strip()
    
    if len(position) > 30:
        position = position[:30]
    
    position = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\-_()（）]', '', position)
    
    injection_patterns = [
        r'```.*?```',  
        r'你.*?现在.*?是',
        r'忽略.*?之前',
    ]
    for pattern in injection_patterns:
        position = re.sub(pattern, '', position, flags=re.IGNORECASE)
    
    escape_map = {
        '"': "'",
        '\n': ' ',
        '\r': ' ',
        '\t': ' ',
    }
    
    for char, replacement in escape_map.items():
        position = position.replace(char, replacement)
    
    position = position.strip()
    if not position:
        return False, "", "岗位名称无效"
    
    return True, position, ""

#管理历史记录
def manage_history(history, max_length=6):
    if len(history) <= max_length:
        return history.copy()
    
    new_history = []
    
    for msg in history:
        if msg.get("role") == "system":
            new_history.append(msg)
            break
    
    recent_count = max_length - len(new_history)
    recent_history = history[-recent_count:]
    
    # 合并
    if new_history:
        new_history.extend(recent_history)
    else:
        new_history = recent_history
    
    return new_history

# 简单评估回答
def evaluate_answer_simple(question, answer):
    score = 3.0 
    if len(answer) > 100:
        score += 0.5
    elif len(answer) < 30:
        score -= 1.0
    
    tech_words = ["Python", "Java", "数据库", "算法", "优化", "框架"]
    for word in tech_words:
        if word in answer:
            score += 0.2
            break
  
    vague_words = ["不太清楚", "不了解", "大概", "可能"]
    for word in vague_words:
        if word in answer:
            score -= 0.3
            break
 
    score = max(1.0, min(5.0, score))
    if score >= 4.0:
        feedback = "回答详细，技术点清晰"
    elif score >= 3.0:
        feedback = "回答基本完整"
    else:
        feedback = "可以更详细一些"
    
    return round(score, 1), feedback

# 判断是否需要追问
def should_followup_simple(answer, history_length):
    if len(answer) < 50:
        return True, "回答可以再详细一些吗？"
    
    vague_words = ["不太清楚", "不了解", "大概"]
    for word in vague_words:
        if word in answer:
            return True, "能具体解释一下吗？"
    
    if history_length > 8:
        return False, "继续下一个问题"
    
    return False, "回答足够详细"

def get_interview_summary(position, questions_asked, scores):
    """
    生成简单的面试总结
    """
    if not scores:
        return "面试还没开始"
    
    avg_score = sum(scores) / len(scores)
    
    summary = f"""
面试结束！
职位：{position}
问题数量：{questions_asked}
平均得分：{avg_score:.1f}/5.0

{"表现不错，技术掌握扎实" if avg_score >= 4.0 else "基本掌握，还有提升空间"}
    """
    
    return summary

# 主函数
def llm_stream_chat(history, user_input, interview_mode=False, position="Python开发", 
                   followup_mode=False, evaluate_mode=False, **kwargs):
    """
    history: 对话历史
    user_input: 用户输入
    interview_mode: 面试模式
    position: 面试职位
    followup_mode: 追问模式
    evaluate_mode: 评估模式（返回评估结果）
    **kwargs: 模型参数
    """
    
    # 输入检查
    if not user_input or not user_input.strip():
        if evaluate_mode:
            return {"score": 0, "feedback": "无有效回答"}
        yield "请说详细一点"
        return

    if len(user_input) > 1500:
        user_input = user_input[:1500]
    
    if interview_mode and position:
        is_valid, cleaned_position, _ = clean_position_input(position)
        if not is_valid:
            cleaned_position = "Python开发"
    
    history = manage_history(history)
    messages = history.copy()
    
    if interview_mode:
        safe_position = cleaned_position if 'cleaned_position' in locals() else position
        
        if followup_mode:
            system_prompt = f"你是{safe_position}面试官，正在追问细节。"
        elif evaluate_mode:
            system_prompt = f"你是{safe_position}面试官，正在评估回答。"
        else:
            system_prompt = f"你是{safe_position}面试官，考察技术深度。"
        
        if not any(msg.get("role") == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": system_prompt})
    
    # 评估模式
    if evaluate_mode:
        score, feedback = evaluate_answer_simple(messages[-2]["content"] if len(messages) > 1 else "", user_input)
        yield {"score": score, "feedback": feedback}
        return
    
    messages.append({"role": "user", "content": user_input})
    
    # 模型参数
    model = kwargs.get('model', 'qwen-plus')
    temperature = kwargs.get('temperature', 0.7)
    max_tokens = kwargs.get('max_tokens', 2000)
    top_p = kwargs.get('top_p', 0.9)
    
    # 流式输出
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )

        full_response = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield full_response

    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            yield "思考中，请稍候..."
        else:
            yield f"抱歉，系统出了点问题: {str(e)}"


