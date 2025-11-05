from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dao.playerDao import PlayerDao

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

@app.post("/filter")
async def filter(query: Query):
    pass