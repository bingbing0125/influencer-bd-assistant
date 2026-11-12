# -*- coding: utf-8 -*-
"""
seed_demo.py — 灌入 30 条 Demo 达人数据（明确标记为模拟数据）。
用法：python seed_demo.py
"""
import database as db


# 30 位模拟达人：覆盖 US/UK/Canada × TikTok/Instagram/YouTube × 5 个 niche
DEMO = [
    # ---- US · Home Decor ----
    ("Sarah Chen",      "Instagram", "https://instagram.com/sarahcozyhome",  "United States", "Home Decor",      85000,  12000, 3.2, "United States", "Female", "25-34", "sarah@cozyhome.example.com",  "warm minimal bedroom styling", "Article, Wayfair",   "$350/post",  "Demo Data"),
    ("Emily Rodriguez", "TikTok",    "https://tiktok.com/emilymakedo",       "United States", "Home Decor",      240000, 95000, 5.1, "United States", "Female", "24-32", "emily@makedo.example.com",    "room makeover transitions",    "Target, Etsy",       "$600/post",  "Demo Data"),
    ("Jessica Park",    "YouTube",   "https://youtube.com/jessicahome",      "United States", "Home Decor",      510000, 45000, 1.8, "United States", "Female", "28-40", "jessica@homevlog.example.com","long-form home tours",         "West Elm, IKEA",     "$1500/video","Demo Data"),
    ("Mia Thompson",    "Instagram", "https://instagram.com/miacozyflat",    "United States", "Home Decor",      42000,  6000,  4.4, "United States", "Female", "26-35", "mia@cozyflat.example.com",    "neutral palette corners",      "Unknown",            "$200/post",  "Demo Data"),
    ("Ava Williams",    "TikTok",    "https://tiktok.com/avasmallspace",     "United States", "Apartment Living",68000,  30000, 4.8, "United States", "Female", "23-30", "ava@smallspace.example.com",  "rent-friendly hacks",          "Amazon home",        "$280/post",  "Demo Data"),

    # ---- US · Smart Home ----
    ("Jason Lee",       "YouTube",   "https://youtube.com/jasonsetups",      "United States", "Smart Home",      890000, 120000,2.1, "United States", "Male",   "25-38", "jason@setups.example.com",    "smart home tour & reviews",    "Govee, TP-Link",     "$2200/video","Demo Data"),
    ("Kevin Zhang",     "TikTok",    "https://tiktok.com/kevindigitizes",    "United States", "Smart Home",      156000, 70000, 3.9, "United States", "Male",   "24-34", "kevin@digitizes.example.com",  "gadget unboxing shorts",       "Anker, Eufy",        "$450/post",  "Demo Data"),
    ("Mike Carter",     "YouTube",   "https://youtube.com/mkccreates",       "United States", "Smart Home",      320000, 28000, 1.5, "United States", "Male",   "30-45", "mike@mkccreates.example.com",  "deep-dive tech reviews",       "Philips Hue",        "$1100/video","Demo Data"),
    ("Andy Ruiz",       "Instagram", "https://instagram.com/andysmartflat",  "United States", "Smart Home",      38000,  4500,  2.8, "United States", "Male",   "26-35", "andy@smartflat.example.com",   "desk & room setup reels",      "Unknown",            "$180/post",  "Demo Data"),

    # ---- US · Lifestyle / Apartment ----
    ("Lily Martinez",   "TikTok",    "https://tiktok.com/lilydailylife",     "United States", "Lifestyle",       410000, 180000,6.2, "United States", "Female", "22-30", "lily@dailylife.example.com",   "morning routine vlogs",        "Dyson, Glossier",    "$900/post",  "Demo Data"),
    ("Sophia Scott",    "Instagram", "https://instagram.com/sophslowliving", "United States", "Lifestyle",       92000,  9000,  3.6, "United States", "Female", "27-38", "soph@slowliving.example.com",  "aesthetic daily life",         "Crate & Barrel",     "$380/post",  "Demo Data"),
    ("Emma Brown",      "YouTube",   "https://youtube.com/emmaapartment",    "United States", "Apartment Living",275000, 22000, 2.0, "United States", "Female", "25-34", "emma@apartment.example.com",   "NYC apartment diaries",        "IKEA, West Elm",     "$800/video", "Demo Data"),
    ("Olivia Davis",    "TikTok",    "https://tiktok.com/oliviabudget",      "United States", "Apartment Living",180000, 60000, 4.0, "United States", "Female", "23-32", "olivia@budget.example.com",    "renter-friendly budget decor", "Target",             "$350/post",  "Demo Data"),
    ("Isabella Garcia", "Instagram", "https://instagram.com/isa cozy",       "United States", "Lifestyle",       54000,  5200,  3.1, "United States", "Female", "25-34", "isa@cozy.example.com",         "cozy Sunday routine",          "Unknown",            "$220/post",  "Demo Data"),

    # ---- US · Furniture ----
    ("Daniel Kim",      "YouTube",   "https://youtube.com/dkfurniture",      "United States", "Furniture",       430000, 38000, 1.7, "United States", "Male",   "30-45", "daniel@dkfurniture.example.com","furniture build & review",    "Article, Burrow",    "$1300/video","Demo Data"),
    ("Ryan Miller",     "TikTok",    "https://tiktok.com/ryandecor",         "United States", "Furniture",       97000,  41000, 4.2, "United States", "Male",   "26-38", "ryan@decor.example.com",       "before/after room flips",      "Wayfair",            "$400/post",  "Demo Data"),

    # ---- UK ----
    ("Chloe Walker",    "Instagram", "https://instagram.com/chloelondonflat","United Kingdom","Home Decor",      76000,  8800,  3.4, "United Kingdom","Female", "26-35", "chloe@londonflat.example.com", "Scandinavian small flat",      "John Lewis",         "£280/post",  "Demo Data"),
    ("James Bennett",   "YouTube",   "https://youtube.com/jbtechuk",         "United Kingdom","Smart Home",      610000, 52000, 1.9, "United Kingdom","Male",   "28-42", "james@jbtech.example.com",    "UK smart home reviews",        "Bosch, Hive",        "£1800/video","Demo Data"),
    ("Holly Ellis",     "TikTok",    "https://tiktok.com/hollymakeshome",    "United Kingdom","Home Decor",      132000, 55000, 5.0, "United Kingdom","Female", "24-32", "holly@makeshome.example.com",  "UK room makeover shorts",      "B&Q, Dunelm",        "£350/post",  "Demo Data"),
    ("Owen Hughes",     "TikTok",    "https://tiktok.com/owensetup",         "United Kingdom","Smart Home",      88000,  36000, 3.7, "United Kingdom","Male",   "23-32", "owen@setup.example.com",       "battestation & desk setups",   "Unknown",            "£260/post",  "Demo Data"),
    ("Amelia Ford",     "Instagram", "https://instagram.com/amelialifeuk",   "United Kingdom","Lifestyle",       49000,  4200,  3.0, "United Kingdom","Female", "25-34", "amelia@lifeuk.example.com",    "cozy UK daily routine",        "M&S",                "£180/post",  "Demo Data"),
    ("George Clarke",   "YouTube",   "https://youtube.com/gcflatliving",     "United Kingdom","Apartment Living",156000, 12000, 1.6, "United Kingdom","Male",   "28-40", "george@flatliving.example.com","London flat renovation",       "Dunelm",             "£650/video", "Demo Data"),

    # ---- Canada ----
    ("Emma MacDonald",  "Instagram", "https://instagram.com/emmacohome",     "Canada",        "Home Decor",      63000,  7100,  3.3, "Canada",        "Female", "26-36", "emma@cohome.example.com",      "Canadian cottage decor",       "Structube",          "C$260/post", "Demo Data"),
    ("Liam O'Connor",   "TikTok",    "https://tiktok.com/liamsetups",        "Canada",        "Smart Home",      118000, 48000, 4.1, "Canada",        "Male",   "24-33", "liam@setups.example.com",      "Toronto tech setup shorts",    "Unknown",            "C$320/post", "Demo Data"),
    ("Sophie Trudeau",  "YouTube",   "https://youtube.com/sophielivingca",   "Canada",        "Lifestyle",       220000, 18000, 1.8, "Canada",        "Female", "26-36", "sophie@livingca.example.com",  "Vancouver lifestyle vlogs",    "Hudson's Bay",       "C$750/video","Demo Data"),
    ("Noah Tremblay",   "TikTok",    "https://tiktok.com/noahreno",          "Canada",        "Furniture",       74000,  29000, 3.9, "Canada",        "Male",   "27-40", "noah@reno.example.com",        "DIY furniture flip",           "Unknown",            "C$250/post", "Demo Data"),
    ("Ava Leblanc",     "Instagram", "https://instagram.com/avacozyca",      "Canada",        "Apartment Living",33000,  3800,  4.5, "Canada",        "Female", "24-31", "ava@cozyca.example.com",       "Montreal small apartment",     "Unknown",            "C$150/post", "Demo Data"),

    # ---- 数据不完整的"边界案例"，用来演示 Unknown 标注 ----
    ("Mystery Creator", "TikTok",    "https://tiktok.com/mystery",           "Unknown",       "Home Decor",      120000, 0,     0.0, "Unknown",       "Unknown","Unknown","",                              "Unknown",                      "Unknown",            "Unknown",    "Demo Data — missing email/metrics"),
    ("No Metrics Kate", "Instagram", "https://instagram.com/nometrics",      "United States", "Lifestyle",       0,      0,     0.0, "Unknown",       "Female", "25-34", "kate@nometrics.example.com",   "soft lifestyle aesthetic",     "Unknown",            "Unknown",    "Demo Data — zero follower data"),
    ("Budget Micro Sam","TikTok",    "https://tiktok.com/microsam",          "United States", "Apartment Living",2200,   1500,  8.5, "United States", "Female", "22-28", "sam@micro.example.com",        "micro influencer high engagement", "Unknown",        "$50/post",   "Demo Data — nano creator"),
]


def seed():
    db.init_db()
    # 示例品牌
    db.save_brand({
        "brand_name": "HomeGlow",
        "product_name": "Smart Ambient Light",
        "category": "Home & Living",
        "product_description": "Wi-Fi enabled smart ambient light strip with app control, scene presets and warm-to-cool dimming. Tool-free installation, designed for bedrooms and living rooms.",
        "target_market": "United States",
        "target_audience": "Women aged 25–40",
        "product_price": "$49.99",
        "brand_positioning": "Affordable premium smart home for modern apartments",
        "key_selling_points": "Smart lighting control\nModern minimalist design\nEasy installation\nSuitable for bedrooms and living rooms",
        "competitor_brands": "Govee, Philips Hue, Nanoleaf",
        "cooperation_budget": "$200–$800 per post",
        "preferred_influencer_type": "Micro / mid-tier creators, 10k–200k followers",
        "campaign_goals": "Awareness + UGC + product seeding",
    })

    n = 0
    for row in DEMO:
        (name, platform, url, country, niche, followers, views, er,
         aud_country, aud_gender, aud_age, email, style, collabs, rate, notes) = row
        db.upsert_influencer({
            "creator_name": name, "platform": platform, "profile_url": url,
            "country": country, "niche": niche, "followers": followers,
            "average_views": views, "engagement_rate": er,
            "audience_country": aud_country, "audience_gender": aud_gender,
            "audience_age": aud_age, "contact_email": email,
            "content_style": style, "previous_brand_collabs": collabs,
            "estimated_rate": rate, "notes": notes,
        }, is_demo=1)
        n += 1
    print(f"Seeded {n} demo influencers + brand HomeGlow.")


if __name__ == "__main__":
    seed()
