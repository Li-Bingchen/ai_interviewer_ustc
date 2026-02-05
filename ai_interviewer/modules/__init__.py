from .llm_stream_chat import (
    llm_stream_chat,                    # 核心流式聊天函数
    manage_history,                     # 历史记录管理
    evaluate_answer_simple,             # 简单评估回答
    should_followup_simple,             # 判断是否需要追问
    get_interview_summary,              # 获取面试总结
    clean_position_input                # 清理岗位输入
)


from .rag_engine import EnhancedRAGEngine, rag_engine
from .audio_processor import AudioProcessor, audio_processor

__all__ = [
    # 流式聊天模块（替换旧的llm_agent）
    'llm_stream_chat',
    'manage_history',
    'evaluate_answer_simple',
    'should_followup_simple',
    'get_interview_summary',
    'clean_position_input',
    
    # 原有模块
    'EnhancedRAGEngine',
    'rag_engine',
    'AudioProcessor',
    'audio_processor'
]

