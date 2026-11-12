# -*- coding: utf-8 -*-
"""
Module 07 — Reply Analyzer（规则式，无需 API Key）。
基于关键词识别合作意向、报价、索要免费样品/佣金、风险点，并生成回复草稿。
"""
import re
from datetime import datetime
import streamlit as st

import database as db


RULES = [
    # (标签, 关键词列表, 中文解释)
    ("interested", [r"\byes\b", r"\bi'?m interested\b", r"\d+", r"love to", r"would love",
                    r"count me in", r"let'?s do", r"sign me", r"available", r"sounds good",
                    r"sounds great", r"happy to", r"interested in"],
     "表达了合作兴趣"),
    ("declined", [r"\bnot interested\b", r"\bpass\b", r"\bunfortunately\b", r"\bnot the right",
                  r"\bwon'?t be able\b", r"\bmaybe next\b", r"\bdecline"],
     "婉拒或暂不合作"),
    ("asks_free_product", [r"free product", r"send me", r"product for free", r"seeding",
                           r"comped", r"complimentary", r"gift"],
     "希望获得免费样品"),
    ("asks_paid", [r"\$\s?\d+", r"my rate", r"my fee", r"media kit", r"pricing",
                   r"what'?s your budget", r"how much do you pay", r"per post", r"per video"],
     "涉及报价/费用"),
    ("asks_commission", [r"commission", r"affiliate", r"sales share", r"referral"],
     "询问佣金/联盟计划"),
    ("needs_info", [r"tell me more", r"what does (that|this) involve", r"could you explain",
                    r"more details", r"what kind of content", r"what would you need"],
     "希望了解更多合作细节"),
    ("asks_exclusivity", [r"exclusive", r"exclusivity", r"no competitor", r"competitor"],
     "提及独家/竞品限制"),
    ("asks_timeline", [r"timeline", r"when do you need", r"deadline", r"by when"],
     "询问时间节点"),
]


def analyze_reply(text: str) -> dict:
    t = text.lower()
    hits = {}
    for label, patterns, desc in RULES:
        matched = [p for p in patterns if re.search(p, t)]
        if matched:
            hits[label] = desc

    # 抽取报价数字
    rates = re.findall(r"\$\s?[\d,]+(?:\.\d+)?(?:\s?(?:/|per)\s?(?:post|video|story|reel))?", text,
                       flags=re.IGNORECASE)

    # 意向判断
    if "declined" in hits and "interested" not in hits:
        intent = "Not interested"
    elif "interested" in hits and "declined" not in hits:
        intent = "Interested"
    elif "asks_paid" in hits or "asks_free_product" in hits:
        intent = "Open but needs negotiation"
    elif "needs_info" in hits:
        intent = "Interested but needs more info"
    else:
        intent = "Ambiguous — follow up"

    # 风险
    risks = []
    if "asks_exclusivity" in hits:
        risks.append("对方要求独家条款——评估是否会影响其他达人合作。")
    if rates:
        # 粗略：>1000 视为偏贵
        nums = [float(r.replace("$", "").replace(",", "").split()[0]) for r in re.findall(r"\$[\d,]+", text)]
        if nums and max(nums) > 1000:
            risks.append(f"报价 ${max(nums):,.0f} 偏高，需确认是否在预算内。")
    if intent == "Ambiguous — follow up":
        risks.append("回复意图不清晰，直接推进可能被忽略。")

    return {
        "intent": intent,
        "hits": hits,
        "rates": rates,
        "risks": risks,
    }


def draft_reply(inf_name: str, intent: str, hits: dict, brand: dict) -> str:
    bname = brand.get("brand_name", "our brand")
    if intent == "Interested":
        body = (
            f"Hi {inf_name},\n\n"
            f"Great to hear from you! I'd love to move forward. "
            f"Could you share your media kit and preferred formats? "
            f"On our side, we can send the product free of charge and discuss a flat fee or commission — "
            f"whichever works best for you.\n\nLooking forward, and happy to hop on a 15-min call if useful.\n\n"
            f"Best,\n{bname} Partnerships"
        )
    elif intent == "Open but needs negotiation":
        body = (
            f"Hi {inf_name},\n\n"
            f"Thanks for getting back. I've noted your rate — let me confirm internally and come back to you "
            f"within 1–2 business days. In the meantime, the product itself is complimentary, and we can be "
            f"flexible on format (single post / Story series / short).\n\nTalk soon,\n{bname} Team"
        )
    elif intent == "Interested but needs more info":
        body = (
            f"Hi {inf_name},\n\n"
            f"Happy to explain more! Briefly: we send you the product free of charge, you create one organic "
            f"post in your usual style, and we offer a flat fee on top. No scripts, no forced lines. "
            f"Would a one-paragraph brief help?\n\nBest,\n{bname} Team"
        )
    elif intent == "Not interested":
        body = (
            f"Hi {inf_name},\n\n"
            f"Totally understand — thanks for letting me know directly. I'll note that and won't follow up again. "
            f"If things change down the road, the door is always open.\n\nWishing you a great rest of the week!\n"
            f"{bname} Team"
        )
    else:
        body = (
            f"Hi {inf_name},\n\n"
            f"Thanks for the reply! Just to make sure I'm on the same page — are you open to trying the product "
            f"and featuring it in one post? Happy to share a quick brief and answer any questions.\n\n"
            f"Best,\n{bname} Team"
        )
    return body


def render():
    st.header("💬 AI Reply Analyzer")
    st.caption("粘贴达人英文回复，自动识别意向、报价与条件，并生成回复草稿。")

    influencers = db.list_influencers()
    opts = [("— standalone (no creator attached) —", None)] + \
           [(f"#{i['id']} {i['creator_name']}", i["id"]) for i in influencers]
    pick = st.selectbox("Attach to creator (optional)", options=[o[0] for o in opts])
    inf_id = dict(opts)[pick]
    inf = db.get_influencer(inf_id) if inf_id else None

    reply = st.text_area("Paste creator's English reply", height=220,
                         placeholder="Hi! Thanks for reaching out. I'd be interested — my rate is $450 per TikTok post, and I'd love the product sent for free...")

    if st.button("🔍 Analyze reply", type="primary"):
        if not reply.strip():
            st.warning("Please paste a reply first.")
            return
        brand = db.get_brand()
        result = analyze_reply(reply)
        draft = draft_reply(inf["creator_name"] if inf else "there", result["intent"], result["hits"], brand)

        st.session_state["reply_result"] = (result, draft, reply, inf_id)

    if "reply_result" in st.session_state:
        result, draft, reply, inf_id = st.session_state["reply_result"]
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.metric("合作意向", result["intent"])
            st.markdown("**识别到的要点：**")
            for label, desc in result["hits"].items():
                st.markdown(f"- 🔹 **{label}**: {desc}")
            if result["rates"]:
                st.markdown(f"**抽取到的报价：** {', '.join(result['rates'])}")
        with c2:
            st.markdown("**⚠️ 商务风险提示：**")
            if result["risks"]:
                for r in result["risks"]:
                    st.markdown(f"- ⚠️ {r}")
            else:
                st.markdown("- 无明显风险。")

        st.markdown("**建议回复策略：**")
        if result["intent"] == "Interested":
            st.markdown("1. 立即索要 media kit；2. 确认免费寄样地址；3. 给出内容方向但不写死脚本。")
        elif result["intent"] == "Open but needs negotiation":
            st.markdown("1. 1-2 个工作日内回价；2. 用佣金/长期合作置换现金价；3. 明确内容形式。")
        elif result["intent"] == "Not interested":
            st.markdown("礼貌收尾，加入 nurtured 列表，3 个月后再触达。")
        else:
            st.markdown("1. 用一句话重新确认意向；2. 附上简短 brief；3. 给一个明确的 CTA。")

        st.markdown("**Draft English reply:**")
        st.code(draft)

        if st.button("💾 Save analysis & update CRM"):
            db.save_reply_analysis({
                "influencer_id": inf_id,
                "raw_reply": reply,
                "translation": "(规则分析结果见上；如需逐句翻译，可把回复粘贴到 Prompt 08)",
                "intent": result["intent"],
                "key_points": "; ".join(f"{k}:{v}" for k, v in result["hits"].items()),
                "risks": "; ".join(result["risks"]),
                "suggested_reply": draft,
            })
            if inf_id:
                new_status = {"Interested": "Negotiating",
                              "Open but needs negotiation": "Negotiating",
                              "Not interested": "Rejected"}.get(result["intent"], "Replied")
                db.update_crm(inf_id, {"status": new_status,
                                       "last_reply_at": datetime.now().strftime("%Y-%m-%d")},
                              append_history=f"Reply analyzed → {result['intent']}")
            st.success("Saved.")
