```mermaid
erDiagram
    users {
        int user_id
        string username
        string email
        string password
        int role_id
    }
    roles {
        int role_id
        string role_name
    }
    cards {
        int id
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
        set colors
        set color_identity
        set color_indicator
        set types
        set subtypes
        set supertypes
        set keywords
        set subsets
        set printings
        uuid scryfall_oracle_id
        string text_to_embed
        vector embedding
        json raw
    }
    histories {
        int user_id
        list history
    }
    user_deck_link {
        id
        user_id
        deck_id
        bool active
    }
    decks {
        int deck_id
        int user_id
        list cards
        string type
        string name
    }
    favorites {
        int user_id
        list cards
    }

    classDef default fill:#f9f,stroke-width:4px
    classDef foo stroke:#f00
    classDef bar stroke:#0f0
    classDef foobar stroke:#00f
