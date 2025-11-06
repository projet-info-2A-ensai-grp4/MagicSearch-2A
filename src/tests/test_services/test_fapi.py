from fastapi.testclient import TestClient
from services.fapi import app

client = TestClient(app)


def test_filter_endpoint_calls_dao(monkeypatch):
    # Mock du DAO pour éviter d’accéder à la vraie DB
    mock_results = [
        {
            "id": 1,
            "name": "Blue Elemental Blast",
            "colors": ["U"],
            "mana_value": "2",
            "type": "Instant",
            "text": "Counter target red spell.",
            "image_url": "https://example.com/blue.jpg",
        },
        {
            "id": 2,
            "name": "Red Elemental Blast",
            "colors": ["R"],
            "mana_value": "5",
            "type": "Instant",
            "text": "Destroy target blue permanent.",
            "image_url": "https://example.com/red.jpg",
        },
    ]

    def mock_filter(self, order_by, asc, limit, offset, **kwargs):
        assert kwargs["colors"] == ["U", "R"]
        assert kwargs["mana_value__lte"] == 4
        assert order_by == "id"
        assert asc is True
        assert limit == 10
        assert offset == 0
        return mock_results

    from dao.cardDao import CardDao

    monkeypatch.setattr(CardDao, "filter", mock_filter)

    response = client.post(
        "/filter",
        json={
            "colors": ["U", "R"],
            "mana_value__lte": 4,
            "order_by": "id",
            "asc": True,
            "limit": 10,
            "offset": 0,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
    assert data["results"][0]["name"] == "Blue Elemental Blast"
    assert data["results"][1]["mana_value"] == "5"


def test_filter_endpoint_integration_real():
    """
    Test d'intégration complet : on appelle /filter et on récupère des cartes
    depuis la DAO réelle (ici on peut utiliser un fake_db pour isoler).
    """

    # --- Préparer le fake DB dans la DAO si nécessaire ---
    # Par exemple CardDao pourrait avoir un fake_db interne pour les tests
    request_payload = {
        "colors": ["U", "R"],
        "mana_value__lte": 4,
        "order_by": "id",
        "asc": True,
        "limit": 1,
        "offset": 0,
    }
    response = client.post("/filter", json=request_payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    # verify the structure and logical content
    assert len(data["results"]) >= 1
    card = data["results"][0]
    assert all(key in card for key in ["id", "name", "colors", "type", "text"])
    assert isinstance(card["id"], int)
