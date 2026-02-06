# audio_processor.py - 修正版
import aiohttp
import asyncio
from typing import Optional
import base64
import json

async def audio_to_text(audio_file_path: str, api_key: str) -> Optional[str]:
    """
    将语音文件转换为文本（使用阶跃星辰API）
    
    Args:
        audio_file_path: 语音文件路径
        api_key: 阶跃星辰API密钥
    
    Returns:
        str: 转换后的文本，失败时返回None
    """
    try:
        # 读取音频文件
        with open(audio_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # 阶跃星辰的语音转文本API端点
        url = "https://api.stepfun.com/v1/audio/transcriptions"
        
        # 准备表单数据
        data = aiohttp.FormData()
        data.add_field('model', 'step-asr')  # 使用语音转文本专用模型
        data.add_field('file', 
                      audio_data, 
                      filename=audio_file_path.split('/')[-1],
                      content_type='audio/wav')
        data.add_field('language', 'zh')  # 中文
        
        # 异步请求API
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            }
            
            async with session.post(
                url,
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    # 提取转换后的文本
                    if 'text' in result:
                        return result['text'].strip()
                    else:
                        print(f"API响应格式异常: {result}")
                        return None
                else:
                    error_text = await response.text()
                    print(f"API请求失败: {response.status}, 错误信息: {error_text}")
                    return None
                    
    except FileNotFoundError:
        print(f"音频文件未找到: {audio_file_path}")
        return None
    except Exception as e:
        print(f"语音转文本过程中出现错误: {str(e)}")
        return None


async def record_audio_to_text(api_key: str, 
                              duration: int = 5, 
                              sample_rate: int = 16000) -> Optional[str]:
    """
    录制音频并转换为文本
    
    Returns:
        str: 转换后的文本，失败时返回None
    """
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np
        import tempfile
        
        # 检查依赖
        print(f"开始录制音频，时长: {duration}秒...")
        print("请开始说话...")
        
        # 录制音频
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # 等待录制完成
        
        print("录制完成，正在转换为文本...")
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_path = temp_audio.name
            # 转换为16位PCM格式，这是大多数API支持的格式
            audio_int16 = (audio_data * 32767).astype(np.int16)
            sf.write(temp_path, audio_int16, sample_rate, subtype='PCM_16')
        
        # 转换为文本
        text = await audio_to_text(temp_path, api_key)
        
        # 清理临时文件
        import os
        os.unlink(temp_path)
        
        return text
        
    except ImportError as e:
        print(f"缺少必要的依赖库: {str(e)}")
        print("请安装: pip install sounddevice soundfile numpy")
        return None
    except Exception as e:
        print(f"录制过程中出现错误: {str(e)}")
        return None


