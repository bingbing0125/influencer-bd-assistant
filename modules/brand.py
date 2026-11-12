# -*- coding: utf-8 -*-
"""Module 01 — Brand & Product 信息管理"""
import streamlit as st
import database as db


def render():
    st.header("🏷️ Brand & Product")
    st.caption("录入品牌与产品信息，系统将据此生成 Brand Brief 作为达人筛选与开发信的依据。")

    brand = db.get_brand()

    with st.form("brand_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            brand_name = st.text_input("Brand Name", value=brand.get("brand_name", ""), placeholder="HomeGlow")
            product_name = st.text_input("Product Name", value=brand.get("product_name", ""), placeholder="Smart Ambient Light")
            category = st.text_input("Product Category", value=brand.get("category", ""), placeholder="Home & Living")
            product_price = st.text_input("Product Price", value=brand.get("product_price", ""), placeholder="$49.99")
            target_market = st.text_input("Target Market", value=brand.get("target_market", ""), placeholder="United States")
            target_audience = st.text_input("Target Audience", value=brand.get("target_audience", ""),
                                            placeholder="Women aged 25–40")
        with c2:
            brand_positioning = st.text_input("Brand Positioning", value=brand.get("brand_positioning", ""),
                                              placeholder="Affordable premium smart home for modern apartments")
            cooperation_budget = st.text_input("Cooperation Budget", value=brand.get("cooperation_budget", ""),
                                               placeholder="$200–$800 per post")
            preferred_influencer_type = st.text_input("Preferred Influencer Type",
                                                      value=brand.get("preferred_influencer_type", ""),
                                                      placeholder="Micro / mid-tier creators, 10k–200k followers")
            campaign_goals = st.text_input("Campaign Goals", value=brand.get("campaign_goals", ""),
                                           placeholder="Awareness + UGC + product seeding")
            competitor_brands = st.text_input("Competitor Brands", value=brand.get("competitor_brands", ""),
                                              placeholder="Govee, Philips Hue, Nanoleaf")

        key_selling_points = st.text_area("Key Selling Points (每行一条)",
                                          value=brand.get("key_selling_points", ""),
                                          placeholder="Smart lighting control\nModern minimalist design\nEasy installation\nSuitable for bedrooms and living rooms")
        product_description = st.text_area("Product Description",
                                           value=brand.get("product_description", ""),
                                           placeholder="A Wi-Fi enabled ambient light strip...")

        submitted = st.form_submit_button("💾 Save Brand Profile", type="primary")
        if submitted:
            db.save_brand({
                "brand_name": brand_name, "product_name": product_name,
                "category": category, "product_description": product_description,
                "target_market": target_market, "target_audience": target_audience,
                "product_price": product_price, "brand_positioning": brand_positioning,
                "key_selling_points": key_selling_points, "competitor_brands": competitor_brands,
                "cooperation_budget": cooperation_budget,
                "preferred_influencer_type": preferred_influencer_type,
                "campaign_goals": campaign_goals,
            })
            st.success("Brand profile saved.")

    # 生成 Brand Brief
    st.divider()
    st.subheader("📄 Generated Brand Brief")
    b = db.get_brand()
    if not b or not b.get("brand_name"):
        st.info("请先保存品牌信息，Brand Brief 将自动生成。")
        return

    sp = b.get("key_selling_points", "") or ""
    brief = f"""**{b.get('brand_name')}** — {b.get('product_name')} ({b.get('category','')})

- **Target Market:** {b.get('target_market','Unknown')}
- **Target Audience:** {b.get('target_audience','Unknown')}
- **Price:** {b.get('product_price','Unknown')}
- **Positioning:** {b.get('brand_positioning','Unknown')}
- **Campaign Goals:** {b.get('campaign_goals','Unknown')}
- **Budget:** {b.get('cooperation_budget','Unknown')}
- **Preferred Creator Type:** {b.get('preferred_influencer_type','Unknown')}

**Key Selling Points:**
""" + "\n".join(f"- {line.strip()}" for line in sp.splitlines() if line.strip())

    st.markdown(brief)
    st.caption("这份 Brief 会自动注入到「AI Creator Matching」「Email Generator」与「Prompt Engineering」工作台。")
