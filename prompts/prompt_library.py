# -*- coding: utf-8 -*-
"""
prompts/prompt_library.py — 8 类 BD 提示词模板。
每个提示词遵循 Role / Context / Task / Input / Constraints / Output Format / Evaluation 结构。
所有模板都是纯字符串拼接：不依赖任何 API，用户可直接复制到 ChatGPT / Claude。
"""
from typing import Optional

# 8 个 Prompt 的元信息（key -> 名称、用途）
PROMPT_INDEX = [
    ("research",   "01 · Influencer Research",     "分析达人主页、内容定位、受众与合作潜力"),
    ("scoring",    "02 · Influencer Scoring",      "根据品牌要求对达人进行量化评分"),
    ("outreach",   "03 · Personalized Email",      "生成个性化英文开发信"),
    ("followup",   "04 · Email Follow-up",         "首次建联后的二次跟进邮件"),
    ("negotiation","05 · Influencer Negotiation",  "模拟品牌与达人的商务合作谈判"),
    ("campaign",   "06 · Campaign Performance",    "分析达人营销活动效果"),
    ("competitor", "07 · Competitor Analysis",     "分析竞品正在合作的达人及内容策略"),
    ("reply",      "08 · Creator Reply Analysis",  "分析达人回复邮件，提取意向与下一步"),
]


def _brand_block(brand: dict) -> str:
    if not brand:
        return "(品牌信息尚未录入，请先在 Brand & Product 页填写)"
    return f"""Brand: {brand.get('brand_name','Unknown')}
Product: {brand.get('product_name','Unknown')}
Category: {brand.get('category','Unknown')}
Target Market: {brand.get('target_market','Unknown')}
Target Audience: {brand.get('target_audience','Unknown')}
Price: {brand.get('product_price','Unknown')}
Positioning: {brand.get('brand_positioning','Unknown')}
Key Selling Points: {brand.get('key_selling_points','Unknown')}
Competitor Brands: {brand.get('competitor_brands','Unknown')}
Cooperation Budget: {brand.get('cooperation_budget','Unknown')}
Preferred Influencer Type: {brand.get('preferred_influencer_type','Unknown')}
Campaign Goals: {brand.get('campaign_goals','Unknown')}"""


def _influencer_block(inf: Optional[dict]) -> str:
    if not inf:
        return "(未指定具体达人，可粘贴批量达人资料)"
    return f"""Creator: {inf.get('creator_name','Unknown')}
Platform: {inf.get('platform','Unknown')}
Profile: {inf.get('profile_url','Unknown')}
Country: {inf.get('country','Unknown')}
Niche: {inf.get('niche','Unknown')}
Followers: {inf.get('followers','Unknown')}
Avg Views: {inf.get('average_views','Unknown')}
Engagement Rate: {inf.get('engagement_rate','Unknown')}
Audience Country: {inf.get('audience_country','Unknown')}
Audience Gender: {inf.get('audience_gender','Unknown')}
Audience Age: {inf.get('audience_age','Unknown')}
Contact Email: {inf.get('contact_email','Unknown')}
Content Style: {inf.get('content_style','Unknown')}
Previous Brand Collabs: {inf.get('previous_brand_collabs','Unknown')}
Estimated Rate: {inf.get('estimated_rate','Unknown')}"""


# 每类提示词的"骨架"模板：用 {brand} 与 {inf} 占位
TEMPLATES = {
"research": """# Role
You are a senior Influencer Marketing analyst with 8 years of experience vetting creators for DTC home & lifestyle brands.

# Context
{brand_block}

# Task
Conduct a structured creator research memo on the influencer below. Assess: content positioning, audience quality, brand-collaboration fit, and 3 specific content angles where our product could naturally appear.

# Input (Creator Profile)
{inf_block}

# Constraints
- If a data point is Unknown, explicitly say "Data missing" — never invent followers, engagement, past collabs, or video titles.
- Base every judgment only on the profile facts above.
- Flag any red flags (audience mismatch, overly sales-heavy history, bot-like engagement).

# Output Format
1. Creator Snapshot (3 bullet points)
2. Content Positioning & Style
3. Audience Quality Assessment
4. Brand–Creator Fit (1–10, with reasons)
5. 3 Content Angles (where the product fits naturally)
6. Red Flags / Data Gaps
7. Recommended Next Step (reach out / pass / gather more data)

# Evaluation Criteria
Accuracy to provided facts, absence of hallucinated data, actionable content angles, clear go/no-go recommendation.""",

"scoring": """# Role
You are an influencer scoring model for a performance-marketing team.

# Context
{brand_block}

# Task
Score the creator below on a 0–100 scale using SIX weighted dimensions. Show per-dimension score, weighted total, tier, and a one-line justification per dimension.

# Input (Creator Profile)
{inf_block}

# Scoring Weights
- Niche / content relevance: 25%
- Target market match: 20%
- Audience demographic match: 20%
- Content quality & style: 15%
- Engagement performance: 10%
- Budget fit: 10%

# Constraints
- Do NOT use follower count as the dominant signal; micro-influencers with high engagement can outscore mega-influencers.
- If data is Unknown for a dimension, score it neutrally (5/10) and mark "insufficient data" — do not assume.
- Tiers: 90–100 Highly Recommended, 80–89 Strong Match, 70–79 Potential Match, 60–69 Low Priority, <60 Not Recommended.

# Output Format
| Dimension | Weight | Raw Score (0-10) | Weighted | Reason |
Then: Total Score, Tier, Recommendation, Data gaps to fill.

# Evaluation Criteria
Weighted math must add up to 100, reasons cite the actual profile fields, Unknown fields are never guessed.""",

"outreach": """# Role
You are a senior partnership manager writing cold outreach emails to creators on behalf of a DTC brand.

# Context
{brand_block}

# Task
Write a personalized English outreach email to the creator below. It must read as if the writer actually studied the creator's channel — not a mail-merge template.

# Input (Creator Profile)
{inf_block}

# Required Sections
Subject Line · Personalized Opening · Brand Intro (2 sentences) · Product Intro · Creator-specific collaboration reason (tie it to the creator's stated niche / content style) · Collaboration Proposal · Call to Action · Professional Closing.

# Constraints
- NEVER invent specific videos, recent posts, brand collabs, or personal details not in the profile above. If you don't know their work, write a respectful, neutral opener referencing their niche — do not fake having watched a video.
- Keep it 120–180 words.
- Offer three subject-line alternatives.
- Tone: warm but professional; one clear CTA (reply with interest).

# Output Format
Subject: ...
Body: ...
Subject alternatives: 1) 2) 3)
Why this creator is a fit: ...
Suggested collaboration format: ...

# Evaluation Criteria
Personalization beyond the creator's first name, zero hallucinated facts, clear CTA, natural tone a real creator would reply to.""",

"followup": """# Role
You are a partnership manager sending a polite second-touch follow-up to a creator who has not replied to your first email.

# Context
{brand_block}
First email sent 5–7 days ago; creator has not replied.

# Task
Write a short, friendly follow-up email. Add one new piece of value (a tiny creative idea, a product perk, or a flexible-format option) to give the creator a reason to reply.

# Input (Creator Profile)
{inf_block}

# Constraints
- 80–120 words max.
- No guilt-tripping, no multiple follow-up labels.
- Never invent details about their content.
- End with a soft CTA.

# Output Format
Subject / Body / Suggested timing for the next (and final) follow-up.

# Evaluation Criteria
Polite, concise, adds new value, respects the creator's time.""",

"negotiation": """# Role
You are an experienced DTC brand manager negotiating paid + seeding collaborations with creators.

# Context
{brand_block}
Creator's estimated rate: {inf_block}

# Task
Role-play the negotiation. Given the creator's likely asks, draft: (1) our opening offer, (2) a fallback package, (3) the walk-away point. Include tradeables we can offer (commission tier, whitelisting rights, future ambassadorship).

# Constraints
- Stay within the stated cooperation budget; if no budget is given, propose a tiered framework and flag it.
- Never promise exclusivity we cannot deliver.
- Distinguish free-product seeding vs paid post vs affiliate commission.

# Output Format
Opening offer / Fallback / Walk-away / Tradeables / Key red lines.

# Evaluation Criteria
Commercially realistic, budget-aware, preserves the relationship, clear walk-away.""",

"campaign": """# Role
You are a campaign analyst measuring influencer marketing performance for a DTC brand.

# Context
{brand_block}

# Task
Given the campaign data pasted below (creator, posts, reach, clicks, conversions, cost), calculate: engagement rate, CTR, conversion rate, cost per result, and ROI per creator. Identify top and bottom performers and recommend who to re-book.

# Input
Paste campaign CSV / numbers here:
{{CAMPAIGN_DATA}}

# Constraints
- Show formulas used.
- If a metric is missing, mark it Unknown rather than estimating.
- Separate correlation from causation (reach vs sales).

# Output Format
KPI summary table · Per-creator ranking · 3 insights · Re-book / drop recommendations.

# Evaluation Criteria
Correct math, honest treatment of missing data, actionable re-book decisions.""",

"competitor": """# Role
You are a competitive intelligence analyst tracking which creators rival brands work with.

# Context
{brand_block}

# Task
Analyze the competitor creator list pasted below. Identify: which niches competitors over-invest in, which under-served niches we could target, creators who appear to be saturated by competitor partnerships (avoid), and white-space opportunities for us.

# Input
Paste competitor creator list here:
{{COMPETITOR_DATA}}

# Constraints
- Do not fabricate competitor campaigns.
- Base conclusions only on the pasted list.

# Output Format
Niche concentration map · Over-saturated creators · White-space opportunities · 5 creator archetypes we should target next.

# Evaluation Criteria
Strategic, non-obvious, grounded in the data, leads to a concrete shortlist.""",

"reply": """# Role
You are a partnership manager triaging incoming creator replies.

# Task
Analyze the creator's English reply pasted below and produce a triage note + a draft reply.

# Input (Creator)
{inf_block}

# Input (Creator's Reply — paste below)
{{CREATOR_REPLY}}

# Constraints
- Classify intent: interested / not interested / price-negotiation / needs-info / declined.
- Extract: quoted rate, asks (free product? commission? exclusivity?), objections, timeline.
- Do not over-read enthusiasm; quote the exact phrase that shows intent.
- Draft reply must be professional, move to the next step, and never concede budget without a trade.

# Output Format
1. Chinese translation of the reply
2. Intent classification + confidence
3. Key extracted points (rate / asks / objections)
4. Business risk flags
5. Recommended reply strategy (3 bullet steps)
6. Draft English reply email

# Evaluation Criteria
Accurate extraction, balanced optimism, draft reply that advances the deal.""",
}


def build_prompt(key: str, brand: dict, inf: Optional[dict]) -> str:
    """根据 key 渲染完整提示词，自动填入品牌与达人信息。"""
    tpl = TEMPLATES.get(key, "")
    return tpl.replace("{brand_block}", _brand_block(brand)).replace("{inf_block}", _influencer_block(inf))
