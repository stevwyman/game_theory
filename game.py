from tabulate import tabulate  # table pretty
from typing import Optional  # annotation


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
        returns the payoff for this strategy given the index, hence the opponents strategy
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
                        payoffs.append(float(payoff))
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

    def weakly_dominated_strategy(self) -> list[Strategy]:
        """
        Weakly dominated strategy: This is a strategy that delivers an equal or worse outcome 
        than an alternative strategy.

        :return: a list holding all the weakly dominated strategies for this player
        :rtype: list
        """

        payoffs_per_strategy: int = len(self._strategy_set[0].payoffs)
        available_strategies: list[Strategy] = self._strategy_set
        weakly_dominated_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return weakly_dominated_strategies

        for strategy_under_test in available_strategies:
            for strategy_to_test in available_strategies:
                if strategy_under_test != strategy_to_test:
                    # counter for the dominance cases
                    weakly_dominates = 0
                    for index in range(payoffs_per_strategy):
                        # is the outcome equal or worse
                        if strategy_under_test.payoff(index) <= strategy_to_test.payoff(index):
                            weakly_dominates += 1
                    
                    # if all payoffs are equal or worse, then the strategy under test is weakly dominated by the strategy to test
                    if weakly_dominates == payoffs_per_strategy:
                        if strategy_under_test not in weakly_dominated_strategies:
                            weakly_dominated_strategies.append(strategy_under_test)


        return weakly_dominated_strategies

    def strictly_dominated_strategy(self) -> list[Strategy]:
        """
        Strictly dominated strategy: This is a strategy that always delivers a worse outcome than an alternative strategy, 
        regardless of what strategy the opponent chooses.
        """
        payoffs_per_strategy: int = len(self._strategy_set[0].payoffs)
        available_strategies: list[Strategy] = self._strategy_set
        strictly_dominated_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return strictly_dominated_strategies

        for strategy_under_test in available_strategies:
            for strategy_to_test in available_strategies:
                if strategy_under_test != strategy_to_test:
                    # counter for the dominance cases
                    strictly_dominates = 0
                    for index in range(payoffs_per_strategy):
                        # is the outcome worse
                        if strategy_under_test.payoff(index) < strategy_to_test.payoff(index):
                            strictly_dominates += 1
                    
                    # if all payoffs are equal or worse, then the strategy under test is weakly dominated by the strategy to test
                    if strictly_dominates == payoffs_per_strategy:
                        if strategy_under_test not in strictly_dominated_strategies:
                            strictly_dominated_strategies.append(strategy_under_test)

        return strictly_dominated_strategies

    def weakly_dominant_strategy(self) -> list[Strategy]:
        """
        A strategy is weakly dominant if it leads to equal or better outcomes than alternative strategies.

        :return: a list holding all the weakly dominated strategies for this player
        :rtype: list
        """

        payoffs_per_strategy: int = len(self._strategy_set[0].payoffs)
        available_strategies: list[Strategy] = self._strategy_set
        weakly_dominant_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return weakly_dominant_strategies

        for strategy_under_test in available_strategies:
            for strategy_to_test in available_strategies:
                if strategy_under_test != strategy_to_test:
                    # counter for the dominance cases
                    weakly_dominant = 0
                    for index in range(payoffs_per_strategy):
                        # is the outcome equal or worse
                        if strategy_under_test.payoff(index) >= strategy_to_test.payoff(index):
                            weakly_dominant += 1
                    
                    # if all payoffs are equal or worse, then the strategy under test is weakly dominated by the strategy to test
                    if weakly_dominant == payoffs_per_strategy:
                        if strategy_under_test not in weakly_dominant_strategies:
                            weakly_dominant_strategies.append(strategy_under_test)

        return weakly_dominant_strategies

    def strictly_dominant_strategy(self) -> list[Strategy]:
        """
        A strategy is strictly (or strongly) dominant if it leads to better outcomes than alternative strategies.
        """
        payoffs_per_strategy: int = len(self._strategy_set[0].payoffs)
        available_strategies: list[Strategy] = self._strategy_set
        strictly_dominant_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return strictly_dominant_strategies

        for strategy_under_test in available_strategies:
            for strategy_to_test in available_strategies:
                if strategy_under_test != strategy_to_test:
                    # counter for the dominance cases
                    strictly_dominant = 0
                    for index in range(payoffs_per_strategy):
                        # is the outcome worse
                        if strategy_under_test.payoff(index) > strategy_to_test.payoff(index):
                            strictly_dominant += 1
                    
                    # if all payoffs are equal or worse, then the strategy under test is weakly dominated by the strategy to test
                    if strictly_dominant == payoffs_per_strategy:
                        if strategy_under_test not in strictly_dominant_strategies:
                            strictly_dominant_strategies.append(strategy_under_test)

        return strictly_dominant_strategies


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

    @property
    def players(self):
        return self._players

    @property
    def player(self) -> Player:
        return self._player

    @property
    def opponent(self) -> Opponent:
        return self._opponent

    def pure_nash_equilibrium(self) -> list[tuple[Strategy, Strategy]]:
        """
        checks for pure nash equilibria by identifying 'cells' where both payoffs are
        the best response

        :return: if found, a list of NE in form of a tuple containing the strategies
        :rtype: list[tuple[Strategy, Strategy]]
        """

        nash_equilibria: list[tuple[Strategy, Strategy]] = list()

        opponent_strategy_set: list[Strategy] = self._opponent.strategy_set
        player_strategy_set: list[Strategy] = self._player.strategy_set

        # result_matrix holding either true = best response, of false otherwise
        player_strategy_size: int = self._player.strategy_set_size()
        opponent_strategy_size: int = self._opponent.strategy_set_size()

        result_matrix = list()
        for p in range(player_strategy_size):
            inner_list = list()
            for o in range(opponent_strategy_size):
                entry = list()
                entry.append(player_strategy_set[p].payoff(o))
                entry.append(False)
                entry.append(opponent_strategy_set[o].payoff(p))
                entry.append(False)
                inner_list.append(entry)
            result_matrix.append(inner_list)

        # to check for the player if there are dominant strategies, we need to get his best response 
        # for every strategy 
        for o in range(opponent_strategy_size):
            payoffs = list()
            for p in range(player_strategy_size):
                # get each entry and add it to the payoff list
                payoffs.append(result_matrix[p][o][0])
            # print(f"   rows payoffs: {payoffs}")
            for p in range(player_strategy_size):
                result = is_biggest_in_list(result_matrix[p][o][0], payoffs)
                result_matrix[p][o][1] = result

        # print(result_matrix)

        # checking now the columns for responses, hence checking the third entries and setting the fourth
        for p in range(player_strategy_size):
            payoffs = list()
            for o in range(opponent_strategy_size):
                # get each entry list
                payoffs.append(result_matrix[p][o][2])
            # print(f"   columns payoffs: {payoffs}")
            for o in range(opponent_strategy_size):
                # print(f"      testing {result_matrix[p][o][2]} against {payoffs}: {is_biggest_in_list(result_matrix[p][o][2], payoffs)}")
                result = is_biggest_in_list(result_matrix[p][o][2], payoffs)
                result_matrix[p][o][3] = result

        # print(result_matrix)
        header = list()
        for strategy in opponent_strategy_set:
            header.append(strategy.name)

        data = list()
        for p in range(player_strategy_size):
            row = list()
            row.append(player_strategy_set[p].name)
            for o in range(opponent_strategy_size):
                row.append((result_matrix[p][o][1],result_matrix[p][o][3]))
            data.append(row)

        print(tabulate(data, header, tablefmt="grid", stralign="center"))

        # a nash equilibrium is a cell which has all entries set to true
        for p in range(player_strategy_size):
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

        This method does not return anything, it has only the side_effect of printing out
        the different steps taken.

        You can afterwards use the print game method to show the updated matrix

        :param : boolean to hint if also weakly dominated strategies shall be removed
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
                        wds = player.weakly_dominated_strategy()
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

    def mixed_nash_equilibrium(self, player: Player) -> tuple[float, ...]:
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

        if len(other_player.strategy_set) == 2:
            try:
                return oddments2(strategy_set)
            except ValueError:
                print(f"  ... need to switch to formula 2x2 ...")
                return formula_2x2(strategy_set)
        elif len(other_player.strategy_set) == 3:
            return oddments3(strategy_set)
        else:
            raise ValueError("Only strategy sets with a length of 2 or 3 are supported")

    def remove_strategy(self, player: Player, strategy: Strategy) -> None:
        """
        removing a strategy means for the player to drop his/her strategy,
        but also to remove the payoffs for the opponent for that strategy
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


def find_dominant_strategies():
    ...

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
    Method to identify, if any, the saddle points of the provided strategy set
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


def formula_2x2(strategy_set: list[Strategy]) -> tuple[float, float]:
    if len(strategy_set) == 2:
        bd = strategy_set[0].payoff(1) - strategy_set[1].payoff(1)
        ca = strategy_set[1].payoff(0) - strategy_set[0].payoff(0)

        q: float = bd / (ca + bd)
    else:
        raise ValueError("only 2x2 games supported")

    return (q, 1 - q)


def oddments2(strategy_set: list[Strategy]) -> tuple[float, float]:
    """
    Finding the oddments of a strategy set with length 2

    Note: this method should not be used when the payoffs for one strategy are the same,
    hence (0, 0), that causes the algorithm to fail and results in a 100 to 0 distribution

    :raise: ValueError when one of the oddments is zero
    :return: a tuple of the suggested distribution amongst the strategy set, should sum up to 1
    :rtype : tuple[float, float]
    """
    if len(strategy_set) != 2:
        raise ValueError("Strategy set must have a length of 2")

    rows_oddments = list()
    rows_oddments.append(abs(strategy_set[1].payoff(0) - strategy_set[1].payoff(1)))
    rows_oddments.append(abs(strategy_set[0].payoff(0) - strategy_set[0].payoff(1)))
    rows_sum = sum(rows_oddments)

    for oddment in rows_oddments:
        if oddment == 0:
            raise ValueError("Oddment is zero, please use different algorithm")

    return (rows_oddments[0] / rows_sum, rows_oddments[1] / rows_sum)


def oddments3(strategy_set: list[Strategy]) -> tuple[float, float, float]:
    """
    Finding the oddments of a strategy set with length 3

    Using strategy sets of length 3, the algorithm look a bit different, ass we need
    to first calculate the column differences, and then use those to get the oddments

    :return: a tuple of the suggested distribution amongst the strategy set, should sum up to 1
    :rtype : tuple[float, float, float]
    """
    if len(strategy_set) != 3:
        raise ValueError("Strategy set must have a length of 3")

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
