while True:
    # 2. 获取用户输入
    user_input = input("\n用户: ")
    if user_input.lower() in ['exit', 'quit', '退出']:
        break
        
    # 3. 将用户的话添加到历史记录
    messages.append({'role': 'user', 'content': user_input})
    
    # 4. 调用模型
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=messages, # 把整个对话历史发过去
        stream=True
    )
    
    # 5. 接收流式返回，并记录 AI 的回答
    print("AI: ", end="")
    full_response = ""
    for chunk in completion:
        if chunk.choices:#chunk会返回一个列表，里面可能有多轮回答，但通常是一轮,所以下面会用chunk.choixes[0],delta为增量
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="")
                full_response += content # 累加 AI 的回答
    
    # 6. 【关键】把 AI 的回答也加入历史记录，这样下次它就知道自己说过什么了
    messages.append({'role': 'assistant', 'content': full_response})