from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
from dao.playerDao import PlayerDao
from services.userService import UserService


app = FastAPI()
player_dao = PlayerDao()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    text: str


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str


@app.post("/search")
async def search(query: Query):
    """
    Endpoint pour effectuer une recherche sémantique sur les cartes Magic.
    """
    text = query.text
    print(f"Requête reçue : {text}")

    try:
        results = player_dao.natural_language_search(text, limit=5)

        if not results:
            return {"results": [], "message": "Aucune carte trouvée."}

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

        user_service = UserService(user_data.username,
                                   user_data.email,
                                   password_hash)

        new_user = user_service.signUp()

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user["id"],
                "username": new_user["username"],
                "email": new_user["email"]
            }
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
