"""SQLite persistence for saved games, players, and strategies."""

from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from project import load_game

MAX_LABEL_LENGTH = 80
MAX_DESCRIPTION_LENGTH = 4000
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,59}$")

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    game_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('player', 'opponent')),
    name TEXT NOT NULL,
    PRIMARY KEY (game_id, role),
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS strategies (
    game_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('player', 'opponent')),
    position INTEGER NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (game_id, role, position),
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payoffs (
    game_id TEXT NOT NULL,
    row_position INTEGER NOT NULL,
    col_position INTEGER NOT NULL,
    player_payoff REAL NOT NULL,
    opponent_payoff REAL NOT NULL,
    PRIMARY KEY (game_id, row_position, col_position),
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);
"""


def default_db_path() -> str:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(root, "data", "games.db")


def db_path() -> str:
    return os.environ.get("GAME_DB_PATH") or default_db_path()


def games_dir() -> str:
    return os.environ.get(
        "GAMES_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "games")),
    )


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    path = db_path()
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_store() -> None:
    with connection() as conn:
        conn.executescript(SCHEMA)
    seed_from_ini_files()


def list_games() -> list[dict[str, str]]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT id, label, description FROM games ORDER BY label COLLATE NOCASE"
        ).fetchall()
    return [
        {"id": row["id"], "label": row["label"], "description": row["description"]}
        for row in rows
    ]


def get_game(game_id: str) -> dict[str, Any]:
    game_id = _clean_id(game_id)
    with connection() as conn:
        game = conn.execute(
            "SELECT id, label, description FROM games WHERE id = ?",
            (game_id,),
        ).fetchone()
        if game is None:
            raise ValueError("unknown example")
        players = {
            row["role"]: row["name"]
            for row in conn.execute(
                "SELECT role, name FROM players WHERE game_id = ?",
                (game_id,),
            )
        }
        strategies = {"player": [], "opponent": []}
        for row in conn.execute(
            """
            SELECT role, name
            FROM strategies
            WHERE game_id = ?
            ORDER BY role, position
            """,
            (game_id,),
        ):
            strategies[row["role"]].append(row["name"])
        cells: list[list[list[float]]] = []
        payoff_rows = conn.execute(
            """
            SELECT row_position, col_position, player_payoff, opponent_payoff
            FROM payoffs
            WHERE game_id = ?
            ORDER BY row_position, col_position
            """,
            (game_id,),
        ).fetchall()
    width = max((row["col_position"] for row in payoff_rows), default=-1) + 1
    height = max((row["row_position"] for row in payoff_rows), default=-1) + 1
    cells = [[[0.0, 0.0] for _ in range(width)] for _ in range(height)]
    for row in payoff_rows:
        cells[row["row_position"]][row["col_position"]] = [
            float(row["player_payoff"]),
            float(row["opponent_payoff"]),
        ]
    return {
        "id": game["id"],
        "label": game["label"],
        "description": game["description"],
        "player_name": players.get("player", "P"),
        "opponent_name": players.get("opponent", "O"),
        "player_strategies": strategies["player"],
        "opponent_strategies": strategies["opponent"],
        "cells": cells,
    }


def upsert_game(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("id"):
        game_id = _clean_id(record.get("id"))
    else:
        game_id = slugify(str(record.get("label") or ""))
        if not ID_PATTERN.match(game_id):
            raise ValueError("game id must be a short lowercase slug")
    label = _clean_label(record.get("label"))
    description = _clean_description(record.get("description"))
    player_name = str(record["player_name"])
    opponent_name = str(record["opponent_name"])
    player_strategies = list(record["player_strategies"])
    opponent_strategies = list(record["opponent_strategies"])
    cells = record["cells"]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with connection() as conn:
        existing = conn.execute(
            "SELECT created_at FROM games WHERE id = ?", (game_id,)
        ).fetchone()
        created_at = existing["created_at"] if existing else now
        conn.execute(
            """
            INSERT INTO games (id, label, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                label = excluded.label,
                description = excluded.description,
                updated_at = excluded.updated_at
            """,
            (game_id, label, description, created_at, now),
        )
        conn.execute("DELETE FROM players WHERE game_id = ?", (game_id,))
        conn.execute("DELETE FROM strategies WHERE game_id = ?", (game_id,))
        conn.execute("DELETE FROM payoffs WHERE game_id = ?", (game_id,))
        conn.execute(
            "INSERT INTO players (game_id, role, name) VALUES (?, 'player', ?)",
            (game_id, player_name),
        )
        conn.execute(
            "INSERT INTO players (game_id, role, name) VALUES (?, 'opponent', ?)",
            (game_id, opponent_name),
        )
        for index, name in enumerate(player_strategies):
            conn.execute(
                """
                INSERT INTO strategies (game_id, role, position, name)
                VALUES (?, 'player', ?, ?)
                """,
                (game_id, index, name),
            )
        for index, name in enumerate(opponent_strategies):
            conn.execute(
                """
                INSERT INTO strategies (game_id, role, position, name)
                VALUES (?, 'opponent', ?, ?)
                """,
                (game_id, index, name),
            )
        for i, row in enumerate(cells):
            for j, cell in enumerate(row):
                conn.execute(
                    """
                    INSERT INTO payoffs (
                        game_id, row_position, col_position, player_payoff, opponent_payoff
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (game_id, i, j, float(cell[0]), float(cell[1])),
                )
    return get_game(game_id)


def seed_from_ini_files() -> None:
    directory = games_dir()
    if not os.path.isdir(directory):
        return
    with connection() as conn:
        existing = {
            row["id"]
            for row in conn.execute("SELECT id FROM games").fetchall()
        }
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".ini"):
            continue
        game_id = filename[:-4]
        slug = slugify(game_id)
        if slug in existing:
            continue
        path = os.path.join(directory, filename)
        try:
            game = load_game(path)
        except (OSError, ValueError):
            continue
        from webapp.service import serialize_game

        record = serialize_game(game)
        record["id"] = slug
        record["label"] = game_id.replace("_", " ")
        record["description"] = _ini_description(path)
        upsert_game(record)
        existing.add(slug)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    slug = slug.strip("-")
    if not slug:
        slug = "game"
    return slug[:60]


def _clean_id(value: Any) -> str:
    game_id = str(value or "").strip()
    if not ID_PATTERN.match(game_id):
        raise ValueError("unknown example")
    return game_id


def _clean_label(value: Any) -> str:
    label = str(value or "").strip()
    if not label:
        raise ValueError("label is required")
    if len(label) > MAX_LABEL_LENGTH:
        raise ValueError(f"label must be at most {MAX_LABEL_LENGTH} characters")
    return label


def _clean_description(value: Any) -> str:
    description = str(value or "").strip()
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(
            f"description must be at most {MAX_DESCRIPTION_LENGTH} characters"
        )
    return description


def _ini_description(path: str) -> str:
    lines: list[str] = []
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            if raw.startswith("#"):
                lines.append(raw[1:].strip())
            elif raw.strip() == "":
                if lines:
                    continue
            else:
                break
    return "\n".join(line for line in lines if line)
