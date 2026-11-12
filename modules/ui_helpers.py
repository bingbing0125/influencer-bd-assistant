# -*- coding: utf-8 -*-
"""modules/ui_helpers.py — 共享 UI 小组件"""
import streamlit as st


def kpi_row(items: list[tuple]):
    """items: [(label, value, delta?)]"""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label, value = item[0], item[1]
        delta = item[2] if len(item) > 2 else None
        col.metric(label, value, delta=delta)


def tag(text: str, color: str = "#1F3A93") -> str:
    return f"<span style='background:{color}15;color:{color};padding:2px 10px;border-radius:999px;font-size:12px;font-weight:600'>{text}</span>"


def unknown_badge():
    return "<span style='color:#9CA3AF;font-style:italic'>Unknown</span>"
