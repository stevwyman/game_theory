from game import Game, Player, Opponent, Strategy
from sys import exit
import os
import configparser
import argparse

use_weakly = False
PATH = os.path.dirname("games")


def main():
    game = game_setup()

    # show the initial payoff matrix
    print("Commencing analysis of the following game/payoff matrix:")
    print(game)

    print("Analysing strict dominance ...")

    p_sds: list[Strategy] = game.player.strictly_dominated_strategy();
    if len(p_sds) > 0:
        print(f"   player has {len(p_sds)} strictly dominated strategies:")
        for strategy in p_sds:
            print("      ", strategy.name)
    else:
        print("   player has no strictly dominated strategies")

    p_strictly_dominant_strategies: list[Strategy] = game.player.strictly_dominant_strategy();
    if len(p_strictly_dominant_strategies) > 0:
        print(f"   player has {len(p_strictly_dominant_strategies)} strictly dominant strategies:")
        for strategy in p_strictly_dominant_strategies:
            print("      ", strategy.name)
    else:
        print("   player has no strictly dominant strategies")

    o_sds: list[Strategy] = game.opponent.strictly_dominated_strategy();
    if len(o_sds) > 0:
        print(f"   opponent has {len(o_sds)} strictly dominated strategies:")
        for strategy in o_sds:
            print("      ", strategy.name)
    else:
        print("   opponent has no strictly dominated strategies")

    o_strictly_dominant_strategies: list[Strategy] = game.opponent.strictly_dominant_strategy();
    if len(o_strictly_dominant_strategies) > 0:
        print(f"   opponent has {len(o_strictly_dominant_strategies)} strictly dominant strategies:")
        for strategy in o_strictly_dominant_strategies:
            print("      ", strategy.name)
    else:
        print("   opponent has no strictly dominant strategies")

    print("Analysing weak dominance ...")

    p_wds: list[Strategy] = game.player.weakly_dominated_strategy();
    if len(p_wds) > 0:
        print(f"   player has {len(p_wds)} weakly dominated strategies:")
        for strategy in p_wds:
            print("      ", strategy.name)
    else:
        print("   player has no weakly dominated strategies")

    p_weakly_dominant_strategy: list[Strategy] = game.player.weakly_dominant_strategy();
    if len(p_weakly_dominant_strategy) > 0:
        print(f"   player has {len(p_weakly_dominant_strategy)} weakly dominant strategies:")
        for strategy in p_weakly_dominant_strategy:
            print("      ", strategy.name)
    else:
        print("   player has no weakly dominant strategies")

    o_wds: list[Strategy] = game.opponent.weakly_dominated_strategy();
    if len(o_wds) > 0:
        print(f"   opponent has {len(o_wds)} weakly dominated strategies:")
        for strategy in o_wds:
            print("      ", strategy.name)
    else:
        print("   opponent has no weakly dominated strategies")

    o_weakly_dominant_strategy: list[Strategy] = game.opponent.weakly_dominant_strategy();
    if len(o_weakly_dominant_strategy) > 0:
        print(f"   opponent has {len(o_weakly_dominant_strategy)} weakly dominant strategies:")
        for strategy in o_weakly_dominant_strategy:
            print("      ", strategy.name)
    else:
        print("   opponent has no weakly dominant strategies")      

    print()
    try:
        nash_equilibria: list = game.pure_nash_equilibrium()
    except IndexError as ie:
        print("Error while looking for pure NE: ", ie)
        nash_equilibria = list()
    if len(nash_equilibria) > 0:
        print(f"Found {len(nash_equilibria)} pure NE:")
        for ne in nash_equilibria:
            print(f"   at {ne[0].name} and {ne[1].name}")
    else:
        print("No pure Nash Equilibrium identified.")

    # try solving by iterated deletion
    print()

    print("Conducting iterated deletion of dominated, strategies ...")
    if use_weakly:
        print("... including weakly dominated strategies ...")
    game.solve_by_iterated_deletion(use_weakly=use_weakly)

    # print the resulting payoff matrix
    print()
    print(game)

    print()
    print("Looking for mixed NE ...")
    try:
        player_mix: list[float] = game.mixed_nash_equilibrium(game.player)
        opponent_mix: list[float] = game.mixed_nash_equilibrium(game.opponent)
    except ValueError as ve:
        print(ve)
        exit(0)

    if len(player_mix) > 0 and len(opponent_mix) > 0:
        print(f"Mix for player")
        for i in range(len(player_mix)):
            print(
                f"   {game.player} should mix {game.player.strategy(i)} with {player_mix[i]:.0%}"
            )
        print(f"Mix for opponent")
        for j in range(len(opponent_mix)):
            print(
                f"   {game.opponent} should mix {game.opponent.strategy(j)} with {opponent_mix[j]:.0%}"
            )
    else:
        print("... no mixed strategies identified")


def game_setup() -> Game:
    parser = argparse.ArgumentParser(description="Solve payoff matrices")
    parser.add_argument(
        "--use_weakly",
        action="store_true",
        help="use also weakly dominated strategies when using iterate deletion, note that this method might not find all NE",
    )
    parser.add_argument(
        "-c",
        type=str,
        help="path to the *.ini file holding the payoffs, should be located in a folder called games",
    )
    args = parser.parse_args()

    global use_weakly
    use_weakly = args.use_weakly

    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(".", "games", "default.ini"))
        if args.c:
            dataset = config.read(os.path.join(".", args.c))
            if len(dataset) != 1:
                exit(f"{args.c} could not be found")

        # init player
        player_payoffs = config.get("payoffs", "player")
        player_name = config.get("names", "player")
        player = Player(player_name, player_payoffs)

        # init opponent
        opponent_payoffs = config.get("payoffs", "opponent")
        opponent_name = config.get("names", "opponent")
        opponent = Opponent(opponent_name, opponent_payoffs)

    except BaseException as be:
        exit(be)

    # init the game
    return Game(player, opponent)


if __name__ == "__main__":
    main()
