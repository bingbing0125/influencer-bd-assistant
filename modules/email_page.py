# -*- coding: utf-8 -*-
"""Module 04 UI — Email Generator"""
import io
import pandas as pd
import streamlit as st

import database as db
from config import EMAIL_STYLES
from modules import email_gen


def render():
    st.header("✉️ AI Personalized Outreach Generator")
    st.caption("三风格英文开发信，按达人 niche 自动选择个性化角度；批量生成后导出 Excel。")

    brand = db.get_brand()
    influencers = [i for i in db.list_influencers() if (i.get("contact_email") or "").strip()]

    if not brand or not brand.get("brand_name"):
        st.warning("请先在 Brand & Product 页录入品牌信息。")
    if not influencers:
        st.info("暂无可联系达人（需要 contact_email）。请到 Influencer Database 添加。")
        return

    style = st.selectbox("Email style", options=list(EMAIL_STYLES.keys()),
                         format_func=lambda s: f"{s} — {EMAIL_STYLES[s]['desc']}")

    mode = st.radio("Mode", ["Single creator", "Batch (top 10 by score)", "Batch (top 50 by score)"],
                    horizontal=True)

    # 预先按评分排序
    from modules import matching
    ranked = matching.score_all(db.list_influencers(), brand)
    by_id = {i["id"]: i for i in db.list_influencers()}

    chosen = []
    if mode.startswith("Single"):
        opts = [r for r in ranked if r["influencer_id"] in {i["id"] for i in influencers}]
        label_to_id = {f"#{r['rank']} {r['creator_name']} ({r['total']})": r["influencer_id"] for r in opts}
        pick = st.selectbox("Choose creator", options=list(label_to_id.keys()))
        chosen = [by_id[label_to_id[pick]]]
    else:
        n = 10 if "10" in mode else 50
        ids = {i["id"] for i in influencers}
        chosen = [by_id[r["influencer_id"]] for r in ranked if r["influencer_id"] in ids][:n]
        st.write(f"Will generate **{len(chosen)}** emails.")

    if st.button("🚀 Generate emails", type="primary"):
        results = []
        for inf in chosen:
            email = email_gen.generate_email(inf, brand, style)
            db.save_email(email)
            db.update_crm(inf["id"], {"status": "Email Generated"},
                          append_history=f"Generated '{style}' outreach email")
            results.append(email)
        st.session_state["emails_last_batch"] = results
        st.success(f"Generated and saved {len(results)} emails.")

    # 展示最近一批
    batch = st.session_state.get("emails_last_batch", [])
    if batch:
        st.divider()
        st.subheader(f"📨 Generated {len(batch)} email(s)")
        for e in batch:
            with st.expander(f"✉️ {e['subject']}"):
                st.markdown("**Subject:**")
                st.code(e["subject"])
                st.markdown("**Body:**")
                st.code(e["body"])
                st.markdown("**中文翻译：**")
                st.text(e["chinese_translation"])
                st.markdown(f"**Why this creator:** {e['match_reason']}")
                st.markdown(f"**Suggested collab:** {e['suggested_collab']}")
                st.markdown(f"**Subject alternatives:** {e['subject_alternatives']}")
                st.caption(f"🧠 {e['personalization_notes']}")

        # 批量导出
        df = pd.DataFrame([{
            "creator_name": db.get_influencer(e["influencer_id"])["creator_name"],
            "platform": db.get_influencer(e["influencer_id"])["platform"],
            "contact_email": db.get_influencer(e["influencer_id"])["contact_email"],
            "style": e["style"], "subject": e["subject"], "body": e["body"],
            "chinese_translation": e["chinese_translation"],
            "suggested_collab": e["suggested_collab"],
        } for e in batch])
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Outreach")
        st.download_button("⬇️ Download batch (.xlsx)", data=out.getvalue(),
                           file_name="outreach_emails.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
