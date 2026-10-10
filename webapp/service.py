"""Structured analysis of a 2-player game for the web API."""

from __future__ import annotations

import math
from typing import Any

from game import Game, Opponent, Player
from repeated import analyze_repeated
from webapp import store

MAX_STRATEGIES = 8
MAX_NAME_LENGTH = 40
ALLOWED_METHODS = ("support", "lemke-howson", "williams")
ALLOWED_REPEAT = ("off", "finite", "infinite")


def list_examples() -> list[dict[str, str]]:
    return store.list_games()


def load_example(example_id: str) -> dict[str, Any]:
    return store.get_game(example_id)


def save_example(payload: dict[str, Any]) -> dict[str, Any]:
    game = game_from_payload(payload)
    record = serialize_game(game)
    record["id"] = payload.get("id")
    record["label"] = payload.get("label")
    record["description"] = payload.get("description", "")
    return store.upsert_game(record)


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    game = game_from_payload(payload)
    use_weakly = bool(payload.get("use_weakly", False))
    method = str(payload.get("mixed_method", "support"))
    if method not in ALLOWED_METHODS:
        raise ValueError("mixed_method must be support, lemke-howson, or williams")

    result: dict[str, Any] = {
        "game": serialize_game(game),
        "constant_sum": game.is_constant_sum(),
        "dominance": _dominance(game),
        "pure_ne": [
            {"player": row.name, "opponent": column.name}
            for row, column in game.pure_nash_equilibrium(verbose=False)
        ],
        "pure_ne_grid": _pure_ne_grid(game),
    }

    reduced = game.copy()
    ieds_log: list[str] = []
    reduced.solve_by_iterated_deletion(
        use_weakly=use_weakly, verbose=False, log=ieds_log
    )
    result["ieds"] = {
        "use_weakly": use_weakly,
        "log": [line.strip() for line in ieds_log],
        "reduced": serialize_game(reduced),
        "unique_pure": (
            reduced.player.strategy_set_size() == 1
            and reduced.opponent.strategy_set_size() == 1
        ),
    }

    result["mixed"] = _mixed_result(reduced, method)
    result["repeated"] = _repeated_result(game, payload)
    return result


def game_from_payload(payload: dict[str, Any]) -> Game:
    player_name = _clean_name(payload.get("player_name"), "P")
    opponent_name = _clean_name(payload.get("opponent_name"), "O")
    if payload.get("cells") is not None:
        player_payoffs, opponent_payoffs = _matrices_from_cells(payload.get("cells"))
    else:
        player_payoffs = _as_matrix(payload.get("player_payoffs"), "player_payoffs")
        opponent_payoffs = _as_matrix(payload.get("opponent_payoffs"), "opponent_payoffs")
    player_names = _strategy_names(payload.get("player_strategies"), len(player_payoffs))
    opponent_names = _strategy_names(
        payload.get("opponent_strategies"), len(opponent_payoffs)
    )

    player = Player.from_payoff_matrix(player_name, player_payoffs, player_names)
    opponent = Opponent.from_payoff_matrix(
        opponent_name, opponent_payoffs, opponent_names
    )
    return Game(player, opponent)


def serialize_game(game: Game) -> dict[str, Any]:
    rows = game.player.strategy_set_size()
    cols = game.opponent.strategy_set_size()
    cells = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(
                [
                    game.player.strategy(i).payoff(j),
                    game.opponent.strategy(j).payoff(i),
                ]
            )
        cells.append(row)
    return {
        "player_name": game.player.name,
        "opponent_name": game.opponent.name,
        "player_strategies": [strategy.name for strategy in game.player.strategy_set],
        "opponent_strategies": [
            strategy.name for strategy in game.opponent.strategy_set
        ],
        "player_payoffs": [
            list(strategy.payoffs) for strategy in game.player.strategy_set
        ],
        "opponent_payoffs": [
            list(strategy.payoffs) for strategy in game.opponent.strategy_set
        ],
        "cells": cells,
    }


def _repeated_result(game: Game, payload: dict[str, Any]) -> dict[str, Any]:
    mode = str(payload.get("repeat") or "off")
    if mode not in ALLOWED_REPEAT:
        raise ValueError("repeat must be off, finite, or infinite")
    if mode == "off":
        return {"mode": "off"}
    return analyze_repeated(
        game,
        mode,
        periods=_optional_int(payload.get("periods"), "periods"),
        discount=_optional_number(payload.get("discount"), "discount"),
        cooperate=_cooperate_from_payload(payload),
    )


def _cooperate_from_payload(payload: dict[str, Any]) -> tuple[int, int] | None:
    row = payload.get("cooperate_row")
    col = payload.get("cooperate_col")
    if row is None and col is None:
        return None
    if row is None or col is None:
        raise ValueError("cooperate_row and cooperate_col must be provided together")
    return (
        _require_int(row, "cooperate_row"),
        _require_int(col, "cooperate_col"),
    )


def _optional_int(value: Any, field: str) -> int | None:
    if value is None or value == "":
        return None
    return _require_int(value, field)


def _optional_number(value: Any, field: str) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number


def _require_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be an integer")
    number = int(value)
    if number != value:
        raise ValueError(f"{field} must be an integer")
    return number


def _pure_ne_grid(game: Game) -> dict[str, Any]:
    marks = game.best_response_grid()
    cells = [
        [
            {
                "player_br": player_br,
                "opponent_br": opponent_br,
                "pure_ne": player_br and opponent_br,
            }
            for player_br, opponent_br in row
        ]
        for row in marks
    ]
    return {
        "player_label": "P",
        "opponent_label": "O",
        "legend": "P = row-player best response, O = column-player best response. A pure NE is P True, O True.",
        "player_strategies": [strategy.name for strategy in game.player.strategy_set],
        "opponent_strategies": [
            strategy.name for strategy in game.opponent.strategy_set
        ],
        "cells": cells,
    }


def _dominance(game: Game) -> dict[str, dict[str, list[str]]]:
    def names(strategies) -> list[str]:
        return [strategy.name for strategy in strategies]

    return {
        "player": {
            "strictly_dominated": names(game.player.strictly_dominated_strategy()),
            "strictly_dominant": names(game.player.strictly_dominant_strategy()),
            "weakly_dominated": names(game.player.weakly_dominated_strategy()),
            "weakly_dominant": names(game.player.weakly_dominant_strategy()),
        },
        "opponent": {
            "strictly_dominated": names(game.opponent.strictly_dominated_strategy()),
            "strictly_dominant": names(game.opponent.strictly_dominant_strategy()),
            "weakly_dominated": names(game.opponent.weakly_dominated_strategy()),
            "weakly_dominant": names(game.opponent.weakly_dominant_strategy()),
        },
    }


def _mixed_result(game: Game, method: str) -> dict[str, Any]:
    if game.player.strategy_set_size() < 2 or game.opponent.strategy_set_size() < 2:
        profile = None
        if (
            game.player.strategy_set_size() == 1
            and game.opponent.strategy_set_size() == 1
        ):
            profile = {
                "player": game.player.strategy(0).name,
                "opponent": game.opponent.strategy(0).name,
            }
        return {
            "method": method,
            "needed": False,
            "message": "IEDS reduced the game to a unique remaining profile.",
            "profile": profile,
            "equilibria": [],
        }

    if method == "williams":
        if not game.is_constant_sum():
            raise ValueError(
                "Williams fictitious play requires a zero-sum or constant-sum game"
            )
        player_mix, opponent_mix, value = game.williams_mixed_equilibrium()
        return {
            "method": method,
            "needed": True,
            "message": "Approximate mixed strategies from Williams fictitious play.",
            "value": value,
            "equilibria": [_mix_payload(game, player_mix, opponent_mix)],
        }

    if method == "lemke-howson":
        equilibria = game.lemke_howson_equilibria()
        return {
            "method": method,
            "needed": True,
            "message": "Nash equilibria reachable by Lemke–Howson from every label.",
            "equilibria": [
                _mix_payload(game, player_mix, opponent_mix)
                for player_mix, opponent_mix in equilibria
            ],
        }

    mixed = game.mixed_nash_equilibria()
    if not mixed:
        return {
            "method": method,
            "needed": True,
            "message": "No mixed Nash equilibrium; remaining equilibria are pure.",
            "equilibria": [],
        }
    return {
        "method": method,
        "needed": True,
        "message": "Mixed Nash equilibria from support enumeration.",
        "equilibria": [
            _mix_payload(game, player_mix, opponent_mix)
            for player_mix, opponent_mix in mixed
        ],
    }


def _mix_payload(game: Game, player_mix, opponent_mix) -> dict[str, Any]:
    return {
        "player": [
            {"strategy": game.player.strategy(i).name, "probability": float(probability)}
            for i, probability in enumerate(player_mix)
        ],
        "opponent": [
            {
                "strategy": game.opponent.strategy(j).name,
                "probability": float(probability),
            }
            for j, probability in enumerate(opponent_mix)
        ],
    }


def _clean_name(value: Any, fallback: str) -> str:
    name = str(value).strip() if value is not None else fallback
    if not name:
        name = fallback
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"names must be at most {MAX_NAME_LENGTH} characters")
    return name


def _strategy_names(value: Any, expected: int) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("strategy names must be a list")
    names = []
    for item in value[:expected]:
        label = str(item).strip()
        if len(label) > MAX_NAME_LENGTH:
            raise ValueError(
                f"strategy names must be at most {MAX_NAME_LENGTH} characters"
            )
        names.append(label)
    return names


def _matrices_from_cells(value: Any) -> tuple[list[list[float]], list[list[float]]]:
    if not isinstance(value, list) or not value:
        raise ValueError("cells must be a non-empty matrix")
    if len(value) > MAX_STRATEGIES:
        raise ValueError(f"at most {MAX_STRATEGIES} strategies per player")
    width = None
    player_payoffs: list[list[float]] = []
    for row in value:
        if not isinstance(row, list) or not row:
            raise ValueError("cells rows must be non-empty lists")
        if width is None:
            width = len(row)
            if width > MAX_STRATEGIES:
                raise ValueError(f"at most {MAX_STRATEGIES} strategies per player")
        elif len(row) != width:
            raise ValueError("cells rows must all have the same length")
        player_row = []
        for cell in row:
            if not isinstance(cell, list) or len(cell) != 2:
                raise ValueError("each cell must be [player_payoff, opponent_payoff]")
            player_row.append(_as_number(cell[0], "cells"))
        player_payoffs.append(player_row)

    opponent_payoffs = []
    for j in range(width or 0):
        opponent_row = []
        for i in range(len(value)):
            opponent_row.append(_as_number(value[i][j][1], "cells"))
        opponent_payoffs.append(opponent_row)
    return player_payoffs, opponent_payoffs


def _as_matrix(value: Any, field: str) -> list[list[float]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty matrix")
    if len(value) > MAX_STRATEGIES:
        raise ValueError(f"at most {MAX_STRATEGIES} strategies per player")
    matrix = []
    width = None
    for row in value:
        if not isinstance(row, list) or not row:
            raise ValueError(f"{field} rows must be non-empty lists")
        if width is None:
            width = len(row)
            if width > MAX_STRATEGIES:
                raise ValueError(f"at most {MAX_STRATEGIES} strategies per player")
        elif len(row) != width:
            raise ValueError(f"{field} rows must all have the same length")
        matrix.append([_as_number(cell, field) for cell in row])
    return matrix


def _as_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must contain numbers")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must contain finite numbers")
    if abs(number) > 1e9:
        raise ValueError(f"{field} values are out of range")
    return number
