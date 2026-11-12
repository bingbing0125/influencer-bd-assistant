# -*- coding: utf-8 -*-
"""
config.py — 全局配置：路径、常量、评分权重、CRM 状态、邮件风格。
所有可调参数集中在这里，避免散落在各模块。
"""
from pathlib import Path

# ---------- 路径 ----------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
DATA_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "influencer_bd.db"
DEMO_CSV = DATA_DIR / "demo_influencers.csv"

# ---------- 视觉主题（现代 SaaS Dashboard） ----------
PRIMARY_COLOR = "#1F3A93"      # 深蓝
PRIMARY_LIGHT = "#3B5BDB"
BG_COLOR = "#F5F7FB"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1A1A2E"
TEXT_MUTED = "#6B7280"
BORDER_COLOR = "#E5E7EB"

# 注入到 Streamlit 的全局 CSS
GLOBAL_CSS = f"""
<style>
.stApp {{ background-color: {BG_COLOR}; }}
section[data-testid="stSidebar"] {{
    background-color: #FFFFFF;
    border-right: 1px solid {BORDER_COLOR};
}}
h1, h2, h3, h4 {{ color: {TEXT_DARK}; font-weight: 700; }}
p, li, label, span {{ color: {TEXT_DARK}; }}
[data-testid="stMetric"] {{
    background: {CARD_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
div[data-testid="stVerticalBlock"] > div {{
    border-radius: 10px;
}}
.stButton > button {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.45rem 1rem;
    font-weight: 600;
}}
.stButton > button:hover {{ background-color: {PRIMARY_LIGHT}; color: white; }}
</style>
"""

# ---------- CRM 合作状态 ----------
CRM_STATUSES = [
    "To Contact",
    "Email Generated",
    "Contacted",
    "Follow-up Needed",
    "Replied",
    "Negotiating",
    "Collaborating",
    "Rejected",
    "Closed",
]

# ---------- 平台 ----------
PLATFORMS = ["TikTok", "Instagram", "YouTube"]

# ---------- 达人评分维度（权重可在 Settings 页修改，默认值） ----------
DEFAULT_WEIGHTS = {
    "niche_match": 25,        # 内容领域匹配度
    "market_match": 20,       # 目标市场匹配度
    "audience_match": 20,     # 受众群体匹配度
    "content_quality": 15,    # 内容质量与风格
    "engagement": 10,         # 互动表现
    "budget_fit": 10,         # 合作成本适配度
}

SCORE_TIERS = [
    (90, "Highly Recommended", "#16A34A"),
    (80, "Strong Match", "#3B82F6"),
    (70, "Potential Match", "#F59E0B"),
    (60, "Low Priority", "#F97316"),
    (0, "Not Recommended", "#DC2626"),
]

# ---------- 邮件风格 ----------
EMAIL_STYLES = {
    "Friendly & Casual": {
        "desc": "适合 TikTok / Instagram 中小型达人，语气轻松、像朋友推荐",
        "platform_hint": ["TikTok", "Instagram"],
    },
    "Professional & Business-oriented": {
        "desc": "适合 YouTube 达人、专业测评博主，正式商务语气",
        "platform_hint": ["YouTube"],
    },
    "Short & Direct": {
        "desc": "适合大批量初次建联，开门见山",
        "platform_hint": ["TikTok", "Instagram", "YouTube"],
    },
}

# ---------- 未知数据标记 ----------
UNKNOWN = "Unknown"
