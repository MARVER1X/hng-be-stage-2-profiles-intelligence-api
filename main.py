from datetime import datetime, timezone
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import time

app = FastAPI(title="Insighta Labs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "profiles.db"

# UUID v7 generator
def generate_uuid_v7() -> str:
    ts_ms = int(time.time() * 1000)
    rand = int.from_bytes(os.urandom(10), "big")

    uuid_int = (
        (ts_ms & 0xFFFFFFFFFFFF) << 80 |
        (0x7 << 76) |
        ((rand >> 50) & 0xFFF) << 64 |
        (0b10 << 62) |
        (rand & 0x3FFFFFFFFFFFFFFF)
    )

    h = format(uuid_int, "032x")
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"



# Time helper
def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Age grouping
def get_age_group(age: int) -> str:
    if age <= 12:
        return "child"
    if age <= 19:
        return "teenager"
    if age <= 59:
        return "adult"
    return "senior"


# DB connection
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# DB schema init
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            gender TEXT,
            gender_probability REAL,
            age INTEGER,
            age_group TEXT,
            country_id TEXT,
            country_name TEXT,
            country_probability REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()
