from project import Player, Opponent, Game, all_entries_equal, is_biggest_in_list


def test_is_biggest_in_list():
    assert is_biggest_in_list(2, (2, 2, 0)) == True
    assert is_biggest_in_list(0, (2, 2, 0)) == False


def test_prison_dilema():
    player = Player("(10, 1), (25, 3)")
    opponent = Opponent("(10, 1), (25, 3)")

    game = Game(player, opponent)
    print(game)

    assert f"{game.strictly_dominating_strategy(0,1)}" == "P_S1 [25, 3]"
    assert f"{game.strictly_dominating_strategy(1,0)}" == "O_S1 [25, 3]"

    assert f"{game.strictly_dominated_strategy(0,1)}" == "P_S0 [10, 1]"
    assert f"{game.strictly_dominated_strategy(1,0)}" == "O_S0 [10, 1]"


def test_weakly_dominated_strategy():
    player = Player("(10, 1), (10, 1)")
    result_list = [player.strategy(1), player.strategy(0)]
    assert player.weakly_domiated_strategy() == result_list

    player = Player("(10, 1), (10, 2)")
    result_list = [player.strategy(0)]
    assert player.weakly_domiated_strategy() == result_list

    player = Player("(10, 1), (1, 10)")
    result_list = []
    assert player.weakly_domiated_strategy() == result_list


def test_strictly_dominated_strategy():
    player = Player("(11, 2), (10, 1)")
    result_list = [player.strategy(1)]
    assert player.strictly_dominated_strategy() == result_list

    player = Player("(10, 1), (1, 10)")
    assert player.strictly_dominated_strategy() == []


def test_all_entries_equal():
    list = ("a", "a", "a")
    assert all_entries_equal(list) == True

    list = ("a", "a", "b")
    assert all_entries_equal(list) == False
