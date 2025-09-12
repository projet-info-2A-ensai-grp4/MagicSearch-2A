import json
import psycopg2
from psycopg2.extras import execute_values

# --- Connect to PostgreSQL ---
conn = psycopg2.connect(
    host="postgresql-885217.user-victorjean",
    port=5432,
    database="defaultdb",
    user="user-victorjean",
    password="pr9yh1516s57jjnmw7ll"
)
cur = conn.cursor()

# --- Create normalized table ---
cur.execute("""
CREATE TABLE IF NOT EXISTS cards (
    id SERIAL PRIMARY KEY,
    card_key TEXT UNIQUE,
    name TEXT,
    text TEXT,
    type TEXT,
    layout TEXT,
    mana_cost TEXT,
    mana_value NUMERIC,
    converted_mana_cost NUMERIC,
    colors TEXT[],
    color_identity TEXT[],
    types TEXT[],
    is_funny BOOLEAN,
    scryfall_oracle_id UUID,
    text_to_embed TEXT,
    
    raw JSONB
)
""")

# --- Load JSON file ---
with open("MagicSearch-2A/data/AtomicCards.json", "r") as file:
    data = json.load(file)

cards = data["data"]

rows = []
for card_key, card_list in cards.items():
    if not card_list:  # skip empty
        continue
    card = card_list[0]  # each entry is a list with one dict
    
    rows.append((
        card_key,
        card.get("name"),
        card.get("text"),
        card.get("type"),
        card.get("layout"),
        card.get("manaCost"),
        card.get("manaValue"),
        card.get("convertedManaCost"),  # new field
        card.get("colors"),
        card.get("colorIdentity"),      # new field
        card.get("types"),
        card.get("isFunny"),
        card.get("identifiers", {}).get("scryfallOracleId"),  # new field
        json.dumps(card)
    ))

# --- Bulk insert/update ---
execute_values(
    cur,
    """
    INSERT INTO cards (
        card_key, name, text, type, layout, mana_cost,
        mana_value, converted_mana_cost, colors, color_identity,
        types, is_funny, scryfall_oracle_id, raw
    )
    VALUES %s
    ON CONFLICT (card_key) DO UPDATE SET
        name = EXCLUDED.name,
        text = EXCLUDED.text,
        type = EXCLUDED.type,
        layout = EXCLUDED.layout,
        mana_cost = EXCLUDED.mana_cost,
        mana_value = EXCLUDED.mana_value,
        converted_mana_cost = EXCLUDED.converted_mana_cost,
        colors = EXCLUDED.colors,
        color_identity = EXCLUDED.color_identity,
        types = EXCLUDED.types,
        is_funny = EXCLUDED.is_funny,
        scryfall_oracle_id = EXCLUDED.scryfall_oracle_id,
        raw = EXCLUDED.raw
    """,
    rows
)

conn.commit()
cur.close()
conn.close()
