"""
Approximate mixed strategies for 2-player zero-sum (or constant-sum) games.

Applies the iterative method described by J.D. Williams in The Compleat
Strategyst, ISBN 0-486-25101-2, chapter 5, page 180.

Ties among equally good replies go to the least-played strategy so cyclic
games such as rock–paper–scissors keep visiting every action.
"""

from operator import add


def transpose_matrix(matrix):
    return [[row[col] for row in matrix] for col, _ in enumerate(matrix[0])]


def _argmin(payoffs, counts):
    """Index of the minimum payoff; ties prefer the least-played strategy."""
    best = None
    choice = 0
    for index, payoff in enumerate(payoffs):
        candidate = (payoff, counts[index], index)
        if best is None or candidate < best:
            best = candidate
            choice = index
    return choice


def _argmax(payoffs, counts):
    """Index of the maximum payoff; ties prefer the least-played strategy."""
    best = None
    choice = 0
    for index, payoff in enumerate(payoffs):
        candidate = (-payoff, counts[index], index)
        if best is None or candidate < best:
            best = candidate
            choice = index
    return choice


def solve(payoff_matrix, iterations=5000):
    """Return row counts, column counts, and an approximate value of the game."""
    transpose = transpose_matrix(payoff_matrix)
    numrows = len(payoff_matrix)
    numcols = len(transpose)
    row_cum_payoff = [0] * numrows
    col_cum_payoff = [0] * numcols
    colcnt = [0] * numcols
    rowcnt = [0] * numrows
    active = 0
    for _ in range(iterations):
        rowcnt[active] += 1
        col_cum_payoff = list(map(add, payoff_matrix[active], col_cum_payoff))
        active = _argmin(col_cum_payoff, colcnt)

        colcnt[active] += 1
        row_cum_payoff = list(map(add, transpose[active], row_cum_payoff))
        active = _argmax(row_cum_payoff, rowcnt)

    value_of_game = (max(row_cum_payoff) + min(col_cum_payoff)) / 2.0 / iterations
    return rowcnt, colcnt, value_of_game


if __name__ == "__main__":
    print(solve([[3, -4, 2], [1, -7, -3], [-2, 4, 7]]))
    print(solve([[2, 3, 1, 4], [1, 2, 5, 4], [2, 3, 4, 1], [4, 2, 2, 2]]))
    print(solve([[4, 0, 2], [6, 7, 1]]))
    print(solve([[50, 80], [90, 20]]))
    print(solve([[-1, 4], [3, 2]]))
    print(solve([[0, 1, -1], [-1, 0, 1], [1, -1, 0]]))
