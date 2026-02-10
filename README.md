# 🎙️ AI 面试官 USTC

一个基于大语言模型（LLM）与语音交互技术的智能化模拟面试系统。系统旨在为求职者、学生提供沉浸式的面试训练体验，通过语音对话、知识库检索、智能评估等功能，帮助用户提升面试技巧与专业能力。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 核心功能

### 💬 智能语音对话
- **语音输入与文字输入**：支持两种交互方式
- **实时语音识别**：基于 StepFun ASR 的精准识别
- **智能语音合成播报**：基于 StepFun TTS 的自然语音输出
- **流式对话响应**：模拟真实面试节奏，LLM 流式输出实时显示

### 👨‍💼 多角色面试官
- **预设多种面试官角色**：技术面试官、算法面试官、系统设计面试官、行为面试官、计算机基础面试官
- **自定义提示词**：灵活调整面试风格与难度
- **上下文记忆**：基于历史对话的连贯追问，保持完整的对话历史

### 📚 知识库检索增强（RAG）
- **多领域向量检索**：支持计算机科学等领域的知识检索
- **智能过滤**：可根据难度、主题等元数据过滤检索结果
- **可视化展示**：查看每轮检索到的知识片段与来源

### 📊 面试过程管理
- **完整对话历史记录**：面试过程中的所有对话可追溯
- **一键开始新对话**：快速开始新的面试训练
- **音频文件管理**：临时存储与自动清理
- **语音片段重播**：可重复播放面试中的语音片段

### 🎨 友好的交互界面
- **响应式 Web 界面**：基于 Streamlit，支持移动端与桌面端
- **侧边栏集中控制**：面试设置、角色选择、功能开关集中管理
- **分页展示**：对话、知识检索、面试报告分页清晰展示

---

## 🛠️ 技术架构亮点

### 1. **模块化架构设计**
```
ai_interviewer/
├── audio_processor.py    # 语音处理模块（ASR/TTS）
├── llm_agent.py         # 大语言模型对话模块
├── rag_engine.py        # 检索增强生成模块
├── ai_report.py         # 面试报告生成模块
└── app_streamlit.py     # 前端交互界面
```
各模块职责清晰，耦合度低，便于扩展与维护。

### 2. **流式对话与语音合成联动**
- LLM 流式输出实时显示在界面
- 支持整段语音合成播报
- 音频文件自动管理，避免资源泄露

### 3. **智能断句与语音触发**
- 基于标点的智能断句（`chunking_tool`）
- 为未来实时流式 TTS 预留接口
- 支持中英文混合文本处理

### 4. **异步语音处理**
- 录音、保存、转写全流程异步化
- 避免界面卡顿，提升用户体验
- 支持高并发场景下的音频处理

### 5. **可扩展的知识库系统**
- 支持多领域向量库（如 cs、business、law 等）
- 基于 Chroma + DashScope Embeddings 的检索方案
- 提供建库脚本（`build_cs_vector_store.py`）与测试工具（`test_rag.py`）

### 6. **统一的配置管理**
- API 密钥、路径、模型参数集中管理（`config.py`）
- 支持环境变量与硬编码双模式
- 自动目录初始化，降低部署门槛

---

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Anaconda/Miniconda（推荐）
- 网络连接（用于 API 调用）

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd ai_interviewer
```

#### 2. 创建并激活 Conda 环境
```bash
conda create -n AI_interviewer python=3.8
conda activate AI_interviewer
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置 API 密钥
编辑 `config.py` 文件，填入你的 API 密钥：
```python
STEPFUN_API_KEY = "your-stepfun-api-key-here"
DASHSCOPE_API_KEY = "your-dashscope-api-key-here"  # 如果使用 RAG 功能
```

#### 5. 构建知识库（如需 RAG 功能）
```bash
python scripts/build_cs_vector_store.py
```

### 启动应用

#### Windows 用户：
```
双击 "启动应用.bat"
```

#### macOS/Linux 用户：
```bash
conda activate AI_interviewer
streamlit run app_streamlit.py
```

应用将在浏览器中自动打开：`http://localhost:8501`

---

## 📖 使用指南

### 1. 基本设置
- 在侧边栏选择面试官类型
- 调整语音播报开关（TTS）
- 选择视觉主题（深色/浅色）

### 2. 开始面试

#### 🎙️ 语音对话模式
1. 切换到"语音对话"标签页
2. 点击麦克风图标开始录音
3. 说话结束后自动识别并发送
4. AI 回复会自动语音播放

#### 💬 文字对话模式
1. 切换到"文字对话"标签页
2. 在输入框中输入回答
3. 点击"发送"按钮或按 Enter 键

### 3. 使用知识检索（RAG）
1. 在侧边栏开启 RAG 功能
2. 选择检索领域（如计算机科学）
3. 面试过程中自动检索相关知识
4. 在"📚 RAG 知识检索"标签页查看检索结果

### 4. 生成面试报告
面试结束后：
1. 切换到"📊 面试报告"标签页
2. 点击"生成 AI 面试评价报告"
3. 等待生成完整的评估报告
4. 可下载报告（支持 Markdown 和 TXT 格式）

---

## 📁 项目结构

```
ai_interviewer/
├── app_streamlit.py          # 主应用（Streamlit 界面）
├── config.py                  # 统一配置文件
├── requirements.txt           # Python 依赖包
├── 启动应用.bat              # Windows 启动脚本
│
├── modules/                   # 核心功能模块
│   ├── llm_agent.py          # 大语言模型对话模块
│   ├── rag_engine.py         # RAG 检索增强模块
│   ├── audio_processor.py    # 语音处理模块（ASR/TTS）
│   └── ai_report.py          # AI 面试报告生成模块
│
├── scripts/                   # 工具脚本
│   ├── build_cs_vector_store.py  # 构建向量数据库
│   └── test_rag.py           # RAG 功能测试
│
├── data/                      # 知识库数据源
│   └── cs/                   # 计算机科学领域数据
│       ├── qa_backend.jsonl
│       ├── qa_database.jsonl
│       ├── qa_datastructure.jsonl
│       └── ...（其他专业领域）
│
├── vector_db/                 # 向量数据库存储
│   └── cs/                   # 计算机科学向量库
│
├── temp_audio/               # 临时音频文件存储
└── outputs/                  # 输出文件（面试报告等）
```

---

## ⚙️ 配置说明

### API 密钥配置
编辑 `config.py` 文件：
```python
# 步 Fun API（用于语音识别和合成）
STEPFUN_API_KEY = "your-api-key-here"

# DashScope API（用于文本嵌入，RAG 功能需要）
DASHSCOPE_API_KEY = "your-dashscope-api-key-here"

# 其他配置项
LLM_MODEL = "step-1-32k"           # 对话模型
REPORT_MODEL = "qwen-max"         # 报告生成模型
EMBEDDING_MODEL = "text-embedding-3-large"  # 嵌入模型
```

### 模型参数调整
- `MAX_TOKENS`: 控制回答长度
- `TEMPERATURE`: 控制回答随机性（0-1）
- `TOP_K`: RAG 检索返回的结果数量

---

## 📝 常见问题

### Q: 语音识别不准确或无法工作？
**A**: 
1. 检查浏览器麦克风权限设置
2. 确认 STEPFUN_API_KEY 配置正确
3. 尝试在安静环境中录音
4. 检查网络连接是否正常

### Q: RAG 检索没有返回结果？
**A**:
1. 确认已运行 `build_cs_vector_store.py` 构建向量库
2. 检查 `vector_db/` 目录是否存在且包含数据
3. 确认在侧边栏开启了 RAG 功能
4. 检查 DashScope API 密钥是否正确配置

### Q: 如何自定义面试官角色？
**A**: 
1. 在侧边栏选择"自定义提示词"选项
2. 在文本框中输入你的自定义提示词
3. 可参考预设角色的提示词格式

### Q: 面试报告生成失败？
**A**:
1. 确保至少有 3 轮以上的对话记录
2. 检查网络连接，报告生成需要调用 Qwen-max 模型
3. 如多次失败，可尝试清除对话历史后重新开始

### Q: 如何导出对话记录？
**A**:
目前支持通过面试报告导出功能保存对话摘要和评价，完整的对话历史可通过复制网页内容保存。

---

## 🔮 未来扩展方向
1. **视频面试模拟**：增加虚拟人像与面部表情交互
2. **多轮面试场景**：模拟群面、技术面、HR面等不同场景
3. **云端部署**：支持多租户和用户管理系统
4. **更多专业领域**：扩展法律、金融、医学等专业面试题库
5. **实时反馈**：在面试过程中提供实时技巧提示

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目！

### 贡献流程
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/NewFeature`)
3. 提交更改 (`git commit -m 'Add NewFeature'`)
4. 推送到分支 (`git push origin feature/NewFeature`)
5. 创建 Pull Request

### 开发规范
- 遵循 PEP 8 Python 代码规范
- 为新功能添加适当的注释和文档
- 确保更改不影响现有功能
- 提交前运行基本测试

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

### 技术栈致谢
- **[Streamlit](https://streamlit.io/)** - 快速构建数据应用的优秀框架
- **[LangChain](https://www.langchain.com/)** - LLM 应用开发框架
- **[ChromaDB](https://www.trychroma.com/)** - 开源向量数据库
- **[StepFun API](https://stepfun.com/)** - 语音识别与合成服务

### 数据来源
- 计算机科学面试题库整理自开源社区和经典面试书籍
- 感谢所有为开源知识库贡献内容的开发者

---

## 📞 联系方式

如有问题或建议：
- 提交 [GitHub Issue](https://github.com/your-repo/issues)
- 查看项目主页获取最新信息

---

**开始你的面试训练之旅，祝你求职顺利！** 🚀
