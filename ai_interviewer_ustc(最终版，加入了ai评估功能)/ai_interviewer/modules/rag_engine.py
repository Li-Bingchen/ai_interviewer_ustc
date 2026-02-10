import os
from typing import Dict, List, Optional
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

from config import DASHSCOPE_API_KEY

'''
一些说明：

text_embedding有很多种model可以选择，比如 BAAI/bge-m3 或者是 BAAI/bge-large-zh-v1.5

在本次，我们选择的是阿里云DashScope的text-embedding-v2，需要阿里云的API来进行使用

'''

# 统一的 RAG 检索入口，llm_agent 只需调用 get_retrieved_context
def get_retrieved_context(
    query: str,
    domain: str = "cs",
    k: int = 6,
    persist_dir: str = "./vector_db",
    search_filter: Optional[Dict[str, str]] = None,
) -> str:
    # 基于指定领域的 Chroma 向量库检索上下文片段
    try:
        if DASHSCOPE_API_KEY:
            os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY
        embeddings = DashScopeEmbeddings(model="text-embedding-v2")
        db_path = os.path.join(persist_dir, domain)
        if not os.path.exists(db_path):
            return "暂无相关领域背景知识"

        vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
        normalized_filter = search_filter
        # 如果传入的是简单键值对且有多个条件，自动组装成 $and 以适配 Chroma 过滤语法。
        if search_filter and all(not key.startswith("$") for key in search_filter):
            if len(search_filter) > 1:
                normalized_filter = {"$and": [{k: v} for k, v in search_filter.items()]}

        docs = vector_db.similarity_search(query, k=k, filter=normalized_filter)
        return "\n".join(doc.page_content for doc in docs)
    except Exception as exc:  # 错误处理
        print(f"检索出错: {exc}")
        raise  # 向调用方抛出，便于前端展示错误信息


def build_vector_store(
    docs: List[Dict[str, str]],
    domain: str = "cs",
    persist_dir: str = "./vector_db",
    k: int = 2,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> str:
    """可选的建库辅助函数：传入已分段好的文本列表，写入 Chroma。"""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", ";", "；"],
    )

    texts, metadatas = [], []
    for item in docs:
        content = item.get("content") or ""
        metadata = item.get("metadata") or {}
        for chunk in splitter.split_text(content):
            texts.append(chunk)
            metadatas.append(metadata)

    if DASHSCOPE_API_KEY:
        os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY
    embeddings = DashScopeEmbeddings(model="text-embedding-v2")
    db_path = os.path.join(persist_dir, domain)
    vector_db = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=db_path,
    )
    vector_db.persist()
    return db_path
