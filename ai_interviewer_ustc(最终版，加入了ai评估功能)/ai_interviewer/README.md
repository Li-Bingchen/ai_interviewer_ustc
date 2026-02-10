# 🎙️ AI 面试官

一个基于 Streamlit 的智能面试训练系统，支持语音/文字对话、RAG 知识检索和 AI 面试评价报告。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 核心特性

### 🎨 双主题系统
- **赛博训练舱**：深蓝黑 + 霓虹青紫，流动极光背景，FUI 装饰
- **霓虹实验室**：多彩渐变，液态玻璃质感，全息光泽效果
- 实时切换，磨砂玻璃效果，流畅动画

### 💬 智能对话
- **多种面试官角色**：技术面试官、算法面试官、系统设计面试官、行为面试官、计算机基础面试官
- **流式对话**：基于大语言模型的实时对话
- **上下文记忆**：保持完整的对话历史

### 🎙️ 语音交互
- **语音输入**：支持实时语音识别（ASR）
- **语音播报**：AI 回复自动语音合成（TTS）
- **自动播放**：语音模式下无需手动操作

### 📚 RAG 知识检索
- **向量数据库**：基于 ChromaDB 的知识库
- **多领域支持**：计算机科学各个方向
- **智能检索**：自动为面试官提供相关知识背景
- **可视化展示**：查看每轮检索到的知识片段

### 📊 AI 面试报告
- **深度分析**：基于 Qwen-max 的面试表现评估
- **多维度评价**：技术能力、沟通表达、问题解决等
- **改进建议**：针对性的提升方向
- **导出功能**：支持 Markdown、TXT 格式

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Anaconda/Miniconda
- 网络连接（用于 API 调用和字体加载）

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd ai_interviewer
```

#### 2. 创建 Conda 环境
```bash
conda create -n AI_interviewer python=3.8
conda activate AI_interviewer
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置 API 密钥

编辑 `config.py`，填入你的 API 密钥：
```python
STEPFUN_API_KEY = "your-api-key-here"
```

#### 5. 构建知识库（可选）

如果需要使用 RAG 功能：
```bash
python scripts/build_cs_vector_store.py
```

### 启动应用

#### 方法 1：双击启动脚本（Windows）
```
双击 "启动应用.bat"
```

#### 方法 2：命令行启动
```bash
conda activate AI_interviewer
streamlit run app_streamlit.py
```

应用将在浏览器中自动打开：`http://localhost:8501`

---

## 📖 使用指南

### 1. 选择主题

在左侧边栏顶部的"视觉主题"下拉菜单中选择：
- **赛博训练舱**：适合长时间使用，视觉舒适
- **霓虹实验室**：视觉冲击力强，适合展示

### 2. 配置面试官

在侧边栏中：
- 选择面试官类型（技术、算法、系统设计等）
- 或自定义系统提示词
- 开启/关闭语音播报（TTS）

### 3. 配置知识库（可选）

如果开启 RAG：
- 选择检索领域（如 cs）
- 调整检索条数（Top-K）

### 4. 开始面试

#### 语音模式
1. 切换到"🎙️ 语音对话" Tab
2. 点击麦克风图标开始录音
3. 录音结束后自动识别并发送
4. AI 回复会自动语音播放

#### 文字模式
1. 切换到"💬 文字对话" Tab
2. 在输入框中输入消息
3. 点击"发送"按钮

### 5. 查看知识检索

切换到"📚 RAG 知识检索" Tab，查看每轮检索到的知识片段。

### 6. 生成面试报告

面试结束后：
1. 切换到"📊 面试报告" Tab
2. 点击"生成 AI 面试评价报告"
3. 等待 15-30 秒生成报告
4. 下载报告（Markdown 或 TXT 格式）

---

## 📁 项目结构

```
ai_interviewer/
├── app_streamlit.py          # 主应用
├── config.py                  # 配置文件
├── requirements.txt           # 依赖列表
├── 启动应用.bat              # Windows 启动脚本
├── .gitignore                 # Git 忽略文件
├── README.md                  # 项目说明
├── 主题系统文档.md           # 主题详细文档
│
├── themes/                    # 主题系统
│   ├── __init__.py           # 主题管理器
│   ├── theme_cyber.py        # 赛博训练舱主题
│   └── theme_neon.py         # 霓虹实验室主题
│
├── modules/                   # 功能模块
│   ├── __init__.py
│   ├── llm_agent.py          # LLM 对话
│   ├── rag_engine.py         # RAG 检索
│   ├── audio_processor.py    # 语音处理
│   └── ai_report.py          # 面试报告生成
│
├── scripts/                   # 工具脚本
│   ├── build_cs_vector_store.py  # 构建向量库
│   └── test_rag.py           # 测试 RAG
│
├── data/                      # 知识数据
│   └── cs/                   # 计算机科学领域
│       ├── qa_backend.jsonl
│       ├── qa_database.jsonl
│       ├── qa_datastructure.jsonl
│       ├── qa_network.jsonl
│       └── qa_system_design.jsonl
│
├── vector_db/                 # 向量数据库
│   └── cs/                   # 计算机科学向量库
│
├── utils/                     # 工具函数
│   ├── logger.py
│   └── video_recorder.py
│
└── output(report&video)/      # 输出目录
```

---

## 🎨 主题系统

### 赛博训练舱

**视觉特征**：
- 深蓝黑背景 + 霓虹青 (#00f5ff) + 紫粉 (#b24bf3)
- 流动的青紫色极光
- FUI 风格的角落装饰
- 磨砂玻璃卡片

**核心动效**：
- 背景极光流动（20秒循环）
- 对话卡片滑入动画
- 按钮波纹扩散效果

### 霓虹实验室

**视觉特征**：
- 深蓝黑背景 + 多彩渐变（粉/青/紫/金）
- 多彩弥散光流动
- 液态玻璃质感
- 全息光泽效果

**核心动效**：
- 弥散光流动（25秒循环）
- 全息光泽扫过卡片
- 渐变彩虹标题脉动
- 按钮磁吸悬停效果

详细说明请查看 [主题系统文档.md](./主题系统文档.md)

---

## 🛠️ 技术栈

### 前端
- **Streamlit** - Web 应用框架
- **CSS3** - 自定义样式和动画
- **Google Fonts** - 字体加载

### 后端
- **Python 3.8+** - 核心语言
- **LangChain** - LLM 应用框架
- **ChromaDB** - 向量数据库
- **OpenAI API** - 语音识别和合成

### AI 模型
- **Step-1-32k** - 对话模型
- **Qwen-max** - 面试报告生成
- **text-embedding-3-large** - 文本嵌入

---

## ⚙️ 配置说明

### config.py

```python
# API 配置
STEPFUN_API_KEY = "your-api-key-here"  # 必填
STEPFUN_BASE_URL = "https://api.stepfun.com/v1"

# 模型配置
LLM_MODEL = "step-1-32k"
EMBEDDING_MODEL = "text-embedding-3-large"
REPORT_MODEL = "qwen-max"

# 音频配置
AUDIO_SAMPLE_RATE = 16000

# 目录配置
TEMP_DIR = Path(__file__).parent / "temp"
OUTPUT_DIR = Path(__file__).parent / "output(report&video)"
```

### 环境变量（可选）

也可以通过环境变量配置：
```bash
export STEPFUN_API_KEY="your-api-key-here"
```

---

## 📝 常见问题

### Q: 如何切换主题？
**A**: 在左侧边栏顶部的"视觉主题"下拉菜单中选择。

### Q: 语音识别不工作？
**A**: 
1. 检查浏览器是否授权麦克风权限
2. 确认 API 密钥配置正确
3. 检查网络连接

### Q: RAG 检索没有结果？
**A**: 
1. 确认已运行 `build_cs_vector_store.py` 构建向量库
2. 检查 `vector_db/cs/` 目录是否存在
3. 确认选择的领域正确

### Q: 主题切换后页面刷新？
**A**: 这是正常的，Streamlit 需要重新加载 CSS。

### Q: 字体加载慢？
**A**: 字体通过 Google Fonts CDN 加载，需要网络连接。如果网络不好，会自动回退到系统默认字体。

### Q: 如何自定义主题？
**A**: 参考 [主题系统文档.md](./主题系统文档.md) 中的"自定义指南"部分。

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献方式
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 报告问题
请在 Issues 中详细描述：
- 问题现象
- 复现步骤
- 环境信息（Python 版本、操作系统等）
- 错误日志

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

### 设计灵感
- [redink.top](https://redink.top/) - 磨砂玻璃和液态效果
- [watcha.cn](https://watcha.cn/products/xiao-yue) - 科技感设计元素
- 《银翼杀手 2049》- 赛博朋克美学
- 《攻壳机动队》- 未来科技风格

### 技术支持
- [Streamlit](https://streamlit.io/) - 优秀的 Web 应用框架
- [LangChain](https://www.langchain.com/) - 强大的 LLM 应用框架
- [ChromaDB](https://www.trychroma.com/) - 高效的向量数据库

---

## 📞 联系方式

如有问题或建议，欢迎联系：
- 项目主页：[GitHub Repository]
- 问题反馈：[GitHub Issues]

---

**祝你面试顺利！** 🚀✨

