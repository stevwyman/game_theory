from tabulate import tabulate  # table pretty
from typing import Optional  # annotation
from sys import exit
import configparser
import argparse


class Strategy:
    """
    a strategy has a name and some payoffs in form of a list
    """

    def __init__(self, name: str, payoffs: list[int]):
        """
        initialise a new strategy by providing a name and the list of payoffs
        """
        self._name = name
        self._payoffs = payoffs

    def __str__(self):
        """
        simply return the name and the payoffs for this strategy
        """
        return f"{self._name} {self._payoffs}"

    # https://stackoverflow.com/questions/46406165/str-method-not-working-when-objects-are-inside-a-list-or-dict
    __repr__ = __str__

    @property
    def name(self) -> str:
        """
        return the name of this strategy
        """
        return self._name

    @property
    def payoffs(self) -> list[int]:
        """
        returns a list of the payoffs
        """
        return self._payoffs

    def payoff(self, index: int) -> int:
        """
        returns the payoff for this stratehy given the index, hence the opponents strategy
        """
        return self._payoffs[index]


class DefaultPlayer:
    """
    a player has a name and a set of strategies
    """

    def __init__(self, name: str, payoffs_str: str):
        """
        initialises a new player with the specified name and payoffs
        in addition a set of strategies is constructed from those payoffs

        """

        self._name = name
        self._strategy_set = list()

        if type(payoffs_str) != str:
            raise ValueError("payoffs need to be a string in form (a, b), (c, d)")

        try:
            strategy_sets = payoffs_str.replace("(", "").split(")")

            for n in range(len(strategy_sets) - 1):
                payoffs_str_list = strategy_sets[n].strip().split(",")
                payoffs = list()
                for payoff in payoffs_str_list:
                    payoff = payoff.strip()
                    if payoff != None and payoff != "":
                        payoffs.append(int(payoff))
                strategy = Strategy(name + "_S" + str(n), payoffs)
                self._strategy_set.append(strategy)
                n += 1

        except BaseException as be:
            raise BaseException(
                f"Error while parsing payoffs for {name}: {payoffs_str}"
            )

    def __str__(self):
        """
        simply returns the name of the player
        """
        return self._name

    @property
    def strategy_set(self) -> list:
        """
        returns the strategy set for this player
        """
        return self._strategy_set

    def strategy(self, index: int) -> Strategy:
        """
        returns the strategy from the set given the index
        """
        return self._strategy_set[index]

    def remove_strategy(self, strategy: Strategy) -> int:
        """
        this method should only be called by the game class to ensure
        the other players payoffs are also updated
        """
        index = self._strategy_set.index(strategy)
        self._strategy_set.remove(strategy)
        return index

    def strategy_set_size(self) -> int:
        return len(self._strategy_set)

    def weakly_domiated_strategy(self) -> list[Strategy]:
        """
        Weakly dominated strategy: This is a strategy that delivers an equal or worse outcome than an alternative strategy.

        :return: a list holding all the weakly dominated strategies for this player
        :rtype: list
        """
        # is any of the strategies always better than <b>one</b> of the other strategies
        # check each against all others
        payoffs_per_strategy = len(self._strategy_set[0].payoffs)
        available_strategies = self._strategy_set
        weakly_dominated_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return weakly_dominated_strategies

        # select one of the strategies
        for strategy_source in available_strategies:
            # selct one of the others
            for strategy_target in available_strategies:
                # if they are not the same ...
                if strategy_target != strategy_source:
                    # go through all of the iterations ...
                    winner_count = 0
                    for p in range(payoffs_per_strategy):
                        # get the payoff for this iteration
                        payoff_for_strategy_source = strategy_source.payoff(p)
                        payoff_for_strategy_taregt = strategy_target.payoff(p)
                        # .. compare their payoffs
                        # print(f' comparing: {strategy_source}{payoff_for_strategy_source} vs {strategy_target}{payoff_for_strategy_taregt}')
                        if payoff_for_strategy_source >= payoff_for_strategy_taregt:
                            # print(f'          source better than target')
                            winner_count += 1
                    if winner_count == payoffs_per_strategy:
                        # print(f'  {strategy_source} always beats {strategy_target}')
                        weakly_dominated_strategies.append(strategy_target)

        return weakly_dominated_strategies

    def strictly_dominated_strategy(self) -> list[Strategy]:
        """
        Strictly dominated strategy: This is a strategy that always delivers a worse outcome than an alternative strategy, regardless of what strategy the opponent chooses.
        """
        payoffs_per_strategy = len(self._strategy_set[0].payoffs)
        available_strategies = self._strategy_set
        strictly_dominated_strategies: list[Strategy] = list()

        if len(available_strategies) < 2:
            return strictly_dominated_strategies

        # this list will hold the strategies, which are best responses to each of the opponents strategies
        worst_responses = []

        # list of lists holding the responses
        responses = []

        for o in range(payoffs_per_strategy):
            results = []
            for p in range(len(available_strategies)):
                # create the result tupel, hence strategy and payoff
                result = (self.strategy(p), self.strategy(p).payoff(o))
                # add to the list of results against opponent strategy o
                results.append(result)

            responses.append(results)
            # sort by payoff and then get the strategy object from the minimum tupel ...
            worst_result = min(results, key=lambda item: item[1])[0]
            # ... and add that strategy to the best responses
            worst_responses.append(worst_result)

        if all_entries_equal(worst_responses):
            strictly_dominated_strategies.append(worst_responses[0])

        return strictly_dominated_strategies


class Player(DefaultPlayer):
    def __init__(self, name, payoffs):
        super().__init__(name, payoffs)


class Opponent(DefaultPlayer):
    def __init__(self, name, payoffs):
        super().__init__(name, payoffs)


class Game:
    def __init__(self, player: Player, opponent: Player):
        self._player = player
        self._opponent = opponent
        self._players = [self._player, self._opponent]

    def __str__(self):
        player = self._players[0]
        opponent = self._players[1]

        header = []
        for strategy in opponent.strategy_set:
            header.append(strategy.name)

        data = []
        for p in range(len(player.strategy_set)):
            strategy_p = player.strategy(p)
            tpp = []
            tpp.append(strategy_p.name)
            for o in range(len(opponent.strategy_set)):
                strategy_o = opponent.strategy(o)
                tp = f"({strategy_p.payoff(o)} | {strategy_o.payoff(p)})"
                tpp.append(tp)
            data.append(tpp)

        return tabulate(data, header, tablefmt="grid", stralign="center")

    def strictly_dominating_strategy(
        self, player_index: int, opponent_index: int
    ) -> Optional[Strategy]:
        """
        :return: if found, a strictly dominated strategy
        :rtype: Strategy
        """
        player = self._players[player_index]
        opponent = self._players[opponent_index]

        # this list will hold the strategies, which are best responses to each of the opponents strategies
        best_responses = []

        for o in range(len(opponent.strategy_set)):
            results = []
            for p in range(len(player.strategy_set)):
                # create the result tupel, hence strategy and payoff
                result = (player.strategy(p), player.strategy(p).payoff(o))
                # add to the list of results against opponent strategy o
                results.append(result)

            # get the strategy which has the highest payoff ...
            best_result = max(results, key=lambda item: item[1])[0]
            # ... and add that strategy to the best responses
            best_responses.append(best_result)

        if all_entries_equal(best_responses):
            return best_responses[0]
        else:
            return None

    def strictly_dominated_strategy(
        self, player_index: int, opponent_index: int
    ) -> Optional[Strategy]:
        """

        :return: the strictly dominated strategy if found, None else
        :rtype: Strategy
        """
        player = self._players[player_index]
        opponent = self._players[opponent_index]

        # this list will hold the strategies, which are best responses to each of the opponents strategies
        worst_responses = []

        # list of lists holding the responses
        responses = []

        for o in range(len(opponent.strategy_set)):
            results = []
            for p in range(len(player.strategy_set)):
                # create the result tupel, hence strategy and payoff
                result = (player.strategy(p), player.strategy(p).payoff(o))
                # add to the list of results against opponent strategy o
                results.append(result)

            responses.append(results)
            # sort by payoff and then get the strategy obejt from the minimum tupel ...
            worst_result = min(results, key=lambda item: item[1])[0]
            # ... and add that strategy to the best responses
            worst_responses.append(worst_result)

        if all_entries_equal(worst_responses):
            return worst_responses[0]
        else:
            return None

    @property
    def players(self):
        return self._players

    def pure_nash_equilibrium(self) -> list[tuple[Strategy, Strategy]]:
        """
        checks for pure nash equilibria

        :return: if found, a list of NE in form of a tup containg the strategy names
        :rtype: list
        """

        nash_equilibria: list[tuple[Strategy, Strategy]] = list()

        opponent_strategy_set: list[Strategy] = self._opponent.strategy_set
        player_strategy_set: list[Strategy] = self._player.strategy_set

        # result_matrix holding either true = best response, of false otherweise
        player_startegy_size: int = self._player.strategy_set_size()
        opponent_strategy_size: int = self._opponent.strategy_set_size()

        result_matrix = []
        for p in range(player_startegy_size):
            inner_list = []
            for o in range(opponent_strategy_size):
                entry = []
                entry.append(player_strategy_set[p].payoff(o))
                entry.append(False)
                entry.append(opponent_strategy_set[o].payoff(p))
                entry.append(False)
                inner_list.append(entry)
            result_matrix.append(inner_list)

        # checking columns for best respose, hence comparing the first entries and setting the second
        for o in range(opponent_strategy_size):
            payoffs = []
            for p in range(player_startegy_size):
                # get each entry list
                payoffs.append(result_matrix[p][o][0])
            for p in range(player_startegy_size):
                result_matrix[p][o][1] = is_biggest_in_list(
                    result_matrix[p][o][0], payoffs
                )

        # checking now the rows for responses, hence checking the third entries and setting the fourth
        for p in range(player_startegy_size):
            payoffs = []
            for o in range(opponent_strategy_size):
                # get each entry list
                payoffs.append(result_matrix[p][o][2])
            for o in range(player_startegy_size):
                result_matrix[p][o][3] = is_biggest_in_list(
                    result_matrix[p][o][2], payoffs
                )

        # a nash equilibrium is a cell which has all entries set to true
        for p in range(player_startegy_size):
            for o in range(opponent_strategy_size):
                if result_matrix[p][o][1] and result_matrix[p][o][3]:
                    nash_equilibria.append(
                        (player_strategy_set[p], opponent_strategy_set[o])
                    )

        return nash_equilibria

    def solve_by_iterated_deletion(self, use_weakly=True) -> None:
        """
        note: when using "weakly", different outcomes are possible, so the one that the
        algorithm creates, might not be the only possible outcome - only one.
        """

        counter = 0
        while True:
            # check each player for strictly dominated strategies and delete them
            print(f"    iteration {counter}")
            further_check_required = False
            for player in self._players:
                sds = player.strictly_dominated_strategy()
                if len(sds) > 0:
                    for strategy in sds:
                        print(
                            f"... found strictly dominated strategy ({strategy}) and remove it now"
                        )
                        try:
                            self.remove_strategy(player, strategy)
                            further_check_required = True
                        except ValueError:
                            pass
                else:
                    if use_weakly:
                        # no strictly dominated strategy, so try weakly dominated strategy
                        wds = player.weakly_domiated_strategy()
                        if len(wds) > 0:
                            for strategy in wds:
                                print(
                                    f"... found weakly dominated strategy ({strategy}) and remove it now"
                                )
                                try:
                                    self.remove_strategy(player, strategy)
                                    further_check_required = True
                                except ValueError:
                                    pass

            # print(f"check completed, another check required: {further_check_required}")
            if further_check_required:
                # print("checking again")
                counter += 1
            else:
                print(f"... no further optimization found")
                break

    def mixed_strategy(self, player: Player) -> tuple[float, float]:
        """
        formular for solving 2x2 games
        """

        # we need the other player payoffs for our distribution
        player_index = self._players.index(player)
        other_player: Player
        if player_index == 0:
            other_player = self.players[1]
        else:
            other_player = self.players[0]

        mix = list()

        if other_player.strategy_set_size() == 2:
            bd = other_player.strategy(0).payoff(1) - other_player.strategy(1).payoff(1)
            ca = other_player.strategy(1).payoff(0) - other_player.strategy(0).payoff(0)

            q: float = bd / (ca + bd)

            mix.append(q)
            mix.append(1 - q)
        else:
            print("   only 2x2 games supported")

        return (q, 1 - q)

    def solve_by_oddment(self, player: Player) -> tuple[float, ...]:
        """ """
        # we need the other player payoffs for our distribution
        player_index = self._players.index(player)
        other_player: Player

        # we analyse for the player and therefore we use the opponents payoffs
        if player_index == 0:
            # the other player is the opponent
            other_player = self.players[1]
            # and hence we use his/hers strategy_set
            strategy_set = other_player.strategy_set
        else:
            other_player = self.players[0]
            strategy_set = other_player.strategy_set

        return oddments3(strategy_set)

    def remove_strategy(self, player: Player, strategy: Strategy) -> None:
        """
        removing a strategy means for the player to drop his/her strategy,
        but also to remove the payoffs for the opponent for that startegy
        """
        # get the index for the player, so we can clean up the other
        player_index = self._players.index(player)
        strategy_index = player.remove_strategy(strategy)
        if player_index == 0:
            other_player = self.players[1]
        else:
            other_player = self.players[0]

        for strategy in other_player.strategy_set:
            # print(f"payoffs: {strategy.payoffs}, need to remove {strategy_index}")
            strategy.payoffs.pop(strategy_index)


def main():
    parser = argparse.ArgumentParser(description="Solve payoff matrices")
    parser.add_argument(
        "--use_weakly",
        action="store_true",
        help="use also weak when using iterate deletion",
    )
    parser.add_argument(
        "-c", type=str, help="path to the *.ini file holding the payoffs"
    )
    args = parser.parse_args()

    USE_WEAKLY = args.use_weakly

    try:
        config = configparser.ConfigParser()
        config.read("default.ini")
        dataset = config.read(args.c)
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
    game = Game(player, opponent)

    # show the initial payoff matrix
    print("Commencing analysis of the following game/payoff matrix:")
    print(game)

    print()
    nash_equilibria: list = game.pure_nash_equilibrium()
    if len(nash_equilibria) > 0:
        for ne in nash_equilibria:
            print(f"Pure nash equilibrium at: {ne[0].name} and {ne[1].name}")
    else:
        print("No pure Nash Equilibrium identified")

    # try solving by iterated deletion
    print()

    print("Conduncting iterated deletion of dominated, strategies ...")
    if USE_WEAKLY:
        print("... including weakly dominated strategies ...")
    game.solve_by_iterated_deletion(use_weakly=USE_WEAKLY)

    # print the resulting payoff matrix
    print()
    print(game)

    print()
    print("Looking for mixed strategy equilibrium ...")
    try:
        if player.strategy_set_size() == 2:
            player_mix: list[float] = game.mixed_strategy(player)
            opponent_mix: list[float] = game.mixed_strategy(opponent)
        elif player.strategy_set_size() == 3:
            player_mix: list[float] = game.solve_by_oddment(player)
            opponent_mix: list[float] = game.solve_by_oddment(opponent)
        else:
            raise ValueError("Can only solve strategy sets of length 2 or 3")
    except ValueError as ve:
        print(ve)
        exit(0)

    if len(player_mix) > 0 and len(opponent_mix) > 0:
        print(f"Mix for player")
        for i in range(len(player_mix)):
            print(f"   player should mix {player.strategy(i)} with {player_mix[i]:.0%}")
        print(f"Mix for opponent")
        for j in range(len(opponent_mix)):
            print(
                f"   opponent should mix {opponent.strategy(j)} with {opponent_mix[j]:.0%}"
            )
    else:
        print("... no mixed stratgies identified")


def all_entries_equal(iterator) -> bool:
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == x for x in iterator)


def is_biggest_in_list(n: int, list: list) -> bool:
    return n == max(list)


def minimaxi(strategy_set: list[Strategy]) -> tuple[float, float]:
    """
    Methode to identfiy, if any, the saddle points of the provided strategy set
    if both values computed by the algorithm are the same, the saddle point is found
    """
    rows_minimums = list()
    for strategy in strategy_set:
        rows_payoffs = list()
        for payoff in strategy.payoffs:
            rows_payoffs.append(payoff)
        rows_minimums.append(min(rows_payoffs))

    columns_maximums = list()
    for column in range(len(strategy_set[0].payoffs)):
        column_payoffs = list()
        for strategy in strategy_set:
            column_payoffs.append(strategy.payoff(column))
        columns_maximums.append(max(column_payoffs))

    rows_max = max(rows_minimums)
    columns_min = min(columns_maximums)

    print(f"rows max = {rows_max} and columns min: {columns_min}")

    return (rows_max, columns_min)


def oddments2(strategy_set: list[Strategy]) -> tuple[float, float]:
    """
    Fiding the oddments of a strategy set with length 2
    :return: a tuple of the suggested distribution amongst the strategy set, should sum up to 1
    :rtype : tuple[float, foat]
    """
    if len(strategy_set) != 2:
        raise ValueError("Strategy set must have a length of 2")

    rows_oddments = list()
    rows_oddments.append(abs(strategy_set[1].payoff(0) - strategy_set[1].payoff(1)))
    rows_oddments.append(abs(strategy_set[0].payoff(0) - strategy_set[0].payoff(1)))
    rows_sum = sum(rows_oddments)

    print(f" running oddment_2 for {strategy_set} resulting in {rows_oddments}")

    return (rows_oddments[0] / rows_sum, rows_oddments[1] / rows_sum)


def oddments3(strategy_set: list[Strategy]) -> tuple[float, float, float]:
    """
    Fiding the oddments of a strategy set with length 3

    Using stratehy sets of length 3, the algorithm look a bit different, ass we need
    to first calculate the colum differences, and then use those to get the oddments

    :return: a tuple of the suggested distribution amongst the strategy set, should sum up to 1
    :rtype : tuple[float, foat, float]
    """
    if len(strategy_set) != 3:
        raise ValueError("Stratgy set must have a length of 3")

    c1c2 = list()
    c2c3 = list()
    for strategy in strategy_set:
        c1c2.append(strategy.payoff(0) - strategy.payoff(1))
        c2c3.append(strategy.payoff(1) - strategy.payoff(2))

    # no we build the oddments
    oddments = list()

    oddments.append(abs(c1c2[1] * c2c3[2] - c1c2[2] * c2c3[1]))
    oddments.append(abs(c1c2[0] * c2c3[2] - c1c2[2] * c2c3[0]))
    oddments.append(abs(c1c2[0] * c2c3[1] - c1c2[1] * c2c3[0]))
    oddments_sum = sum(oddments)

    return (
        oddments[0] / oddments_sum,
        oddments[1] / oddments_sum,
        oddments[2] / oddments_sum,
    )


def transpose_strategy_set(strategy_set) -> list[Strategy]:
    strategies: int = len(strategy_set)
    payoffs_size: int = len(strategy_set[0].payoffs)

    transposed_set: list[Strategy] = list()

    for p in range(payoffs_size):
        transposed_payoffs = list()
        for s in range(strategies):
            transposed_payoffs.append(strategy_set[s].payoff(p))
        strategy: Strategy = Strategy("S*_" + str(p), transposed_payoffs)
        transposed_set.append(strategy)

    return transposed_set


if __name__ == "__main__":
    main()
