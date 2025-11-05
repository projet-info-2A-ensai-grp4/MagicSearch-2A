from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dao.playerDao import PlayerDao
from dao.cardDao import CardDao

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


class CardFilterQuery(BaseModel):
    colors: Optional[List[str]] = None
    mana_value: Optional[int] = None
    mana_value__lte: Optional[int] = None
    mana_value__gte: Optional[int] = None
    order_by: Optional[str] = "id"
    asc: Optional[bool] = True
    limit: Optional[int] = 10
    offset: Optional[int] = 0


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
            query.order_by, query.asc, query.limit, query.offset, **filter_kwargs)
        return {"results": results}
    except Exception as e:
        print(f"Erreur dans /search : {e}")
        return {"error": str(e)}
