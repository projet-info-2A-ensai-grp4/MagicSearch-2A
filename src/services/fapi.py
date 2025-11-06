from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from dao.playerDao import PlayerDao
from dao.cardDao import CardDao
import hashlib
from services.userService import UserService
from dao.deckDao import DeckDao

app = FastAPI()
player_dao = PlayerDao()
card_dao = CardDao()
deck_dao = DeckDao()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchQuery(BaseModel):
    text: str
    limit: Optional[int] = 10
    filters: Optional[Dict] = None  # Add filters parameter


class CardFilterQuery(BaseModel):
    colors: Optional[List[str]] = None
    mana_value: Optional[int] = None
    mana_value__lte: Optional[int] = None
    mana_value__gte: Optional[int] = None
    order_by: Optional[str] = "id"
    asc: Optional[bool] = True
    limit: Optional[int] = 10
    offset: Optional[int] = 0


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password_hash: str


class DeckcreateQuery(BaseModel):
    deck_name: str
    deck_type: Optional[str] = Field(None, alias="type")


class DeckupdateQuery(BaseModel):
    deck_id: int
    deck_name: str
    deck_type: Optional[str] = None


class DeckdeleteQuery(BaseModel):
    deck_id: int


class DeckreadingQuery(BaseModel):
    deck_id: int


class DeckaddCardQuery(BaseModel):
    deck_id: int
    card_id: int


@app.post("/search")
async def search(query: SearchQuery):
    """
    Endpoint pour effectuer une recherche sémantique sur les cartes Magic.
    """
    text = query.text
    limit = min(query.limit, 50)  # Maximum 50 cards
    filters = query.filters or {}

    print(f"Requête reçue : {text}, limit: {limit}, filters: {filters}")

    try:
        results = player_dao.natural_language_search(text, filters=filters, limit=limit)

        if not results:
            return {"results": [], "message": "Aucune carte trouvée."}

        return {"results": results}

    except Exception as e:
        print(f"Erreur dans /search : {e}")
        return {"error": str(e)}


@app.post("/filter")
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
        return {"error": str(e)}


@app.post("/register")
async def register(user_data: UserRegistration):
    """
    Endpoint pour l'inscription d'un nouvel utilisateur.
    """
    try:
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

        user_service = UserService(user_data.username, user_data.email, password_hash)

        new_user = user_service.signUp()

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user["id"],
                "username": new_user["username"],
                "email": new_user["email"],
            },
        }
    except ValueError as e:
        error_message = str(e)
        if "username" in error_message.lower():
            return {"error": "USERNAME ISSUE", "message": error_message}
        elif "email" in error_message.lower():
            return {"error": "EMAIL ISSUE", "message": error_message}
        else:
            return {"error": "INVALID_INPUT", "message": error_message}

    except Exception as e:
        print(f"Erreur dans /register : {e}")
        return {"error": "SERVER_ERROR", "message": "Une erreur serveur est survenue"}


@app.post("/login")
async def login(user_data: UserLogin):
    try:
        user_service = UserService(
            username=user_data.username,
            email=None,
            password_hash=user_data.password_hash,
        )

        user = user_service.signIn()

        return {
            "message": "Login successful",
            "user": {
                "id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
            },
        }

    except ValueError as e:
        return {"error": "INVALID_CREDENTIALS", "message": str(e)}

    except Exception as e:
        print(f"Erreur dans /login : {e}")
        return {"error": "SERVER_ERROR", "message": "Une erreur serveur est survenue"}


@app.post("/deck/read")
async def reading_deck(query: DeckreadingQuery):
    try:
        results = deck_dao.get_by_id(query.deck_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/read : {e}")
        return {"error": str(e)}


@app.post("/deck/create")
async def create_deck(query: DeckcreateQuery):
    try:
        results = deck_dao.create(deck_id=query.deck_name, name=query.deck_type)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/create : {e}")
        return {"error": str(e)}


@app.put("/deck/update")
async def update_deck(query: DeckupdateQuery):
    try:
        results = deck_dao.update(query.deck_id, query.deck_name, query.deck_type)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/update : {e}")
        return {"error": str(e)}


@app.delete("/deck/delete")
async def delete_deck(query: DeckdeleteQuery):
    try:
        results = deck_dao.delete(query.deck_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/delete : {e}")
        return {"error": str(e)}


@app.get("/deck/user/read")
async def read_user_deck(
    user_id: int = Query(..., description="ID de l'utilisateur"),
    deck_id: Optional[int] = Query(None, description="ID du deck (facultatif)")
):
    try:
        if deck_id:
            results = deck_dao.get_by_id(deck_id)
        else:
            results = deck_dao.get_all_deck_user_id(user_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/user/read : {e}")
        return {"error": str(e)}


@app.post("/deck/card/add")
async def add_card_deck(query: DeckaddCardQuery):
    try:
        results = deck_dao.add_card_to_deck(query.deck_id, query.card_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/card/add : {e}")
        return {"error": str(e)}


@app.delete("/deck/card/remove")
async def remove_card_deck(
    deck_id: int = Query(..., description="ID du deck"),
    card_id: int = Query(..., description="ID de la carte à retirer")
):
    try:
        results = deck_dao.remove_card_from_deck(deck_id, card_id)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /deck/card/remove : {e}")
        return {"error": str(e)}
