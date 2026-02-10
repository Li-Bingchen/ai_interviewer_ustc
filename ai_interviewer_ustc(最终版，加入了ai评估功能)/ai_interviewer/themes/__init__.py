# -*- coding: utf-8 -*-
"""
主题管理器
"""

from . import theme_cyber, theme_neon

AVAILABLE_THEMES = {
    "赛博训练舱": theme_cyber,
    "霓虹实验室": theme_neon,
}

def get_theme_css(theme_name):
    """获取指定主题的 CSS"""
    theme = AVAILABLE_THEMES.get(theme_name)
    if theme:
        return theme.CSS_STYLE
    return AVAILABLE_THEMES["赛博训练舱"].CSS_STYLE  # 默认主题

def get_theme_list():
    """获取所有可用主题列表"""
    return list(AVAILABLE_THEMES.keys())

