from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dao.playerDao import PlayerDao
from dao.cardDao import CardDao
import hashlib
from services.userService import UserService


app = FastAPI()
player_dao = PlayerDao()
card_dao = CardDao()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    text: str
    limit: Optional[int] = 10


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


@app.post("/search")
async def search(query: Query):
    """
    Endpoint pour effectuer une recherche sémantique sur les cartes Magic.
    """
    text = query.text
    limit = min(query.limit, 50)  # Maximum 50 cards
    print(f"Requête reçue : {text}, limit: {limit}")

    try:
        results = player_dao.natural_language_search(text, limit=limit)

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
        print(f"Erreur dans /search : {e}")
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
            password_hash=user_data.password_hash
        )

        user = user_service.signIn()

        return {
            "message": "Login successful",
            "user": {
                "id": user["user_id"], 
                "username": user["username"],
                "email": user["email"]
            }
        }

    except ValueError as e:
        return {"error": "INVALID_CREDENTIALS", "message": str(e)}

    except Exception as e:
        print(f"Erreur dans /login : {e}")
        return {"error": "SERVER_ERROR", "message": "Une erreur serveur est survenue"}
