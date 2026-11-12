# -*- coding: utf-8 -*-
"""Module 03 UI — AI Creator Matching 评分展示"""
import pandas as pd
import streamlit as st

import database as db
from modules import matching


def render():
    st.header("🎯 AI Creator Matching")
    st.caption("100 分加权评分模型。权重可在 Settings 调整；缺失数据按中性分处理并明确标注，绝不猜测。")

    brand = db.get_brand()
    influencers = db.list_influencers()

    if not brand or not brand.get("brand_name"):
        st.warning("请先在 Brand & Product 页录入品牌信息，否则评分只能给出中性结果。")
    if not influencers:
        st.info("达人库为空，请先导入或手动添加达人。")
        return

    col1, col2 = st.columns([1, 3])
    with col1:
        top_n = st.selectbox("Show Top", options=[10, 20, 50, len(influencers)], index=0)
        only_with_email = st.checkbox("Only creators with contact email", value=False)

    pool = influencers
    if only_with_email:
        pool = [i for i in pool if (i.get("contact_email") or "").strip()]

    results = matching.score_all(pool, brand)
    results = results[:top_n]

    # 汇总表
    summary = [{
        "Rank": r["rank"],
        "Creator": r["creator_name"],
        "Platform": r["platform"],
        "Score": r["total"],
        "Tier": r["tier"],
    } for r in results]
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📊 Per-creator breakdown")

    for r in results:
        with st.expander(f"#{r['rank']}  {r['creator_name']}  —  {r['total']}/100  ({r['tier']})"):
            cols = st.columns(6)
            for col, d in zip(cols, r["details"]):
                col.metric(d["label"], f"{d['raw']}/10", f"×{d['weight']}%")
                if d["status"] != "real":
                    col.caption(f"⚠️ {d['status']}")
            st.markdown("**Reasons:**")
            for d in r["details"]:
                icon = "✅" if d["status"] == "real" else ("🟡" if d["status"] == "partial" else "⚪")
                st.markdown(f"- {icon} **{d['label']}**: {d['reason']}")
            if r["data_gaps"]:
                st.info("Data gaps to fill: " + " | ".join(r["data_gaps"]))
