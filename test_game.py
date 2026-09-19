import pytest
from game import (
    Strategy,
    Player,
    Opponent,
    Game,
    all_entries_equal,
    is_biggest_in_list,
    minimaxi,
    formula_2x2,
    oddments2,
    oddments3,
    transpose_strategy_set,
)
from project import load_game, game_setup


def test_transpose_strategy():
    s_01 = Strategy("S_01", (0, 0))
    s_02 = Strategy("S_02", (-10, 4))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    new_strategy_set = transpose_strategy_set(strategy_set)

    assert f"{new_strategy_set}" == "[S*_0 [0, -10], S*_1 [0, 4]]"


def test_minimaxi():
    s_01 = Strategy("S_01", (9, 7))
    s_02 = Strategy("S_02", (5, 11))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    assert minimaxi(strategy_set) == (7, 9)


def test_formula_2x2():
    # tax payers example
    s_01 = Strategy("S_01", (2, 4))
    s_02 = Strategy("S_02", (4, 0))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    assert formula_2x2(strategy_set)[0] == pytest.approx(2 / 3)
    assert formula_2x2(strategy_set)[1] == pytest.approx(1 / 3)

    s_01 = Strategy("S_01", (0, 0))
    s_02 = Strategy("S_02", (-10, 4))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    assert formula_2x2(strategy_set) == (2 / 7, 5 / 7)


def test_oddments2():
    # wrong number of strategies in the set
    s_01 = Strategy("S_01", (0, 0))
    strategy_set = list()
    strategy_set.append(s_01)

    with pytest.raises(ValueError) as e_info:
        oddments2(strategy_set)
    assert str(e_info.value) == "Strategy set must have a length of 2"

    # tax payers example
    s_01 = Strategy("S_01", (2, 4))
    s_02 = Strategy("S_02", (4, 0))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    assert oddments2(strategy_set) == (2 / 3, 1 / 3)

    # tax payers example not working, because of the 0 oddment
    s_01 = Strategy("S_01", (0, 0))
    s_02 = Strategy("S_02", (-10, 4))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    with pytest.raises(ValueError) as e_info:
        oddments2(strategy_set)
    assert str(e_info.value) == "Oddment is zero, please use different algorithm"

    # tennis
    s_01 = Strategy("S_01", (50, 80))
    s_02 = Strategy("S_02", (90, 20))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    assert oddments2(strategy_set) == (0.7, 0.3)

    s_01 = Strategy("S_01", (50, 10))
    s_02 = Strategy("S_02", (20, 80))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    assert oddments2(strategy_set) == (0.6, 0.4)

    s_01 = Strategy("S_01", (9, 7))
    s_02 = Strategy("S_02", (5, 11))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)

    assert oddments2(strategy_set) == (0.75, 0.25)


def test_oddments3():
    s_01 = Strategy("S_01", (7, 1, 7))
    s_02 = Strategy("S_02", (9, -1, 1))
    s_03 = Strategy("S_03", (5, 7, 6))
    strategy_set = list()
    strategy_set.append(s_01)
    strategy_set.append(s_02)
    strategy_set.append(s_03)

    assert oddments3(strategy_set) == (0.1, 0.1, 0.8)


def test_is_biggest_in_list():
    assert is_biggest_in_list(2, (2, 2, 0)) == True
    assert is_biggest_in_list(0, (2, 2, 0)) == False


def test_prison_dilemma():
    player = Player("P", "(10, 1), (25, 3)")
    opponent = Opponent("O", "(10, 1), (25, 3)")

    assert f"{player.strictly_dominant_strategy()}" == "[P_S1 [25.0, 3.0]]"
    assert f"{opponent.strictly_dominant_strategy()}" == "[O_S1 [25.0, 3.0]]"

    assert f"{player.strictly_dominated_strategy()}" == "[P_S0 [10.0, 1.0]]"
    assert f"{opponent.strictly_dominated_strategy()}" == "[O_S0 [10.0, 1.0]]"


def test_weakly_dominated_strategy():
    # identical payoffs are not weakly dominated: weak dominance needs a
    # strict improvement against at least one opponent action
    player = Player("P", "(10, 1), (10, 1)")
    assert player.weakly_dominated_strategy() == []

    player = Player("P", "(10, 1), (10, 2)")
    result_list = [player.strategy(0)]
    assert player.weakly_dominated_strategy() == result_list

    player = Player("P", "(10, 1), (1, 10)")
    result_list = []
    assert player.weakly_dominated_strategy() == result_list


def test_strictly_dominated_strategy():
    player = Player("P", "(11, 2), (10, 1)")
    result_list = [player.strategy(1)]
    assert player.strictly_dominated_strategy() == result_list

    player = Player("P", "(10, 1), (1, 10)")
    assert player.strictly_dominated_strategy() == []


def test_strictly_dominant_requires_all_alternatives():
    # beer-pricing: $2 is strictly dominated, but neither $4 nor $5 dominates
    # the other, so there is no strictly dominant strategy
    player = Player("P", "(60, 80, 80), (80, 120, 160), (100, 100, 150)")
    assert player.strictly_dominated_strategy() == [player.strategy(0)]
    assert player.strictly_dominant_strategy() == []
    assert player.weakly_dominant_strategy() == []


def test_weakly_dominant_strategy():
    player = Player("P", "(10, 2), (10, 1)")
    assert player.weakly_dominant_strategy() == [player.strategy(0)]
    assert player.weakly_dominated_strategy() == [player.strategy(1)]

    player = Player("P", "(10, 1), (1, 10)")
    assert player.weakly_dominant_strategy() == []


def test_tennis_mixed_nash():
    # lecture 9: Venus (0.7, 0.3), Serena (0.6, 0.4)
    player = Player("Venus", "(50, 80), (90, 20)")
    opponent = Opponent("Serena", "(50, 10), (20, 80)")
    game = Game(player, opponent)

    venus_mix = game.mixed_nash_equilibrium(player)
    serena_mix = game.mixed_nash_equilibrium(opponent)

    assert venus_mix[0] == pytest.approx(0.7)
    assert venus_mix[1] == pytest.approx(0.3)
    assert serena_mix[0] == pytest.approx(0.6)
    assert serena_mix[1] == pytest.approx(0.4)
    assert game.player.strategy_set_size() == 2
    assert game.opponent.strategy_set_size() == 2


def test_taxpayer_mixed_nash():
    player = Player("Auditor", "(2, 4), (4, 0)")
    opponent = Opponent("TaxPayers", "(0, 0), (-10, 4)")
    game = Game(player, opponent)

    auditor_mix = game.mixed_nash_equilibrium(player)
    taxpayers_mix = game.mixed_nash_equilibrium(opponent)

    assert auditor_mix[0] == pytest.approx(2 / 7)
    assert auditor_mix[1] == pytest.approx(5 / 7)
    assert taxpayers_mix[0] == pytest.approx(2 / 3)
    assert taxpayers_mix[1] == pytest.approx(1 / 3)


def test_ieds_copy_preserves_original_and_1x1_is_pure():
    player = Player("P", "(-2, -10), (0, -5)")
    opponent = Opponent("O", "(-2, -10), (0, -5)")
    game = Game(player, opponent)

    reduced = game.copy()
    reduced.solve_by_iterated_deletion(use_weakly=False)

    assert game.player.strategy_set_size() == 2
    assert game.opponent.strategy_set_size() == 2
    assert reduced.player.strategy_set_size() == 1
    assert reduced.opponent.strategy_set_size() == 1
    assert reduced.mixed_nash_equilibrium(reduced.player) == (1.0,)
    assert reduced.mixed_nash_equilibrium(reduced.opponent) == (1.0,)


def test_all_entries_equal():
    list = ("a", "a", "a")
    assert all_entries_equal(list) == True

    list = ("a", "a", "b")
    assert all_entries_equal(list) == False


def test_pure_nash_prisoners_dilemma():
    player = Player("P", "(-2, -10), (0, -5)")
    opponent = Opponent("O", "(-2, -10), (0, -5)")
    game = Game(player, opponent)
    equilibria = game.pure_nash_equilibrium()
    assert len(equilibria) == 1
    assert equilibria[0][0] is player.strategy(1)
    assert equilibria[0][1] is opponent.strategy(1)


def test_pure_nash_battle_of_the_sexes():
    player = Player("P", "(2, 0, 0), (0, 1, 0), (-1, -1, -2)")
    opponent = Opponent("O", "(1, 0, 0), (0, 2, 0), (-1, -1, -2)")
    game = Game(player, opponent)
    equilibria = game.pure_nash_equilibrium()
    names = {(row.name, col.name) for row, col in equilibria}
    assert names == {("P_S0", "O_S0"), ("P_S1", "O_S1")}


def test_mismatched_payoff_dimensions():
    player = Player("P", "(1, 0), (0, 1)")
    opponent = Opponent("O", "(1, 0, 0), (0, 1, 0)")
    with pytest.raises(ValueError, match="opponent payoffs"):
        Game(player, opponent)


def test_strategy_prefix():
    player = Player("P", "(1, 0), (0, 1)", strategy_prefix="Row")
    assert player.strategy(0).name == "Row0"
    assert player.name == "P"


def test_rps_mixed_nash():
    player = Player("P", "(0, 1, -1), (-1, 0, 1), (1, -1, 0)")
    opponent = Opponent("O", "(0, 1, -1), (-1, 0, 1), (1, -1, 0)")
    game = Game(player, opponent)
    player_mix = game.mixed_nash_equilibrium(player)
    opponent_mix = game.mixed_nash_equilibrium(opponent)
    assert player_mix == pytest.approx((1 / 3, 1 / 3, 1 / 3))
    assert opponent_mix == pytest.approx((1 / 3, 1 / 3, 1 / 3))


def test_battle_of_the_sexes_mixed_on_full_matrix():
    player = Player("P", "(2, 0, 0), (0, 1, 0), (-1, -1, -2)")
    opponent = Opponent("O", "(1, 0, 0), (0, 2, 0), (-1, -1, -2)")
    game = Game(player, opponent)
    mixed = game.mixed_nash_equilibria()
    assert len(mixed) >= 1
    player_mix, opponent_mix = mixed[0]
    assert player_mix[2] == pytest.approx(0)
    assert opponent_mix[2] == pytest.approx(0)
    assert player_mix[0] == pytest.approx(2 / 3)
    assert player_mix[1] == pytest.approx(1 / 3)
    assert opponent_mix[0] == pytest.approx(1 / 3)
    assert opponent_mix[1] == pytest.approx(2 / 3)


def test_sharing_4x4_enumerates_without_size_limit():
    player = Player(
        "P", "(3, 3, 8, 8), (3, 3, 8, 8), (5, 2, 5, 2), (5, 1, 5, 1)"
    )
    opponent = Opponent(
        "O", "(8, 8, 5, 5), (8, 8, 10, 0), (3, 3, 5, 5), (3, 3, 10, 0)"
    )
    game = Game(player, opponent)
    equilibria = game.nash_equilibria()
    assert len(equilibria) >= 3
    for player_mix, opponent_mix in equilibria:
        assert sum(player_mix) == pytest.approx(1)
        assert sum(opponent_mix) == pytest.approx(1)
        assert len(player_mix) == 4
        assert len(opponent_mix) == 4
    fallback = game.mixed_nash_equilibrium(player)
    assert len(fallback) == 4
    assert sum(fallback) == pytest.approx(1)


def test_4x4_embedded_tennis_mixed_ne():
    player = Player(
        "Venus",
        "(50, 80, -100, -100), (90, 20, -100, -100), (-200, -200, -200, -200), (-200, -200, -200, -200)",
    )
    opponent = Opponent(
        "Serena",
        "(50, 10, 100, 100), (20, 80, 100, 100), (-200, -200, -200, -200), (-200, -200, -200, -200)",
    )
    game = Game(player, opponent)
    mixed = game.mixed_nash_equilibria()
    assert len(mixed) >= 1
    player_mix, opponent_mix = next(
        (p, q)
        for p, q in mixed
        if p[0] > 0.5 and p[1] > 0.2 and q[0] > 0.5
    )
    assert player_mix[0] == pytest.approx(0.7)
    assert player_mix[1] == pytest.approx(0.3)
    assert player_mix[2] == pytest.approx(0)
    assert player_mix[3] == pytest.approx(0)
    assert opponent_mix[0] == pytest.approx(0.6)
    assert opponent_mix[1] == pytest.approx(0.4)


def test_williams_import_has_no_stdout(capsys):
    import importlib
    import williams

    importlib.reload(williams)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_williams_constant_sum_tennis():
    player = Player("Venus", "(50, 80), (90, 20)")
    opponent = Opponent("Serena", "(50, 10), (20, 80)")
    game = Game(player, opponent)
    assert game.is_constant_sum()
    row_mix, col_mix, _value = game.williams_mixed_equilibrium(iterations=2000)
    assert row_mix[0] == pytest.approx(0.7, abs=0.05)
    assert col_mix[0] == pytest.approx(0.6, abs=0.05)


def test_load_tennis_ini():
    game = load_game("games/tennis.ini")
    assert game.player.name == "Venus"
    assert game.opponent.name == "Serena"
    assert game.player.strategy(0).name == "Venus_S0"
    venus_mix = game.mixed_nash_equilibrium(game.player)
    serena_mix = game.mixed_nash_equilibrium(game.opponent)
    assert venus_mix[0] == pytest.approx(0.7)
    assert serena_mix[0] == pytest.approx(0.6)


def test_load_default_ini_honors_strategy_prefix():
    game = load_game("games/default.ini")
    assert game.player.name == "P"
    assert game.player.strategy(0).name == "S0"
    assert game.opponent.strategy(0).name == "S0"


def test_load_ini_without_names_uses_fallbacks():
    game = load_game("games/prisoners_dilemma.ini")
    assert game.player.name == "P"
    assert game.opponent.name == "O"
    assert game.player.strategy(0).name == "P_S0"


def test_load_game_does_not_overlay_default_payoffs(tmp_path):
    config = tmp_path / "partial.ini"
    config.write_text(
        "[names]\n"
        "player = Alice\n"
        "opponent = Bob\n"
        "[payoffs]\n"
        "player = (1, 0), (0, 1)\n"
        "opponent = (1, 0), (0, 1)\n"
    )
    game = load_game(str(config))
    assert game.player.name == "Alice"
    assert game.opponent.name == "Bob"
    assert game.player.strategy(0).payoffs == [1.0, 0.0]


def test_load_missing_ini():
    with pytest.raises(FileNotFoundError):
        load_game("games/does_not_exist.ini")


def test_game_setup_reads_c_flag():
    game, args = game_setup(["-c", "games/tennis.ini"])
    assert game.player.name == "Venus"
    assert args.use_weakly is False
    assert args.zero_sum is False
    assert args.lemke_howson is False


def test_lemke_howson_tennis():
    from lemke_howson import lemke_howson

    player = Player("Venus", "(50, 80), (90, 20)")
    opponent = Opponent("Serena", "(50, 10), (20, 80)")
    game = Game(player, opponent)
    row_mix, col_mix = game.lemke_howson_equilibrium(0)
    assert row_mix[0] == pytest.approx(0.7)
    assert row_mix[1] == pytest.approx(0.3)
    assert col_mix[0] == pytest.approx(0.6)
    assert col_mix[1] == pytest.approx(0.4)

    # every starting label reaches the unique mixed NE
    for drop_label in range(4):
        row_mix, col_mix = lemke_howson(
            [[50, 80], [90, 20]], [[50, 20], [10, 80]], drop_label
        )
        assert row_mix[0] == pytest.approx(0.7)
        assert col_mix[0] == pytest.approx(0.6)


def test_lemke_howson_prisoners_dilemma():
    player = Player("P", "(-2, -10), (0, -5)")
    opponent = Opponent("O", "(-2, -10), (0, -5)")
    game = Game(player, opponent)
    equilibria = game.lemke_howson_equilibria()
    assert len(equilibria) == 1
    assert equilibria[0][0] == pytest.approx((0.0, 1.0))
    assert equilibria[0][1] == pytest.approx((0.0, 1.0))


def test_lemke_howson_rps_and_taxpayer():
    player = Player("P", "(0, 1, -1), (-1, 0, 1), (1, -1, 0)")
    opponent = Opponent("O", "(0, 1, -1), (-1, 0, 1), (1, -1, 0)")
    game = Game(player, opponent)
    row_mix, col_mix = game.lemke_howson_equilibrium()
    assert row_mix == pytest.approx((1 / 3, 1 / 3, 1 / 3))
    assert col_mix == pytest.approx((1 / 3, 1 / 3, 1 / 3))

    player = Player("Auditor", "(2, 4), (4, 0)")
    opponent = Opponent("TaxPayers", "(0, 0), (-10, 4)")
    game = Game(player, opponent)
    row_mix, col_mix = game.lemke_howson_equilibrium()
    assert row_mix[0] == pytest.approx(2 / 7)
    assert col_mix[0] == pytest.approx(2 / 3)


def test_lemke_howson_drop_label_implies_flag():
    _, args = game_setup(["-c", "games/tennis.ini", "--drop-label", "1"])
    assert args.lemke_howson is True
    assert args.drop_label == 1
