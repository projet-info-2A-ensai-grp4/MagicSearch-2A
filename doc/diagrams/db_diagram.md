```mermaid
classDiagram
    class User {
        <<PK>> int user_id
        string username
        string email
        string password
        <<FK>> int role_id
    }

    class Role {
        <<PK>> int role_id
        string role_name
    }

    class Card {
        <<PK>> int card_id
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

    class History {
        <<PK>> int history_id
        <<FK>> int user_id
        string details
    }

    class Deck {
        <<PK>> int deck_id
        <<FK>> int user_id
        string type
        string name
    }

    class DeckCard {
        <<FK>> int deck_id
        <<FK>> int card_id
        int quantity
    }

    class Favorite {
        <<FK>> int user_id
        <<FK>> int card_id
    }

    class UserDeckLink {
        <<FK>> int user_id
        <<FK>> int deck_id
    }

    %% UML-style associations
    Role "1" --> "0..*" User : has
    User "1" --> "0..*" Deck : owns
    Deck "1" --> "0..*" DeckCard : contains
    Card "1" --> "0..*" DeckCard : in
    User "1" --> "0..*" UserDeckLink : collaborates
    Deck "1" --> "0..*" UserDeckLink : shared_with
    User "1" --> "0..*" Favorite : has_favorite
    Card "1" --> "0..*" Favorite : is_favorited_in
    User "1" --> "0..*" History : has
