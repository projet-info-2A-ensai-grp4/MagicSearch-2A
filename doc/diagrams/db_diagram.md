```mermaid
erDiagram
    users {
        int user_id PK
        string username
        string email
        string password
        int role_id FK
    }

    roles {
        int role_id PK
        string role_name
    }

    cards {
        int card_id PK
        string card_key
        string name
        string ascii_name
        string text
        string type
        string layout
        string mana_cost
        numeric mana_value
        numeric converted_mana_cost
        numeric face_converted_mana_cost
        numeric face_mana_value
        string face_name
        string first_printing
        string hand
        string life
        string loyalty
        string power
        string toughness
        string side
        string defense
        numeric edhrec_rank
        numeric edhrec_saltiness
        boolean is_funny
        boolean is_game_changer
        boolean is_reserved
        boolean has_alternative_deck_limit
        uuid scryfall_oracle_id
        string text_to_embed
        vector embedding
        json raw
    }

    histories {
        int history_id PK
        int user_id FK
        string details
    }

    decks {
        int deck_id PK
        int user_id FK
        string type
        string name
    }

    deck_cards {
        int deck_id FK
        int card_id FK
        int quantity
    }

    favorites {
        int user_id FK
        int card_id FK
    }

    user_deck_link {
        int user_id FK
        int deck_id FK
    }

    %% Relations
    roles ||--o{ users : "has"
    users ||--o{ decks : "owns"
    decks ||--o{ deck_cards : "contains"
    cards ||--o{ deck_cards : "in"
    users ||--o{ user_deck_link : "links"
    decks ||--o{ user_deck_link : "linked to"
    users ||--o{ favorites : "favorites"
    cards ||--o{ favorites : "favored in"
    users ||--o{ histories : "performs"
