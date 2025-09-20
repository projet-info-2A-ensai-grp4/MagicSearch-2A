import json
import psycopg2
from psycopg2.extras import execute_values

# --- Connect to PostgreSQL ---
conn = psycopg2.connect(
    host="postgresql-885217.user-victorjean",
    port=5432,
    database="defaultdb",
    user="user-victorjean",
    password="pr9yh1516s57jjnmw7ll",
)
cur = conn.cursor()

# --- Create normalized table ---
cur.execute("""
CREATE TABLE IF NOT EXISTS cards (
    id SERIAL PRIMARY KEY,
    card_key TEXT UNIQUE,
    name TEXT,
    ascii_name TEXT,
    text TEXT,
    type TEXT,
    layout TEXT,
    mana_cost TEXT,
    mana_value NUMERIC,
    converted_mana_cost NUMERIC,
    face_converted_mana_cost NUMERIC,
    face_mana_value NUMERIC,
    face_name TEXT,
    first_printing TEXT,
    hand TEXT,
    life TEXT,
    loyalty TEXT,
    power TEXT,
    toughness TEXT,
    side TEXT,
    defense TEXT,
    edhrec_rank NUMERIC,
    edhrec_saltiness NUMERIC,
    is_funny BOOLEAN,
    is_game_changer BOOLEAN,
    is_reserved BOOLEAN,
    has_alternative_deck_limit BOOLEAN,
    colors TEXT[],
    color_identity TEXT[],
    color_indicator TEXT[],
    types TEXT[],
    subtypes TEXT[],
    supertypes TEXT[],
    keywords TEXT[],
    subsets TEXT[],
    printings TEXT[],
    scryfall_oracle_id UUID,
    text_to_embed TEXT,
    embedding VECTOR,
    raw JSONB
)
""")

# --- Load JSON file ---
with open("MagicSearch-2A/data/AtomicCards.json", "r") as file:
    data = json.load(file)

cards = data["data"]

rows = []
for card_key, card_list in cards.items():
    if not card_list:
        continue
    card = card_list[0]

    rows.append(
        (
            card_key,
            card.get("name"),
            card.get("asciiName"),
            card.get("text"),
            card.get("type"),
            card.get("layout"),
            card.get("manaCost"),
            card.get("manaValue"),
            card.get("convertedManaCost"),
            card.get("faceConvertedManaCost"),
            card.get("faceManaValue"),
            card.get("faceName"),
            card.get("firstPrinting"),
            card.get("hand"),
            card.get("life"),
            card.get("loyalty"),
            card.get("power"),
            card.get("toughness"),
            card.get("side"),
            card.get("defense"),
            card.get("edhrecRank"),
            card.get("edhrecSaltiness"),
            card.get("isFunny"),
            card.get("isGameChanger"),
            card.get("isReserved"),
            card.get("hasAlternativeDeckLimit"),
            card.get("colors"),
            card.get("colorIdentity"),
            card.get("colorIndicator"),
            card.get("types"),
            card.get("subtypes"),
            card.get("supertypes"),
            card.get("keywords"),
            card.get("subsets"),
            card.get("printings"),
            card.get("identifiers", {}).get("scryfallOracleId"),
            json.dumps(card),
        )
    )

# --- Bulk insert/update ---
execute_values(
    cur,
    """
    INSERT INTO cards (
        card_key, name, ascii_name, text, type, layout, mana_cost,
        mana_value, converted_mana_cost, face_converted_mana_cost, face_mana_value,
        face_name, first_printing, hand, life, loyalty, power, toughness, side,
        defense, edhrec_rank, edhrec_saltiness, is_funny, is_game_changer,
        is_reserved, has_alternative_deck_limit, colors, color_identity, color_indicator,
        types, subtypes, supertypes, keywords, subsets, printings,
        scryfall_oracle_id, raw
    )
    VALUES %s
    ON CONFLICT (card_key) DO UPDATE SET
        name = EXCLUDED.name,
        ascii_name = EXCLUDED.ascii_name,
        text = EXCLUDED.text,
        type = EXCLUDED.type,
        layout = EXCLUDED.layout,
        mana_cost = EXCLUDED.mana_cost,
        mana_value = EXCLUDED.mana_value,
        converted_mana_cost = EXCLUDED.converted_mana_cost,
        face_converted_mana_cost = EXCLUDED.face_converted_mana_cost,
        face_mana_value = EXCLUDED.face_mana_value,
        face_name = EXCLUDED.face_name,
        first_printing = EXCLUDED.first_printing,
        hand = EXCLUDED.hand,
        life = EXCLUDED.life,
        loyalty = EXCLUDED.loyalty,
        power = EXCLUDED.power,
        toughness = EXCLUDED.toughness,
        side = EXCLUDED.side,
        defense = EXCLUDED.defense,
        edhrec_rank = EXCLUDED.edhrec_rank,
        edhrec_saltiness = EXCLUDED.edhrec_saltiness,
        is_funny = EXCLUDED.is_funny,
        is_game_changer = EXCLUDED.is_game_changer,
        is_reserved = EXCLUDED.is_reserved,
        has_alternative_deck_limit = EXCLUDED.has_alternative_deck_limit,
        colors = EXCLUDED.colors,
        color_identity = EXCLUDED.color_identity,
        color_indicator = EXCLUDED.color_indicator,
        types = EXCLUDED.types,
        subtypes = EXCLUDED.subtypes,
        supertypes = EXCLUDED.supertypes,
        keywords = EXCLUDED.keywords,
        subsets = EXCLUDED.subsets,
        printings = EXCLUDED.printings,
        scryfall_oracle_id = EXCLUDED.scryfall_oracle_id,
        raw = EXCLUDED.raw
    """,
    rows,
)

conn.commit()
cur.close()
conn.close()
