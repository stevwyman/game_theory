from game import Game, Player, Opponent, Strategy
from sys import exit
import os
import configparser
import argparse


def main(argv=None):
    game, args = game_setup(argv)

    # show the initial payoff matrix
    print("Commencing analysis of the following game/payoff matrix:")
    print(game)

    print("Analysing strict dominance ...")

    p_sds: list[Strategy] = game.player.strictly_dominated_strategy()
    if len(p_sds) > 0:
        print(f"   player has {len(p_sds)} strictly dominated strategies:")
        for strategy in p_sds:
            print("      ", strategy.name)
    else:
        print("   player has no strictly dominated strategies")

    p_strictly_dominant_strategies: list[Strategy] = (
        game.player.strictly_dominant_strategy()
    )
    if len(p_strictly_dominant_strategies) > 0:
        print(
            f"   player has {len(p_strictly_dominant_strategies)} strictly dominant strategies:"
        )
        for strategy in p_strictly_dominant_strategies:
            print("      ", strategy.name)
    else:
        print("   player has no strictly dominant strategies")

    o_sds: list[Strategy] = game.opponent.strictly_dominated_strategy()
    if len(o_sds) > 0:
        print(f"   opponent has {len(o_sds)} strictly dominated strategies:")
        for strategy in o_sds:
            print("      ", strategy.name)
    else:
        print("   opponent has no strictly dominated strategies")

    o_strictly_dominant_strategies: list[Strategy] = (
        game.opponent.strictly_dominant_strategy()
    )
    if len(o_strictly_dominant_strategies) > 0:
        print(
            f"   opponent has {len(o_strictly_dominant_strategies)} strictly dominant strategies:"
        )
        for strategy in o_strictly_dominant_strategies:
            print("      ", strategy.name)
    else:
        print("   opponent has no strictly dominant strategies")

    print("Analysing weak dominance ...")

    p_wds: list[Strategy] = game.player.weakly_dominated_strategy()
    if len(p_wds) > 0:
        print(f"   player has {len(p_wds)} weakly dominated strategies:")
        for strategy in p_wds:
            print("      ", strategy.name)
    else:
        print("   player has no weakly dominated strategies")

    p_weakly_dominant_strategy: list[Strategy] = game.player.weakly_dominant_strategy()
    if len(p_weakly_dominant_strategy) > 0:
        print(
            f"   player has {len(p_weakly_dominant_strategy)} weakly dominant strategies:"
        )
        for strategy in p_weakly_dominant_strategy:
            print("      ", strategy.name)
    else:
        print("   player has no weakly dominant strategies")

    o_wds: list[Strategy] = game.opponent.weakly_dominated_strategy()
    if len(o_wds) > 0:
        print(f"   opponent has {len(o_wds)} weakly dominated strategies:")
        for strategy in o_wds:
            print("      ", strategy.name)
    else:
        print("   opponent has no weakly dominated strategies")

    o_weakly_dominant_strategy: list[Strategy] = (
        game.opponent.weakly_dominant_strategy()
    )
    if len(o_weakly_dominant_strategy) > 0:
        print(
            f"   opponent has {len(o_weakly_dominant_strategy)} weakly dominant strategies:"
        )
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

    # IEDS mutates the matrix, so shrink a copy and keep the original game intact
    print()

    print("Conducting iterated deletion of dominated, strategies ...")
    if args.use_weakly:
        print("... including weakly dominated strategies ...")
    reduced = game.copy()
    reduced.solve_by_iterated_deletion(use_weakly=args.use_weakly)

    # print the resulting payoff matrix
    print()
    print(reduced)

    print()
    print("Looking for mixed NE ...")
    if (
        reduced.player.strategy_set_size() < 2
        or reduced.opponent.strategy_set_size() < 2
    ):
        print(
            "IEDS reduced the game to a unique remaining profile; "
            "that cell is a pure NE, so no mixed strategy is needed."
        )
        if (
            reduced.player.strategy_set_size() == 1
            and reduced.opponent.strategy_set_size() == 1
        ):
            print(
                f"   {reduced.player.strategy(0).name} vs {reduced.opponent.strategy(0).name}"
            )
        return

    if args.zero_sum:
        _print_williams_mix(reduced)
        return

    if args.lemke_howson:
        _print_lemke_howson_mix(reduced, args.drop_label)
        return

    _print_support_enumeration_mix(reduced)


def _print_williams_mix(game: Game) -> None:
    if not game.is_constant_sum():
        print(
            "Williams fictitious play is for zero-sum / constant-sum games; "
            "this payoff matrix is not constant-sum. Falling back to support enumeration."
        )
        _print_support_enumeration_mix(game)
        return

    print("Using Williams fictitious play (zero-sum / constant-sum approximation) ...")
    try:
        player_mix, opponent_mix, value = game.williams_mixed_equilibrium()
    except ValueError as ve:
        print(ve)
        exit(0)

    print(f"Approximate value of the game (row player): {value}")
    _print_mix(game, player_mix, opponent_mix)


def _print_lemke_howson_mix(game: Game, drop_label) -> None:
    print("Using Lemke–Howson complementary pivoting ...")
    try:
        if drop_label is None:
            equilibria = game.lemke_howson_equilibria()
        else:
            equilibria = [game.lemke_howson_equilibrium(drop_label)]
    except ValueError as ve:
        print(ve)
        exit(0)

    if not equilibria:
        print("... Lemke–Howson did not find an equilibrium.")
        return

    print(f"Found {len(equilibria)} NE (Lemke–Howson):")
    for index, (player_mix, opponent_mix) in enumerate(equilibria, start=1):
        if len(equilibria) > 1:
            print(f"Mix {index}")
        _print_mix(game, player_mix, opponent_mix)


def _print_support_enumeration_mix(game: Game) -> None:
    try:
        mixed = game.mixed_nash_equilibria()
    except ValueError as ve:
        print(ve)
        exit(0)

    if not mixed:
        print(
            "... no mixed Nash equilibrium identified "
            "(remaining equilibria are pure)."
        )
        return

    print(f"Found {len(mixed)} mixed NE (support enumeration):")
    for index, (player_mix, opponent_mix) in enumerate(mixed, start=1):
        if len(mixed) > 1:
            print(f"Mix {index}")
        _print_mix(game, player_mix, opponent_mix)


def _print_mix(game: Game, player_mix, opponent_mix) -> None:
    print(f"Mix for player")
    for i, probability in enumerate(player_mix):
        print(
            f"   {game.player} should mix {game.player.strategy(i)} with {probability:.0%}"
        )
    print(f"Mix for opponent")
    for j, probability in enumerate(opponent_mix):
        print(
            f"   {game.opponent} should mix {game.opponent.strategy(j)} with {probability:.0%}"
        )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Solve payoff matrices")
    parser.add_argument(
        "--use_weakly",
        action="store_true",
        help="also delete weakly dominated strategies during iterated deletion; this may drop some NE",
    )
    parser.add_argument(
        "--zero-sum",
        dest="zero_sum",
        action="store_true",
        help="approximate mixed strategies with Williams fictitious play (zero-sum / constant-sum games)",
    )
    parser.add_argument(
        "--lemke-howson",
        dest="lemke_howson",
        action="store_true",
        help="find Nash equilibria with the Lemke–Howson complementary pivoting algorithm",
    )
    parser.add_argument(
        "--drop-label",
        type=int,
        default=None,
        metavar="K",
        help="Lemke–Howson starting label (default: try every label). Implies --lemke-howson.",
    )
    parser.add_argument(
        "-c",
        type=str,
        help="path to the *.ini file holding the payoffs (default: games/default.ini)",
    )
    args = parser.parse_args(argv)
    if args.drop_label is not None:
        args.lemke_howson = True
    return args


def load_game(config_path: str) -> Game:
    """Load a single INI file. Missing names/strategy prefixes use built-in defaults."""
    config = configparser.ConfigParser()
    loaded = config.read(config_path)
    if len(loaded) != 1:
        raise FileNotFoundError(f"{config_path} could not be found")

    player_payoffs = config.get("payoffs", "player")
    opponent_payoffs = config.get("payoffs", "opponent")
    player_name = config.get("names", "player", fallback="P")
    opponent_name = config.get("names", "opponent", fallback="O")
    player_prefix = config.get(
        "strategies", "player", fallback=f"{player_name}_S"
    )
    opponent_prefix = config.get(
        "strategies", "opponent", fallback=f"{opponent_name}_S"
    )

    player = Player(player_name, player_payoffs, strategy_prefix=player_prefix)
    opponent = Opponent(
        opponent_name, opponent_payoffs, strategy_prefix=opponent_prefix
    )
    return Game(player, opponent)


def game_setup(argv=None) -> tuple[Game, argparse.Namespace]:
    args = parse_args(argv)
    config_path = args.c if args.c else os.path.join(".", "games", "default.ini")
    try:
        game = load_game(config_path)
    except (OSError, ValueError, configparser.Error) as error:
        exit(error)
    return game, args


if __name__ == "__main__":
    main()
