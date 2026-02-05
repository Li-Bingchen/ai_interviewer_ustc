"""
视频录制模块 - 支持屏幕录制和摄像头录制
"""
import cv2
import numpy as np
import threading
import queue
import time
from typing import Optional, Tuple, Dict
from datetime import datetime
from pathlib import Path
import sys
import os
# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AUDIO_VIDEO_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class VideoRecorder:
    """视频录制器"""
    
    def __init__(self):
        self.recording = False
        self.video_thread = None
        self.frame_queue = queue.Queue(maxsize=100)
        
        self.fps = AUDIO_VIDEO_CONFIG.frame_rate
        self.resolution = AUDIO_VIDEO_CONFIG.resolution
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        self.video_writer = None
        
        logger.info("视频录制器初始化完成")
    
    def start_recording(
        self, 
        output_path: str = None,
        use_camera: bool = False,
        camera_index: int = 0
    ) -> bool:
        if self.recording or not AUDIO_VIDEO_CONFIG.enable_video:
            return False
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("output/recordings")
            output_dir.mkdir(exist_ok=True, parents=True)
            output_path = str(output_dir / f"interview_{timestamp}.mp4")
        
        self.output_path = output_path
        
        try:
            self.video_writer = cv2.VideoWriter(
                output_path,
                self.fourcc,
                self.fps,
                self.resolution
            )
            
            if not self.video_writer.isOpened():
                logger.error("无法打开视频写入器")
                return False
        except Exception as e:
            logger.error(f"初始化视频写入器失败: {e}")
            return False
        
        self.recording = True
        
        if use_camera:
            self.video_thread = threading.Thread(
                target=self._record_from_camera,
                args=(camera_index,)
            )
        else:
            self.video_thread = threading.Thread(
                target=self._record_simulation
            )
        
        self.video_thread.start()
        
        logger.info(f"开始视频录制: {output_path}")
        return True
    
    def _record_from_camera(self, camera_index: int):
        cap = None
        
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                logger.error(f"无法打开摄像头 {camera_index}")
                return
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            while self.recording:
                ret, frame = cap.read()
                
                if ret:
                    frame = cv2.resize(frame, self.resolution)
                    self.video_writer.write(frame)
                else:
                    logger.warning("摄像头读取失败")
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"摄像头录制错误: {e}")
        finally:
            if cap:
                cap.release()
            cv2.destroyAllWindows()
    
    def _record_simulation(self):
        try:
            import numpy as np
            frame_count = 0
            
            while self.recording and frame_count < self.fps * 60 * 10:
                frame = np.full(
                    (self.resolution[1], self.resolution[0], 3), 
                    128, 
                    dtype=np.uint8
                )
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(
                    frame,
                    f"模拟面试录制 - {timestamp}",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2
                )
                
                cv2.putText(
                    frame,
                    "Frame: {}".format(frame_count),
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (200, 200, 200),
                    1
                )
                
                self.video_writer.write(frame)
                frame_count += 1
                
                time.sleep(1 / self.fps)
                
        except Exception as e:
            logger.error(f"模拟录制错误: {e}")
    
    def stop_recording(self) -> Optional[str]:
        if not self.recording:
            return None
        
        self.recording = False
        
        if self.video_thread:
            self.video_thread.join(timeout=2)
        
        if self.video_writer:
            self.video_writer.release()
        
        logger.info(f"停止视频录制，文件: {self.output_path}")
        
        return self.output_path

class InterviewRecorder:
    """面试录制管理器"""
    
    def __init__(self, interview_id: str):
        self.interview_id = interview_id
        self.video_recorder = VideoRecorder()
        
        self.is_recording = False
        self.video_path = None
        
    def start_interview_recording(self) -> bool:
        if self.is_recording:
            return False
        
        output_dir = Path("output/recordings")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        self.video_path = str(
            output_dir / f"interview_{self.interview_id}_{datetime.now().strftime('%H%M%S')}.mp4"
        )
        
        success = self.video_recorder.start_recording(
            output_path=self.video_path,
            use_camera=False
        )
        
        if success:
            self.is_recording = True
            logger.info(f"面试录制开始: {self.interview_id}")
        
        return success
    
    def stop_interview_recording(self) -> Optional[str]:
        if not self.is_recording:
            return None
        
        final_path = self.video_recorder.stop_recording()
        
        self.is_recording = False
        
        logger.info(f"面试录制结束: {self.interview_id}, 文件: {final_path}")
        
        return final_path
    
    def get_recording_status(self) -> Dict:
        return {
            "is_recording": self.is_recording,
            "interview_id": self.interview_id,
            "video_path": self.video_path,
            "timestamp": datetime.now().isoformat()
        }
    
    def cleanup(self):
        if self.is_recording:
            self.stop_interview_recording()

video_recorder = VideoRecorder()
