"""
配置文件 - 集中管理 API 密钥和系统路径
"""

import os
from pathlib import Path

# ==================== API 密钥配置 ====================
# StepFun API (用于 TTS 和 ASR)
STEPFUN_API_KEY = os.getenv("STEPFUN_API_KEY", "6pZ3jWJGHoMXAcZZpjF3ierYzYDqHEpQLU9gK6auHIWhB1uthsLfqUAnzGLcBiW5x")

# 阿里云 DashScope API (用于 LLM)
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-97cc56de88184ad1913987c3005a8c93")

# ==================== 路径配置 ====================
# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
RAW_KNOWLEDGE_DIR = DATA_DIR / "raw_knowledge"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

# 输出目录
OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"
VIDEOS_DIR = OUTPUT_DIR / "videos"

# 临时文件目录
TEMP_DIR = BASE_DIR / "temp_audio"

# ==================== 模型配置 ====================
# LLM 模型
LLM_MODEL = "qwen-plus"
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# TTS 模型
TTS_MODEL = "step-tts-mini"
TTS_VOICE = "cixingnansheng"  # 磁性男声

# ASR 模型
ASR_MODEL = "step-asr"

# ==================== 应用配置 ====================
# 音频采样率
AUDIO_SAMPLE_RATE = 16000

# 最大对话轮数
MAX_CONVERSATION_TURNS = 50

# 流式输出延迟（秒）
STREAM_DELAY = 0.01

# ==================== 初始化目录 ====================
def init_directories():
    """创建必要的目录结构"""
    directories = [
        DATA_DIR,
        RAW_KNOWLEDGE_DIR,
        VECTOR_STORE_DIR,
        OUTPUT_DIR,
        REPORTS_DIR,
        VIDEOS_DIR,
        TEMP_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录初始化完成")

# 自动初始化
if __name__ == "__main__":
    init_directories()