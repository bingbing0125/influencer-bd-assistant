# -*- coding: utf-8 -*-
"""
AI-Powered Influencer BD Assistant — 主入口
运行：streamlit run app.py
"""
import streamlit as st

import config
import database as db
from modules import (brand as brand_page,
                     influencers as inf_page,
                     matching_page,
                     email_page,
                     prompt_page,
                     crm_page,
                     reply_page,
                     overview_page,
                     settings_page)

st.set_page_config(
    page_title="Influencer BD Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(config.GLOBAL_CSS, unsafe_allow_html=True)

# 初始化数据库；若为空则自动灌入 Demo 数据（云端部署重启后也能自举）
db.init_db()
if not db.list_influencers():
    try:
        import seed_demo
        seed_demo.seed()
    except Exception as _e:
        import sys
        print(f"[boot] auto-seed skipped: {_e}", file=sys.stderr)

# 左侧导航
st.sidebar.title("🚀 Influencer BD")
st.sidebar.caption("AI-Powered Overseas Creator Workbench")

NAV = {
    "📊 Overview": overview_page.render,
    "🏷️ Brand & Product": brand_page.render,
    "👥 Influencer Database": inf_page.render,
    "🎯 AI Creator Matching": matching_page.render,
    "✉️ Email Generator": email_page.render,
    "🧪 Prompt Engineering": prompt_page.render,
    "🤝 BD CRM": crm_page.render,
    "💬 Reply Analyzer": reply_page.render,
    "⏱️ Analytics & Efficiency": settings_page.render_efficiency,
    "⚙️ Settings": settings_page.render_settings,
}

choice = st.sidebar.radio("Navigate", list(NAV.keys()))
st.sidebar.divider()
st.sidebar.caption("Local-first · SQLite · No API key required for core features")

# 渲染对应页面
NAV[choice]()
