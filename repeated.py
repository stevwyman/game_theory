"""Lecture-style repeated-game analysis on a 2-player stage game.

Finite games use backward induction / unraveling. Infinite games use
discounted grim trigger and a critical discount factor. The repeated
strategy space is not enumerated.
"""

from __future__ import annotations

from typing import Any

from game import Game

MAX_PERIODS = 50
ALLOWED_MODES = ("finite", "infinite")


def analyze_repeated(
    game: Game,
    mode: str,
    periods: int | None = None,
    discount: float | None = None,
    cooperate: tuple[int, int] | None = None,
) -> dict[str, Any]:
    if mode not in ALLOWED_MODES:
        raise ValueError("repeat must be finite or infinite")
    if mode == "finite":
        return analyze_finite(game, periods)
    return analyze_infinite(game, discount, cooperate)


def analyze_finite(game: Game, periods: int | None) -> dict[str, Any]:
    periods = _require_periods(periods)
    equilibria = stage_equilibria(game)
    result: dict[str, Any] = {
        "mode": "finite",
        "periods": periods,
        "stage_ne": equilibria,
    }
    if not equilibria:
        result["unique"] = False
        result["message"] = "No stage-game Nash equilibrium, so unraveling has no terminal NE."
        result["path"] = []
        return result

    if len(equilibria) == 1:
        profile = equilibria[0]
        path = [_period_profile(profile, period) for period in range(1, periods + 1)]
        payoffs = profile["payoffs"]
        result.update(
            {
                "unique": True,
                "message": (
                    "Unique stage NE: the unique SPNE is that profile in every period "
                    "(unraveling)."
                ),
                "path": path,
                "total_payoffs": [payoffs[0] * periods, payoffs[1] * periods],
                "average_payoffs": list(payoffs),
            }
        )
        return result

    result.update(
        {
            "unique": False,
            "message": (
                "Several stage NE: the last period can be any of them. "
                "This version does not solve the full finite SPE with intertemporal rewards."
            ),
            "last_period": equilibria,
            "path": [],
        }
    )
    return result


def analyze_infinite(
    game: Game,
    discount: float | None,
    cooperate: tuple[int, int] | None = None,
) -> dict[str, Any]:
    discount = _require_discount(discount)
    equilibria = stage_equilibria(game)
    rows = game.player.strategy_set_size()
    cols = game.opponent.strategy_set_size()
    if cooperate is not None:
        cooperate = _require_cell(cooperate, rows, cols)

    candidates = grim_candidates(game, equilibria, cooperate)
    for item in candidates:
        item["sustainable"] = _is_sustainable(item, discount)
    selected = _select_candidate(candidates)
    result: dict[str, Any] = {
        "mode": "infinite",
        "discount": discount,
        "stage_ne": equilibria,
        "candidates": candidates,
        "selected": selected,
        "message": _infinite_message(selected, discount, cooperate),
    }
    if selected:
        result["sustainable"] = selected["sustainable"]
        result["critical_delta"] = selected["critical_delta"]
        result["grim_payoffs"] = list(selected["cooperate"]["payoffs"])
        result["punishment_payoffs"] = list(selected["punishment"]["payoffs"])
    return result


def stage_payoffs(game: Game, row: int, col: int) -> list[float]:
    return [
        float(game.player.strategy(row).payoff(col)),
        float(game.opponent.strategy(col).payoff(row)),
    ]


def expected_payoffs(game: Game, player_mix, opponent_mix) -> list[float]:
    player_matrix, opponent_matrix = game.payoff_matrices()
    row_payoff = 0.0
    col_payoff = 0.0
    for i, p_prob in enumerate(player_mix):
        for j, o_prob in enumerate(opponent_mix):
            weight = float(p_prob) * float(o_prob)
            row_payoff += weight * player_matrix[i][j]
            col_payoff += weight * opponent_matrix[i][j]
    return [row_payoff, col_payoff]


def stage_equilibria(game: Game) -> list[dict[str, Any]]:
    pures = []
    for row_strategy, col_strategy in game.pure_nash_equilibrium(verbose=False):
        row = game.player.strategy_set.index(row_strategy)
        col = game.opponent.strategy_set.index(col_strategy)
        pures.append(_pure_profile(game, row, col, kind="pure_ne"))
    if pures:
        return pures

    mixed = []
    for player_mix, opponent_mix in game.nash_equilibria():
        mixed.append(
            {
                "kind": "mixed",
                "row": None,
                "col": None,
                "player": None,
                "opponent": None,
                "player_mix": [float(probability) for probability in player_mix],
                "opponent_mix": [float(probability) for probability in opponent_mix],
                "payoffs": expected_payoffs(game, player_mix, opponent_mix),
            }
        )
    return mixed


def grim_candidates(
    game: Game,
    equilibria: list[dict[str, Any]],
    cooperate: tuple[int, int] | None,
) -> list[dict[str, Any]]:
    rows = game.player.strategy_set_size()
    cols = game.opponent.strategy_set_size()
    ne_cells = {
        (item["row"], item["col"])
        for item in equilibria
        if item["kind"] == "pure_ne" and item["row"] is not None
    }
    if cooperate is not None:
        cells = [cooperate]
    else:
        cells = [
            (i, j)
            for i in range(rows)
            for j in range(cols)
            if (i, j) not in ne_cells
            and any(_pareto_dominates(stage_payoffs(game, i, j), eq["payoffs"]) for eq in equilibria)
        ]

    candidates = []
    for row, col in cells:
        profile = _pure_profile(game, row, col, kind="cooperate")
        if (row, col) in ne_cells:
            candidates.append(
                {
                    "cooperate": profile,
                    "punishment": None,
                    "player": None,
                    "opponent": None,
                    "critical_delta": 0.0,
                    "sustainable": True,
                    "already_stage_ne": True,
                }
            )
            continue
        if not equilibria:
            candidates.append(
                {
                    "cooperate": profile,
                    "punishment": None,
                    "player": None,
                    "opponent": None,
                    "critical_delta": None,
                    "sustainable": False,
                    "already_stage_ne": False,
                }
            )
            continue
        best = None
        for punishment in equilibria:
            evaluation = _grim_against(game, row, col, punishment)
            if best is None or _better_grim(evaluation, best):
                best = evaluation
        if best:
            best["already_stage_ne"] = False
            candidates.append(best)
    return candidates


def critical_delta(u_coop: float, u_dev: float, u_punish: float) -> float | None:
    if u_dev <= u_coop:
        return 0.0
    denom = u_dev - u_punish
    if denom <= 0:
        return None
    return (u_dev - u_coop) / denom


def parse_cooperate(value: str | None) -> tuple[int, int] | None:
    if value is None or str(value).strip() == "":
        return None
    parts = str(value).replace(" ", "").split(",")
    if len(parts) != 2:
        raise ValueError("cooperate must be row,column indices, for example 0,0")
    try:
        row = int(parts[0])
        col = int(parts[1])
    except ValueError as error:
        raise ValueError("cooperate must be row,column indices, for example 0,0") from error
    return row, col


def _grim_against(game: Game, row: int, col: int, punishment: dict[str, Any]) -> dict[str, Any]:
    coop = stage_payoffs(game, row, col)
    player = _best_deviation(game, col, role="player")
    opponent = _best_deviation(game, row, role="opponent")
    player_delta = critical_delta(coop[0], player["payoff"], punishment["payoffs"][0])
    opponent_delta = critical_delta(coop[1], opponent["payoff"], punishment["payoffs"][1])
    if player_delta is None or opponent_delta is None:
        critical = None
    else:
        critical = max(player_delta, opponent_delta)
    return {
        "cooperate": _pure_profile(game, row, col, kind="cooperate"),
        "punishment": punishment,
        "player": {**player, "critical_delta": player_delta},
        "opponent": {**opponent, "critical_delta": opponent_delta},
        "critical_delta": critical,
        "sustainable": False,
    }


def _best_deviation(game: Game, other_index: int, role: str) -> dict[str, Any]:
    if role == "player":
        payoffs = [
            float(game.player.strategy(i).payoff(other_index))
            for i in range(game.player.strategy_set_size())
        ]
        index = max(range(len(payoffs)), key=lambda i: (payoffs[i], -i))
        return {
            "strategy": game.player.strategy(index).name,
            "index": index,
            "payoff": payoffs[index],
        }
    payoffs = [
        float(game.opponent.strategy(j).payoff(other_index))
        for j in range(game.opponent.strategy_set_size())
    ]
    index = max(range(len(payoffs)), key=lambda j: (payoffs[j], -j))
    return {
        "strategy": game.opponent.strategy(index).name,
        "index": index,
        "payoff": payoffs[index],
    }


def _pure_profile(game: Game, row: int, col: int, kind: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "row": row,
        "col": col,
        "player": game.player.strategy(row).name,
        "opponent": game.opponent.strategy(col).name,
        "payoffs": stage_payoffs(game, row, col),
    }


def _period_profile(profile: dict[str, Any], period: int) -> dict[str, Any]:
    return {"period": period, **profile}


def _pareto_dominates(left: list[float], right: list[float]) -> bool:
    weakly = left[0] >= right[0] and left[1] >= right[1]
    strictly = left[0] > right[0] or left[1] > right[1]
    return weakly and strictly


def _select_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    return min(candidates, key=_candidate_rank)


def _candidate_rank(candidate: dict[str, Any]) -> tuple:
    delta = candidate.get("critical_delta")
    payoffs = candidate["cooperate"]["payoffs"]
    return (
        0 if candidate.get("already_stage_ne") else 1,
        0 if candidate.get("sustainable") else 1,
        float("inf") if delta is None else delta,
        -(payoffs[0] + payoffs[1]),
    )


def _better_grim(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return _candidate_rank(left) < _candidate_rank(right)


def _is_sustainable(candidate: dict[str, Any], discount: float) -> bool:
    if candidate.get("already_stage_ne"):
        return True
    delta = candidate.get("critical_delta")
    return delta is not None and discount >= delta


def _infinite_message(
    selected: dict[str, Any] | None, discount: float, cooperate: tuple[int, int] | None
) -> str:
    if selected is None:
        if cooperate is None:
            return "No cell Pareto-dominates a stage NE, so grim trigger has no cooperative candidate."
        return "That cooperative cell could not be evaluated."
    if selected.get("already_stage_ne"):
        return "The chosen cell is already a stage NE; grim trigger is not needed."
    if selected["critical_delta"] is None:
        return "Grim trigger cannot sustain that profile: punishment is not worse than the temptation."
    if discount >= selected["critical_delta"]:
        return (
            f"Grim trigger is sustainable at δ = {discount:g} "
            f"(critical δ* = {selected['critical_delta']:.4g})."
        )
    return (
        f"Grim trigger is not sustainable at δ = {discount:g} "
        f"(critical δ* = {selected['critical_delta']:.4g})."
    )


def _require_periods(periods: int | None) -> int:
    if periods is None:
        raise ValueError("periods is required for a finite repeated game")
    try:
        value = int(periods)
    except (TypeError, ValueError) as error:
        raise ValueError("periods must be an integer") from error
    if value != periods:
        raise ValueError("periods must be an integer")
    if value < 2 or value > MAX_PERIODS:
        raise ValueError(f"periods must be between 2 and {MAX_PERIODS}")
    return value


def _require_discount(discount: float | None) -> float:
    if discount is None:
        raise ValueError("discount is required for an infinite repeated game")
    try:
        value = float(discount)
    except (TypeError, ValueError) as error:
        raise ValueError("discount must be a number") from error
    if not (0 <= value < 1):
        raise ValueError("discount must be in [0, 1)")
    return value


def _require_cell(cell: tuple[int, int], rows: int, cols: int) -> tuple[int, int]:
    row, col = cell
    if row < 0 or col < 0 or row >= rows or col >= cols:
        raise ValueError("cooperate indices are outside the matrix")
    return row, col
