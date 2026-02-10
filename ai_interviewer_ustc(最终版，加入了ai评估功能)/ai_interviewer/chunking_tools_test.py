import re

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

# 测试一下
test_text = "你好！我是今天的面试官。请问你准备好了吗？我们开始面"
print(chunking_tool(test_text)) 


