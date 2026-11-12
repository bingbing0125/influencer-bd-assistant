# -*- coding: utf-8 -*-
"""
Module 03 — AI Creator Matching（规则式评分引擎，无需 API Key）。
对每位达人按 6 个维度打 0-10 分，加权得到 0-100 总分。
- 所有判断只基于已录入字段；缺失数据标记 unknown，绝不猜测。
- 权重从数据库读取，可在 Settings 页修改。
"""
import re
from typing import Optional

import database as db
from config import SCORE_TIERS


# 关键词词表：把"内容领域"映射到产品大类。后续可在 Settings 扩展。
NICHE_KEYWORDS = {
    "home": ["home", "decor", "interior", "bedroom", "living room", "apartment",
             "furniture", "cozy", "room make", "renovation", "design"],
    "smart_home": ["smart home", "gadget", "tech", "tech review", "unboxing",
                   "setup", "automation", "led", "lighting"],
    "lifestyle": ["lifestyle", "vlog", "daily", "routine", "minimalist", "aesthetic"],
    "beauty_fashion": ["beauty", "makeup", "fashion", "ootd", "skincare"],
    "fitness": ["fitness", "gym", "workout", "yoga"],
    "food": ["food", "cooking", "recipe", "baking"],
    "parenting": ["mom", "parent", "family", "kid"],
    "travel": ["travel", "trip", "hotel"],
}


def _text(*parts) -> str:
    return " ".join(str(p) for p in parts if p).lower()


def _kw_hits(text: str, words: list[str]) -> int:
    return sum(1 for w in words if w in text)


def score_niche(inf: dict, brand: dict) -> tuple[float, str, str]:
    """内容领域匹配度 0-10"""
    inf_text = _text(inf.get("niche"), inf.get("content_style"))
    brand_text = _text(brand.get("category"), brand.get("key_selling_points"),
                       brand.get("product_name"), brand.get("brand_name"))
    if not inf_text or not brand_text:
        return 5.0, "Niche or brand category missing — scored neutrally.", "unknown"

    # 找出品牌文本命中了哪些主题簇，再看达人是否命中同簇
    brand_clusters = [c for c, words in NICHE_KEYWORDS.items() if _kw_hits(brand_text, words) > 0]
    if not brand_clusters:
        return 6.0, "Brand category has no keyword cluster — neutral match.", "partial"

    best = 0.0
    hit_cluster = ""
    for c in brand_clusters:
        hits = _kw_hits(inf_text, NICHE_KEYWORDS[c])
        # 每个词命中给 3.3 分，上限 10
        s = min(10.0, hits * 3.3)
        if s > best:
            best, hit_cluster = s, c

    if best >= 9:
        reason = f"Strong content overlap with '{hit_cluster}' cluster."
    elif best >= 5:
        reason = f"Partial overlap with '{hit_cluster}' content."
    elif best > 0:
        reason = f"Weak overlap with '{hit_cluster}' — audience may still fit."
    else:
        reason = f"No keyword overlap with brand clusters {brand_clusters}."
    return best, reason, "real"


def score_market(inf: dict, brand: dict) -> tuple[float, str, str]:
    """目标市场匹配度 0-10：达人所在国 + 受众国"""
    target = (brand.get("target_market") or "").strip().lower()
    if not target:
        return 5.0, "Brand target market not set — scored neutrally.", "unknown"

    creator_country = (inf.get("country") or "").strip().lower()
    aud_country = (inf.get("audience_country") or "").strip().lower()

    score = 0.0
    notes = []
    if creator_country and target in creator_country:
        score += 5.0
        notes.append(f"creator is based in {inf.get('country')}")
    elif creator_country:
        notes.append(f"creator based in {inf.get('country')}")

    if aud_country and target in aud_country:
        score += 5.0
        notes.append(f"audience is mainly in {inf.get('audience_country')}")
    elif aud_country:
        notes.append(f"audience mainly in {inf.get('audience_country')}")

    if not creator_country and not aud_country:
        return 5.0, "No country / audience-country data — scored neutrally.", "unknown"

    return score, "; ".join(notes) or "Market not matched.", "real"


def score_audience(inf: dict, brand: dict) -> tuple[float, str, str]:
    """受众群体匹配度 0-10：性别 + 年龄"""
    target_aud = (brand.get("target_audience") or "").lower()
    if not target_aud:
        return 5.0, "Target audience not set — scored neutrally.", "unknown"

    score = 0.0
    notes = []
    gender = (inf.get("audience_gender") or "").strip().lower()
    age = (inf.get("audience_age") or "").strip()

    # 性别
    wants_female = "women" in target_aud or "female" in target_aud
    wants_male = "men" in target_aud or "male" in target_aud
    if gender:
        if (wants_female and gender.startswith("female")) or \
           (wants_male and gender.startswith("male")):
            score += 5.0
            notes.append(f"audience gender {gender} matches target")
        elif gender.startswith("mixed"):
            score += 3.0
            notes.append("mixed audience — partial match")
        else:
            notes.append(f"audience gender {gender} does not match target")
    else:
        notes.append("audience gender unknown")

    # 年龄：粗匹配数字区间
    want_ages = [int(x) for x in re.findall(r"(\d{2})", target_aud)]
    if age:
        have_ages = [int(x) for x in re.findall(r"(\d{2})", str(age))]
        if want_ages and have_ages:
            overlap = max(0, min(max(want_ages), max(have_ages)) - max(min(want_ages), min(have_ages)))
            if overlap >= 5:
                score += 5.0
                notes.append(f"age {age} overlaps target {target_aud}")
            else:
                score += 2.0
                notes.append(f"age {age} weak overlap with target")
        else:
            score += 2.5
            notes.append("age band not parsed — neutral")
    else:
        notes.append("audience age unknown")

    if not gender and not age:
        return 5.0, "No audience demographic data — scored neutrally.", "unknown"
    return min(10.0, score), "; ".join(notes), "real"


def score_content_quality(inf: dict, brand: dict) -> tuple[float, str, str]:
    """内容质量与风格 0-10：粉丝量级（偏好 mid-tier）+ 是否有内容风格描述"""
    followers = inf.get("followers") or 0
    style = (inf.get("content_style") or "").strip()

    # 偏好：10k-200k 为优质 mid-tier（避免 mega 号互动低）
    if 10_000 <= followers <= 200_000:
        base = 8.0
        tier = "mid-tier (10k–200k)"
    elif 200_000 < followers <= 1_000_000:
        base = 6.5
        tier = "mid-macro (200k–1M)"
    elif 1_000 <= followers < 10_000:
        base = 7.0
        tier = "nano / micro (1k–10k)"
    elif followers > 1_000_000:
        base = 5.0
        tier = "macro (>1M)"
    else:
        base = 4.0
        tier = "unknown follower count"

    if style:
        base = min(10.0, base + 1.5)
        note = f"{tier}; content style documented: {style[:60]}"
        return base, note, "real"
    else:
        note = f"{tier}; no content-style note — assume neutral quality"
        return max(3.0, base - 1.0), note, "partial"


def score_engagement(inf: dict, brand: dict) -> tuple[float, str, str]:
    """互动表现 0-10：engagement rate"""
    er = inf.get("engagement_rate")
    if er in (None, 0):
        return 5.0, "Engagement rate not provided — scored neutrally.", "unknown"
    # 经验区间：TikTok/IG 1-3% 健康，>5% 优秀；YouTube 0.5-2%
    if er >= 5:
        s, tag = 9.5, "very high"
    elif er >= 3:
        s, tag = 8.0, "healthy"
    elif er >= 1.5:
        s, tag = 6.0, "average"
    elif er >= 0.5:
        s, tag = 4.0, "below average"
    else:
        s, tag = 2.0, "very low — possible bot audience"
    return s, f"engagement rate {er}% — {tag}", "real"


def _parse_rate(rate_text: str) -> Optional[float]:
    """从 '$300/post' 之类解析美元报价"""
    if not rate_text:
        return None
    m = re.search(r"\$?\s*(\d{2,6})", str(rate_text).replace(",", ""))
    return float(m.group(1)) if m else None


def score_budget(inf: dict, brand: dict) -> tuple[float, str, str]:
    """合作成本适配度 0-10"""
    budget_text = brand.get("cooperation_budget") or ""
    rate = _parse_rate(inf.get("estimated_rate"))
    if rate is None:
        return 6.0, "Estimated rate missing — neutral (cost unknown).", "unknown"

    # 解析预算上限（取文本中最大的数字）
    nums = [float(x) for x in re.findall(r"(\d{2,6})", budget_text.replace(",", ""))]
    if not nums:
        return 6.5, f"Creator rate ${rate:.0f}; brand budget not specified.", "partial"
    budget_max = max(nums)
    ratio = rate / budget_max if budget_max else 1
    if ratio <= 0.5:
        s, tag = 9.0, "well under budget"
    elif ratio <= 1.0:
        s, tag = 7.5, "within budget"
    elif ratio <= 1.5:
        s, tag = 5.0, "slightly above budget"
    else:
        s, tag = 2.5, "well above budget"
    return s, f"Creator rate ${rate:.0f} vs budget ceiling ~${budget_max:.0f} — {tag}", "real"


DIMENSION_FUNCS = {
    "niche_match": ("Niche Relevance", score_niche),
    "market_match": ("Target Market", score_market),
    "audience_match": ("Audience Fit", score_audience),
    "content_quality": ("Content Quality", score_content_quality),
    "engagement": ("Engagement", score_engagement),
    "budget_fit": ("Budget Fit", score_budget),
}


def score_influencer(inf: dict, brand: dict, weights: dict) -> dict:
    """对单个达人评分，返回完整结果字典。"""
    details = []
    weighted_total = 0.0
    data_gaps = []

    for dim, (label, fn) in DIMENSION_FUNCS.items():
        raw, reason, status = fn(inf, brand)
        w = weights.get(dim, 0)
        weighted = raw / 10.0 * w
        weighted_total += weighted
        details.append({
            "dimension": dim,
            "label": label,
            "raw": round(raw, 1),
            "weight": w,
            "weighted": round(weighted, 1),
            "reason": reason,
            "status": status,   # real / partial / unknown
        })
        if status in ("unknown", "partial"):
            data_gaps.append(f"{label}: {reason}")

    total = round(weighted_total, 1)
    tier_label, tier_color = "Not Recommended", "#DC2626"
    for threshold, label, color in SCORE_TIERS:
        if total >= threshold:
            tier_label, tier_color = label, color
            break

    return {
        "influencer_id": inf["id"],
        "creator_name": inf.get("creator_name"),
        "platform": inf.get("platform"),
        "total": total,
        "tier": tier_label,
        "tier_color": tier_color,
        "details": details,
        "data_gaps": data_gaps,
    }


def score_all(influencers: list[dict], brand: dict) -> list[dict]:
    weights = db.get_weights()
    results = [score_influencer(inf, brand, weights) for inf in influencers]
    results.sort(key=lambda r: r["total"], reverse=True)
    for i, r in enumerate(results, 1):
        r["rank"] = i
    return results
