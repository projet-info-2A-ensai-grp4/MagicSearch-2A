import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.dao.cardDao import CardDao
from src.business_object.cardBusiness import CardBusiness
from dotenv import load_dotenv
import time

PROGRESS_FILE = ".embed_progress"


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


def process_all_cards(max_card_id=32548):
    """Process all cards with resume capability."""
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY")

    if not api_key:
        print("❌ LLM_API_KEY not found in .env file!")
        return

    start_id = get_last_processed_id() + 1
    print(f"🔄 Resuming from card ID: {start_id}")
    print(f"📊 Total cards to process: {max_card_id - start_id + 1}")

    try:
        with CardDao() as dao:
            for card_id in range(start_id, max_card_id + 1):
                try:
                    # Progress indicator
                    if card_id % 100 == 0:
                        progress = (
                            (card_id - start_id + 1) / (max_card_id - start_id + 1)
                        ) * 100
                        print(
                            f"📈 Progress: {progress:.1f}% (Card {card_id}/{max_card_id})"
                        )

                    # Create business object and generate text to embed
                    business = CardBusiness(dao, card_id)

                    # Generate the text_to_embed first
                    business.generate_text_to_embed2()

                    # Then vectorize it (no need to pass text since it uses self.text_to_embed)
                    business.vectorize()

                    save_progress(card_id)

                    # Rate limiting to avoid API throttling
                    time.sleep(0.1)

                except ValueError as e:
                    print(f"⚠️  Error processing card {card_id}: {e}")
                    save_progress(card_id)  # Save progress even on error
                    continue
                except Exception as e:
                    print(f"❌ Unexpected error on card {card_id}: {e}")
                    raise

        print("✨ All embeddings generated successfully!")
        # Clean up progress file
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)

    except KeyboardInterrupt:
        print("\n⏸️  Process interrupted. Progress saved.")
        print(f"   Last processed card ID: {get_last_processed_id()}")
        print("   Run the script again to resume.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print(f"   Last processed card ID: {get_last_processed_id()}")
        raise


if __name__ == "__main__":
    process_all_cards()
