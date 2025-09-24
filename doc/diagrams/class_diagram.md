```mermaid
classDiagram
    class UserDAO {
        -UUID userId
        -String username
        -String email
        -String passwordHash
        +getUsername()
        +getEmail()
        +getId()
        +signUp()
        +signIn()
    }

    class PlayerDAO {
        -Search[] searchHistory
        -Card[] favorites
        -Deck[] decks
        -searchCards(query, filters)
        -addFavorite(card)
        -createDeck(name)
        +viewSuggestions()
    }

    class AdminDAO {
        -addCard(card)
        -editCard(card)
        -deleteCard(card)
        -manageUser(user)
        -editEmbedding(card)
    }

    UserDAO <|-- PlayerDAO
    UserDAO <|-- AdminDAO


    class CardBusiness {
        -UUID cardId
        -UUID scryfallOracleId
        -String name
        -String manaCost
        -Numeric convertedManaCost
        -String[] colors
        -String typeLine
        -String effectText
        -String cardType
        -String cardSubtype
        -String setCode
        -String firstPrinting
        -String power
        -String toughness
        -String textToEmbed
        -Vector embedding
        -_Text colorIdentity
        +getInfo()
        +detailSpecifity(effectText)
        +generateEmbedText(data)
        +vectorize(textToEmbed)
    }

    class CardDao {
        - UUID cardId
        +get_card_by_id(cardId)
        +edit_text_to_embed(cardId,embed_me)
        +edit_embedding(cardId,text_to_embed)
    }
    class Deck {
        -UUID deckId
        -String name
        -Card[] cards
        +addCard(card, qty)
        +removeCard(card, qty)
        +export(format)
    }

    class Search {
        -UUID id
        -String query
        -appliedFilters
        -Card[] results
        +execute()
        +saveToHistory()
    }

    class Suggestion {
        -UUID id
        -Card[] suggestedCards
        +generateSuggestions(history, currentCard)
    }

    PlayerDAO "1" o-- "*" Search : history
    PlayerDAO "1" o-- "*" Deck : owns
    PlayerDAO "*" -- "*" CardBusiness : favorites
    Deck "*" -- "*" CardBusiness : cards
    Search "*" --> "*" CardBusiness : results
    PlayerDAO "1" o-- "*" Suggestion
    Suggestion "*" --> "*" CardBusiness : suggested
    CardBusiness "1" <--> "1" CardDao: card information
```