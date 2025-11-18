```mermaid
erDiagram
    cards {
        int id PK
        varchar card_key
        varchar name
        varchar ascii_name
        text text
        varchar type
        varchar layout
        varchar mana_cost
        int mana_value
        int converted_mana_cost
        int face_converted_mana_cost
        int face_mana_value
        varchar face_name
        date first_printing
        varchar hand
        varchar life
        varchar loyalty
        varchar power
        varchar toughness
        varchar side
        varchar defense
        int edhrec_rank
        float edhrec_saltiness
        boolean is_funny
        boolean is_game_changer
        boolean is_reserved
        boolean has_alternative_deck_limit
        varchar colors
        varchar color_identity
        varchar color_indicator
        varchar types
        varchar subtypes
        varchar supertypes
        varchar keywords
        varchar subsets
        varchar printings
        uuid scryfall_oracle_id
        text text_to_embed
        vector embedding
        json raw
        text image_url
    }

    users {
        int user_id PK
        varchar username
        varchar email
        varchar password_hash
        int role_id FK
    }

    roles {
        int role_id PK
        varchar role_name
    }

    decks {
        int deck_id PK
        varchar type
        varchar name
    }

    deck_cards {
        int deck_id FK
        int card_id FK
        int quantity
    }

    user_deck_link {
        int user_id FK
        int deck_id FK
    }

    histories {
        int history_id PK
        int user_id FK
        text prompt
    }

    favorites {
        int user_id FK
        int card_id FK
    }

    roles ||--o{ users : "has"
    users ||--o{ decks : "owns"
    decks ||--o{ deck_cards : "contains"
    cards ||--o{ deck_cards : "in"
    users ||--o{ user_deck_link : "links"
    decks ||--o{ user_deck_link : "linked to"
    users ||--o{ favorites : "favorites"
    cards ||--o{ favorites : "favored in"
    users ||--o{ histories : "has"