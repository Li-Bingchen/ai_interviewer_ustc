"""
音频处理模块 - 录音、转文字、沉默分析
"""
import wave
import pyaudio
import numpy as np
from typing import Optional, Tuple, Dict
import threading
import queue
import time
import tempfile
import os

from config import AUDIO_VIDEO_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class AudioRecorder:
    """音频录制器"""
    
    def __init__(self):
        self.recording = False
        self.frames = []
        self.audio_thread = None
        self.audio_queue = queue.Queue()
        
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = AUDIO_VIDEO_CONFIG.sample_rate
        
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("PyAudio初始化成功")
        except Exception as e:
            logger.error(f"PyAudio初始化失败: {e}")
            self.audio = None
    
    def start_recording(self):
        """开始录音"""
        if not self.audio or self.recording:
            return False
            
        self.recording = True
        self.frames = []
        
        def record_callback():
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            while self.recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                    self.audio_queue.put(data)
                except Exception as e:
                    logger.error(f"录音错误: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
        
        self.audio_thread = threading.Thread(target=record_callback)
        self.audio_thread.start()
        
        logger.info("开始录音")
        return True
    
    def stop_recording(self) -> Optional[bytes]:
        """停止录音并返回音频数据"""
        if not self.recording:
            return None
            
        self.recording = False
        
        if self.audio_thread:
            self.audio_thread.join(timeout=2)
        
        audio_data = b''.join(self.frames)
        
        logger.info(f"停止录音，获取 {len(audio_data)} 字节音频数据")
        return audio_data
    
    def save_to_wav(self, audio_data: bytes, filename: str) -> bool:
        """保存为WAV文件"""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(audio_data)
            
            logger.info(f"音频已保存到: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存WAV文件失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.audio:
            self.audio.terminate()

class SilenceAnalyzer:
    """沉默分析器"""
    
    @staticmethod
    def analyze_silence_patterns(audio_data: bytes, sample_rate: int = 16000) -> Dict:
        """
        分析音频中的沉默模式
        返回沉默时长、比例、分布
        """
        if not audio_data:
            return {
                "silence_ratio": 0.0,
                "total_silence_seconds": 0.0,
                "silent_segments": [],
                "long_silence_count": 0,
                "speech_activity_percent": 0.0,
                "audio_duration": 0.0
            }
        
        try:
            # 转换为numpy数组
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            if len(audio_array) == 0:
                return {
                    "silence_ratio": 1.0,
                    "total_silence_seconds": 0.0,
                    "silent_segments": [],
                    "long_silence_count": 0,
                    "speech_activity_percent": 0.0,
                    "audio_duration": 0.0
                }
            
            # 计算能量
            energy = np.abs(audio_array).astype(np.float32)
            
            # 沉默检测阈值
            if len(energy) > 0:
                silence_threshold = np.percentile(energy, 25)  # 能量最低的25%作为沉默基线
                silence_threshold = max(silence_threshold, 100)  # 最小阈值
            else:
                silence_threshold = 100
            
            is_silence = energy < silence_threshold
            
            # 计算沉默比例
            silence_ratio = np.mean(is_silence)
            
            # 找到沉默段
            silent_segments = []
            current_segment = []
            
            for i, silent in enumerate(is_silence):
                if silent:
                    current_segment.append(i)
                elif current_segment:
                    segment_duration = len(current_segment) / sample_rate
                    if segment_duration > 0.5:  # 超过0.5秒的沉默
                        start_time = current_segment[0] / sample_rate
                        end_time = current_segment[-1] / sample_rate
                        silent_segments.append({
                            "start": round(start_time, 2),
                            "end": round(end_time, 2),
                            "duration": round(segment_duration, 2)
                        })
                    current_segment = []
            
            # 处理最后的沉默段
            if current_segment:
                segment_duration = len(current_segment) / sample_rate
                if segment_duration > 0.5:
                    start_time = current_segment[0] / sample_rate
                    end_time = current_segment[-1] / sample_rate
                    silent_segments.append({
                        "start": round(start_time, 2),
                        "end": round(end_time, 2),
                        "duration": round(segment_duration, 2)
                    })
            
            # 长沉默标记（>3秒）
            long_silences = [s for s in silent_segments if s["duration"] > 3.0]
            
            # 计算语音活跃度
            total_duration = len(audio_array) / sample_rate
            if total_duration > 0:
                speech_duration = total_duration - sum(s["duration"] for s in silent_segments)
                speech_activity = (speech_duration / total_duration) * 100
            else:
                speech_activity = 0.0
            
            return {
                "silence_ratio": round(float(silence_ratio), 3),
                "total_silence_seconds": round(sum(s["duration"] for s in silent_segments), 2),
                "silent_segments": silent_segments[:10],  # 只保留前10个
                "long_silence_count": len(long_silences),
                "speech_activity_percent": round(speech_activity, 1),
                "audio_duration": round(total_duration, 2),
                "silence_threshold": float(silence_threshold)
            }
            
        except Exception as e:
            logger.error(f"沉默分析失败: {e}")
            return {
                "silence_ratio": 0.0,
                "total_silence_seconds": 0.0,
                "silent_segments": [],
                "long_silence_count": 0,
                "speech_activity_percent": 0.0,
                "audio_duration": 0.0,
                "error": str(e)
            }
    
    @staticmethod
    def calculate_hesitation_score(silence_analysis: Dict) -> float:
        """计算犹豫分数（基于沉默模式）"""
        if not silence_analysis:
            return 0.0
        
        long_silence_count = silence_analysis.get("long_silence_count", 0)
        silence_ratio = silence_analysis.get("silence_ratio", 0.0)
        
        # 基于长沉默次数和沉默比例计算犹豫分数（0-10分，越高越犹豫）
        hesitation_score = (long_silence_count * 2) + (silence_ratio * 5)
        
        return min(round(hesitation_score, 1), 10.0)

class SpeechToText:
    """语音转文字"""
    
    @staticmethod
    def transcribe(audio_data: bytes, use_api: bool = False) -> str:
        if not audio_data:
            return ""
            
        if use_api:
            try:
                import openai
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                
                with open(tmp_path, 'rb') as audio_file:
                    transcript = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file
                    )
                
                os.unlink(tmp_path)
                
                return transcript.text
                
            except ImportError:
                logger.warning("未安装openai库，使用本地模式")
            except Exception as e:
                logger.error(f"Whisper API调用失败: {e}")
        
        # 本地模式：返回模拟结果
        logger.warning("使用模拟语音识别，实际项目应集成真实ASR")
        
        mock_responses = [
            "我对Python有深入的了解，特别是在后端开发方面。",
            "我最近的项目是一个微服务架构的电商系统。",
            "我熟悉Django和Flask框架，并有实际项目经验。",
            "在数据库方面，我使用过MySQL和Redis。",
            "我对分布式系统和高并发处理有一定经验。"
        ]
        
        import random
        return random.choice(mock_responses)

class TextToSpeech:
    """文字转语音"""
    
    @staticmethod
    def synthesize(text: str, use_api: bool = False) -> Optional[bytes]:
        if not text:
            return None
            
        if use_api:
            try:
                logger.info(f"TTS API转换: {text[:50]}...")
                return b'mock_audio_data'
            except Exception as e:
                logger.error(f"TTS API调用失败: {e}")
        
        logger.warning("使用模拟TTS，实际项目应集成真实TTS")
        return None

class AudioProcessor:
    """音频处理器"""
    
    def __init__(self):
        self.recorder = AudioRecorder()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.analyzer = SilenceAnalyzer()
        
    def record_and_transcribe(self, duration: int = 5) -> Tuple[str, bytes, Dict]:
        """
        录制并转文字
        
        Returns:
            (转录文字, 音频数据, 沉默分析结果)
        """
        if not AUDIO_VIDEO_CONFIG.enable_audio:
            logger.warning("音频功能未启用")
            return "", b'', {}
        
        if not self.recorder.start_recording():
            return "", b'', {}
        
        time.sleep(duration)
        
        audio_data = self.recorder.stop_recording()
        
        if not audio_data:
            return "", b'', {}
        
        # 语音转文字
        text = self.stt.transcribe(audio_data)
        
        # 分析沉默模式
        silence_analysis = self.analyzer.analyze_silence_patterns(
            audio_data, AUDIO_VIDEO_CONFIG.sample_rate
        )
        
        return text, audio_data, silence_analysis
    
    def analyze_audio_silence(self, audio_data: bytes) -> Dict:
        """分析音频沉默模式"""
        return self.analyzer.analyze_silence_patterns(
            audio_data, AUDIO_VIDEO_CONFIG.sample_rate
        )
    
    def text_to_speech(self, text: str) -> Optional[bytes]:
        """文字转语音"""
        if not AUDIO_VIDEO_CONFIG.enable_audio:
            return None
            
        return self.tts.synthesize(text)
    
    def save_interview_audio(self, audio_segments: list, output_path: str) -> bool:
        """保存面试音频"""
        try:
            combined_data = b''.join(audio_segments)
            return self.recorder.save_to_wav(combined_data, output_path)
        except Exception as e:
            logger.error(f"保存面试音频失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        self.recorder.cleanup()

# 全局音频处理器实例
audio_processor = AudioProcessor()