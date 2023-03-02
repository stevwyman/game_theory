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

    game = Game(player, opponent)

    assert f"{game.strictly_dominating_strategy(0,1)}" == "P_S1 [25, 3]"
    assert f"{game.strictly_dominating_strategy(1,0)}" == "O_S1 [25, 3]"

    assert f"{game.strictly_dominated_strategy(0,1)}" == "P_S0 [10, 1]"
    assert f"{game.strictly_dominated_strategy(1,0)}" == "O_S0 [10, 1]"


def test_weakly_dominated_strategy():
    player = Player("P", "(10, 1), (10, 1)")
    result_list = [player.strategy(1), player.strategy(0)]
    assert player.weakly_dominated_strategy() == result_list

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


def test_all_entries_equal():
    list = ("a", "a", "a")
    assert all_entries_equal(list) == True

    list = ("a", "a", "b")
    assert all_entries_equal(list) == False
