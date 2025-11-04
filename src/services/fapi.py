from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "MagicSearch Engine"}


class Query(BaseModel):
    text: str


@app.post("/search")
async def search(query: Query):
    print(f"Requête reçue : {query.text}")
    request = query.text

    # ICI ON APPELLE LES FONCTIONS DONT ON A BESOIN POUR EMBED LA REQUETE ET COMPARER AVEC LES
    # EMBEDDINGS DES CARTES

    results = request[::-1]

    return {"results": results}
