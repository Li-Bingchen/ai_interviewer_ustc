"""
智能面试官代理 - 管理面试流程、评估回答、生成反馈
"""
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime

from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOpenAI

from config import MODEL_CONFIG, INTERVIEW_CONFIG, config
from modules.rag_engine import rag_engine
from utils.logger import get_logger

logger = get_logger(__name__)

class InterviewPhase(Enum):
    """面试阶段枚举"""
    WELCOME = "welcome"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CODING = "coding"
    Q_A = "q_a"
    CLOSING = "closing"
    EVALUATION = "evaluation"

class EvaluationResult:
    """评估结果"""
    
    def __init__(self):
        self.scores = {criterion: 0.0 for criterion in INTERVIEW_CONFIG.evaluation_criteria}
        self.feedback = []
        self.strengths = []
        self.weaknesses = []
        self.overall_score = 0.0
        self.silence_analysis = {}
        
    def add_feedback(self, criterion: str, score: float, comment: str):
        self.scores[criterion] = score
        self.feedback.append({
            "criterion": criterion,
            "score": score,
            "comment": comment
        })
        
        if score >= 4.0:
            self.strengths.append(criterion)
        elif score <= 2.0:
            self.weaknesses.append(criterion)
            
    def calculate_overall(self):
        if self.scores:
            self.overall_score = sum(self.scores.values()) / len(self.scores)
        return self.overall_score
    
    def to_dict(self) -> Dict:
        return {
            "scores": self.scores,
            "overall_score": self.calculate_overall(),
            "feedback": self.feedback,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "silence_analysis": self.silence_analysis,
            "timestamp": datetime.now().isoformat()
        }

class LLMProvider:
    """LLM提供者工厂"""
    
    @staticmethod
    def create_provider():
        """创建LLM提供者"""
        llm_config = config.get_llm_config()
        provider = llm_config["provider"]
        
        if provider == "ollama":
            return Ollama(
                model=llm_config["ollama_model_name"],
                base_url=llm_config.get("base_url", "http://localhost:11434"),
                temperature=llm_config.get("temperature", 0.7)
            )
        elif provider == "openai":
            return ChatOpenAI(
                model_name=llm_config["openai_model_name"],
                temperature=llm_config.get("temperature", 0.7),
                openai_api_key=llm_config["openai_api_key"]
            )
        elif provider == "custom_transformers":
            # TODO: 实现自定义Transformers模型
            return CustomTransformersLLM(
                model_path=llm_config["transformers_model_path"],
                tokenizer_path=llm_config["transformers_tokenizer_path"],
                temperature=llm_config.get("temperature", 0.7)
            )
        elif provider == "custom_ollama":
            # TODO: 实现自定义Ollama模型
            return CustomOllamaLLM(
                model_name=llm_config["custom_ollama_model"],
                base_url=llm_config.get("base_url", "http://localhost:11434"),
                temperature=llm_config.get("temperature", 0.7)
            )
        elif provider == "custom_api":
            # TODO: 实现自定义API
            return CustomAPILLM(
                endpoint=llm_config["custom_api_endpoint"],
                api_key=llm_config["custom_api_key"],
                temperature=llm_config.get("temperature", 0.7)
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

# 自定义模型基类
class BaseCustomLLM:
    def invoke(self, prompt: str) -> str:
        raise NotImplementedError("子类必须实现invoke方法")

class CustomTransformersLLM(BaseCustomLLM):
    def __init__(self, model_path: str, tokenizer_path: str = None, **kwargs):
        self.temperature = kwargs.get("temperature", 0.7)
        # TODO: 加载你的微调模型
        # from transformers import AutoModelForCausalLM, AutoTokenizer
        # self.model = AutoModelForCausalLM.from_pretrained(model_path)
        # self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path or model_path)
        pass
    
    def invoke(self, prompt: str) -> str:
        # TODO: 实现模型推理
        return f"[自定义Transformers模型] {prompt[:50]}..."

class CustomOllamaLLM(BaseCustomLLM):
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434", **kwargs):
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = kwargs.get("temperature", 0.7)
    
    def invoke(self, prompt: str) -> str:
        import requests
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error(f"自定义Ollama调用失败: {e}")
            return f"[Ollama错误] {str(e)}"

class CustomAPILLM(BaseCustomLLM):
    def __init__(self, endpoint: str, api_key: str = "", **kwargs):
        self.endpoint = endpoint
        self.api_key = api_key
        self.temperature = kwargs.get("temperature", 0.7)
        self.model = "deepseek-chat"  # 或 "deepseek-reasoner"
        
        # 初始化OpenAI客户端
        from openai import OpenAI
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.endpoint  # DeepSeek API地址
        )
    
    def invoke(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=2000,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return f"[DeepSeek API错误] {str(e)}"
        
class PromptTemplates:
    """提示词模板集合"""
    
    @staticmethod
    def get_welcome_prompt(position: str) -> str:
        return f"""你是一位资深的{position}技术面试官，以考察技术深度和细节著称。
请开始面试：
1. 简短自我介绍
2. 说明今天将重点考察{position}相关的核心技术
3. 提出第一个深入的技术问题

直接开始，不要等待回应。"""
    
    @staticmethod
    def get_technical_question_prompt(context: str, position: str) -> str:
        return f"""你正在面试{position}职位的候选人。基于以下知识，提出一个相关的技术问题：
        
        相关知识：
        {context}
        
        要求：
        1. 问题要有一定深度，能考察候选人的理解程度
        2. 问题要具体，不要过于宽泛
        3. 如果是概念性问题，可以要求举例说明
        4. 如果合适，可以包含一个简单的场景题
        5.请时刻牢记面试特点，适当给予压力


        只输出问题，不要输出其他内容。"""
    
    @staticmethod
    def get_evaluation_prompt(question: str, answer: str, silence_analysis: Dict = None, criteria: List[str] = None) -> str:
        if criteria is None:
            criteria = INTERVIEW_CONFIG.evaluation_criteria
        
        silence_feedback = ""
        if silence_analysis:
            silence_feedback = f"""
            语音模式分析：
            - 沉默比例：{silence_analysis.get('silence_ratio', 0)*100:.1f}%
            - 长停顿次数（>3秒）：{silence_analysis.get('long_silence_count', 0)}
            - 语音活跃度：{silence_analysis.get('speech_activity_percent', 0)}%
            - 音频总时长：{silence_analysis.get('audio_duration', 0)}秒
            
            注意：{silence_analysis.get('long_silence_count', 0)}次过长停顿可能表明紧张或思考不流畅。
            """
        
        criteria_str = "\n".join([f"{criterion}: 1-5分" for criterion in criteria])
        
        return f"""作为技术面试官，评估候选人表现：

问题：{question}
回答：{answer}

{silence_feedback}

评估标准（1-5分，5分最高）：
{criteria_str}

请输出JSON格式：
{{
    "technical_scores": {{"技术知识深度": 分数, "问题解决能力": 分数, ...}},
    "communication_evaluation": {{
        "clarity": 分数,
        "conciseness": 分数,
        "response_fluency": 分数,
        "silence_impact": "沉默模式对沟通的影响分析"
    }},
    "detailed_feedback": "综合反馈（技术+沟通）",
    "follow_up_question": "针对性跟进问题"
}}"""
    
    @staticmethod
    def get_follow_up_prompt(previous_qa: Tuple[str, str], context: str) -> str:
        previous_q, previous_a = previous_qa
        
        return f"""基于之前的问答，提出一个跟进问题：
        
        之前问题：{previous_q}
        候选人回答：{previous_a}
        
        相关背景知识：
        {context}
        
        要求：
        1. 问题要与之前的问答、相关专业知识相关
        2. 可以深入挖掘，要求举例，或者询问替代方案
        3. 可以稍微增加难度
        4. 如果候选人是模糊的回答，可以要求澄清
        
        只输出问题，不要输出其他内容。"""
    
    @staticmethod
    def get_closing_prompt(evaluation: Dict, position: str) -> str:
        strengths = evaluation.get('strengths', [])
        weaknesses = evaluation.get('weaknesses', [])
        overall = evaluation.get('overall_score', 0)
        
        return f"""面试结束，请向候选人做总结。
        
        职位：{position}
        总体评分：{overall}/5
        优势：{', '.join(strengths) if strengths else '无明显突出优势'}
        待改进：{', '.join(weaknesses) if weaknesses else '无明显短板'}
        
        要求：
        1. 感谢候选人参加面试
        2. 简要总结表现（优势和改进点）
        3. 说明下一步流程（如：3个工作日内通知结果）
        4. 保持专业和友好
        
        输出格式：
        面试官：[你的结束语]"""


class InterviewAgent:
    """面试官代理"""
    
    def __init__(self, position: str = None):
        self.position = position or INTERVIEW_CONFIG.positions[0]
        self.phase = InterviewPhase.WELCOME
        self.questions_asked = []
        self.qa_history = []
        self.evaluation = EvaluationResult()
        
        self.llm = LLMProvider.create_provider()
        
        self.technical_questions_count = 0
        self.behavioral_questions_count = 0
        self.current_context = ""
        self._init_fallback_system()
        logger.info(f"面试官代理初始化完成，职位：{self.position}")
        
    def _init_fallback_system(self):
        """初始化统一的备用问题系统"""
        self.fallback_questions = {
            # 欢迎和结束语（固定）
            "welcome": [
                "你好，我是你的{position}面试官。我们开始今天的面试吧。首先，请介绍一下你最近做过的项目。",
                "欢迎参加{position}面试。请先简要介绍你的技术背景和主要经验。"
            ],
            "closing": [
                "感谢你参加今天的面试，我们会尽快通知你结果。",
                "面试到此结束，感谢你的时间和分享，后续会有HR与你联系。"
            ],
            
            # 技术问题（按职位分类）
            "technical": {
                "Python后端开发": [
                    "请解释Python中的GIL（全局解释器锁）及其对多线程编程的影响。",
                    "Django和Flask框架的主要区别是什么？各自适用什么场景？",
                    "如何设计RESTful API？请说明核心原则和最佳实践。"
                ],
                "Java开发": [
                    "请解释JVM内存模型和垃圾回收机制。",
                    "Spring框架的核心特性有哪些？IoC和AOP是什么？"
                ],
                "通用": [
                    "请你解释一下RESTful API的设计原则。",
                    "请说明数据库索引的原理和优化策略。"
                ]
            },
            
            # 行为问题（按类型分类）
            "behavioral": {
                "压力处理": "请分享一个你面临压力或紧迫期限的经历，你是如何处理的？",
                "团队合作": "描述一次你与团队成员发生分歧的情况，你是如何解决的？",
                "学习能力": "请举例说明你如何学习一项新技术或工具，并应用于实际项目中？",
                "失败经验": "描述一次你失败的经历，你从中学到了什么？",
                "优先级管理": "你如何确定任务的优先级？请举例说明。",
                "技术难题": "请分享一个你解决过的复杂技术难题，描述问题、你的角色和最终结果。"
            },
            
            # 编码问题
            "coding": [
                "实现一个LRU缓存算法，说明时间复杂度和空间复杂度。",
                "写一个函数判断字符串是否为有效的括号序列。"
            ],
            
            # 智能追问模板
            "followup": {
                "short_answer": [
                    "刚才的问题可能需要更详细的回答。能否更具体地解释一下？",
                    "关于这个问题，能否分享更多细节或例子？"
                ],
                "vague_answer": [
                    "你提到了一些概念，能否给出具体的例子或数据支持？",
                    "在实际项目中，你是如何应用这个方案的？"
                ],
                "low_depth": [
                    "请深入解释这个技术的底层原理。",
                    "在大规模生产环境中，这个方案可能遇到什么挑战？"
                ]
            }
        }
    
    def _get_fallback_question(self, question_type: str = None, 
                              context: Dict = None) -> str:
        """
        统一的备用问题获取
        
        Args:
            question_type: 问题类型 (technical/behavioral/coding/welcome/closing)
            context: 上下文信息，用于智能选择
        """
        import random
        
        # 如果没有指定类型，根据当前阶段推断
        if question_type is None:
            question_type = self._get_current_question_type()
        
        # 特殊处理：欢迎和结束语
        if question_type in ["welcome", "closing"]:
            questions = self.fallback_questions.get(question_type, [])
            if questions:
                question = random.choice(questions)
                return question.format(position=self.position)
        
        # 智能追问逻辑
        if context and question_type == "followup":
            followup_type = self._analyze_answer_for_followup(context.get("answer", ""))
            followup_templates = self.fallback_questions["followup"].get(followup_type)
            if followup_templates:
                return random.choice(followup_templates)
        
        # 技术问题：优先职位特定，后通用
        if question_type == "technical":
            # 职位特定的技术问题
            if self.position in self.fallback_questions["technical"]:
                questions = self.fallback_questions["technical"][self.position]
                if questions:
                    return random.choice(questions)
            # 通用技术问题
            return random.choice(self.fallback_questions["technical"]["通用"])
        
        # 行为问题：随机选择一个类型
        elif question_type == "behavioral":
            # 可以选择特定类型，或随机选择
            if context and "behavioral_type" in context:
                behavioral_type = context["behavioral_type"]
                if behavioral_type in self.fallback_questions["behavioral"]:
                    return self.fallback_questions["behavioral"][behavioral_type]
            
            # 随机选择一个行为问题类型
            behavioral_types = list(self.fallback_questions["behavioral"].keys())
            selected_type = random.choice(behavioral_types)
            return self.fallback_questions["behavioral"][selected_type]
        
        # 编码问题
        elif question_type == "coding":
            questions = self.fallback_questions.get("coding", [])
            if questions:
                return random.choice(questions)
        
        # 默认备用
        return "请继续你的回答。"
    
    def _get_current_question_type(self) -> str:
        """根据当前面试阶段返回问题类型"""
        phase_to_type = {
            InterviewPhase.WELCOME: "welcome",
            InterviewPhase.TECHNICAL: "technical",
            InterviewPhase.BEHAVIORAL: "behavioral",
            InterviewPhase.CODING: "coding",
            InterviewPhase.CLOSING: "closing"
        }
        return phase_to_type.get(self.phase, "technical")
    
    def _analyze_answer_for_followup(self, answer: str) -> str:
        """分析回答特征，确定追问类型"""
        if len(answer) < 50:
            return "short_answer"
        elif any(word in answer for word in ["可能", "大概", "不太确定", "应该是"]):
            return "vague_answer"
        elif len(answer.split()) < 80 and "具体" not in answer:
            return "low_depth"
        else:
            return "short_answer"  # 默认 
    

    def start_interview(self) -> str:
        """开始面试"""
        self.phase = InterviewPhase.WELCOME
        
        context_docs = rag_engine.retrieve_for_interview(
            "introduction", self.position
        )
        self.current_context = "\n".join([doc.page_content for doc in context_docs[:2]])
        
        prompt = PromptTemplates.get_welcome_prompt(self.position)
        welcome_message = self._generate_response(prompt)
        
        first_question = self._generate_technical_question()
        
        full_welcome = f"{welcome_message}\n\n{first_question}"
        
        self.questions_asked.append(first_question)
        self.technical_questions_count += 1
        
        logger.info(f"面试开始 - 职位：{self.position}")
        return full_welcome
    
    def _generate_response(self, prompt: str, max_retries: int = 2) -> str:
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(prompt)
                cleaned = self._clean_response(response)
                
                if cleaned and len(cleaned) > 15:
                    logger.info(f"LLM响应成功: {cleaned[:50]}...")
                    return cleaned
                
                logger.warning(f"第{attempt+1}次响应过短: {cleaned}")
                
            except Exception as e:
                logger.error(f"第{attempt+1}次生成失败: {e}")
                
            if attempt < max_retries - 1:
                import time
                time.sleep(0.5)
        
        # LLM失败，根据prompt类型使用合适的备用问题
        if "行为问题" in prompt or "behavioral" in prompt.lower():
            return self._get_fallback_question("behavioral")
        elif "技术问题" in prompt or "technical" in prompt.lower():
            return self._get_fallback_question("technical")
        elif "欢迎" in prompt or "welcome" in prompt.lower():
            return self._get_fallback_question("welcome")
        elif "结束" in prompt or "closing" in prompt.lower():
            return self._get_fallback_question("closing")
        else:
            return self._get_fallback_question()

    def _clean_response(self, response: str) -> str:
        if not response:
            return ""
            
        cleaned = response.strip()
        
        prefixes = ["面试官：", "Assistant：", "AI：", "回答：", "Output："]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        return cleaned.strip()
    
    def _generate_technical_question(self) -> str:
        # 1. 尝试从RAG获取
        try:
            context_docs = rag_engine.retrieve_for_interview(
                "technical", 
                self.position,
                self.questions_asked[-3:] if self.questions_asked else None
            )
            
            if context_docs:
                context = "\n".join([doc.page_content for doc in context_docs[:3]])
                self.current_context = context
                
                prompt = PromptTemplates.get_technical_question_prompt(context, self.position)
                question = self._generate_response(prompt)
                
                if question and len(question) > 10:
                    if not question.endswith("？") and not question.endswith("?"):
                        question += "？"
                    return question
        except Exception as e:
            logger.warning(f"生成自定义技术问题失败: {e}")
        
        # 2. 使用备用系统
        return self._get_fallback_question("technical")
    
    def process_answer(self, answer: str, audio_data: bytes = None, silence_analysis: Dict = None) -> Tuple[str, Dict]:
        """
        处理候选人的回答
        """
        if not self.questions_asked:
            logger.error("还没有提出问题，无法处理回答")
            return "请让我先提出问题。", {}
        
        last_question = self.questions_asked[-1]
        
        # 如果没有传入沉默分析但传入了音频数据，分析沉默
        if audio_data and not silence_analysis:
            try:
                from modules.audio_processor import audio_processor
                silence_analysis = audio_processor.analyze_audio_silence(audio_data)
            except Exception as e:
                logger.error(f"沉默分析失败: {e}")
                silence_analysis = None
        
        # 评估回答（传入沉默分析结果）
        evaluation_data = self._evaluate_answer(last_question, answer, silence_analysis)
        
        # 记录沉默分析
        if silence_analysis:
            self.evaluation.silence_analysis = silence_analysis
            
            # 如果有沉默分析，添加到评估数据
            if evaluation_data and isinstance(evaluation_data, dict):
                evaluation_data["raw_silence_analysis"] = silence_analysis
                
                # 计算犹豫分数
                from modules.audio_processor import SilenceAnalyzer
                hesitation_score = SilenceAnalyzer.calculate_hesitation_score(silence_analysis)
                evaluation_data["hesitation_score"] = hesitation_score
        
        # 记录QA历史
        self.qa_history.append({
            "question": last_question,
            "answer": answer,
            "evaluation": evaluation_data,
            "silence_analysis": silence_analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        # 更新评估结果
        if evaluation_data and 'technical_scores' in evaluation_data:
            for criterion, score in evaluation_data['technical_scores'].items():
                self.evaluation.add_feedback(criterion, score, "")
        
        # 决定下一步
        next_response = self._decide_next_step(answer, evaluation_data)
        
        return next_response, evaluation_data
    
    def _evaluate_answer(self, question: str, answer: str, silence_analysis: Dict = None) -> Dict:
        prompt = PromptTemplates.get_evaluation_prompt(
            question=question,
            answer=answer,
            silence_analysis=silence_analysis,
            criteria=INTERVIEW_CONFIG.evaluation_criteria
        )
        
        try:
            response = self._generate_response(prompt)
            evaluation = json.loads(response)
            
            logger.debug(f"回答评估完成 - 问题: {question[:50]}...")
            return evaluation
            
        except json.JSONDecodeError as e:
            logger.error(f"评估结果JSON解析失败: {e}\n响应: {response}")
            
            return {
                "technical_scores": {c: 3.0 for c in INTERVIEW_CONFIG.evaluation_criteria},
                "communication_evaluation": {
                    "clarity": 3.0,
                    "conciseness": 3.0,
                    "response_fluency": 3.0,
                    "silence_impact": "无法分析沉默模式"
                },
                "detailed_feedback": "由于技术原因，无法进行详细评估。",
                "follow_up_question": "你能更详细地解释一下吗？"
            }
        except Exception as e:
            logger.error(f"评估失败: {e}")
            return {}
    
    def _decide_next_step(self, answer: str, evaluation: Dict) -> str:
        # 检查是否需要跟进问题
        needs_follow_up = (
            len(answer) < 50 or
            "不太清楚" in answer or "不了解" in answer or "不知道" in answer or
            evaluation.get('technical_scores', {}).get('技术知识深度', 3) < 2.5
        )
        
        if self.phase == InterviewPhase.TECHNICAL:
            if self.technical_questions_count >= INTERVIEW_CONFIG.max_technical_questions:
                self.phase = InterviewPhase.BEHAVIORAL
                return self._generate_behavioral_question()
            elif needs_follow_up and evaluation.get('follow_up_question'):
                follow_up = evaluation['follow_up_question']
                self.questions_asked.append(follow_up)
                return follow_up
            else:
                next_question = self._generate_technical_question()
                self.questions_asked.append(next_question)
                self.technical_questions_count += 1
                return next_question
                
        elif self.phase == InterviewPhase.BEHAVIORAL:
            if self.behavioral_questions_count >= INTERVIEW_CONFIG.max_behavioral_questions:
                self.phase = InterviewPhase.CLOSING
                return self._generate_closing()
            else:
                next_question = self._generate_behavioral_question()
                self.questions_asked.append(next_question)
                self.behavioral_questions_count += 1
                return next_question
                
        else:
            return "请继续。"
    
    def _generate_behavioral_question(self) -> str:
        # 1. 首先尝试从RAG获取专业的行为问题
        try:
            context_docs = rag_engine.retrieve_for_interview("behavioral", self.position)
            if context_docs:
                context = "\n".join([doc.page_content for doc in context_docs[:2]])
                prompt = f"""基于以下行为面试知识，提出一个针对{self.position}职位的行为问题：
                
                {context}
                
                只输出问题，不要其他内容。"""
                
                custom_question = self._generate_response(prompt)
                if custom_question and len(custom_question) > 10:
                    return custom_question
        except Exception as e:
            logger.warning(f"生成自定义行为问题失败: {e}")
        
        # 2. 使用统一的备用系统
        return self._get_fallback_question("behavioral")
        
    
    def _generate_closing(self) -> str:
        self.phase = InterviewPhase.CLOSING
        
        self.evaluation.calculate_overall()
        evaluation_dict = self.evaluation.to_dict()
        
        prompt = PromptTemplates.get_closing_prompt(evaluation_dict, self.position)
        closing = self._generate_response(prompt)
        
        return closing
    
    def get_interview_summary(self) -> Dict:
        return {
            "position": self.position,
            "phase": self.phase.value,
            "total_questions": len(self.questions_asked),
            "technical_questions": self.technical_questions_count,
            "behavioral_questions": self.behavioral_questions_count,
            "qa_history": [
                {
                    "question": qa["question"],
                    "answer": qa["answer"][:200] + "..." if len(qa["answer"]) > 200 else qa["answer"],
                    "has_evaluation": bool(qa.get("evaluation"))
                }
                for qa in self.qa_history
            ],
            "evaluation": self.evaluation.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    def reset(self, new_position: str = None):
        """重置面试状态"""
        if new_position:
            self.position = new_position
            
        self.phase = InterviewPhase.WELCOME
        self.questions_asked = []
        self.qa_history = []
        self.evaluation = EvaluationResult()
        self.technical_questions_count = 0
        self.behavioral_questions_count = 0
        self.current_context = ""
        
        logger.info(f"面试官代理已重置，职位：{self.position}")

# 全局面试官实例
interview_agent = InterviewAgent()