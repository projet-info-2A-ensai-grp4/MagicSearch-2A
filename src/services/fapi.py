from fastapi import FastAPI, Query, HTTPException, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from dao.playerDao import PlayerDao
from dao.cardDao import CardDao
from dao.userDao import UserDao
import hashlib
from services.userService import UserService
from dao.deckDao import DeckDao
from utils.auth import create_access_token
from utils.auth import get_current_user
from dao.favoriteDao import FavoriteDao
from business_object.favoriteBusiness import FavoriteBusiness
from dao.historyDao import HistoryDao
from business_object.historyBusiness import HistoryBusiness


app = FastAPI(
    title="Magic: The Gathering Card Search API",
    description="""
    A comprehensive API for searching, filtering, and managing Magic: The Gathering cards.

    ## Features

    * **Semantic Search**: Natural language search using vector embeddings
    * **Advanced Filtering**: Filter cards by colors, mana value, type, etc.
    * **Card Browsing**: Get random cards or search by name
    * **User Management**: Registration, login, and authentication
    * **Deck Management**: Create, update, and manage card decks

    ## Authentication

    Protected endpoints require authentication using JWT tokens obtained from the `/login` endpoint.
    """,
    version="1.0.0",
    contact={
        "name": "Groupe 4 à l'ensai",
        "email": "victor.jean@eleve.ensai.fr",
    },
    license_info={
        "name": "MIT",
    },
)

player_dao = PlayerDao()
card_dao = CardDao()
deck_dao = DeckDao()
favorite_dao = FavoriteDao()
user_dao = UserDao()
favorite_business = FavoriteBusiness(favorite_dao, user_dao, card_dao)
history_dao = HistoryDao()
history_business = HistoryBusiness(history_dao, user_dao)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchQuery(BaseModel):
    text: str = Field(
        ...,
        description="Natural language search query",
        example="blue control cards with flying",
    )
    limit: Optional[int] = Field(
        10, ge=1, le=150, description="Maximum number of results"
    )
    filters: Optional[Dict] = Field(
        None,
        description="Additional filters (colors, mana_value, etc.)",
        example={"colors": ["U"], "mana_value__lte": 3},
    )


class CardFilterQuery(BaseModel):
    colors: Optional[List[str]] = Field(
        None, description="Color filter (W, U, B, R, G)", example=["U", "B"]
    )
    mana_value: Optional[int] = Field(None, ge=0, description="Exact mana value")
    mana_value__lte: Optional[int] = Field(None, ge=0, description="Maximum mana value")
    mana_value__gte: Optional[int] = Field(None, ge=0, description="Minimum mana value")
    order_by: Optional[str] = Field("id", description="Column to sort by")
    asc: Optional[bool] = Field(
        True, description="Sort ascending (True) or descending (False)"
    )
    limit: Optional[int] = Field(
        10, ge=1, le=100, description="Maximum number of results"
    )
    offset: Optional[int] = Field(0, ge=0, description="Pagination offset")


class UserRegistration(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username",
        example="magic_player_123",
    )
    email: str = Field(
        ..., description="Valid email address", example="player@example.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (min 8 characters)",
        example="SecurePass123!",
    )


class UserLogin(BaseModel):
    username: str = Field(..., description="Username", example="magic_player_123")
    password_hash: str = Field(..., description="SHA-256 hashed password")


class DeckcreateQuery(BaseModel):
    deck_name: str = Field(
        ..., description="Name of the deck", example="My Control Deck"
    )
    deck_type: Optional[str] = Field(
        None,
        alias="type",
        description="Deck format (Standard, Modern, Commander, etc.)",
        example="Commander",
    )


class DeckupdateQuery(BaseModel):
    deck_id: int = Field(..., gt=0, description="ID of the deck to update")
    deck_name: str = Field(..., description="New deck name")
    deck_type: Optional[str] = Field(None, description="New deck type")


class DeckdeleteQuery(BaseModel):
    deck_id: int = Field(..., gt=0, description="ID of the deck to delete")


class DeckreadingQuery(BaseModel):
    deck_id: int = Field(..., gt=0, description="ID of the deck to retrieve")


class DeckaddCardQuery(BaseModel):
    deck_id: int = Field(..., gt=0, description="Deck ID")
    card_id: int = Field(..., gt=0, description="Card ID to add")


class FavoriteAction(BaseModel):
    card_id: int


class HistoryAction(BaseModel):
    prompt: str = Field(..., description="Search text to store in history")


@app.post(
    "/search",
    tags=["Search"],
    summary="Semantic card search",
    description="""
    Perform a natural language search on Magic cards using vector embeddings.

    This endpoint converts your text query into a vector and finds the most similar cards
    based on their semantic meaning, not just keyword matching.

    **Examples:**
    - "powerful creatures with trample"
    - "blue control spells that counter"
    - "cheap removal for artifacts"
    """,
    response_description="List of cards matching the semantic search",
)
async def search(query: SearchQuery):
    text = query.text
    limit = min(query.limit, 300)
    filters = query.filters or {}

    print(f"Requête reçue : {text}, limit: {limit}, filters: {filters}")

    try:
        results = player_dao.natural_language_search(text, filters=filters, limit=limit)

        if not results:
            return {"results": [], "message": "Aucune carte trouvée."}

        return {"results": results}

    except Exception as e:
        print(f"Erreur dans /search : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/filter",
    tags=["Search"],
    summary="Filter cards by attributes",
    description="""
    Filter cards using structured attributes like colors, mana value, type, etc.

    **Supported Operators:**
    - `mana_value`: Exact match
    - `mana_value__lte`: Less than or equal
    - `mana_value__gte`: Greater than or equal
    - `colors`: Array overlap (card must have at least one matching color)

    **Example:** Get all blue cards with CMC ≤ 3, sorted by name
    """,
    response_description="Filtered list of cards",
)
async def filter(query: CardFilterQuery):
    try:
        filter_kwargs = {}
        if query.colors:
            filter_kwargs["colors"] = query.colors
        if query.mana_value:
            filter_kwargs["mana_value"] = query.mana_value
        if query.mana_value__gte:
            filter_kwargs["mana_value__gte"] = query.mana_value__gte
        if query.mana_value__lte:
            filter_kwargs["mana_value__lte"] = query.mana_value__lte
        results = card_dao.filter(
            query.order_by, query.asc, query.limit, query.offset, **filter_kwargs
        )
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /filter : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/cards/random",
    tags=["Browse"],
    summary="Get a random card",
    description="""Retrieve a randomly selected card from the database.
                Perfect for discovery and inspiration!""",
    response_description="A randomly selected Magic card",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "card": {
                            "id": 12345,
                            "name": "Lightning Bolt",
                            "mana_cost": "{R}",
                            "type": "Instant",
                            "text": "Lightning Bolt deals 3 damage to any target.",
                        }
                    }
                }
            },
        },
        404: {"description": "No cards found in database"},
    },
)
async def get_random_card():
    try:
        card = card_dao.get_random_card()

        if not card:
            raise HTTPException(status_code=404, detail="No cards found in database")

        return {"card": card}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /cards/random: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get(
    "/cards/{card_id}",
    tags=["Browse"],
    summary="Get card by ID",
    description="Retrieve detailed information about a specific card using its unique ID.",
    response_description="Card details",
    responses={
        200: {"description": "Card found"},
        400: {"description": "Invalid card ID"},
        404: {"description": "Card not found"},
    },
)
async def get_card_by_id(
    card_id: int = Path(..., gt=0, description="Unique card identifier"),
):
    if card_id <= 0:
        raise HTTPException(
            status_code=400, detail="Card ID must be a positive integer"
        )

    try:
        card = card_dao.get_by_id(card_id)

        if not card:
            raise HTTPException(
                status_code=404, detail=f"Card with ID {card_id} not found"
            )

        return {"card": card}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /cards/{card_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get(
    "/cards",
    tags=["Browse"],
    summary="Search cards by name",
    description="""
    Search for cards using partial or exact name matching (case-insensitive).

    **Examples:**
    - `name=bolt` → finds "Lightning Bolt", "Bolt Bend", etc.
    - `name=Jace` → finds all cards with "Jace" in the name
    """,
    response_description="List of matching cards with pagination info",
)
async def search_cards_by_name(
    name: Optional[str] = Query(
        None, min_length=1, description="Full or partial card name"
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    if not name:
        raise HTTPException(
            status_code=400, detail="Query parameter 'name' is required"
        )

    limit = min(limit, 100)

    try:
        cards = card_dao.search_by_name(name, limit=limit, offset=offset)

        return {"results": cards, "count": len(cards), "limit": limit, "offset": offset}

    except Exception as e:
        print(f"Error in /cards?name={name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post(
    "/register",
    tags=["Authentication"],
    summary="Register new user",
    description="Create a new user account with username, email, and password.",
    response_description="Registration confirmation with user details",
    responses={
        200: {"description": "User registered successfully"},
        400: {"description": "Invalid input or user already exists"},
    },
)
async def register(user_data: UserRegistration):
    try:
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

        user_service = UserService(
            user_data.username, user_data.email, password_hash, UserDao()
        )

        new_user = user_service.signUp()

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user["user_id"],
                "username": new_user["username"],
                "email": new_user["email"],
            },
        }
    except ValueError as e:
        error_message = str(e)
        if "username" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail={"error": "USERNAME_ISSUE", "message": error_message},
            )
        elif "email" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail={"error": "EMAIL_ISSUE", "message": error_message},
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_INPUT", "message": error_message},
            )

    except Exception as e:
        print(f"Erreur dans /register : {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post(
    "/login",
    tags=["Authentication"],
    summary="User login",
    description="Authenticate a user and receive a JWT access token for protected endpoints.",
    response_description="Login confirmation with JWT token",
)
async def login(user_data: UserLogin):
    try:
        user_service = UserService(
            username=user_data.username,
            email=None,
            password_hash=user_data.password_hash,
            user_dao=UserDao(),
        )

        user = user_service.signIn()

        token_data = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
        }

        access_token = create_access_token(token_data)

        return {
            "message": "Login successful",
            "user": {
                "id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
            },
            "access_token": access_token,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=401, detail={"error": "INVALID_CREDENTIALS", "message": str(e)}
        )

    except Exception as e:
        print(f"Erreur dans /login : {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post(
    "/deck/read",
    tags=["Deck Management"],
    summary="Get deck by ID",
    description="Retrieve all cards in a specific deck.",
)
async def reading_deck(query: DeckreadingQuery):
    try:
        results = deck_dao.get_by_id(query.deck_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/read : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/deck/create",
    tags=["Deck Management"],
    summary="Create new deck",
    description="Create a new empty deck with a name and optional format type.",
)
async def create_deck(query: DeckcreateQuery):
    try:
        results = deck_dao.create(name=query.deck_name, type=query.deck_type)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/create : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put(
    "/deck/update",
    tags=["Deck Management"],
    summary="Update deck",
    description="Update deck name and/or type.",
)
async def update_deck(query: DeckupdateQuery):
    try:
        results = deck_dao.update(
            query.deck_id, name=query.deck_name, type=query.deck_type
        )
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/update : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/deck/delete",
    tags=["Deck Management"],
    summary="Delete deck",
    description="Permanently delete a deck and all its card associations.",
)
async def delete_deck(query: DeckdeleteQuery):
    try:
        results = deck_dao.delete(query.deck_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/delete : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/deck/user/read",
    tags=["Deck Management"],
    summary="Get user's decks",
    description="Retrieve all decks belonging to a user, or a specific deck if deck_id is provided.",
)
async def read_user_deck(
    user_id: int = Query(..., gt=0, description="User ID"),
    deck_id: Optional[int] = Query(
        None, gt=0, description="Specific deck ID (optional)"
    ),
):
    try:
        if deck_id:
            results = deck_dao.get_by_id(deck_id)
        else:
            results = deck_dao.get_all_deck_user_id(user_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/user/read : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/deck/card/add",
    tags=["Deck Management"],
    summary="Add card to deck",
    description="Add a card to a deck. If the card already exists, increments quantity.",
)
async def add_card_deck(query: DeckaddCardQuery):
    try:
        results = deck_dao.add_card_to_deck(query.deck_id, query.card_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/card/add : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/deck/card/remove",
    tags=["Deck Management"],
    summary="Remove card from deck",
    description="""Remove one copy of a card from a deck. If quantity reaches 0,
                removes the card entirely.""",
)
async def remove_card_deck(
    deck_id: int = Query(..., gt=0, description="Deck ID"),
    card_id: int = Query(..., gt=0, description="Card ID to remove"),
):
    try:
        results = deck_dao.remove_card_from_deck(deck_id, card_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/card/remove : {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# 🔹 DECK MANAGEMENT – Player-linked Deck Operations
# ==========================================================

class DeckCreateByPlayerQuery(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID who creates the deck")
    name: str = Field(..., description="Deck name", example="Aggro Goblins")
    type: Optional[str] = Field(None, description="Deck format type", example="Modern")


class DeckUpdateByPlayerQuery(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    deck_id: int = Field(..., gt=0, description="Deck ID to update")
    name: Optional[str] = Field(None, description="New deck name")
    type: Optional[str] = Field(None, description="New deck type")


class DeckDeleteByPlayerQuery(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    deck_id: int = Field(..., gt=0, description="Deck ID to delete")


class DeckOwnershipQuery(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    deck_id: int = Field(..., gt=0, description="Deck ID")


@app.post(
    "/deck/player/create",
    tags=["Deck Management"],
    summary="Create a deck linked to a specific user",
    description="""
    Create a new deck **and** link it to a specific player (user).
    Returns both the created deck and the link record.
    """,
)
async def create_deck_by_player(query: DeckCreateByPlayerQuery):
    try:
        result = deck_dao.create_user_deck(query.user_id, name=query.name, type=query.type)
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "message": "Deck successfully created for user",
            "deck": result["deck"],
            "link": result["link"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erreur dans /deck/player/create : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/deck/player/owns",
    tags=["Deck Management"],
    summary="Check if a user owns a given deck",
    description="Returns True if the user owns the deck, False otherwise.",
)
async def check_deck_ownership(
    user_id: int = Query(..., gt=0, description="User ID"),
    deck_id: int = Query(..., gt=0, description="Deck ID"),
):
    try:
        owns = deck_dao.get_by_id_player(deck_id, user_id)
        if owns is None:
            raise HTTPException(status_code=404, detail="User or deck not found")
        return {"user_id": user_id, "deck_id": deck_id, "owns": owns}
    except Exception as e:
        print(f"Erreur dans /deck/player/owns : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/deck/player/create_simple",
    tags=["Deck Management"],
    summary="Create and link a deck to user (simplified version)",
    description="Creates a new deck for a player and returns the tuple (user_id, deck_id).",
)
async def create_deck_player_simple(query: DeckCreateByPlayerQuery):
    try:
        result = deck_dao.create_by_player(query.user_id, name=query.name, type=query.type)
        return {
            "message": "Deck successfully created and linked",
            "user_id": result[0],
            "deck_id": result[1],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erreur dans /deck/player/create_simple : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put(
    "/deck/player/update",
    tags=["Deck Management"],
    summary="Update a deck owned by a player",
    description="Updates the deck’s attributes if both player and deck exist.",
)
async def update_deck_by_player(query: DeckUpdateByPlayerQuery):
    try:
        result = deck_dao.update_by_player(query.user_id,
                                           query.deck_id,
                                           name=query.name,
                                           type=query.type)
        if not result:
            raise HTTPException(status_code=404, detail="User or deck not found")
        return {"message": "Deck successfully updated", "deck": result}
    except Exception as e:
        print(f"Erreur dans /deck/player/update : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/deck/player/delete",
    tags=["Deck Management"],
    summary="Delete a deck owned by a player",
    description="Deletes a deck if it belongs to the specified player.",
)
async def delete_deck_by_player(query: DeckDeleteByPlayerQuery):
    try:
        result = deck_dao.delete_by_player(query.user_id, query.deck_id)
        return {"message": "Deck successfully deleted", "results": result}
    except Exception as e:
        print(f"Erreur dans /deck/player/delete : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/favorite/add", tags=["Favorite"])
async def add_to_favorites(fav: FavoriteAction, current_user: dict = Depends(get_current_user)):
    try:
        result = favorite_business.add_favorite(current_user["user_id"], fav.card_id)
        return {"message": "Added to favorites", "favorite": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/favorite/remove", tags=["Favorite"])
async def remove_from_favorites(fav: FavoriteAction,
                                current_user: dict = Depends(get_current_user)):
    try:
        result = favorite_business.remove_favorite(current_user["user_id"], fav.card_id)
        return {"message": "Removed from favorites", "favorite": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/favorite", tags=["Favorite"])
async def list_favorites(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        favorites = favorite_business.favorite.get_by_id(user_id)
        return {"user_id": user_id, "favorites": favorites}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/history/add", tags=["History"])
async def add_history(entry: HistoryAction, current_user: dict = Depends(get_current_user)):
    try:
        result = history_business.add(current_user["user_id"], entry.prompt)
        return {"message": "Added to history", "history": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history", tags=["History"])
async def list_history(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        hist = history_business.history.get_by_id(user_id)
        return {"user_id": user_id, "history": hist}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
