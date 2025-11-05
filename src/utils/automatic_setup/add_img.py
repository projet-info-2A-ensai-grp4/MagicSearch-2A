import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import time
import os
from dotenv import load_dotenv

PROGRESS_FILE = ".img_progress"


def get_last_processed_id():
    """Get the last successfully processed card ID."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return int(f.read().strip())
    return 0


def save_progress(card_id):
    """Save the last successfully processed card ID."""
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(card_id))


def get_card_image_url(scryfall_oracle_id: str) -> str:
    """Fetch the image URL of a Magic card from Scryfall API."""
    api_url = f"https://api.scryfall.com/cards/search?q=oracleid:{scryfall_oracle_id}"

    try:
        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            print(
                f"⚠️  API error for oracle ID {scryfall_oracle_id}: {response.status_code}"
            )
            return None

        data = response.json()
        if not data.get("data"):
            print(f"⚠️  No card found for oracle ID {scryfall_oracle_id}")
            return None

        card = data["data"][0]

        # Single-faced cards
        if "image_uris" in card:
            return card["image_uris"].get("normal")

        # Multi-faced cards
        elif "card_faces" in card:
            if card["card_faces"] and "image_uris" in card["card_faces"][0]:
                return card["card_faces"][0]["image_uris"].get("normal")

        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return None


def fetch_and_update_images():
    """Fetch and update card images with resume capability."""
    load_dotenv()

    conn_params = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    last_processed = get_last_processed_id()
    print(f"🔄 Resuming from card ID: {last_processed + 1}")

    try:
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Fetch cards that need images, starting from last processed
                cursor.execute(
                    """
                    SELECT id, scryfall_oracle_id, name
                    FROM cards
                    WHERE scryfall_oracle_id IS NOT NULL
                    AND image_url IS NULL
                    AND id > %s
                    ORDER BY id
                """,
                    (last_processed,),
                )

                cards = cursor.fetchall()
                total = len(cards)

                print(f"📊 Found {total} cards without image URL")

                for idx, card in enumerate(cards, 1):
                    oracle_id = card["scryfall_oracle_id"]
                    card_id = card["id"]
                    card_name = card["name"]

                    print(f"[{idx}/{total}] Processing: {card_name} (ID: {card_id})")

                    # Rate limiting: Scryfall allows ~10 requests per second
                    time.sleep(0.1)

                    image_url = get_card_image_url(oracle_id)

                    if image_url:
                        cursor.execute(
                            """
                            UPDATE cards
                            SET image_url = %s
                            WHERE id = %s;
                        """,
                            (image_url, card_id),
                        )
                        conn.commit()
                        save_progress(card_id)
                        print(f"✅ Updated card {card_id}")
                    else:
                        print(f"⚠️  No image found for card {card_id}")
                        # Still save progress even if image not found
                        save_progress(card_id)

                print("✨ All images processed successfully!")
                # Clean up progress file
                if os.path.exists(PROGRESS_FILE):
                    os.remove(PROGRESS_FILE)

    except KeyboardInterrupt:
        print("\n⏸️  Process interrupted. Progress saved.")
        print(f"   Last processed card ID: {get_last_processed_id()}")
        print("   Run the script again to resume.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Last processed card ID: {get_last_processed_id()}")
        raise


if __name__ == "__main__":
    fetch_and_update_images()
