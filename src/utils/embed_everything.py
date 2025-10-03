from dao.cardDao import CardDao
from business_object.cardBusiness import CardBusiness
from dotenv import load_dotenv
import os

def process_all_cards(max_card_id=4):
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY")
    endpoint_url = "https://llm.lab.sspcloud.fr/ollama/api/embed"

    with CardDao() as dao:
        for card_id in range(1, max_card_id + 1):
            try:
                business = CardBusiness(dao, card_id)
                business.generate_text_to_embed2()
                business.vectorize(business.text_to_embed, endpoint_url, api_key)
                print(f"Processed card {card_id}: embedding generated.")
            except ValueError as e:
                print(f"Error processing card {card_id}: {e}")

if __name__ == "__main__":
    process_all_cards()
