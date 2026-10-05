import pytest
from fastapi.testclient import TestClient

from webapp.app import app
from webapp.service import analyze, game_from_payload

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_index_renders_patternfly():
    response = client.get("/")
    assert response.status_code == 200
    assert "Game theory solver" in response.text
    assert "patternfly.min.css" in response.text
    assert "theme.js" in response.text
    assert "Reset" in response.text
    assert 'data-theme-mode="auto"' in response.text
    assert "tennis" in response.text


def test_example_tennis():
    response = client.get("/api/examples/tennis")
    assert response.status_code == 200
    data = response.json()
    assert data["player_name"] == "Venus"
    assert data["cells"][0][0] == [50.0, 50.0]


def test_example_rejects_path_traversal():
    assert client.get("/api/examples/not-a-game").status_code == 404
    assert client.get("/api/examples/..").status_code == 404


def test_solve_tennis_mixed():
    payload = {
        "player_name": "Venus",
        "opponent_name": "Serena",
        "player_strategies": ["Venus_S0", "Venus_S1"],
        "opponent_strategies": ["Serena_S0", "Serena_S1"],
        "cells": [[[50, 50], [80, 20]], [[90, 10], [20, 80]]],
        "use_weakly": False,
        "mixed_method": "support",
    }
    response = client.post("/api/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["pure_ne"] == []
    grid = data["pure_ne_grid"]
    assert grid["legend"].startswith("P = row-player best response")
    assert grid["player_strategies"] == ["Venus_S0", "Venus_S1"]
    assert grid["opponent_strategies"] == ["Serena_S0", "Serena_S1"]
    assert grid["cells"][0][0]["player_br"] is False
    assert grid["cells"][0][0]["pure_ne"] is False
    mix = data["mixed"]["equilibria"][0]
    assert mix["player"][0]["probability"] == pytest.approx(0.7)
    assert mix["opponent"][0]["probability"] == pytest.approx(0.6)


def test_solve_rejects_oversized_matrix():
    cells = [[[0, 0] for _ in range(9)] for _ in range(9)]
    response = client.post(
        "/api/solve",
        json={"cells": cells, "mixed_method": "support"},
    )
    assert response.status_code == 400


def test_solve_rejects_non_finite():
    response = client.post(
        "/api/solve",
        json={"cells": [[[1, 0], [0, 1e12]]], "mixed_method": "support"},
    )
    assert response.status_code == 400


def test_game_from_cells_matches_ini_layout():
    game = game_from_payload(
        {
            "player_name": "P",
            "opponent_name": "O",
            "cells": [[[-2, -2], [-10, 0]], [[0, -10], [-5, -5]]],
        }
    )
    assert game.player.strategy(0).payoff(1) == -10
    assert game.opponent.strategy(1).payoff(0) == 0
    result = analyze(
        {
            "cells": [[[-2, -2], [-10, 0]], [[0, -10], [-5, -5]]],
            "use_weakly": False,
            "mixed_method": "support",
        }
    )
    assert result["pure_ne"] == [{"player": "P_S1", "opponent": "O_S1"}]
    assert result["ieds"]["unique_pure"] is True
    assert result["pure_ne_grid"]["cells"][1][1] == {
        "player_br": True,
        "opponent_br": True,
        "pure_ne": True,
    }


def test_module_starts_uvicorn(monkeypatch):
    calls = []

    def fake_run(app, host, port):
        calls.append((app, host, port))

    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setattr("uvicorn.run", fake_run)

    from webapp.__main__ import main

    main()
    assert calls == [("webapp.app:app", "127.0.0.1", 8080)]
