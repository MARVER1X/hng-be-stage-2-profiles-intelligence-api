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

# Country name → ISO 2-letter code mapping (for NLP parser)
COUNTRY_NAME_TO_ID = {
    "nigeria": "NG", "nigerian": "NG",
    "ghana": "GH", "ghanaian": "GH",
    "kenya": "KE", "kenyan": "KE",
    "south africa": "ZA", "south african": "ZA",
    "ethiopia": "ET", "ethiopian": "ET",
    "tanzania": "TZ", "tanzanian": "TZ",
    "uganda": "UG", "ugandan": "UG",
    "angola": "AO", "angolan": "AO",
    "mozambique": "MZ",
    "cameroon": "CM", "cameroonian": "CM",
    "niger": "NE",
    "mali": "ML", "malian": "ML",
    "malawi": "MW", "malawian": "MW",
    "zambia": "ZM", "zambian": "ZM",
    "senegal": "SN", "senegalese": "SN",
    "zimbabwe": "ZW", "zimbabwean": "ZW",
    "guinea": "GN", "guinean": "GN",
    "rwanda": "RW", "rwandan": "RW",
    "benin": "BJ", "beninese": "BJ",
    "burundi": "BI", "burundian": "BI",
    "tunisia": "TN", "tunisian": "TN",
    "somalia": "SO", "somali": "SO",
    "chad": "TD", "chadian": "TD",
    "sierra leone": "SL",
    "togo": "TG", "togolese": "TG",
    "libya": "LY", "libyan": "LY",
    "congo": "CG",
    "democratic republic of congo": "CD",
    "dr congo": "CD", "drc": "CD",
    "central african republic": "CF",
    "liberia": "LR", "liberian": "LR",
    "mauritania": "MR",
    "eritrea": "ER", "eritrean": "ER",
    "namibia": "NA", "namibian": "NA",
    "gambia": "GM", "gambian": "GM",
    "botswana": "BW",
    "gabon": "GA", "gabonese": "GA",
    "lesotho": "LS",
    "algeria": "DZ", "algerian": "DZ",
    "morocco": "MA", "moroccan": "MA",
    "egypt": "EG", "egyptian": "EG",
    "sudan": "SD", "sudanese": "SD",
    "south sudan": "SS",
    "ivory coast": "CI", "côte d'ivoire": "CI", "cote d'ivoire": "CI",
    "burkina faso": "BF",
    "madagascar": "MG", "malagasy": "MG",
    "mauritius": "MU",
    "seychelles": "SC",
    "comoros": "KM",
    "djibouti": "DJ",
    "eswatini": "SZ", "swaziland": "SZ",

    "united states": "US", "usa": "US", "america": "US", "american": "US",
    "united kingdom": "GB", "uk": "GB", "britain": "GB", "british": "GB",
    "france": "FR", "french": "FR",
    "germany": "DE", "german": "DE",
    "italy": "IT", "italian": "IT",
    "spain": "ES", "spanish": "ES",
    "portugal": "PT", "portuguese": "PT",
    "brazil": "BR", "brazilian": "BR",
    "india": "IN", "indian": "IN",
    "china": "CN", "chinese": "CN",
    "japan": "JP", "japanese": "JP",
    "russia": "RU", "russian": "RU",
    "canada": "CA", "canadian": "CA",
    "australia": "AU", "australian": "AU",
    "mexico": "MX", "mexican": "MX",
}

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
