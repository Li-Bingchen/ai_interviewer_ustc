import os
from typing import List, Dict, Any
from langchain.schema import Document

from config import RAG_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class SimplifiedRAGEngine:
    """简化版RAG引擎（不依赖向量数据库）"""
    
    def __init__(self):
        self.knowledge_dir = RAG_CONFIG.knowledge_base_dir
        os.makedirs(self.knowledge_dir, exist_ok=True)
        
        # 创建示例知识库
        self._create_sample_knowledge()
        
        logger.info("简化版RAG引擎初始化完成（模拟模式）")
    
    def _create_sample_knowledge(self):
        """创建示例面试题"""
        sample_content = """Q: Python中的GIL是什么？对多线程有什么影响？
A: GIL是全局解释器锁，确保同一时刻只有一个线程执行Python字节码。

Q: 解释数据库事务的ACID特性
A: 原子性、一致性、隔离性、持久性。

Q: RESTful API设计原则
A: 使用HTTP方法表达操作，资源使用名词复数，统一响应格式。

Q: 如何处理CPU密集型任务？
A: 使用多进程、C扩展、PyPy或异步编程。

Q: 缓存雪崩、击穿、穿透的区别
A: 雪崩：大量缓存同时过期；击穿：热点key过期；穿透：查询不存在的数据。"""
        
        sample_file = os.path.join(self.knowledge_dir, "sample.txt")
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
    
    def retrieve_for_interview(self, question_type: str, position: str, 
                              previous_questions: List[str] = None) -> List[Document]:
        """模拟检索（返回固定的文档）"""
        # 模拟返回一些文档
        documents = [
            Document(
                page_content="GIL是Python的全局解释器锁，影响多线程性能。",
                metadata={"type": "technical", "position": "Python后端开发"}
            ),
            Document(
                page_content="对于CPU密集型任务，可以使用多进程或C扩展。",
                metadata={"type": "technical", "position": "Python后端开发"}
            ),
            Document(
                page_content="数据库事务需要保证ACID特性。",
                metadata={"type": "technical", "position": "Python后端开发"}
            )
        ]
        
        # 过滤掉之前问过的问题
        if previous_questions:
            documents = [doc for doc in documents 
                        if not any(q in doc.page_content for q in previous_questions[-3:])]
        
        return documents[:2]  # 返回最多2个文档
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """模拟检索"""
        # 根据查询返回相关文档
        docs = []
        if "GIL" in query:
            docs.append(Document(page_content="GIL全局解释器锁影响Python多线程。"))
        if "数据库" in query or "事务" in query:
            docs.append(Document(page_content="数据库事务需要保证ACID特性。"))
        if "缓存" in query:
            docs.append(Document(page_content="缓存问题有雪崩、击穿、穿透。"))
        
        return docs[:k]

# 全局实例
rag_engine = SimplifiedRAGEngine()
