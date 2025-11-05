from dao.cardDao import CardDao
from business_object.cardBusiness import CardBusiness
from dotenv import load_dotenv
import os
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
    endpoint_url = "https://llm.lab.sspcloud.fr/ollama/api/embed"

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

                    business = CardBusiness(dao, card_id)
                    business.generate_text_to_embed2()
                    business.vectorize(business.text_to_embed, endpoint_url, api_key)

                    save_progress(card_id)

                    # Rate limiting
                    time.sleep(0.5)

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
