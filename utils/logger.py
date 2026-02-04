"""
专业日志系统 - 支持文件、控制台输出，带颜色和结构化格式
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import colorlog
from datetime import datetime
import json
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)

class ColoredConsoleFormatter(colorlog.ColoredFormatter):
    """彩色控制台格式化器"""
    
    def __init__(self):
        super().__init__(
            fmt="%(log_color)s%(asctime)s - %(levelname)-8s - %(name)s:%(funcName)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    level = getattr(logging, log_level.upper())
    logger.setLevel(level)
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    if log_to_file:
        log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        
        logger.addHandler(file_handler)
    
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredConsoleFormatter()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)
        
        logger.addHandler(console_handler)
    
    logger.propagate = False
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return setup_logger(name)

class InterviewLogger:
    """面试专用日志记录器"""
    
    def __init__(self, interview_id: str):
        self.interview_id = interview_id
        self.logger = get_logger(f"interview_{interview_id}")
        
        self.interview_log_file = Path("logs") / "interviews" / f"{interview_id}.jsonl"
        self.interview_log_file.parent.mkdir(exist_ok=True, parents=True)
        
    def log_question(self, question: str, question_type: str = "technical"):
        log_data = {
            "interview_id": self.interview_id,
            "type": "question",
            "question_type": question_type,
            "content": question,
            "timestamp": datetime.now().isoformat()
        }
        
        self._write_jsonl(log_data)
        self.logger.info(f"问题记录: {question[:50]}...")
    
    def log_answer(self, answer: str, evaluation: Dict = None, duration: float = None):
        log_data = {
            "interview_id": self.interview_id,
            "type": "answer",
            "content": answer[:500],
            "duration_seconds": duration,
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat()
        }
        
        self._write_jsonl(log_data)
        
        if duration:
            self.logger.info(f"回答记录: {answer[:50]}... (耗时: {duration:.1f}s)")
        else:
            self.logger.info(f"回答记录: {answer[:50]}...")
    
    def log_evaluation(self, evaluation: Dict):
        log_data = {
            "interview_id": self.interview_id,
            "type": "evaluation",
            "data": evaluation,
            "timestamp": datetime.now().isoformat()
        }
        
        self._write_jsonl(log_data)
        self.logger.info(f"评估记录: {evaluation.get('overall_score', 'N/A')}")
    
    def log_silence_analysis(self, silence_analysis: Dict):
        log_data = {
            "interview_id": self.interview_id,
            "type": "silence_analysis",
            "data": silence_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        self._write_jsonl(log_data)
        self.logger.info(f"沉默分析记录: {silence_analysis.get('long_silence_count', 0)}次长停顿")
    
    def _write_jsonl(self, data: Dict):
        try:
            with open(self.interview_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"写入日志文件失败: {e}")
    
    def get_interview_log(self) -> list:
        try:
            with open(self.interview_log_file, 'r', encoding='utf-8') as f:
                return [json.loads(line) for line in f]
        except FileNotFoundError:
            return []
        except Exception as e:
            self.logger.error(f"读取日志文件失败: {e}")
            return []

logger = get_logger()

def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger.debug(f"开始执行: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.debug(
                f"执行完成: {func.__name__}, "
                f"耗时: {execution_time:.2f}秒"
            )
            
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"执行失败: {func.__name__}, "
                f"耗时: {execution_time:.2f}秒, "
                f"错误: {e}"
            )
            raise
    
    return wrapper