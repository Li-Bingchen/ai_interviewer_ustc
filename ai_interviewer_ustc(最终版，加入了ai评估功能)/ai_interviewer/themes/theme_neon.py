# -*- coding: utf-8 -*-
"""
主题方案 C：霓虹实验室
深蓝黑 + 多彩霓虹 + 液态玻璃 + 强动效
"""

THEME_NAME = "霓虹实验室"
THEME_ID = "neon"

CSS_STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
    /* ==================== 全局样式 ==================== */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        position: relative;
        overflow-x: hidden;
    }
    
    /* 多彩弥散光背景 */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: 
            radial-gradient(circle at 15% 20%, rgba(255, 0, 128, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 85% 30%, rgba(0, 255, 255, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 50% 80%, rgba(128, 0, 255, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 30% 60%, rgba(255, 200, 0, 0.1) 0%, transparent 35%);
        animation: neon-flow 25s ease-in-out infinite;
        pointer-events: none;
        z-index: -1;
        filter: blur(80px);
    }
    
    @keyframes neon-flow {
        0%, 100% { 
            transform: translate(0, 0) rotate(0deg) scale(1); 
            opacity: 1;
        }
        25% { 
            transform: translate(8%, 5%) rotate(5deg) scale(1.05); 
            opacity: 0.9;
        }
        50% { 
            transform: translate(-5%, 8%) rotate(-3deg) scale(1.08); 
            opacity: 0.95;
        }
        75% { 
            transform: translate(6%, -4%) rotate(4deg) scale(1.03); 
            opacity: 0.92;
        }
    }
    
    /* 噪点质感 */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='3.5' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: -1;
        opacity: 0.5;
    }
    
    /* 确保内容在背景之上 */
    .main, 
    [data-testid="stSidebar"],
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .stApp > header,
    .stApp > div {
        position: relative;
        z-index: 2;
    }
    
    /* ==================== 顶部导航栏 ==================== */
    [data-testid="stHeader"] {
        background: rgba(13, 17, 23, 0.85);
        backdrop-filter: blur(25px) saturate(180%);
        border-bottom: 1px solid rgba(255, 0, 255, 0.2);
        box-shadow: 0 4px 30px rgba(255, 0, 255, 0.1);
    }
    
    /* ==================== 侧边栏样式 ==================== */
    [data-testid="stSidebar"] {
        background: rgba(13, 17, 23, 0.9);
        backdrop-filter: blur(30px) saturate(180%);
        border-right: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 4px 0 40px rgba(0, 255, 255, 0.15);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
        color: #e6edf3;
    }
    
    [data-testid="stSidebar"] h1 {
        font-family: 'Exo 2', sans-serif;
        background: linear-gradient(135deg, #ff0080 0%, #00ffff 50%, #ff00ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        letter-spacing: 3px;
        filter: drop-shadow(0 0 20px rgba(255, 0, 255, 0.5));
        animation: rainbow-shift 8s ease-in-out infinite;
    }
    
    @keyframes rainbow-shift {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(255, 0, 255, 0.5)); }
        33% { filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.5)); }
        66% { filter: drop-shadow(0 0 20px rgba(255, 200, 0, 0.5)); }
    }
    
    /* ==================== 主容器 ==================== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    
    /* ==================== 标题样式 ==================== */
    h1 {
        font-family: 'Exo 2', sans-serif;
        background: linear-gradient(135deg, #ff0080 0%, #00ffff 50%, #ff00ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        letter-spacing: 4px;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 30px rgba(255, 0, 255, 0.6));
        animation: title-pulse 3s ease-in-out infinite;
    }
    
    @keyframes title-pulse {
        0%, 100% { 
            filter: drop-shadow(0 0 30px rgba(255, 0, 255, 0.6));
            transform: scale(1);
        }
        50% { 
            filter: drop-shadow(0 0 40px rgba(0, 255, 255, 0.8));
            transform: scale(1.02);
        }
    }
    
    h2, h3 {
        font-family: 'Exo 2', sans-serif;
        color: #00ffff;
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.6);
        font-weight: 700;
        letter-spacing: 2px;
    }
    
    h4 {
        font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
        color: #ff0080;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(255, 0, 128, 0.4);
    }
    
    p, .stMarkdown {
        font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #c9d1d9;
    }
    
    /* ==================== 对话卡片（液态玻璃） ==================== */
    .chat-card-user {
        background: linear-gradient(135deg, 
            rgba(255, 0, 128, 0.1) 0%, 
            rgba(255, 0, 255, 0.08) 100%);
        border: 1px solid rgba(255, 0, 255, 0.4);
        border-radius: 20px;
        padding: 18px 22px;
        margin: 14px 0;
        margin-left: 15%;
        box-shadow: 
            0 8px 32px rgba(255, 0, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            0 0 0 1px rgba(255, 0, 255, 0.1);
        position: relative;
        animation: float-in-right 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(20px) saturate(180%);
        overflow: hidden;
    }
    
    /* 全息光泽效果 */
    .chat-card-user::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 70%
        );
        animation: holographic-shine 3s ease-in-out infinite;
    }
    
    @keyframes holographic-shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .chat-card-assistant {
        background: linear-gradient(135deg, 
            rgba(0, 255, 255, 0.08) 0%, 
            rgba(0, 200, 255, 0.06) 100%);
        border: 1px solid rgba(0, 255, 255, 0.4);
        border-radius: 20px;
        padding: 18px 22px;
        margin: 14px 0;
        margin-right: 15%;
        box-shadow: 
            0 8px 32px rgba(0, 255, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            0 0 0 1px rgba(0, 255, 255, 0.1);
        position: relative;
        animation: float-in-left 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(20px) saturate(180%);
        overflow: hidden;
    }
    
    .chat-card-assistant::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            -45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.08) 50%,
            transparent 70%
        );
        animation: holographic-shine-reverse 3s ease-in-out infinite;
    }
    
    @keyframes holographic-shine-reverse {
        0% { transform: translateX(100%) translateY(-100%) rotate(-45deg); }
        100% { transform: translateX(-100%) translateY(100%) rotate(-45deg); }
    }
    
    .chat-card-user p, .chat-card-assistant p {
        margin: 0;
        color: #e6edf3;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    @keyframes float-in-right {
        from {
            opacity: 0;
            transform: translateX(40px) translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateX(0) translateY(0);
        }
    }
    
    @keyframes float-in-left {
        from {
            opacity: 0;
            transform: translateX(-40px) translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateX(0) translateY(0);
        }
    }
    
    /* ==================== RAG 卡片 ==================== */
    .rag-card {
        background: rgba(13, 17, 23, 0.7);
        border-left: 4px solid #ff0080;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 12px 0;
        box-shadow: 
            0 4px 20px rgba(255, 0, 128, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px) saturate(180%);
        animation: fade-slide-in 0.4s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .rag-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(255, 0, 128, 0.05) 50%, 
            transparent 100%);
        animation: scan-line 2s linear infinite;
    }
    
    @keyframes scan-line {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .rag-card .rag-query {
        color: #ff0080;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 10px;
        text-shadow: 0 0 15px rgba(255, 0, 128, 0.5);
        position: relative;
        z-index: 1;
    }
    
    .rag-card .rag-content {
        color: #c9d1d9;
        font-size: 13px;
        line-height: 1.7;
        white-space: pre-wrap;
        position: relative;
        z-index: 1;
    }
    
    .rag-meta {
        color: #8b949e;
        font-size: 12px;
        margin-top: 8px;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    @keyframes fade-slide-in {
        from { 
            opacity: 0; 
            transform: translateY(15px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    /* ==================== 按钮样式（磁吸效果） ==================== */
    .stButton > button {
        background: linear-gradient(135deg, 
            rgba(255, 0, 128, 0.2) 0%, 
            rgba(255, 0, 255, 0.15) 100%);
        border: 2px solid rgba(255, 0, 255, 0.5);
        color: #ff00ff;
        font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
        font-weight: 700;
        border-radius: 12px;
        padding: 0.7rem 1.8rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 0 30px rgba(255, 0, 255, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 0, 255, 0.4) 0%, transparent 70%);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 400px;
        height: 400px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, 
            rgba(255, 0, 128, 0.3) 0%, 
            rgba(255, 0, 255, 0.25) 100%);
        border-color: #ff00ff;
        box-shadow: 
            0 0 50px rgba(255, 0, 255, 0.5),
            inset 0 0 30px rgba(255, 0, 255, 0.2);
        transform: translateY(-3px) scale(1.02);
        color: #fff;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1);
    }
    
    /* ==================== 输入框样式 ==================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(13, 17, 23, 0.7);
        border: 1px solid rgba(0, 255, 255, 0.3);
        color: #e6edf3;
        border-radius: 12px;
        font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
        backdrop-filter: blur(15px) saturate(180%);
        transition: all 0.3s ease;
        box-shadow: 0 0 0 0 rgba(0, 255, 255, 0);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00ffff;
        box-shadow: 
            0 0 30px rgba(0, 255, 255, 0.4),
            inset 0 0 20px rgba(0, 255, 255, 0.05);
        background: rgba(13, 17, 23, 0.85);
    }
    
    /* ==================== 选择框样式 ==================== */
    .stSelectbox > div > div {
        background: rgba(13, 17, 23, 0.7);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(15px) saturate(180%);
    }
    
    .stSelectbox [data-baseweb="select"] {
        color: #e6edf3;
    }
    
    /* ==================== Tab 样式 ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(13, 17, 23, 0.5);
        padding: 10px;
        border-radius: 16px;
        backdrop-filter: blur(15px) saturate(180%);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 1px solid rgba(255, 0, 255, 0.3);
        color: #8b949e;
        border-radius: 10px;
        padding: 12px 24px;
        font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 0, 255, 0.1);
        border-color: rgba(255, 0, 255, 0.5);
        color: #ff00ff;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, 
            rgba(255, 0, 128, 0.2) 0%, 
            rgba(255, 0, 255, 0.15) 100%);
        border-color: #ff00ff;
        color: #ff00ff;
        box-shadow: 
            0 0 30px rgba(255, 0, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    /* ==================== 信息提示框 ==================== */
    .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(13, 17, 23, 0.7);
        border-left-width: 4px;
        border-radius: 12px;
        backdrop-filter: blur(15px) saturate(180%);
    }
    
    .stInfo {
        border-left-color: #00ffff;
        color: #c9d1d9;
    }
    
    /* ==================== 隐藏默认元素 ==================== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* ==================== 滚动条样式 ==================== */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(13, 17, 23, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ff0080 0%, #00ffff 50%, #ff00ff 100%);
        border-radius: 6px;
        box-shadow: 0 0 10px rgba(255, 0, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #ff0099 0%, #00ffff 50%, #ff00ff 100%);
        box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
    }
    
    /* ==================== 加载动画 ==================== */
    .stSpinner > div {
        border-top-color: #ff0080 !important;
        border-right-color: #00ffff !important;
        animation: spinner-rainbow 1.5s linear infinite;
    }
    
    @keyframes spinner-rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
    
    /* ==================== 音频播放器 ==================== */
    audio {
        filter: hue-rotate(270deg) saturate(2) brightness(1.2);
    }
</style>
"""

