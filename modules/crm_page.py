# -*- coding: utf-8 -*-
"""Module 06 UI — Influencer CRM"""
import pandas as pd
import streamlit as st

import database as db
from config import CRM_STATUSES


def render():
    st.header("🤝 Influencer CRM")
    st.caption("第一阶段只生成邮件、管理状态与跟进记录；不自动发信。")

    records = db.list_crm()
    if not records:
        st.info("还没有达人。请到 Influencer Database 添加。")
        return

    # 状态筛选
    status_filter = st.multiselect("Filter by status", options=CRM_STATUSES, default=[])
    view = records
    if status_filter:
        view = [r for r in records if r["status"] in status_filter]

    df = pd.DataFrame([{
        "ID": r["influencer_id"],
        "Creator": r["creator_name"],
        "Platform": r["platform"],
        "Country": r["country"],
        "Niche": r["niche"],
        "Status": r["status"],
        "Email Sent": r.get("email_sent_at") or "—",
        "Last Reply": r.get("last_reply_at") or "—",
        "Next Follow-up": r.get("next_followup_at") or "—",
        "Quoted Rate": r.get("quoted_rate") or "—",
    } for r in view])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🔧 Detail / Update")
    ids = [r["influencer_id"] for r in view]
    if not ids:
        return
    sel = st.selectbox("Creator", options=ids,
                       format_func=lambda x: next((r["creator_name"] for r in view if r["influencer_id"] == x), str(x)))
    rec = db.get_crm(sel)
    inf = db.get_influencer(sel)

    c1, c2 = st.columns(2)
    with c1:
        new_status = st.selectbox("Status", options=CRM_STATUSES,
                                  index=CRM_STATUSES.index(rec["status"]) if rec["status"] in CRM_STATUSES else 0)
        email_sent_at = st.text_input("Email sent at (YYYY-MM-DD)", value=rec.get("email_sent_at") or "")
        last_reply_at = st.text_input("Last reply at (YYYY-MM-DD)", value=rec.get("last_reply_at") or "")
        next_followup = st.text_input("Next follow-up at (YYYY-MM-DD)", value=rec.get("next_followup_at") or "")
    with c2:
        quoted = st.text_input("Quoted rate", value=rec.get("quoted_rate") or "")
        collab_type = st.text_input("Collaboration type", value=rec.get("collaboration_type") or "")
        reply_summary = st.text_area("Reply summary", value=rec.get("reply_summary") or "")
        notes = st.text_area("Notes", value=rec.get("notes") or "")

    log_event = st.text_input("Log event (optional, e.g. 'Sent second follow-up')")

    if st.button("💾 Update CRM record", type="primary"):
        db.update_crm(sel, {
            "status": new_status,
            "email_sent_at": email_sent_at or None,
            "last_reply_at": last_reply_at or None,
            "next_followup_at": next_followup or None,
            "quoted_rate": quoted,
            "collaboration_type": collab_type,
            "reply_summary": reply_summary,
            "notes": notes,
        }, append_history=log_event or None)
        st.success("CRM updated.")
        st.rerun()

    # 历史
    st.markdown("**History**")
    for h in reversed(rec.get("history", [])):
        st.markdown(f"- 🕒 {h.get('time')}: {h.get('event')}")

    # 已生成邮件
    st.markdown("**Generated emails for this creator:**")
    emails = db.list_emails(sel)
    if not emails:
        st.caption("No emails generated yet.")
    for e in emails:
        st.markdown(f"- ✉️ [{e['created_at']}] {e['style']} — {e['subject']}")
