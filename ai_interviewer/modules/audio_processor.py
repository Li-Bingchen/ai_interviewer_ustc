import os
import tempfile

# 检查是否在魔搭社区
IS_MODELSCOPE = os.getenv('MODELSCOPE_ENVIRONMENT', 'False') == 'True'
print(f"当前环境：{'魔搭社区' if IS_MODELSCOPE else '本地'}")

def speech_to_text_simple(audio_path):
    # 如果在魔搭社区，用魔搭的模型
    if IS_MODELSCOPE:
        try:
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            
            print("使用魔搭语音识别模型...")
            asr_pipeline = pipeline(
                task=Tasks.auto_speech_recognition,
                model='damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch'
            )
            
            result = asr_pipeline(audio_path)
            text = result.get('text', '')
            print(f"识别结果：{text}")
            return text
            
        except Exception as e:
            print(f"魔搭识别失败：{e}")
    
    # 本地环境，用简单方法
    try:
        import speech_recognition as sr
        
        print("使用本地语音识别...")
        r = sr.Recognizer()
        
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
        
        text = r.recognize_google(audio, language='zh-CN')
        print(f"识别结果：{text}")
        return text
        
    except Exception as e:
        print(f"本地识别失败：{e}")
        return ""

#文字转语音函数 
def text_to_speech_simple(text, output_path=None):
    if not text:
        print("错误：没有文字内容")
        return None
    
    # 如果在魔搭社区
    if IS_MODELSCOPE:
        try:
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            
            print("使用魔搭语音合成模型...")
            tts_pipeline = pipeline(
                task=Tasks.text_to_speech,
                model='damo/speech_sambert-hifigan_tts_zh-cn_16k'
            )
            
            # 如果没有指定输出路径，创建临时文件
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                output_path = temp_file.name
            output = tts_pipeline(text, voice='zhitian_emo')
            output.save(output_path)
            
            print(f"语音已保存到：{output_path}")
            return output_path
            
        except Exception as e:
            print(f"魔搭语音合成失败：{e}")
    
    # 本地环境
    try:
        from gtts import gTTS
        import pygame
        
        print("使用本地语音合成...")
        
        #创建临时文件
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            output_path = temp_file.name

        tts = gTTS(text=text, lang='zh-cn')
        tts.save(output_path)
        
        pygame.mixer.init()
        pygame.mixer.music.load(output_path)
        pygame.mixer.music.play()
        
        print(f"语音已保存到：{output_path}")
        return output_path
        
    except Exception as e:
        print(f"本地语音合成失败：{e}")
        return None

def record_audio(duration=5, sample_rate=16000):

    try:
        import pyaudio
        import wave
        
        print(f"开始录音 {duration} 秒...")
        
        # 录音参数
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        
        # 创建PyAudio实例
        p = pyaudio.PyAudio()
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # 开始录音
        stream = p.open(
            format=format,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk
        )
        
        frames = []
        for i in range(0, int(sample_rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
        
        print("录音结束")
        
        # 停止录音
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # 保存为WAV文件
        wf = wave.open(temp_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return temp_path
        
    except Exception as e:
        print(f"录音失败：{e}")
        return None
def process_voice_interview():
    import time
    
    print("=" * 50)
    print("开始语音面试")
    print("=" * 50)
    
    position = input("请输入面试岗位（默认Python开发）: ") or "Python开发"
    interview_mode = True
    history = []
    scores = []
    question_count = 0
    
    print(f"\n开始{position}面试，请准备回答问题...")
    
    # 生成欢迎语（文字）
    welcome_prompt = f"作为{position}面试官，请做简短开场、自我介绍并问第一个技术问题"
    welcome_response = ""
    for text in llm_stream_chat([], welcome_prompt, interview_mode=True, position=position):
        welcome_response = text
    
    print(f"面试官: {welcome_response}")
    
    # 把欢迎语加入历史
    history.append({"role": "assistant", "content": welcome_response})
    
    # 把欢迎语转为语音播放
    print("正在播放欢迎语...")
    tts_path = text_to_speech_simple(welcome_response)
    if tts_path:
        print("语音播放完成")
    
    # 面试循环
    while True:
        print("\n" + "=" * 30)
        print(f"第{question_count + 1}个问题")
        

        print("\n请开始回答（5秒后自动结束）...")
        audio_path = record_audio(duration=5)
        
        if not audio_path:
            print("录音失败，请重试")
            continue
        
        # 语音转文字
        print("正在识别语音...")
        user_text = speech_to_text(audio_path)
        
        if not user_text:
            print("语音识别失败，请重说一次")
            continue
        
        print(f"你的回答: {user_text}")
        
        # 3. 评估回答
        print("正在评估回答...")
        evaluation_result = None
        for result in llm_stream_chat(history, user_text, 
                                     interview_mode=True, 
                                     position=position,
                                     evaluate_mode=True):
            evaluation_result = result
        
        if evaluation_result:
            score = evaluation_result["score"]
            feedback = evaluation_result["feedback"]
            scores.append(score)
            print(f"评分: {score}/5.0 - {feedback}")
        
        history.append({"role": "user", "content": user_text})
        
        print("\nAI思考中...")
        ai_response = ""
        
        need_followup, _ = should_followup_simple(user_text, len(history))
        
        for text in llm_stream_chat(history, "", 
                                   interview_mode=True,
                                   position=position,
                                   followup_mode=need_followup):
            ai_response = text
       
            print(f"\rAI: {text}", end="")
        
        print(f"\nAI回复: {ai_response}")
        

        history.append({"role": "assistant", "content": ai_response})
        
        print("正在生成语音回复...")
        tts_path = text_to_speech_simple(ai_response)
        if tts_path:
            print("语音回复播放完成")
        else:
            print("语音生成失败，但对话继续")
        
        question_count += 1
        if question_count >= 5:  # 最多问5个问题
            print("\n已达到最大问题数量")
            break
        
        continue_interview = input("\n继续下一个问题吗？(y/n): ").lower()
        if continue_interview != 'y':
            break

    print("\n" + "=" * 50)
    print("面试结束，正在生成总结...")
    
    summary = get_interview_summary(position, question_count, scores)
    print(summary)
    
    print("\n正在播放面试总结...")
    tts_path = text_to_speech_simple(summary)
    if tts_path:
        print("总结语音播放完成")
    
    print("=" * 50)
    print("语音面试流程结束")
    print("=" * 50)
    
    # 保存面试记录
    try:
        with open(f"interview_record_{int(time.time())}.json", "w", encoding="utf-8") as f:
            record = {
                "position": position,
                "question_count": question_count,
                "scores": scores,
                "history": history,
                "summary": summary,
                "timestamp": time.time()
            }
            json.dump(record, f, ensure_ascii=False, indent=2)
        print(f"面试记录已保存")
    except Exception as e:
        print(f"保存记录失败: {e}")
