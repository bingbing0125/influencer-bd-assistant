# -*- coding: utf-8 -*-
"""Module 09 — Efficiency Analysis & Settings(weights)"""
import pandas as pd
import plotly.express as px
import streamlit as st

import database as db
from config import DEFAULT_WEIGHTS


def render_efficiency():
    st.header("⏱️ Efficiency Analysis")
    st.caption("用真实计时记录对比「传统人工」与「AI 辅助」模式；系统不会编造效率倍数。")

    st.markdown("### 📋 Workflow comparison")
    cmp_df = pd.DataFrame([
        ["达人初步筛选", "人工逐个查看主页、估算粉丝与互动", "AI 加权评分，秒级输出可解释分数"],
        ["达人资料整理", "手动逐字段录入 Excel", "Excel 批量导入 + 自动清洗"],
        ["开发信撰写", "逐封手写 20–40 分钟/封", "批量个性化生成，秒级出稿"],
        ["邮件翻译", "人工中英对照", "自动附带中文翻译"],
        ["达人回复分析", "人工阅读、判断意向、回忆历史", "规则引擎自动提取意向/报价/风险"],
        ["数据统计", "手动透视表", "实时 Dashboard 与 BD 漏斗"],
    ], columns=["工作环节", "传统人工模式", "AI 辅助模式"])
    st.dataframe(cmp_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🧪 Run your own timed test")
    st.caption("记录你自己的真实用时，系统据此计算效率提升倍数。")

    with st.form("eff_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            task_type = st.selectbox("Task", ["screening_10", "emails_10"],
                                     format_func=lambda x: {"screening_10": "筛选 10 位达人",
                                                            "emails_10": "撰写 10 封开发信"}[x])
        with c2:
            mode = st.selectbox("Mode", ["manual", "ai"],
                                format_func=lambda x: {"manual": "传统人工", "ai": "AI 辅助"}[x])
        with c3:
            seconds = st.number_input("用时（秒）", min_value=1, step=30)
        note = st.text_input("备注（可选）")
        if st.form_submit_button("Record time"):
            db.add_efficiency_test(task_type, mode, 10, float(seconds), note)
            st.success("Recorded.")

    # 计算对比
    tests = db.list_efficiency_tests()
    if not tests:
        st.info("还没有计时记录。请先跑一次你自己的对比测试。")
        return

    tdf = pd.DataFrame(tests)
    st.dataframe(tdf[["task_type", "mode", "n_items", "seconds", "note", "created_at"]],
                 use_container_width=True, hide_index=True)

    st.subheader("📈 Result")
    for task in ["screening_10", "emails_10"]:
        sub = tdf[tdf["task_type"] == task]
        man = sub[sub["mode"] == "manual"]["seconds"].mean()
        ai = sub[sub["mode"] == "ai"]["seconds"].mean()
        name = "筛选 10 位达人" if task == "screening_10" else "撰写 10 封开发信"
        if pd.notna(man) and pd.notna(ai) and ai > 0:
            lift = man / ai
            saved_pct = (1 - ai / man) * 100
            st.markdown(f"- **{name}**：人工 {man:.0f}s vs AI {ai:.0f}s → "
                        f"**效率提升 {lift:.2f}×**，时间节省 **{saved_pct:.0f}%**")
        else:
            st.markdown(f"- **{name}**：还缺 {'人工' if pd.isna(man) else ''}{'AI' if pd.isna(ai) else ''} 数据。")

    st.caption("注：效率提升倍数 = 人工用时 / AI 用时；时间节省百分比 = (人工−AI)/人工。两者不是同一个数，请勿混用。")


def render_settings():
    st.header("⚙️ Settings")
    st.subheader("Scoring Weights")
    st.caption("调整 6 个维度权重（合计建议 100，系统会自动归一化显示）。")
    weights = db.get_weights()
    new_w = {}
    cols = st.columns(3)
    labels = {
        "niche_match": "Niche Relevance %",
        "market_match": "Target Market %",
        "audience_match": "Audience Fit %",
        "content_quality": "Content Quality %",
        "engagement": "Engagement %",
        "budget_fit": "Budget Fit %",
    }
    for i, (k, label) in enumerate(labels.items()):
        with cols[i % 3]:
            new_w[k] = st.number_input(label, min_value=0, max_value=100,
                                       value=int(weights.get(k, DEFAULT_WEIGHTS[k])))
    total_w = sum(new_w.values())
    st.caption(f"当前权重合计：{total_w}（非 100 时，匹配页按比例归一化计算）")
    if st.button("Save weights", type="primary"):
        # 归一化到 100
        if total_w > 0:
            norm = {k: v / total_w * 100 for k, v in new_w.items()}
            db.set_weights(norm)
            st.success("Weights saved (normalized to 100).")
        else:
            st.error("权重不能全为 0。")

    st.divider()
    st.subheader("🔌 AI API 接入（可选）")
    st.info("第一阶段默认使用规则式本地引擎，无需 API Key。"
            "若未来接入 OpenAI / Anthropic，请在环境变量中配置 OPENAI_API_KEY / ANTHROPIC_API_KEY，"
            "不要把 Key 写进代码。当前所有核心功能（评分、邮件、回复分析）均不依赖付费 API。")
