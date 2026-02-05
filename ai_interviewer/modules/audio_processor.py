import os
import tempfile
from typing import Optional, Union, BinaryIO
import requests
import json
import base64
import io
from pathlib import Path

# ===================== 配置区 =====================
# 阶跃星辰API配置
STEPFUN_API_KEY = os.getenv("STEPFUN_API_KEY", "")
STEPFUN_API_BASE = "https://api.stepfun.com/v1"

# 默认声音配置
DEFAULT_VOICES = {
    "zh-CN": "zh-CN-qiuqiu",  # 中文默认声音
    "en-US": "en-US-amber",   # 英文默认声音
    "jp": "jp-sakura",        # 日文默认声音
}

# 语音转文字（ASR）

def speech_to_text(
    audio_input: Union[str, BinaryIO],
    language: str = "zh-CN",
    model: str = "step-asr",
    **kwargs
) -> str:
    """
    使用阶跃星辰API将语音转换为文字
    
    参数:
        audio_input: 音频文件路径 或 文件对象
        language: 语言代码 (zh-CN, en-US, jp等)
        model: 使用的模型 (step-asr, step-asr-v2等)
        **kwargs: 其他API参数
    
    返回:
        识别出的文字
        
    注意:
        支持的音频格式: wav, mp3, m4a, flac, aac, ogg
        最大文件大小: 25MB
        支持语言: 中文、英文、日文等
    """

    
    # 处理音频输入
    audio_data = _prepare_audio_data(audio_input)
    
    # 构建API请求
    url = f"{STEPFUN_API_BASE}/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {STEPFUN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 将音频数据转换为base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    payload = {
        "model": model,
        "audio": f"data:audio/wav;base64,{audio_base64}",
        "language": language,
        **kwargs
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get("text", "")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API请求失败: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"API响应解析失败: {e}")

# ===================== 文字转语音（TTS） =====================

def text_to_speech(
    text: str,
    voice: Optional[str] = None,
    language: str = "zh-CN",
    model: str = "step-tts",
    speed: float = 1.0,
    pitch: float = 0.0,
    output_file: Optional[str] = None,
    **kwargs
) -> Union[str, bytes]:
    """
    使用阶跃星辰API将文字转换为语音
    
    参数:
        text: 要转换的文字
        voice: 声音类型，如不指定则根据语言选择默认声音
        language: 语言代码
        model: 使用的模型 (step-tts, step-tts-v2等)
        speed: 语速 (0.5-2.0)
        pitch: 音高 (-12.0到12.0)
        output_file: 输出文件路径（如不提供则返回二进制数据）
        **kwargs: 其他API参数
    
    返回:
        如果output_file提供则返回文件路径，否则返回音频二进制数据
        
    注意:
        支持的声音类型请参考阶跃星辰文档
        输出格式: mp3
    """
    
    # 检查API密钥
    if not STEPFUN_API_KEY:
        raise ValueError("请设置STEPFUN_API_KEY环境变量")
    
    # 设置默认声音
    if voice is None:
        voice = DEFAULT_VOICES.get(language, "zh-CN-qiuqiu")
    
    # 构建API请求
    url = f"{STEPFUN_API_BASE}/audio/speech"
    
    headers = {
        "Authorization": f"Bearer {STEPFUN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "language": language,
        "speed": max(0.5, min(2.0, speed)),  # 限制范围
        "pitch": max(-12.0, min(12.0, pitch)),  # 限制范围
        **kwargs
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # 获取音频数据
        audio_data = response.content
        
        # 处理输出
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            return output_file
        else:
            return audio_data
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API请求失败: {e}")

# ===================== 辅助函数 =====================

def _prepare_audio_data(audio_input: Union[str, BinaryIO]) -> bytes:
    """准备音频数据"""
    if isinstance(audio_input, str):
        # 文件路径
        if not os.path.exists(audio_input):
            raise FileNotFoundError(f"音频文件不存在: {audio_input}")
        
        with open(audio_input, 'rb') as f:
            return f.read()
    elif hasattr(audio_input, 'read'):
        # 文件对象
        audio_input.seek(0)  # 重置指针
        return audio_input.read()
    else:
        raise TypeError("audio_input必须是文件路径或文件对象")

def list_available_voices() -> dict:
    return {
        "zh-CN": ["zh-CN-qiuqiu", "zh-CN-xiaoxiao", "zh-CN-yunxi", "zh-CN-yunyang"],
        "en-US": ["en-US-amber", "en-US-andrew", "en-US-ava", "en-US-bella"],
        "jp": ["jp-sakura", "jp-akira", "jp-daichi"],
    }

def record_audio(
    duration: int = 5,
    output_file: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1
) -> str:
    """
    录制麦克风音频（用于测试）
    
    参数:
        duration: 录制时长（秒）
        output_file: 输出文件路径（WAV格式）
        sample_rate: 采样率
        channels: 声道数
    
    返回:
        音频文件路径
    """
    try:
        import pyaudio
        import wave
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        
        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        print(f"🎤 开始录制 {duration} 秒...")
        frames = []
        
        for i in range(0, int(sample_rate / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("✅ 录制完成")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # 保存文件
        if output_file is None:
            output_file = tempfile.mktemp(suffix='.wav')
        
        wf = wave.open(output_file, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return output_file
    except ImportError:
        raise ImportError("请安装pyaudio: pip install pyaudio")
    except Exception as e:
        raise Exception(f"音频录制失败: {e}")

def play_audio(audio_data: Union[str, bytes]):
    """
    播放音频（用于测试）
    
    参数:
        audio_data: 音频文件路径 或 二进制数据
    """
    try:
        import pyaudio
        import wave
        import io
        
        if isinstance(audio_data, str):
            # 文件路径
            wf = wave.open(audio_data, 'rb')
        else:
            # 二进制数据 - 假设是WAV格式
            wf = wave.open(io.BytesIO(audio_data), 'rb')
        
        p = pyaudio.PyAudio()
        
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        data = wf.readframes(1024)
        print("🔊 播放音频...")
        
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        
        print("✅ 播放完成")
    except ImportError:
        print("⚠️  请安装pyaudio以播放音频")
    except Exception as e:
        print(f"❌ 播放失败: {e}")

# ===================== 测试函数 =====================

def test_stepfun_apis():
    """测试阶跃星辰API功能"""
    print("🎯 阶跃星辰API测试")
    print("=" * 40)
    
    if not STEPFUN_API_KEY:
        print("❌ 未设置STEPFUN_API_KEY环境变量")
        print("请设置: export STEPFUN_API_KEY='your-api-key'")
        return False
    
    # 测试TTS
    print("1. 测试文字转语音（TTS）...")
    try:
        test_text = "你好，这是一个阶跃星辰TTS的测试。"
        
        # 生成语音
        audio_data = text_to_speech(
            text=test_text,
            language="zh-CN",
            voice="zh-CN-qiuqiu",
            speed=1.0,
            output_file="test_stepfun_tts.mp3"
        )
        
        print(f"✅ TTS成功，文件保存到: {audio_data}")
        
        # 播放测试
        play_audio(audio_data)
        
    except Exception as e:
        print(f"❌ TTS测试失败: {e}")
        return False
    
    # 测试ASR（需要先有音频文件）
    print("\n2. 测试语音转文字（ASR）...")
    try:
        # 先录制一段音频
        print("   请对着麦克风说几句话...")
        audio_file = record_audio(5, "test_recording.wav")
        print(f"   录制完成: {audio_file}")
        
        # 识别语音
        text = speech_to_text(audio_file, language="zh-CN")
        print(f"✅ 识别结果: {text}")
        
        # 清理
        os.remove(audio_file)
        
    except Exception as e:
        print(f"❌ ASR测试失败: {e}")
        print("提示: 需要安装pyaudio录制音频")
    
    print("\n" + "=" * 40)
    print("📊 测试完成")
    print("可用声音:", list_available_voices())
    print("=" * 40)
    
    return True

def quick_tts_demo():
    """快速TTS演示"""
    if not STEPFUN_API_KEY:
        print("请先设置STEPFUN_API_KEY环境变量")
        return
    
    print("🎤 阶跃星辰TTS快速演示")
    print("输入 'quit' 退出")
    print("-" * 30)
    
    while True:
        text = input("\n请输入要转换的文字: ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            break
        
        if not text:
            continue
        
        try:
            print("生成语音中...")
            audio_file = text_to_speech(
                text=text,
                output_file="demo_output.mp3"
            )
            
            print(f"✅ 语音已保存: {audio_file}")
            
            # 询问是否播放
            play = input("是否播放？(y/n): ").strip().lower()
            if play == 'y':
                play_audio(audio_file)
                
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    print("选择测试模式:")
    print("  1. 完整API测试")
    print("  2. TTS快速演示")
    print("  3. 检查配置")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        test_stepfun_apis()
    elif choice == "2":
        quick_tts_demo()
    elif choice == "3":
        print(f"API密钥: {'已设置' if STEPFUN_API_KEY else '未设置'}")
        print(f"可用声音: {list_available_voices()}")
    else:
        test_stepfun_apis()
