from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse  # , HTMLResponse
from pathlib import Path
from dao.playerDao import PlayerDao


app = FastAPI()

player_dao = PlayerDao()


BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
PAGES_DIR = BASE_DIR / "pages"


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index():
    return FileResponse(PAGES_DIR / "index.html")


@app.get("/login")
async def login():
    return FileResponse(PAGES_DIR / "login.html")


@app.get("/register")
async def register():
    return FileResponse(PAGES_DIR / "register.html")


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

        # si on trouve pas de carte
        if not results:
            return {"results": [], "message": "Aucune carte trouvée."}

        return {"results": results}

    except Exception as e:
        print(f"Erreur dans /search : {e}")
        return {"error": str(e)}


# @app.get("/search")
# async def search_get(text: str = None):
#     content = "<h1>Résultat de la recherche</h1>"
#     if text:
#         content += f"<p>Texte inversé : {text[::-1]}</p>"
#     else:
#         content += "<p>Rien à afficher. Passez un paramètre 'text' dans l'URL.</p>"
#     return HTMLResponse(content)
