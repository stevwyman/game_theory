"""
Approximate mixed strategies for 2-player zero-sum (or constant-sum) games.

Applies the iterative method described by J.D. Williams in The Compleat
Strategyst, ISBN 0-486-25101-2, chapter 5, page 180.
"""

from operator import add, neg


def transpose_matrix(matrix):
    return [[row[col] for row in matrix] for col, _ in enumerate(matrix[0])]


def solve(payoff_matrix, iterations=100):
    """Return row counts, column counts, and an approximate value of the game."""
    transpose = transpose_matrix(payoff_matrix)
    numrows = len(payoff_matrix)
    numcols = len(transpose)
    row_cum_payoff = [0] * numrows
    col_cum_payoff = [0] * numcols
    colpos = range(numcols)
    rowpos = list(map(neg, range(numrows)))
    colcnt = [0] * numcols
    rowcnt = [0] * numrows
    active = 0
    for _ in range(iterations):
        rowcnt[active] += 1
        col_cum_payoff = list(map(add, payoff_matrix[active], col_cum_payoff))

        col_cum_payoffs = [(col_cum_payoff[j], j) for j in colpos]
        active = min(col_cum_payoffs)[1]

        colcnt[active] += 1
        row_cum_payoff = list(map(add, transpose[active], row_cum_payoff))

        row_cum_payoffs = [(row_cum_payoff[j], j) for j in rowpos]
        active = -max(row_cum_payoffs)[1]

    value_of_game = (max(row_cum_payoff) + min(col_cum_payoff)) / 2.0 / iterations
    return rowcnt, colcnt, value_of_game


if __name__ == "__main__":
    print(solve([[3, -4, 2], [1, -7, -3], [-2, 4, 7]]))
    print(solve([[2, 3, 1, 4], [1, 2, 5, 4], [2, 3, 4, 1], [4, 2, 2, 2]]))
    print(solve([[4, 0, 2], [6, 7, 1]]))
    print(solve([[50, 80], [90, 20]]))
    print(solve([[-1, 4], [3, 2]]))
