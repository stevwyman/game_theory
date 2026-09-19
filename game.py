from copy import deepcopy
from itertools import combinations
from tabulate import tabulate  # table pretty


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

    def __init__(
        self, name: str, payoffs_str: str, strategy_prefix: str | None = None
    ):
        """
        initialises a new player with the specified name and payoffs
        in addition a set of strategies is constructed from those payoffs
        """

        self._name = name
        self._strategy_set = list()
        prefix = strategy_prefix if strategy_prefix else f"{name}_S"

        if not isinstance(payoffs_str, str):
            raise ValueError("payoffs need to be a string in form (a, b), (c, d)")

        try:
            strategy_sets = payoffs_str.replace("(", "").split(")")

            for n in range(len(strategy_sets) - 1):
                payoffs_str_list = strategy_sets[n].strip().split(",")
                payoffs = list()
                for payoff in payoffs_str_list:
                    payoff = payoff.strip()
                    if payoff != "":
                        payoffs.append(float(payoff))
                strategy = Strategy(prefix + str(n), payoffs)
                self._strategy_set.append(strategy)

        except Exception as error:
            raise ValueError(
                f"Error while parsing payoffs for {name}: {payoffs_str}"
            ) from error

    def __str__(self):
        """
        simply returns the name of the player
        """
        return self._name

    @property
    def name(self) -> str:
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

    def _strictly_dominates(self, candidate: Strategy, other: Strategy) -> bool:
        """True if candidate is strictly better than other against every opponent action."""
        return all(
            candidate.payoff(i) > other.payoff(i)
            for i in range(len(candidate.payoffs))
        )

    def _weakly_dominates(self, candidate: Strategy, other: Strategy) -> bool:
        """
        True if candidate is never worse than other, and strictly better
        against at least one opponent action.
        """
        strictly_better_somewhere = False
        for i in range(len(candidate.payoffs)):
            if candidate.payoff(i) < other.payoff(i):
                return False
            if candidate.payoff(i) > other.payoff(i):
                strictly_better_somewhere = True
        return strictly_better_somewhere

    def weakly_dominated_strategy(self) -> list[Strategy]:
        """
        A strategy is weakly dominated if some alternative is always at least
        as good and sometimes strictly better.

        :return: a list holding all the weakly dominated strategies for this player
        :rtype: list
        """
        available_strategies: list[Strategy] = self._strategy_set
        weakly_dominated_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return weakly_dominated_strategies

        for strategy_under_test in available_strategies:
            for alternative in available_strategies:
                if alternative is strategy_under_test:
                    continue
                if self._weakly_dominates(alternative, strategy_under_test):
                    weakly_dominated_strategies.append(strategy_under_test)
                    break

        return weakly_dominated_strategies

    def strictly_dominated_strategy(self) -> list[Strategy]:
        """
        A strategy is strictly dominated if some alternative is strictly better
        against every opponent action.
        """
        available_strategies: list[Strategy] = self._strategy_set
        strictly_dominated_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return strictly_dominated_strategies

        for strategy_under_test in available_strategies:
            for alternative in available_strategies:
                if alternative is strategy_under_test:
                    continue
                if self._strictly_dominates(alternative, strategy_under_test):
                    strictly_dominated_strategies.append(strategy_under_test)
                    break

        return strictly_dominated_strategies

    def weakly_dominant_strategy(self) -> list[Strategy]:
        """
        A strategy is weakly dominant if it weakly dominates every alternative:
        never worse than any other strategy, and strictly better against each
        of them for at least one opponent action.

        :return: a list holding all the weakly dominant strategies for this player
        :rtype: list
        """
        available_strategies: list[Strategy] = self._strategy_set
        weakly_dominant_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return weakly_dominant_strategies

        for strategy_under_test in available_strategies:
            others = [
                alternative
                for alternative in available_strategies
                if alternative is not strategy_under_test
            ]
            if others and all(
                self._weakly_dominates(strategy_under_test, alternative)
                for alternative in others
            ):
                weakly_dominant_strategies.append(strategy_under_test)

        return weakly_dominant_strategies

    def strictly_dominant_strategy(self) -> list[Strategy]:
        """
        A strategy is strictly (or strongly) dominant if it is strictly better
        than every alternative against every opponent action.
        """
        available_strategies: list[Strategy] = self._strategy_set
        strictly_dominant_strategies: list[Strategy] = []

        if len(available_strategies) < 2:
            return strictly_dominant_strategies

        for strategy_under_test in available_strategies:
            others = [
                alternative
                for alternative in available_strategies
                if alternative is not strategy_under_test
            ]
            if others and all(
                self._strictly_dominates(strategy_under_test, alternative)
                for alternative in others
            ):
                strictly_dominant_strategies.append(strategy_under_test)

        return strictly_dominant_strategies


class Player(DefaultPlayer):
    """Row player."""


class Opponent(DefaultPlayer):
    """Column player."""


class Game:
    def __init__(self, player: Player, opponent: Player):
        _validate_payoff_dimensions(player, opponent)
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

    def copy(self) -> "Game":
        """Return a deep copy so IEDS can shrink a working copy of the matrix."""
        return deepcopy(self)

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
        """
        Return one mixed (or pure) Nash mix for `player`.

        Uses support enumeration so the result is a Nash equilibrium of a
        general-sum 2-player game, including matrices larger than 3×3.
        Prefers an equilibrium in which this player actually mixes.
        """
        if player.strategy_set_size() == 1:
            return (1.0,)

        player_index = self._players.index(player)
        equilibria = self.mixed_nash_equilibria()
        if not equilibria:
            equilibria = self.nash_equilibria()
        if not equilibria:
            raise ValueError("No Nash equilibrium identified")

        mix = equilibria[0][player_index]
        return tuple(mix)

    def mixed_nash_equilibria(
        self,
    ) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
        """Nash equilibria in which at least one player mixes."""
        mixed = []
        for player_mix, opponent_mix in self.nash_equilibria():
            if _support_size(player_mix) > 1 or _support_size(opponent_mix) > 1:
                mixed.append((player_mix, opponent_mix))
        return mixed

    def nash_equilibria(
        self,
    ) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
        """All Nash equilibria found by support enumeration, including pures."""
        return support_enumeration(self)

    def is_constant_sum(self, tol: float = 1e-9) -> bool:
        """True if every cell has the same player + opponent payoff."""
        player_payoffs, opponent_payoffs = self.payoff_matrices()
        totals = [
            player_payoffs[i][j] + opponent_payoffs[i][j]
            for i in range(len(player_payoffs))
            for j in range(len(player_payoffs[0]))
        ]
        return max(totals) - min(totals) <= tol

    def payoff_matrices(self) -> tuple[list[list[float]], list[list[float]]]:
        """Row-player and column-player payoff matrices, both n×m."""
        n = self._player.strategy_set_size()
        m = self._opponent.strategy_set_size()
        player_payoffs = [
            [self._player.strategy(i).payoff(j) for j in range(m)] for i in range(n)
        ]
        opponent_payoffs = [
            [self._opponent.strategy(j).payoff(i) for j in range(m)] for i in range(n)
        ]
        return player_payoffs, opponent_payoffs

    def williams_mixed_equilibrium(
        self, iterations: int = 1000
    ) -> tuple[tuple[float, ...], tuple[float, ...], float]:
        """
        Approximate mixed strategies by Williams fictitious play.

        Only meaningful for zero-sum or constant-sum games. Uses the row
        player's payoff matrix.
        """
        from williams import solve as williams_solve

        player_payoffs, _ = self.payoff_matrices()
        rowcnt, colcnt, value = williams_solve(player_payoffs, iterations=iterations)
        row_total = sum(rowcnt)
        col_total = sum(colcnt)
        if row_total == 0 or col_total == 0:
            raise ValueError("Williams iteration produced an empty mix")
        row_mix = tuple(count / row_total for count in rowcnt)
        col_mix = tuple(count / col_total for count in colcnt)
        return row_mix, col_mix, value

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
            strategy.payoffs.pop(strategy_index)


def _validate_payoff_dimensions(player: DefaultPlayer, opponent: DefaultPlayer) -> None:
    if player.strategy_set_size() == 0 or opponent.strategy_set_size() == 0:
        raise ValueError("each player needs at least one strategy")

    player_widths = {len(strategy.payoffs) for strategy in player.strategy_set}
    opponent_widths = {len(strategy.payoffs) for strategy in opponent.strategy_set}
    if len(player_widths) != 1 or len(opponent_widths) != 1:
        raise ValueError("all strategies for a player must have the same number of payoffs")

    if player_widths.pop() != opponent.strategy_set_size():
        raise ValueError(
            "player payoffs must have one entry per opponent strategy"
        )
    if opponent_widths.pop() != player.strategy_set_size():
        raise ValueError(
            "opponent payoffs must have one entry per player strategy"
        )


def _support_size(mix: tuple[float, ...], tol: float = 1e-8) -> int:
    return sum(1 for probability in mix if probability > tol)


def _solve_linear_system(
    matrix: list[list[float]], rhs: list[float]
) -> list[float] | None:
    """Gaussian elimination with partial pivoting. None if the system is singular."""
    n = len(rhs)
    if n == 0 or any(len(row) != n for row in matrix):
        return None

    augmented = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        pivot_value = augmented[col][col]
        for j in range(col, n + 1):
            augmented[col][j] /= pivot_value
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            for j in range(col, n + 1):
                augmented[row][j] -= factor * augmented[col][j]
    return [augmented[i][n] for i in range(n)]


def _mix_on_support(
    support: tuple[int, ...], weights: list[float], size: int, tol: float = 1e-8
) -> tuple[float, ...] | None:
    if any(weight <= tol for weight in weights):
        return None
    mix = [0.0] * size
    for index, weight in zip(support, weights):
        mix[index] = weight
    total = sum(mix)
    if total <= tol:
        return None
    return tuple(value / total for value in mix)


def _expected_payoffs(payoffs: list[list[float]], mix: tuple[float, ...], by_row: bool) -> list[float]:
    if by_row:
        return [
            sum(payoffs[i][j] * mix[j] for j in range(len(mix)))
            for i in range(len(payoffs))
        ]
    return [
        sum(payoffs[i][j] * mix[i] for i in range(len(payoffs)))
        for j in range(len(payoffs[0]))
    ]


def _is_best_reply(
    expected: list[float], support: tuple[int, ...], tol: float = 1e-6
) -> bool:
    value = max(expected)
    for index, payoff in enumerate(expected):
        if index in support:
            if abs(payoff - value) > tol:
                return False
        elif payoff > value + tol:
            return False
    return True


def _solve_indifferent_mix(
    payoffs: list[list[float]],
    maker_support: tuple[int, ...],
    mixing_support: tuple[int, ...],
    mix_size: int,
    mix_over_columns: bool,
) -> tuple[float, ...] | None:
    """
    Solve for a mix on `mixing_support` that makes the other player indifferent
    on `maker_support`.
    """
    k = len(mixing_support)
    if k == 0 or len(maker_support) == 0:
        return None

    matrix = []
    rhs = []
    matrix.append([1.0] * k)
    rhs.append(1.0)

    base = maker_support[0]
    indifference_needed = min(k - 1, len(maker_support) - 1)
    for other in maker_support[1 : 1 + indifference_needed]:
        row = []
        for column in mixing_support:
            if mix_over_columns:
                row.append(payoffs[other][column] - payoffs[base][column])
            else:
                row.append(payoffs[column][other] - payoffs[column][base])
        matrix.append(row)
        rhs.append(0.0)

    # underdetermined: pin leftover weights to the first so we get one interior point
    while len(matrix) < k:
        row = [0.0] * k
        extra_index = len(matrix)
        row[0] = -1.0
        row[extra_index] = 1.0
        matrix.append(row)
        rhs.append(0.0)

    weights = _solve_linear_system(matrix, rhs)
    if weights is None:
        return None
    return _mix_on_support(mixing_support, weights, mix_size)


def support_enumeration(
    game: Game,
) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
    """
    Enumerate Nash equilibria of a finite 2-player game (Porter et al. 2004).
    """
    player_payoffs, opponent_payoffs = game.payoff_matrices()
    n = len(player_payoffs)
    m = len(player_payoffs[0])
    equilibria: list[tuple[tuple[float, ...], tuple[float, ...]]] = []

    for player_size in range(1, n + 1):
        for opponent_size in range(1, m + 1):
            for player_support in combinations(range(n), player_size):
                for opponent_support in combinations(range(m), opponent_size):
                    opponent_mix = _solve_indifferent_mix(
                        player_payoffs,
                        player_support,
                        opponent_support,
                        m,
                        mix_over_columns=True,
                    )
                    player_mix = _solve_indifferent_mix(
                        opponent_payoffs,
                        opponent_support,
                        player_support,
                        n,
                        mix_over_columns=False,
                    )
                    if player_mix is None or opponent_mix is None:
                        continue

                    player_expected = _expected_payoffs(
                        player_payoffs, opponent_mix, by_row=True
                    )
                    opponent_expected = _expected_payoffs(
                        opponent_payoffs, player_mix, by_row=False
                    )
                    if not _is_best_reply(player_expected, player_support):
                        continue
                    if not _is_best_reply(opponent_expected, opponent_support):
                        continue

                    candidate = (player_mix, opponent_mix)
                    if not any(
                        _same_equilibrium(candidate, existing) for existing in equilibria
                    ):
                        equilibria.append(candidate)

    return equilibria


def _same_equilibrium(
    left: tuple[tuple[float, ...], tuple[float, ...]],
    right: tuple[tuple[float, ...], tuple[float, ...]],
    tol: float = 1e-6,
) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(left[0], right[0])) and all(
        abs(a - b) <= tol for a, b in zip(left[1], right[1])
    )

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
