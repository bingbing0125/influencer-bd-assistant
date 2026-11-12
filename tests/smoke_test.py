# -*- coding: utf-8 -*-
"""用 streamlit AppTest 跑一遍所有页面，捕捉渲染异常。"""
from streamlit.testing.v1 import AppTest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PAGES = ["📊 Overview", "🏷️ Brand & Product", "👥 Influencer Database",
         "🎯 AI Creator Matching", "✉️ Email Generator", "🧪 Prompt Engineering",
         "🤝 BD CRM", "💬 Reply Analyzer", "⏱️ Analytics & Efficiency", "⚙️ Settings"]

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "..", "app.py")

for page in PAGES:
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    # 选择侧边栏
    try:
        at.sidebar.radio[0].set_value(page)
        at.run()
    except Exception as e:
        print(f"[{page}] select err: {e}")
    if at.exception:
        print(f"[{page}] EXCEPTION:")
        for e in at.exception:
            print("   ", e.value[:300])
    else:
        print(f"[{page}] OK  (titles={[t.value for t in at.title][:1]})")
