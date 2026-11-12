# -*- coding: utf-8 -*-
"""
database.py — SQLite 持久层。
负责建表、连接管理与所有 CRUD 操作。Streamlit 中每个 session 按需 get_conn()。
"""
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Any

import config


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        c = conn.cursor()

        # 品牌信息（单条活跃记录，id=1）
        c.execute("""
        CREATE TABLE IF NOT EXISTS brand (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            brand_name TEXT, product_name TEXT, category TEXT,
            product_description TEXT, target_market TEXT, target_audience TEXT,
            product_price TEXT, brand_positioning TEXT, key_selling_points TEXT,
            competitor_brands TEXT, cooperation_budget TEXT,
            preferred_influencer_type TEXT, campaign_goals TEXT,
            updated_at TEXT
        )""")

        # 达人库
        c.execute("""
        CREATE TABLE IF NOT EXISTS influencers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_name TEXT NOT NULL,
            platform TEXT, profile_url TEXT, country TEXT, niche TEXT,
            followers INTEGER DEFAULT 0, average_views INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0,
            audience_country TEXT, audience_gender TEXT, audience_age TEXT,
            contact_email TEXT, content_style TEXT, previous_brand_collabs TEXT,
            estimated_rate TEXT, notes TEXT,
            is_demo INTEGER DEFAULT 0,
            created_at TEXT
        )""")

        # 评分权重（可调）
        c.execute("""
        CREATE TABLE IF NOT EXISTS scoring_weights (
            dimension TEXT PRIMARY KEY,
            weight REAL NOT NULL
        )""")
        for dim, w in config.DEFAULT_WEIGHTS.items():
            c.execute("INSERT OR IGNORE INTO scoring_weights(dimension, weight) VALUES (?,?)",
                      (dim, w))

        # 已生成的邮件
        c.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_id INTEGER,
            style TEXT,
            subject TEXT, body TEXT, chinese_translation TEXT,
            personalization_notes TEXT, match_reason TEXT,
            suggested_collab TEXT, subject_alternatives TEXT,
            created_at TEXT,
            FOREIGN KEY(influencer_id) REFERENCES influencers(id) ON DELETE CASCADE
        )""")

        # CRM
        c.execute("""
        CREATE TABLE IF NOT EXISTS crm (
            influencer_id INTEGER PRIMARY KEY,
            status TEXT DEFAULT 'To Contact',
            first_contacted_at TEXT, email_sent_at TEXT, last_reply_at TEXT,
            next_followup_at TEXT, quoted_rate TEXT, collaboration_type TEXT,
            reply_summary TEXT, notes TEXT,
            history TEXT DEFAULT '[]',
            updated_at TEXT,
            FOREIGN KEY(influencer_id) REFERENCES influencers(id) ON DELETE CASCADE
        )""")

        # 邮件回复分析记录
        c.execute("""
        CREATE TABLE IF NOT EXISTS reply_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_id INTEGER,
            raw_reply TEXT, translation TEXT, intent TEXT,
            key_points TEXT, risks TEXT, suggested_reply TEXT,
            created_at TEXT
        )""")

        # 效率测试记录
        c.execute("""
        CREATE TABLE IF NOT EXISTS efficiency_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT, mode TEXT, n_items INTEGER,
            seconds REAL, note TEXT, created_at TEXT
        )""")

        # 用户自定义 Prompt
        c.execute("""
        CREATE TABLE IF NOT EXISTS custom_prompts (
            key TEXT PRIMARY KEY,
            name TEXT, content TEXT, updated_at TEXT
        )""")


# ==================== 品牌 ====================
def save_brand(data: dict):
    data = dict(data)
    data["updated_at"] = _now()
    cols = ", ".join(data.keys())
    marks = ", ".join(["?"] * len(data))
    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO brand(id, {cols}) VALUES (1, {marks}) "
            f"ON CONFLICT(id) DO UPDATE SET {', '.join(f'{k}=excluded.{k}' for k in data)}",
            list(data.values()),
        )


def get_brand() -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM brand WHERE id=1").fetchone()
        return dict(row) if row else {}


# ==================== 达人 ====================
INFLUENCER_FIELDS = [
    "creator_name", "platform", "profile_url", "country", "niche",
    "followers", "average_views", "engagement_rate",
    "audience_country", "audience_gender", "audience_age",
    "contact_email", "content_style", "previous_brand_collabs",
    "estimated_rate", "notes",
]


def upsert_influencer(data: dict, inf_id: int = None, is_demo: int = 0) -> int:
    payload = {k: data.get(k) for k in INFLUENCER_FIELDS}
    # 数值清洗
    for k in ("followers", "average_views"):
        try:
            payload[k] = int(float(payload[k] or 0))
        except (TypeError, ValueError):
            payload[k] = 0
    try:
        payload["engagement_rate"] = float(payload.get("engagement_rate") or 0)
    except (TypeError, ValueError):
        payload["engagement_rate"] = 0.0

    with get_conn() as conn:
        if inf_id:
            cols = ", ".join(f"{k}=?" for k in payload)
            conn.execute(f"UPDATE influencers SET {cols} WHERE id=?",
                         list(payload.values()) + [inf_id])
            return inf_id
        else:
            cols = ", ".join(payload.keys())
            marks = ", ".join(["?"] * len(payload))
            cur = conn.execute(
                f"INSERT INTO influencers({cols}, is_demo, created_at) "
                f"VALUES ({marks}, ?, ?)",
                list(payload.values()) + [is_demo, _now()],
            )
            new_id = cur.lastrowid
            # 自动建立 CRM 行
            conn.execute("INSERT OR IGNORE INTO crm(influencer_id, status) VALUES (?, 'To Contact')",
                         (new_id,))
            return new_id


def list_influencers() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM influencers ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def get_influencer(inf_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM influencers WHERE id=?", (inf_id,)).fetchone()
        return dict(row) if row else None


def delete_influencer(inf_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM influencers WHERE id=?", (inf_id,))


def bulk_insert_influencers(rows: list[dict], is_demo: int = 0) -> int:
    n = 0
    for r in rows:
        if r.get("creator_name"):
            upsert_influencer(r, is_demo=is_demo)
            n += 1
    return n


# ==================== 评分权重 ====================
def get_weights() -> dict:
    with get_conn() as conn:
        rows = conn.execute("SELECT dimension, weight FROM scoring_weights").fetchall()
        return {r["dimension"]: r["weight"] for r in rows} or dict(config.DEFAULT_WEIGHTS)


def set_weights(weights: dict):
    with get_conn() as conn:
        for k, v in weights.items():
            conn.execute("UPDATE scoring_weights SET weight=? WHERE dimension=?", (v, k))


# ==================== 邮件 ====================
def save_email(email: dict):
    email = dict(email)
    email["created_at"] = _now()
    cols = ", ".join(email.keys())
    marks = ", ".join(["?"] * len(email))
    with get_conn() as conn:
        conn.execute(f"INSERT INTO emails({cols}) VALUES ({marks})", list(email.values()))


def list_emails(influencer_id: int = None) -> list[dict]:
    q = "SELECT * FROM emails"
    args = []
    if influencer_id:
        q += " WHERE influencer_id=?"
        args = [influencer_id]
    q += " ORDER BY id DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, args).fetchall()]


# ==================== CRM ====================
def get_crm(inf_id: int) -> dict:
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO crm(influencer_id, status) VALUES (?, 'To Contact')",
                     (inf_id,))
        row = conn.execute("SELECT * FROM crm WHERE influencer_id=?", (inf_id,)).fetchone()
        d = dict(row)
        try:
            d["history"] = json.loads(d.get("history") or "[]")
        except Exception:
            d["history"] = []
        return d


def update_crm(inf_id: int, fields: dict, append_history: str | None = None):
    crm = get_crm(inf_id)
    history = crm["history"]
    if append_history:
        history.append({"time": _now(), "event": append_history})
    fields = dict(fields)
    fields["history"] = json.dumps(history, ensure_ascii=False)
    fields["updated_at"] = _now()
    cols = ", ".join(f"{k}=?" for k in fields)
    with get_conn() as conn:
        conn.execute(f"UPDATE crm SET {cols} WHERE influencer_id=?",
                     list(fields.values()) + [inf_id])


def list_crm() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT c.*, i.creator_name, i.platform, i.country, i.niche
            FROM crm c JOIN influencers i ON i.id = c.influencer_id
            ORDER BY c.updated_at DESC
        """).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["history"] = json.loads(d.get("history") or "[]")
            except Exception:
                d["history"] = []
            out.append(d)
        return out


# ==================== 回复分析 ====================
def save_reply_analysis(data: dict):
    data = dict(data)
    data["created_at"] = _now()
    cols = ", ".join(data.keys())
    marks = ", ".join(["?"] * len(data))
    with get_conn() as conn:
        conn.execute(f"INSERT INTO reply_analyses({cols}) VALUES ({marks})", list(data.values()))


def list_reply_analyses() -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM reply_analyses ORDER BY id DESC").fetchall()]


# ==================== 效率测试 ====================
def add_efficiency_test(task_type: str, mode: str, n_items: int, seconds: float, note: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO efficiency_tests(task_type, mode, n_items, seconds, note, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (task_type, mode, n_items, seconds, note, _now()),
        )


def list_efficiency_tests() -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM efficiency_tests ORDER BY id DESC").fetchall()]


# ==================== 自定义 Prompt ====================
def save_custom_prompt(key: str, name: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO custom_prompts(key, name, content, updated_at) VALUES (?,?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET name=excluded.name, content=excluded.content, updated_at=excluded.updated_at",
            (key, name, content, _now()),
        )


def get_custom_prompt(key: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM custom_prompts WHERE key=?", (key,)).fetchone()
        return dict(row) if row else None
