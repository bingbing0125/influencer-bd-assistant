# -*- coding: utf-8 -*-
"""Module 08 — Overview Dashboard"""
import pandas as pd
import plotly.express as px
import streamlit as st

import database as db
from modules import matching


def render():
    st.header("📊 Overview Dashboard")
    st.caption("所有指标基于数据库中真实录入的数据计算；未真实发送邮件时，不会把生成数当发送数。")

    influencers = db.list_influencers()
    crm = db.list_crm()
    emails = db.list_emails()
    brand = db.get_brand()

    total = len(influencers)
    emails_generated = len(emails)
    emails_sent = sum(1 for r in crm if (r.get("email_sent_at") or "").strip())
    replies = sum(1 for r in crm if r["status"] in ("Replied", "Negotiating"))
    positive = sum(1 for r in crm if r["status"] in ("Negotiating", "Collaborating"))
    collab = sum(1 for r in crm if r["status"] == "Collaborating")

    scores = matching.score_all(influencers, brand) if influencers else []
    avg_score = round(sum(s["total"] for s in scores) / len(scores), 1) if scores else 0
    qualified = sum(1 for s in scores if s["total"] >= 70)

    def rate(a, b):
        return f"{(a/b*100):.1f}%" if b else "—"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Influencers", total)
    k2.metric("Qualified (≥70)", qualified)
    k3.metric("Emails Generated", emails_generated)
    k4.metric("Avg Match Score", avg_score)

    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Emails Sent (real)", emails_sent)
    k6.metric("Replies", replies, f"Reply rate {rate(replies, emails_sent)}")
    k7.metric("Positive Replies", positive, f"Positive rate {rate(positive, emails_sent)}")
    k8.metric("Collaborations", collab, f"Collab rate {rate(collab, emails_sent)}")

    st.divider()
    if not influencers:
        st.info("暂无数据——先导入 Demo 数据或添加达人。")
        return

    df = pd.DataFrame(influencers)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(df, names="platform", title="Influencers by Platform", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(df, names="country", title="Influencers by Country", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.histogram(df, x="niche", title="Influencers by Niche",
                           color="platform", barmode="group")
        fig.update_xaxes(categoryorder="total descending")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        if scores:
            sdf = pd.DataFrame([{"tier": s["tier"], "n": 1} for s in scores])
            fig = px.bar(sdf.groupby("tier").count().reset_index(),
                         x="tier", y="n", title="Match Score Distribution",
                         color="tier")
            st.plotly_chart(fig, use_container_width=True)

    # BD 漏斗
    st.subheader("BD Funnel")
    funnel_stages = [
        ("Total Influencers", total),
        ("Qualified ≥70", qualified),
        ("Emails Generated", emails_generated),
        ("Emails Sent", emails_sent),
        ("Replies", replies),
        ("Positive", positive),
        ("Collaborations", collab),
    ]
    fdf = pd.DataFrame(funnel_stages, columns=["stage", "count"])
    fig = px.funnel(fdf, x="count", y="stage")
    st.plotly_chart(fig, use_container_width=True)
