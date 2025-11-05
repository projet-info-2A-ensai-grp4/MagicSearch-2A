import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import time


def get_card_image_url(scryfall_oracle_id: str) -> str:
	"""
	Fetch the image URL of a Magic: The Gathering card from the Scryfall API using its
    scryfall_oracle_id.

	Parameters
	----------
	scryfall_oracle_id : str
		The oracle ID (UUID) of the card.

	Returns
	-------
	str
		The URL of the card's normal-sized image, or None if not found.
	"""

	api_url = f"https://api.scryfall.com/cards/search?q=oracleid:{scryfall_oracle_id}"
	response = requests.get(api_url)

	if response.status_code != 200:
		print(f" API error for oracle ID {scryfall_oracle_id}: {response.status_code}")
		return None

	data = response.json()
	if not data.get("data"):
		print(f"No card found for oracle ID {scryfall_oracle_id}")
		return None
	return data["data"][0]["image_uris"].get("normal")


def fetch_and_update_images():
	"""
	Fetch scryfall_oracle_id from PostgreSQL, query the Scryfall API, and update the database with the
    image URL.
	"""

	conn_params = {
		"host": "postgresql-885217.user-victorjean",
		"port": 5432,
		"database": "defaultdb",
		"user": "user-victorjean",
		"password": "pr9yh1516s57jjnmw7ll",
	}

	with psycopg2.connect(**conn_params) as conn:
		with conn.cursor(cursor_factory=RealDictCursor) as cursor:
			cursor.execute("""
				SELECT id, scryfall_oracle_id
				FROM cards
				WHERE scryfall_oracle_id IS NOT NULL
				AND image_url IS NULL
			""")
			cards = cursor.fetchall()

			print(f"Found {len(cards)} cards without image URL.")
			for card in cards:
				time.sleep(0.2)
				oracle_id = card["scryfall_oracle_id"]
				card_id = card["id"]
				image_url = get_card_image_url(oracle_id)
				print(image_url)
				if image_url:
					cursor.execute("""
						UPDATE cards
						SET image_url = %s
						WHERE id = %s;
					""", (image_url, card_id))
					conn.commit()
					print(f"Card {card_id} updated with image URL.")
				else:
					print(f"No image found for card {card_id}")


if __name__ == "__main__":
	fetch_and_update_images()