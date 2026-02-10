# 这里处理 TTS 和 ASR 的 API 调用
# modules/audio_processor.py
from openai import OpenAI
import os
import re
from pathlib import Path

try:
    from config import TTS_MODEL, TTS_VOICE
except ImportError:
    TTS_MODEL = "step-tts-mini"
    TTS_VOICE = "cixingnansheng"

# 永远不要在代码里写死绝对路径，尤其是带中文的(血的教训)
# 这里保留为空或默认值即可，实际由 app 控制
speech_file_path = "temp_audio_test.mp3"


class TTS_no_stream:
    def __init__(self, api_key, model=None, voice=None):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.stepfun.com/v1"
        )
        self.model = model or TTS_MODEL
        self.default_voice = voice or TTS_VOICE

    def to_speech(self, text, output_path):
        """
        output_path: 必须是完整的文件路径 (str 或 Path 对象)
        返回 True 表示成功，False 表示失败。
        """
        try:
            save_path = Path(output_path).resolve()

            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.default_voice,
                input=text,
                extra_body={"volume": 1.0}
            )
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True

        except Exception as e:
            err_type = type(e).__name__
            msg = str(e)
            if "401" in msg or "authentication" in msg.lower() or "api_key" in msg.lower():
                print(f"❌ TTS 鉴权失败（请检查 STEPFUN_API_KEY）: {msg}")
            elif "429" in msg or "rate" in msg.lower():
                print(f"❌ TTS 请求限流: {msg}")
            elif "500" in msg or "502" in msg or "503" in msg:
                print(f"❌ TTS 服务端错误: {err_type} - {msg}")
            else:
                print(f"❌ TTS 生成错误: {err_type} - {msg}")
            return False

# 下面的 chunking_tool 保持不变...
def chunking_tool(text):
    """
    将 AI 生成的文本流切分为完整的句子，以便触发实时 TTS。
    架构思考：此函数通常位于 modules/audio_processor.py 中，作为 TTS 流的前置过滤。
    """
    # 1. 定义断句标点：句号、问号、感叹号（包含中英文）
    # 2. 使用正则表达式进行切分，捕获组 () 确保标点符号被保留在列表中
    punc_list = r'([。！？.?!\n])'
    
    # 初始切分
    raw_chunks = re.split(punc_list, text)
    
    combined_chunks = []
    # 3. 将标点符号合并回前面的句子
    for i in range(0, len(raw_chunks) - 1, 2):
        sentence = raw_chunks[i].strip()
        punctuation = raw_chunks[i+1]
        if sentence:
            combined_chunks.append(f"{sentence}{punctuation}")
    
    # 处理最后一段可能没有标点的文字（LLM 正在生成中）
    if len(raw_chunks) % 2 == 1:
        last_chunk = raw_chunks[-1].strip()
        if last_chunk:
            combined_chunks.append(last_chunk)
            
    return combined_chunks







# audio_processor.py - 修复版本
import asyncio
import aiohttp
from typing import Optional
import tempfile
import os

async def audio_to_text(audio_file_path: str, api_key: str) -> Optional[str]:
    """异步语音转文本"""
    try:
        # 异步读取文件
        audio_data = await asyncio.to_thread(_read_file, audio_file_path)
        if not audio_data:
            return None
        
        # 准备请求
        data = aiohttp.FormData()
        data.add_field('model', 'step-asr')
        data.add_field('file', audio_data, 
                      filename=os.path.basename(audio_file_path),
                      content_type='audio/wav')
        data.add_field('language', 'zh')
        
        # 异步API请求
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with session.post(
                "https://api.stepfun.com/v1/audio/transcriptions",
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return result.get('text', '').strip()
                else:
                    print(f"API错误: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"转换错误: {e}")
        return None

def _read_file(path: str) -> Optional[bytes]:
    """同步读取文件"""
    try:
        with open(path, 'rb') as f:
            return f.read()
    except:
        return None


async def record_audio_async(sample_rate: int = 16000) -> Optional[bytes]:
    """异步录音"""
    try:
        import sounddevice as sd
        import numpy as np
        
        # 等待开始
        await _async_input("")
        
        print("开始录音，按回车键停止...")
        
        # 使用事件控制录音
        is_recording = True
        audio_chunks = []
        
        # 音频回调
        def audio_callback(indata, frames, time_info, status):
            if is_recording:
                audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
                audio_chunks.append(audio_int16.tobytes())
        
        # 在后台线程中运行录音
        async def run_recording():
            with sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                dtype='float32',
                callback=audio_callback,
                blocksize=int(sample_rate * 0.1)
            ):
                # 等待停止
                await stop_event.wait()
        
        # 创建停止事件
        stop_event = asyncio.Event()
        recording_task = asyncio.create_task(run_recording())
        
        # 等待停止输入
        async def wait_for_stop():
            await _async_input()
            stop_event.set()
        
        stop_task = asyncio.create_task(wait_for_stop())
        
        # 显示进度
        start_time = asyncio.get_event_loop().time()
        
        while not stop_event.is_set():
            duration = asyncio.get_event_loop().time() - start_time
            print(f"\r录音中... {duration:.1f}秒", end="", flush=True)
            await asyncio.sleep(0.1)
        
        # 停止录音
        is_recording = False
        await recording_task
        await stop_task
        
        print(f"\n录音完成，时长: {duration:.1f}秒")
        
        if audio_chunks:
            return b''.join(audio_chunks)
        return None
        
    except Exception as e:
        print(f"录音错误: {e}")
        return None


async def _async_input(prompt: str = "") -> str:
    """异步输入"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)


async def save_audio_simple(audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
    """简化版音频保存"""
    try:
        import wave
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_file = tmp.name
        
        # 写入WAV文件
        def write_wav():
            with wave.open(temp_file, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(audio_data)
        
        # 在单独线程中执行
        await asyncio.to_thread(write_wav)
        
        return temp_file
        
    
    except Exception as e:
        print(f"保存错误: {e}")
        return None

async def cleanup_file(path: str):
    """异步清理文件"""
    if path and os.path.exists(path):
        await asyncio.to_thread(os.unlink, path)


async def voice_to_text(api_key: str, sample_rate: int = 16000) -> Optional[str]:
    """完整的语音转文本流程"""
    print("开始语音输入...")
    
    # 1. 异步录音
    audio_data = await record_audio_async(sample_rate)
    if not audio_data:
        print("录音失败")
        return None
    
    # 2. 异步保存
    temp_file = await save_audio_simple(audio_data, sample_rate)
    if not temp_file:
        print("保存失败")
        return None
    
    try:
        # 3. 异步转文本
        text = await audio_to_text(temp_file, api_key)
        return text
        
    finally:
        await cleanup_file(temp_file)


async def transcribe_file(file_path: str, api_key: str) -> Optional[str]:
    """转录已有音频文件"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    
    print(f"处理文件: {file_path}")
    return await audio_to_text(file_path, api_key)