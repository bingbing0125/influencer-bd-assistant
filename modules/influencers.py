# -*- coding: utf-8 -*-
"""Module 02 — Influencer Database：增删改查、CSV/Excel 导入导出、筛选、详情"""
import io
import pandas as pd
import streamlit as st

import database as db
from config import UNKNOWN, PLATFORMS


def _df_from_rows(rows):
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df[[
        "id", "creator_name", "platform", "country", "niche", "followers",
        "average_views", "engagement_rate", "audience_country",
        "audience_gender", "audience_age", "contact_email", "content_style",
        "previous_brand_collabs", "estimated_rate", "is_demo",
    ]]


def render():
    st.header("👥 Influencer Database")
    st.caption("手动新增 / Excel·CSV 批量导入 / 条件筛选 / 导出。无数据字段标记为 Unknown，系统不会编造。")

    rows = db.list_influencers()
    df = _df_from_rows(rows)

    # ---------- 工具栏 ----------
    t1, t2, t3, t4 = st.tabs(["➕ Add Manually", "📥 Import Excel/CSV", "🔍 Browse & Filter", "📤 Export"])

    # ---- 手动新增 ----
    with t1:
        with st.form("add_inf", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                creator_name = st.text_input("Creator Name *")
                platform = st.selectbox("Platform", PLATFORMS)
                profile_url = st.text_input("Profile URL")
                country = st.text_input("Country (e.g. United States)")
                niche = st.text_input("Niche (e.g. Home Decor)")
                followers = st.number_input("Followers", min_value=0, step=1000)
                average_views = st.number_input("Average Views", min_value=0, step=1000)
                engagement_rate = st.number_input("Engagement Rate (%)", min_value=0.0, max_value=100.0, step=0.1)
            with c2:
                audience_country = st.text_input("Audience Country")
                audience_gender = st.selectbox("Audience Gender", ["", "Female", "Male", "Mixed"])
                audience_age = st.text_input("Audience Age (e.g. 25-34)")
                contact_email = st.text_input("Contact Email")
                content_style = st.text_input("Content Style")
                previous_brand_collabs = st.text_input("Previous Brand Collabs")
                estimated_rate = st.text_input("Estimated Rate (e.g. $300/post)")
                notes = st.text_area("Notes")
            if st.form_submit_button("Add Influencer", type="primary"):
                if not creator_name.strip():
                    st.error("Creator Name is required.")
                else:
                    db.upsert_influencer({
                        "creator_name": creator_name, "platform": platform,
                        "profile_url": profile_url, "country": country, "niche": niche,
                        "followers": followers, "average_views": average_views,
                        "engagement_rate": engagement_rate,
                        "audience_country": audience_country,
                        "audience_gender": audience_gender, "audience_age": audience_age,
                        "contact_email": contact_email, "content_style": content_style,
                        "previous_brand_collabs": previous_brand_collabs,
                        "estimated_rate": estimated_rate, "notes": notes,
                    })
                    st.success(f"Added {creator_name}.")
                    st.rerun()

    # ---- 批量导入 ----
    with t2:
        st.write("上传 `.xlsx` 或 `.csv`，列名需与下表一致（缺列自动留空）。")
        template_cols = ["creator_name", "platform", "profile_url", "country", "niche",
                         "followers", "average_views", "engagement_rate",
                         "audience_country", "audience_gender", "audience_age",
                         "contact_email", "content_style", "previous_brand_collabs",
                         "estimated_rate", "notes"]
        st.code(", ".join(template_cols))
        up = st.file_uploader("Upload file", type=["xlsx", "csv"])
        is_demo = st.checkbox("标记为 Demo Data（模拟数据）", value=False)
        if up is not None:
            try:
                if up.name.lower().endswith(".csv"):
                    data = pd.read_csv(up)
                else:
                    data = pd.read_excel(up)
                # 列名兼容（忽略大小写）
                data.columns = [c.strip().lower().replace(" ", "_") for c in data.columns]
                records = data.to_dict(orient="records")
                n = db.bulk_insert_influencers(records, is_demo=1 if is_demo else 0)
                st.success(f"成功导入 {n} 位达人。")
                st.rerun()
            except Exception as e:
                st.error(f"导入失败：{e}")

    # ---- 浏览与筛选 ----
    with t3:
        if df.empty:
            st.info("数据库为空。请手动添加或导入 Demo 数据。")
        else:
            f1, f2, f3 = st.columns(3)
            with f1:
                plat_choice = st.multiselect("Platform", options=sorted(df["platform"].dropna().unique().tolist()))
            with f2:
                country_choice = st.multiselect("Country", options=sorted(df["country"].dropna().unique().tolist()))
            with f3:
                niche_choice = st.multiselect("Niche", options=sorted(df["niche"].dropna().unique().tolist()))

            filtered = df.copy()
            if plat_choice:
                filtered = filtered[filtered["platform"].isin(plat_choice)]
            if country_choice:
                filtered = filtered[filtered["country"].isin(country_choice)]
            if niche_choice:
                filtered = filtered[filtered["niche"].isin(niche_choice)]

            st.write(f"共 **{len(filtered)}** 位达人")
            st.dataframe(filtered, use_container_width=True, hide_index=True)

            # 详情
            ids = filtered["id"].tolist() if not filtered.empty else []
            if ids:
                detail_id = st.selectbox("View detail (ID)", options=ids,
                                         format_func=lambda x: f"#{x} — {db.get_influencer(x)['creator_name']}")
                inf = db.get_influencer(detail_id)
                if inf:
                    st.subheader(f"📌 {inf['creator_name']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        for k in ["platform", "profile_url", "country", "niche", "followers",
                                  "average_views", "engagement_rate"]:
                            v = inf.get(k)
                            st.markdown(f"**{k}:** {v if v not in (None, '', 0) else UNKNOWN}")
                    with c2:
                        for k in ["audience_country", "audience_gender", "audience_age",
                                  "contact_email", "content_style", "previous_brand_collabs",
                                  "estimated_rate"]:
                            v = inf.get(k)
                            st.markdown(f"**{k}:** {v if v not in (None, '') else UNKNOWN}")
                    if inf.get("notes"):
                        st.markdown(f"**Notes:** {inf['notes']}")
                    if inf.get("is_demo"):
                        st.info("⚠️ This is Demo Data — simulated for product demo, not a real creator.")
                    if st.button("🗑️ Delete this influencer", type="secondary"):
                        db.delete_influencer(detail_id)
                        st.rerun()

    # ---- 导出 ----
    with t4:
        if df.empty:
            st.info("没有可导出的数据。")
        else:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine="openpyxl") as w:
                df.to_excel(w, index=False, sheet_name="Influencers")
            st.download_button(
                "⬇️ Download Influencer Database (.xlsx)",
                data=out.getvalue(),
                file_name="influencer_database.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
