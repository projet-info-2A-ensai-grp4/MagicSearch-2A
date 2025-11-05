from dao.cardDao import CardDao
from business_object.cardBusiness import CardBusiness
from dotenv import load_dotenv
import os
import time
from typing import Optional


def process_single_card(
    dao: CardDao,
    card_id: int,
    max_retries: int = 3
) -> bool:
    """
    Process a single card with retry logic.
     
    Parameters
    ----------
    dao : CardDao
        Database access object
    card_id : int
        ID of the card to process
    max_retries : int
        Maximum number of retry attempts
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    for attempt in range(1, max_retries + 1):
        try:
            business = CardBusiness(dao, card_id)
            business.generate_text_to_embed2()
            business.vectorize()  # Fixed: no arguments needed
            print(f"✓ Card {card_id} processed successfully.")
            return True
            
        except ValueError as e:
            print(f"✗ Card {card_id} - ValueError (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                
        except Exception as e:
            print(f"✗ Card {card_id} - Unexpected error (attempt {attempt}/{max_retries}): {type(e).__name__}: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                
    print(f"✗ Card {card_id} failed after {max_retries} attempts. Skipping.")
    return False


def process_all_cards(
    start_id: int = 1,
    max_card_id: int = 32548,
    max_retries: int = 3,
    delay_between_cards: float = 1.0
):
    """
    Process all cards with robust error handling and progress tracking.
    
    Parameters
    ----------
    start_id : int
        Starting card ID (useful for resuming)
    max_card_id : int
        Maximum card ID to process
    max_retries : int
        Maximum retry attempts per card
    delay_between_cards : float
        Delay in seconds between processing cards
    """
    load_dotenv()
    
    # Verify environment is set up
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        print("Error: LLM_API_KEY not found in environment variables.")
        return
    
    stats = {
        "success": 0,
        "failed": 0,
        "total": max_card_id - start_id + 1
    }
    
    failed_cards = []
    
    print(f"Starting processing from card {start_id} to {max_card_id}")
    print(f"Total cards to process: {stats['total']}")
    print("-" * 60)
    
    start_time = time.time()
    
    with CardDao() as dao:
        for card_id in range(start_id, max_card_id + 1):
            success = process_single_card(dao, card_id, max_retries)
            
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
                failed_cards.append(card_id)
            
            # Progress update every 100 cards
            if card_id % 100 == 0:
                elapsed = time.time() - start_time
                progress = ((card_id - start_id + 1) / stats["total"]) * 100
                avg_time = elapsed / (card_id - start_id + 1)
                remaining = (max_card_id - card_id) * avg_time
                
                print(f"\n--- Progress: {progress:.1f}% ({card_id}/{max_card_id}) ---")
                print(f"Elapsed: {elapsed/60:.1f}m | Remaining: ~{remaining/60:.1f}m")
                print(f"Success: {stats['success']} | Failed: {stats['failed']}")
                print("-" * 60)
            
            time.sleep(delay_between_cards)
    
    # Final summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total cards processed: {stats['total']}")
    print(f"Successful: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    print(f"Success rate: {(stats['success']/stats['total']*100):.1f}%")
    print(f"Total time: {elapsed/60:.1f} minutes")
    
    if failed_cards:
        print(f"\nFailed card IDs ({len(failed_cards)}):")
        # Print in groups of 10 for readability
        for i in range(0, len(failed_cards), 10):
            print(failed_cards[i:i+10])


if __name__ == "__main__":
    # You can easily resume from a specific card ID if needed
    process_all_cards(start_id=118, max_card_id=32548, delay_between_cards=0.2)