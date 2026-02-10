# -*- coding: utf-8 -*-
"""
主题方案 A：赛博训练舱
深色 + 霓虹青紫 + 流动极光 + FUI 装饰
"""

THEME_NAME = "赛博训练舱"
THEME_ID = "cyber"

CSS_STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Inter:wght@300;400;500;600&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
    /* ==================== 全局样式 ==================== */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0a0e27 100%);
        position: relative;
        overflow-x: hidden;
    }
    
    /* 背景极光效果 */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(0, 245, 255, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(178, 75, 243, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(0, 200, 255, 0.1) 0%, transparent 60%);
        animation: aurora-flow 20s ease-in-out infinite;
        pointer-events: none;
        z-index: -1;
    }
    
    @keyframes aurora-flow {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(5%, 5%) rotate(5deg); }
        66% { transform: translate(-5%, 3%) rotate(-3deg); }
    }
    
    /* 网格背景 */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: -1;
    }
    
    /* 确保内容在背景之上 */
    .main, 
    [data-testid="stSidebar"],
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .stApp > header,
    .stApp > div {
        position: relative;
        z-index: 1;
    }
    
    /* ==================== 顶部导航栏 ==================== */
    [data-testid="stHeader"] {
        background: rgba(10, 14, 39, 0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0, 245, 255, 0.2);
    }
    
    /* ==================== 侧边栏样式 ==================== */
    [data-testid="stSidebar"] {
        background: rgba(15, 20, 45, 0.7);
        backdrop-filter: blur(40px) saturate(180%);
        border-right: 1px solid rgba(0, 245, 255, 0.3);
        box-shadow: 4px 0 30px rgba(0, 245, 255, 0.1);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
        color: #e0e7ff;
    }
    
    [data-testid="stSidebar"] h1 {
        font-family: 'Orbitron', sans-serif;
        color: #00f5ff;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
        font-weight: 700;
        letter-spacing: 2px;
    }
    
    /* ==================== 主容器 ==================== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    
    /* ==================== 标题样式 ==================== */
    h1 {
        font-family: 'Orbitron', sans-serif;
        color: #00f5ff;
        text-shadow: 0 0 30px rgba(0, 245, 255, 0.6);
        font-weight: 900;
        letter-spacing: 3px;
        margin-bottom: 0.5rem;
    }
    
    h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #b24bf3;
        text-shadow: 0 0 15px rgba(178, 75, 243, 0.4);
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    h4 {
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
        color: #00d4ff;
        font-weight: 600;
    }
    
    p, .stMarkdown {
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #c7d2fe;
    }
    
    /* ==================== 对话卡片 ==================== */
    .chat-card-user {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.15) 0%, rgba(0, 200, 255, 0.1) 100%);
        border: 1px solid rgba(0, 245, 255, 0.4);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 12px 0;
        margin-left: 15%;
        box-shadow: 
            0 4px 20px rgba(0, 245, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        animation: slide-in-right 0.4s ease-out;
        backdrop-filter: blur(10px);
    }
    
    /* FUI 装饰 - 用户消息 */
    .chat-card-user::before {
        content: '';
        position: absolute;
        top: 8px;
        right: 8px;
        width: 20px;
        height: 20px;
        border-top: 2px solid rgba(0, 245, 255, 0.6);
        border-right: 2px solid rgba(0, 245, 255, 0.6);
    }
    
    .chat-card-user::after {
        content: '';
        position: absolute;
        bottom: 8px;
        left: 8px;
        width: 20px;
        height: 20px;
        border-bottom: 2px solid rgba(0, 245, 255, 0.6);
        border-left: 2px solid rgba(0, 245, 255, 0.6);
    }
    
    .chat-card-assistant {
        background: rgba(20, 25, 50, 0.8);
        border: 1px solid rgba(178, 75, 243, 0.3);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 12px 0;
        margin-right: 15%;
        box-shadow: 
            0 4px 20px rgba(178, 75, 243, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        position: relative;
        animation: slide-in-left 0.4s ease-out;
        backdrop-filter: blur(10px);
    }
    
    /* FUI 装饰 - AI 消息 */
    .chat-card-assistant::before {
        content: '';
        position: absolute;
        top: 8px;
        left: 8px;
        width: 20px;
        height: 20px;
        border-top: 2px solid rgba(178, 75, 243, 0.6);
        border-left: 2px solid rgba(178, 75, 243, 0.6);
    }
    
    .chat-card-assistant::after {
        content: '';
        position: absolute;
        bottom: 8px;
        right: 8px;
        width: 20px;
        height: 20px;
        border-bottom: 2px solid rgba(178, 75, 243, 0.6);
        border-right: 2px solid rgba(178, 75, 243, 0.6);
    }
    
    .chat-card-user p, .chat-card-assistant p {
        margin: 0;
        color: #e0e7ff;
        font-weight: 400;
    }
    
    @keyframes slide-in-right {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slide-in-left {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* ==================== RAG 卡片 ==================== */
    .rag-card {
        background: rgba(20, 25, 50, 0.6);
        border-left: 4px solid #00f5ff;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 10px 0;
        box-shadow: 
            0 2px 15px rgba(0, 245, 255, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        animation: fade-in 0.3s ease-out;
    }
    
    .rag-card .rag-query {
        color: #00f5ff;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 8px;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
    }
    
    .rag-card .rag-content {
        color: #c7d2fe;
        font-size: 13px;
        line-height: 1.7;
        white-space: pre-wrap;
    }
    
    .rag-meta {
        color: #818cf8;
        font-size: 12px;
        margin-top: 6px;
        opacity: 0.8;
    }
    
    @keyframes fade-in {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* ==================== 按钮样式 ==================== */
    .stButton > button {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(0, 200, 255, 0.15) 100%);
        border: 1px solid rgba(0, 245, 255, 0.5);
        color: #00f5ff;
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(0, 245, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.3) 0%, rgba(0, 200, 255, 0.25) 100%);
        border-color: #00f5ff;
        box-shadow: 
            0 0 30px rgba(0, 245, 255, 0.4),
            inset 0 0 20px rgba(0, 245, 255, 0.1);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* ==================== 输入框样式 ==================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(20, 25, 50, 0.6);
        border: 1px solid rgba(0, 245, 255, 0.3);
        color: #e0e7ff;
        border-radius: 10px;
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00f5ff;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    }
    
    /* ==================== 选择框样式 ==================== */
    .stSelectbox > div > div {
        background: rgba(20, 25, 50, 0.6);
        border: 1px solid rgba(0, 245, 255, 0.3);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    .stSelectbox [data-baseweb="select"] {
        color: #e0e7ff;
    }
    
    /* ==================== Tab 样式 ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(20, 25, 50, 0.4);
        padding: 8px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 1px solid rgba(0, 245, 255, 0.2);
        color: #818cf8;
        border-radius: 8px;
        padding: 10px 20px;
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 245, 255, 0.1);
        border-color: rgba(0, 245, 255, 0.4);
        color: #00f5ff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(0, 200, 255, 0.15) 100%);
        border-color: #00f5ff;
        color: #00f5ff;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    }
    
    /* ==================== 信息提示框 ==================== */
    .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(20, 25, 50, 0.6);
        border-left-width: 4px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    .stInfo {
        border-left-color: #00f5ff;
        color: #c7d2fe;
    }
    
    /* ==================== 隐藏默认元素 ==================== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* ==================== 滚动条样式 ==================== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 14, 39, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00f5ff 0%, #b24bf3 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00d4ff 0%, #a03de0 100%);
    }
    
    /* ==================== 加载动画 ==================== */
    .stSpinner > div {
        border-top-color: #00f5ff !important;
        border-right-color: #b24bf3 !important;
    }
    
    /* ==================== 音频播放器 ==================== */
    audio {
        filter: hue-rotate(180deg) saturate(2);
    }
</style>
"""

