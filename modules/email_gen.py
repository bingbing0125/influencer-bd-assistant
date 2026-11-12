# -*- coding: utf-8 -*-
"""
Module 04 — AI Personalized Outreach Generator（规则式，无需 API Key）。
根据达人 niche / platform / content_style 选择不同的"合作理由"与场景角度，
生成三风格英文邮件 + 中文翻译 + 个性化说明。严格不编造未提供的作品/合作经历。
"""
import database as db
from config import EMAIL_STYLES


# 不同 niche 的"场景角度"——这是个性化的核心
NICHN_ANGLES = {
    "home decor": {
        "angle_en": "a warm bedroom or living-room refresh",
        "angle_zh": "卧室/客厅氛围感改造",
        "pitch": "imagine it as the ambient layer in your next room makeover — warm dimming that shifts the whole mood of a corner",
    },
    "smart home": {
        "angle_en": "a smart-home setup upgrade",
        "angle_zh": "智能家居场景升级",
        "pitch": "it slots into an existing smart-home routine — app control, scene presets, and a minimal form factor that won't clutter a clean setup",
    },
    "lifestyle": {
        "angle_en": "an everyday-lifestyle upgrade",
        "angle_zh": "日常生活质感提升",
        "pitch": "it's the small detail that makes a home feel put-together after a long day — something easy to show in a casual daily routine",
    },
    "apartment living": {
        "angle_en": "small-space apartment living",
        "angle_zh": "小户型公寓生活",
        "pitch": "it's made for renters and small apartments — no hard wiring, tool-free installation, and a slim profile that fits shelves and headboards",
    },
    "furniture": {
        "angle_en": "styling furniture and interiors",
        "angle_zh": "家具与空间搭配",
        "pitch": "the light works as a styling layer for furniture shots — it adds depth and warmth to corners that usually fall flat",
    },
}

DEFAULT_ANGLE = {
    "angle_en": "a tasteful home-lifestyle feature",
    "angle_zh": "家居生活方式植入",
    "pitch": "it fits naturally into a home or lifestyle scene without feeling forced",
}


def _pick_angle(niche: str, content_style: str) -> dict:
    text = f"{niche} {content_style}".lower()
    for key, angle in NICHN_ANGLES.items():
        if key in text:
            return angle
    return DEFAULT_ANGLE


def _first_name(creator_name: str) -> str:
    name = (creator_name or "").strip()
    if not name:
        return "there"
    return name.split()[0].title()


def _selling_points(brand: dict, n: int = 3) -> list[str]:
    sp = (brand.get("key_selling_points") or "").splitlines()
    sp = [s.strip("-• ").strip() for s in sp if s.strip()]
    return sp[:n] if sp else ["a simple, well-designed product"]


def generate_email(inf: dict, brand: dict, style: str) -> dict:
    name = _first_name(inf.get("creator_name"))
    platform = inf.get("platform") or "social"
    niche = (inf.get("niche") or "home & lifestyle").strip()
    angle = _pick_angle(niche, inf.get("content_style", ""))
    sp = _selling_points(brand)
    product = brand.get("product_name") or "our product"
    bname = brand.get("brand_name") or "our brand"
    price = brand.get("product_price") or "an accessible price point"

    # ---------- 开头称呼 ----------
    if style == "Friendly & Casual":
        greeting = f"Hi {name},"
    elif style == "Professional & Business-oriented":
        greeting = f"Dear {name},"
    else:
        greeting = f"Hi {name},"

    # ---------- 个性化开场：不假装看过视频 ----------
    if style == "Friendly & Casual":
        opening = (
            f"I've been following your {niche.lower()} content and really love the vibe "
            f"you're building — your feel for {angle['angle_en']} stood out to me."
        )
    elif style == "Professional & Business-oriented":
        opening = (
            f"I'm reaching out because your profile as a {niche} creator on {platform.title()} aligns "
            f"well with a brand collaboration we are currently planning."
        )
    else:
        opening = (
            f"Loved your {niche} angle on {platform.title()}. Quick idea that might fit your channel."
        )

    # ---------- 品牌 + 产品 ----------
    brand_intro = (
        f"We're {bname}, a home & living brand focused on {brand.get('brand_positioning','thoughtfully designed home products').lower()}."
    )
    product_intro = (
        f"Our {product} ({price}) is designed for {brand.get('target_audience','modern homes').lower()}. "
        f"What makes it different: {'; '.join(sp)}."
    )

    # ---------- 达人专属合作理由 ----------
    creator_reason = (
        f"Given your focus on {niche}, I think {angle['pitch']}. "
        f"That's a genuinely useful fit rather than a random plug."
    )

    # ---------- 合作提案 ----------
    if style == "Friendly & Casual":
        proposal = (
            f"We'd love to send you a free {product} to try, and — if you like it — "
            f"feature it in one organic {platform.title()} post or short. We can also discuss a paid "
            f"partnership that fits your rates."
        )
        cta = "Would you be open to chatting? Happy to send the product and more details your way."
        signoff = f"Cheers,\nThe {bname} Team"
    elif style == "Professional & Business-oriented":
        proposal = (
            f"We would like to propose a paid collaboration: a dedicated review or integration video "
            f"on your {platform.title()} channel, including the product free of charge. "
            f"We are flexible on format — dedicated video, integration, or short — and open to discussing "
            f"your media kit and rates."
        )
        cta = (
            "Could you share your media kit and current rates? We'd be glad to send a short brief "
            "and set up a quick call."
        )
        signoff = f"Best regards,\nPartnerships Team, {bname}"
    else:
        proposal = (
            f"Short version: we'll send you the {product} for free and pay a flat fee for one "
            f"organic {platform.title()} post. No scripts, no forced lines — just your honest take."
        )
        cta = "Interested? Reply 'yes' and I'll send details."
        signoff = f"Thanks,\n{bname} Team"

    # ---------- 主题行 ----------
    if style == "Professional & Business-oriented":
        subject = f"Collaboration opportunity — {bname} × {inf.get('creator_name','your channel')}"
        alt_subjects = [
            f"Partnership proposal for {inf.get('creator_name','your channel')}",
            f"{bname} — paid {platform.title()} collaboration",
            f"Quick question about featuring {product}",
        ]
    elif style == "Short & Direct":
        subject = f"{bname} × {inf.get('creator_name','you')} — quick idea"
        alt_subjects = [
            f"Free {product} for your {niche} content?",
            f"Paid collab — {bname}",
            f"Quick partnership idea for {platform.title()}",
        ]
    else:
        subject = f"Loved your {niche} content — {bname} collab?"
        alt_subjects = [
            f"Thought this would fit your channel ✨",
            f"{bname} × {inf.get('creator_name','your handle')}",
            f"Free {product} + partnership?",
        ]

    body = "\n\n".join([greeting, opening, brand_intro, product_intro,
                        creator_reason, proposal, cta, signoff])

    # ---------- 中文翻译（粗略但可读） ----------
    translation = (
        f"【主题】{subject}\n\n"
        f"{greeting}\n\n"
        f"开场：我一直关注你在「{niche}」方向的内容，你在{angle['angle_zh']}上的风格让我印象深刻。\n"
        f"品牌：我们是 {bname}，主打{brand.get('brand_positioning','有设计感的家居产品')}。\n"
        f"产品：{product}（{price}），面向{brand.get('target_audience','现代家庭')}。卖点：{'；'.join(sp)}。\n"
        f"合作理由：结合你的{niche}内容，我们认为{angle['angle_zh']}的植入会很自然，而不是硬广。\n"
        f"合作方式：{proposal}\n"
        f"行动号召：{cta}\n"
        f"落款：{signoff}"
    )

    personalization_notes = (
        f"角度选择：基于 niche='{niche}' 与 content_style='{inf.get('content_style') or 'Unknown'}' "
        f"选中「{angle['angle_zh']}」场景。"
        f"风格：{style}（适配 {', '.join(EMAIL_STYLES[style]['platform_hint'])}）。"
        f"未编造任何具体作品名/历史合作——若需更深度个性化，请用 Prompt 工作台粘贴达人近期内容链接。"
    )

    match_reason = (
        f"达人领域 {niche} 与品牌 {brand.get('category','Home & Living')} 相关；"
        f"平台 {platform} 与目标市场 {brand.get('target_market','Unknown')} 匹配。"
    )

    if style == "Professional & Business-oriented":
        suggested_collab = "Dedicated review video or long integration"
    elif style == "Short & Direct":
        suggested_collab = "Single organic post, flat fee + free product"
    else:
        suggested_collab = "Free product + optional paid short / Story"

    return {
        "influencer_id": inf["id"],
        "style": style,
        "subject": subject,
        "body": body,
        "chinese_translation": translation,
        "personalization_notes": personalization_notes,
        "match_reason": match_reason,
        "suggested_collab": suggested_collab,
        "subject_alternatives": " | ".join(alt_subjects),
    }
