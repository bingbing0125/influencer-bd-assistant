# -*- coding: utf-8 -*-
"""Module 05 UI — Prompt Engineering Workbench"""
import streamlit as st

import database as db
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import prompt_library as PL


def render():
    st.header("🧪 Prompt Engineering Workbench")
    st.caption("8 类 BD 提示词模板，自动注入品牌与达人信息；复制到 ChatGPT / Claude，再把结果粘回。")

    brand = db.get_brand()
    influencers = db.list_influencers()

    # 选达人
    names = [("None", None)] + [(f"#{i['id']} {i['creator_name']}", i["id"]) for i in influencers]
    labels = [n[0] for n in names]
    pick_label = st.selectbox("Target creator (optional)", options=labels)
    pick_id = dict(names)[pick_label]
    inf = db.get_influencer(pick_id) if pick_id else None

    # 选 prompt
    key_labels = {f"{name}": key for key, name, _ in PL.PROMPT_INDEX}
    chosen_label = st.selectbox("Choose a prompt template", options=list(key_labels.keys()))
    key = key_labels[chosen_label]
    desc = next(d for k, _, d in PL.PROMPT_INDEX if k == key)
    st.info(f"**{chosen_label}** — {desc}")

    prompt_text = PL.build_prompt(key, brand, inf)

    st.subheader("📋 Rendered Prompt")
    st.caption("一键复制后粘贴到 ChatGPT / Claude；返回结果可粘到下方「AI Result 解析」保存。")
    st.text_area("Prompt", value=prompt_text, height=420)
    st.code(prompt_text, language="markdown")

    # 自定义 prompt 保存
    with st.expander("💾 Save / edit as my own template"):
        ck = st.text_input("Template key (e.g. my_followup_v2)", value=f"custom_{key}")
        existing = db.get_custom_prompt(ck)
        initial = existing["content"] if existing else prompt_text
        edited = st.text_area("Edit prompt", value=initial, height=300)
        if st.button("Save custom template"):
            db.save_custom_prompt(ck, ck, edited)
            st.success(f"Saved '{ck}'.")

    # 粘回 AI 结果（仅展示+备注，不做猜测式解析）
    st.divider()
    st.subheader("📥 Paste AI result back")
    ai_result = st.text_area("Paste ChatGPT / Claude output here", height=250)
    note = st.text_input("Note (e.g. 'Used for Sarah Zhang scoring')")
    if st.button("Save result as note"):
        if not ai_result.strip():
            st.warning("Nothing to save.")
        else:
            # 存到达人 notes 或独立说明：这里追加到达人 notes（若选了达人）
            if inf:
                old = inf.get("notes") or ""
                db.upsert_influencer({**inf, "notes": (old + f"\n[AI result {note}]:\n" + ai_result)[:8000]},
                                     inf_id=inf["id"])
                st.success("Appended to creator's notes.")
            else:
                st.info("未选择达人——结果已展示但未入库（选一位达人后再点保存即可归档到该达人）。")
