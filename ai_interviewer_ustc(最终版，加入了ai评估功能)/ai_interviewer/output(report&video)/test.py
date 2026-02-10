#假流式输出和真流式输出测试
# 模拟你的生成器
def mock_llm():
    yield "金融面试"
    yield "金融面试官"
    yield "金融面试官为您服务"

res = mock_llm()

# --- 实验 A ---
print(f"实验 A (直接打印对象): {res}") 
# 预期：你会看到 <generator object...>。如果没有看到，说明你的环境对对象做了特殊渲染。

# --- 实验 B (只用一次 next) ---
print(f"实验 B (调用一次 next): {next(res)}")
# 预期：只看到 "金融面试"。后面的“为您服务”消失了。

# --- 实验 C (真正的流式遍历) ---
print("实验 C (真流式): ", end="")
for chunk in mock_llm():
    import time
    time.sleep(2) # 故意放慢速度看效果
    print(f"\rAI: {chunk}", end="") # \r 回到行首覆盖，模拟 Gradio 效果