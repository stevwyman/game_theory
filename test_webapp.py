import pytest
from fastapi.testclient import TestClient

from webapp.app import app
from webapp.service import analyze, game_from_payload
from webapp.store import init_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("GAME_DB_PATH", str(tmp_path / "games.db"))
    init_store()


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
    assert 'data-app-root=""' in response.text
    assert 'href="/static/app.css"' in response.text
    assert "logo.svg" in response.text
    assert "patternfly.min.css" in response.text
    assert "theme.js" in response.text
    assert "Reset" in response.text
    assert "Save game" in response.text
    assert "Explanation" in response.text
    assert 'data-repeat-mode="finite"' in response.text
    assert 'data-theme-mode="auto"' in response.text
    assert "tennis" in response.text


def test_root_path_prefix(monkeypatch):
    monkeypatch.setenv("ROOT_PATH", "/game-theory")
    prefixed = TestClient(app)
    page = prefixed.get("/game-theory/")
    assert page.status_code == 200
    assert 'data-app-root="/game-theory"' in page.text
    assert 'href="/game-theory/static/app.css"' in page.text
    assert prefixed.get("/game-theory/health").json() == {"status": "ok"}
    assert prefixed.get("/health").json() == {"status": "ok"}
    assert prefixed.get("/game-theory/api/examples").status_code == 200
    assert prefixed.get("/game-theory/static/app.js").status_code == 200
    assert prefixed.get("/static/app.js").status_code == 200
    stripped = prefixed.get("/")
    assert stripped.status_code == 200
    assert 'data-app-root="/game-theory"' in stripped.text


def test_root_path_normalizes_and_rejects_traversal(monkeypatch):
    from webapp.app import configured_root_path

    monkeypatch.setenv("ROOT_PATH", "game-theory")
    assert configured_root_path() == "/game-theory"
    monkeypatch.setenv("ROOT_PATH", "/game-theory/")
    assert configured_root_path() == "/game-theory"
    monkeypatch.setenv("ROOT_PATH", "/game-theory/../secret")
    assert configured_root_path() == ""
    monkeypatch.delenv("ROOT_PATH", raising=False)
    assert configured_root_path() == ""


def test_example_tennis():
    response = client.get("/api/examples/tennis")
    assert response.status_code == 200
    data = response.json()
    assert data["player_name"] == "Venus"
    assert data["cells"][0][0] == [50.0, 50.0]
    assert "lecture 9" in data["description"]


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
    assert result["repeated"] == {"mode": "off"}


def test_solve_repeated_pd_finite():
    payload = {
        "cells": [[[-2, -2], [-10, 0]], [[0, -10], [-5, -5]]],
        "repeat": "finite",
        "periods": 4,
    }
    response = client.post("/api/solve", json=payload)
    assert response.status_code == 200
    repeated = response.json()["repeated"]
    assert repeated["mode"] == "finite"
    assert repeated["unique"] is True
    assert len(repeated["path"]) == 4
    assert repeated["path"][0]["player"] == "P_S1"


def test_solve_repeated_pd_infinite():
    payload = {
        "cells": [[[-2, -2], [-10, 0]], [[0, -10], [-5, -5]]],
        "repeat": "infinite",
        "discount": 0.6,
        "cooperate_row": 0,
        "cooperate_col": 0,
    }
    response = client.post("/api/solve", json=payload)
    assert response.status_code == 200
    repeated = response.json()["repeated"]
    assert repeated["sustainable"] is True
    assert repeated["critical_delta"] == pytest.approx(0.4)


def test_solve_repeated_rejects_bad_discount_and_periods():
    cells = [[[-2, -2], [-10, 0]], [[0, -10], [-5, -5]]]
    assert client.post(
        "/api/solve",
        json={"cells": cells, "repeat": "infinite", "discount": 1},
    ).status_code == 400
    assert client.post(
        "/api/solve",
        json={"cells": cells, "repeat": "finite", "periods": 80},
    ).status_code == 400
    assert client.post(
        "/api/solve",
        json={
            "cells": cells,
            "repeat": "infinite",
            "discount": 0.5,
            "cooperate_row": 9,
            "cooperate_col": 0,
        },
    ).status_code == 400


def test_save_and_reload_game():
    payload = {
        "label": "My coordination game",
        "description": "Both players want to match.",
        "player_name": "Ann",
        "opponent_name": "Bob",
        "player_strategies": ["Left", "Right"],
        "opponent_strategies": ["Left", "Right"],
        "cells": [[[2, 1], [0, 0]], [[0, 0], [1, 2]]],
    }
    created = client.post("/api/games", json=payload)
    assert created.status_code == 200
    data = created.json()
    assert data["id"] == "my-coordination-game"
    assert data["description"] == "Both players want to match."
    assert data["player_strategies"] == ["Left", "Right"]
    assert data["cells"][0][0] == [2.0, 1.0]

    listed = client.get("/api/examples").json()["examples"]
    assert any(item["id"] == "my-coordination-game" for item in listed)

    loaded = client.get("/api/examples/my-coordination-game")
    assert loaded.status_code == 200
    assert loaded.json()["opponent_name"] == "Bob"

    payload["id"] = "my-coordination-game"
    payload["description"] = "Updated notes."
    updated = client.post("/api/games", json=payload)
    assert updated.status_code == 200
    assert updated.json()["description"] == "Updated notes."


def test_save_game_requires_label():
    response = client.post(
        "/api/games",
        json={"cells": [[[1, 0], [0, 1]], [[0, 1], [1, 0]]]},
    )
    assert response.status_code == 400


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
