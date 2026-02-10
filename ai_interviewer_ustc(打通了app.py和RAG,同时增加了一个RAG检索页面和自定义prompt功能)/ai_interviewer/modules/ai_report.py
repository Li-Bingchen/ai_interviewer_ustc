# -*- coding: utf-8 -*-
"""
AI 面试报告生成模块
使用阿里云 DashScope API 调用 Qwen-max (思考模式) 对面试对话进行评价。
"""

from typing import List, Dict, Optional
from openai import OpenAI

from config import DASHSCOPE_API_KEY, LLM_BASE_URL

# ==================== 客户端初始化 ====================
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=LLM_BASE_URL,  # https://dashscope.aliyuncs.com/compatible-mode/v1
)

# ==================== 评价用系统提示词 ====================
REPORT_SYSTEM_PROMPT = """你是一位资深的技术面试评审专家。你的任务是根据一段完整的面试对话记录，对被面试者的表现进行全面、客观、专业的评价。

请从以下维度进行评价，并给出总体评分（满分100分）：

## 评价维度

1. **技术能力**（权重 30%）
   - 对技术问题的理解深度
   - 知识面的广度
   - 是否能准确运用技术概念

2. **问题解决能力**（权重 25%）
   - 分析问题的逻辑性
   - 解题思路是否清晰
   - 能否提出有效的解决方案

3. **沟通表达能力**（权重 20%）
   - 回答是否条理清晰
   - 能否简洁准确地表达观点
   - 是否善于用例子说明问题

4. **学习潜力与思维深度**（权重 15%）
   - 面对不熟悉的问题是否能合理推导
   - 是否展现出举一反三的能力
   - 思考是否有深度

5. **综合素养**（权重 10%）
   - 面试态度与自信程度
   - 面对压力的表现
   - 回答的完整性

## 输出格式要求

请按以下格式输出评价报告：

---
# 📋 AI 面试评价报告

## 一、总体评分：XX / 100

## 二、各维度详细评价

### 1. 技术能力（XX / 30）
[具体评价内容]

### 2. 问题解决能力（XX / 25）
[具体评价内容]

### 3. 沟通表达能力（XX / 20）
[具体评价内容]

### 4. 学习潜力与思维深度（XX / 15）
[具体评价内容]

### 5. 综合素养（XX / 10）
[具体评价内容]

## 三、亮点总结
[被面试者表现突出的地方]

## 四、改进建议
[需要加强和改进的地方]

## 五、总体评语
[一段简洁的总结性评语]
---

请确保评价客观、公正，既要肯定优点也要指出不足，给出有建设性的反馈。"""


def _format_history_for_report(history: List[Dict[str, str]]) -> str:
    """
    将对话历史格式化为面试对话记录文本，供评价模型阅读。

    参数:
        history: 对话历史列表，每个元素为 {"role": "user"|"assistant", "content": "..."}

    返回:
        格式化后的对话记录字符串
    """
    if not history:
        return "（无对话记录）"

    lines = []
    turn = 0
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "").strip()
        if not content:
            continue
        if role == "user":
            turn += 1
            lines.append(f"【第 {turn} 轮】")
            lines.append(f"候选人：{content}")
        elif role == "assistant":
            lines.append(f"面试官：{content}")
        lines.append("")  # 空行分隔

    return "\n".join(lines)


def ai_report(
    history: List[Dict[str, str]],
    model: str = "qwen-max",
    enable_thinking: bool = True,
) -> str:
    """
    根据完整对话历史，调用阿里云 Qwen-max (思考模式) 生成面试评价报告。

    参数:
        history:  完整的面试对话历史列表
                  格式: [{"role": "user"|"assistant", "content": "..."}, ...]
                  其中 role="user" 是被面试者的回答，role="assistant" 是面试官的提问/追问。
        model:    使用的模型名称，默认 "qwen-max"（思考模式下实际会走 qwen-max 的深度推理）
        enable_thinking: 是否开启思考模式（深度推理），默认开启

    返回:
        str: AI 生成的面试评价报告文本

    异常:
        如果 API 调用失败，会抛出异常。

    使用示例:
        >>> from modules.ai_report import ai_report
        >>> history = [
        ...     {"role": "assistant", "content": "请做一下自我介绍"},
        ...     {"role": "user", "content": "我是XXX，本科计算机科学..."},
        ...     {"role": "assistant", "content": "请介绍一下TCP三次握手"},
        ...     {"role": "user", "content": "TCP三次握手是..."},
        ... ]
        >>> report = ai_report(history)
        >>> print(report)
    """
    if not history:
        return "⚠️ 没有对话记录，无法生成面试评价报告。"

    # 格式化对话记录
    formatted_history = _format_history_for_report(history)

    # 统计基本信息
    user_turns = sum(1 for msg in history if msg.get("role") == "user")
    assistant_turns = sum(1 for msg in history if msg.get("role") == "assistant")

    # 构造用户消息：把整段面试对话交给评价模型
    user_message = (
        f"以下是一段完整的技术面试对话记录，共 {user_turns} 轮候选人回答、"
        f"{assistant_turns} 轮面试官提问。\n"
        f"请根据对话内容对被面试者的表现进行全面评价。\n\n"
        f"--- 面试对话记录 ---\n\n"
        f"{formatted_history}\n"
        f"--- 对话记录结束 ---\n\n"
        f"请按要求的格式输出评价报告。"
    )

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        # 构造请求参数
        request_params = {
            "model": model,
            "messages": messages,
        }

        # 开启思考模式（Qwen-max 深度推理）
        # DashScope 兼容模式下，通过 extra_body 传递 enable_thinking 参数
        if enable_thinking:
            request_params["extra_body"] = {"enable_thinking": True}

        completion = client.chat.completions.create(**request_params)

        # 提取回复内容
        if completion.choices and completion.choices[0].message:
            return completion.choices[0].message.content or "⚠️ 模型未返回有效内容。"
        else:
            return "⚠️ 模型返回为空，请稍后重试。"

    except Exception as e:
        raise RuntimeError(f"面试评价报告生成失败: {str(e)}") from e


def ai_report_stream(
    history: List[Dict[str, str]],
    model: str = "qwen-max",
    enable_thinking: bool = True,
):
    """
    流式版本：根据完整对话历史，流式生成面试评价报告。
    适用于 Streamlit 等需要逐步显示内容的前端。

    参数:
        history:  完整的面试对话历史列表
        model:    使用的模型名称
        enable_thinking: 是否开启思考模式

    返回:
        Generator[str]: 逐步累积的报告文本（每次 yield 包含从开头到当前的完整文本）

    使用示例（Streamlit 集成）:
        >>> placeholder = st.empty()
        >>> for partial_report in ai_report_stream(st.session_state.history):
        ...     placeholder.markdown(partial_report)
    """
    if not history:
        yield "⚠️ 没有对话记录，无法生成面试评价报告。"
        return

    # 格式化对话记录
    formatted_history = _format_history_for_report(history)

    user_turns = sum(1 for msg in history if msg.get("role") == "user")
    assistant_turns = sum(1 for msg in history if msg.get("role") == "assistant")

    user_message = (
        f"以下是一段完整的技术面试对话记录，共 {user_turns} 轮候选人回答、"
        f"{assistant_turns} 轮面试官提问。\n"
        f"请根据对话内容对被面试者的表现进行全面评价。\n\n"
        f"--- 面试对话记录 ---\n\n"
        f"{formatted_history}\n"
        f"--- 对话记录结束 ---\n\n"
        f"请按要求的格式输出评价报告。"
    )

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        request_params = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        if enable_thinking:
            request_params["extra_body"] = {"enable_thinking": True}
            # 流式 + 思考模式下，需要设置 stream_options 以获取增量输出
            request_params["stream_options"] = {"include_usage": True}

        completion = client.chat.completions.create(**request_params)

        full_response = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield full_response

    except Exception as e:
        yield f"⚠️ 面试评价报告生成失败: {str(e)}"
