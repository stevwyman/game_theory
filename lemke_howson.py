"""
Lemke–Howson complementary pivoting for 2-player bimatrix games.

Lemke, C. E. & Howson, J. T. (1964). Equilibrium points of bimatrix games.
von Stengel, B. (2002). Computing equilibria for two-person games.

A completely labelled pair of points on the two best-response polytopes is a
Nash equilibrium after normalisation. The algorithm drops one label at the
origin and follows the unique almost-completely-labelled path until that
label is recovered.
"""

from fractions import Fraction


def _as_fraction(value) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(str(value)).limit_denominator()


def _to_fraction_matrix(matrix: list[list[float]]) -> list[list[Fraction]]:
    return [[_as_fraction(value) for value in row] for row in matrix]


def _shift_positive(
    row_payoffs: list[list[Fraction]], column_payoffs: list[list[Fraction]]
) -> tuple[list[list[Fraction]], list[list[Fraction]]]:
    """Adding a constant does not change best responses; LH needs positive payoffs."""
    minimum = min(min(row) for row in row_payoffs)
    minimum = min(minimum, min(min(row) for row in column_payoffs))
    shift = Fraction(1) - minimum
    if shift == 0:
        return row_payoffs, column_payoffs
    row_shifted = [[value + shift for value in row] for row in row_payoffs]
    column_shifted = [[value + shift for value in row] for row in column_payoffs]
    return row_shifted, column_shifted


def _label(variable: str, row_count: int) -> int:
    kind, index = variable[0], int(variable[1:])
    if kind in ("x", "r"):
        return index
    return row_count + index


def _complement(variable: str) -> str:
    kind, index = variable[0], variable[1:]
    if kind == "x":
        return f"r{index}"
    if kind == "r":
        return f"x{index}"
    if kind == "y":
        return f"s{index}"
    return f"y{index}"


def _tableau_for(variable: str, tableau_x: "_Tableau", tableau_y: "_Tableau") -> "_Tableau":
    if variable[0] in ("x", "s"):
        return tableau_x
    return tableau_y


class _Tableau:
    """Dictionary tableau: each basic variable = rhs + sum coeff[nonbasic] * nonbasic."""

    def __init__(self, rows: dict, nonbasic: set[str]):
        self.rows = rows
        self.nonbasic = set(nonbasic)

    def value(self, variable: str) -> Fraction:
        if variable in self.rows:
            return self.rows[variable][0]
        return Fraction(0)

    def enter(self, entering: str) -> str:
        candidates = []
        for basic, (rhs, coeffs) in self.rows.items():
            coeff = coeffs.get(entering, Fraction(0))
            if coeff < 0:
                candidates.append((rhs / (-coeff), basic))
        if not candidates:
            raise ValueError("Lemke-Howson pivot is unbounded")
        min_ratio = min(ratio for ratio, _ in candidates)
        tied = [basic for ratio, basic in candidates if ratio == min_ratio]
        leaving = min(tied)
        self._pivot(entering, leaving)
        return leaving

    def _pivot(self, entering: str, leaving: str) -> None:
        rhs_leave, coeffs_leave = self.rows[leaving]
        pivot = coeffs_leave[entering]

        new_rhs_enter = -rhs_leave / pivot
        new_coeffs_enter = {leaving: 1 / pivot}
        for variable, coeff in coeffs_leave.items():
            if variable == entering:
                continue
            new_coeffs_enter[variable] = -coeff / pivot

        new_rows = {}
        for basic, (rhs, coeffs) in self.rows.items():
            if basic == leaving:
                continue
            enter_coeff = coeffs.get(entering, Fraction(0))
            updated_rhs = rhs + enter_coeff * new_rhs_enter
            updated_coeffs = {}
            for variable, coeff in coeffs.items():
                if variable == entering:
                    continue
                updated_coeffs[variable] = coeff
            for variable, coeff in new_coeffs_enter.items():
                updated_coeffs[variable] = (
                    updated_coeffs.get(variable, Fraction(0)) + enter_coeff * coeff
                )
            updated_coeffs = {
                variable: coeff for variable, coeff in updated_coeffs.items() if coeff != 0
            }
            new_rows[basic] = (updated_rhs, updated_coeffs)

        new_rows[entering] = (
            new_rhs_enter,
            {variable: coeff for variable, coeff in new_coeffs_enter.items() if coeff != 0},
        )
        self.rows = new_rows
        self.nonbasic.remove(entering)
        self.nonbasic.add(leaving)


def _build_tableaus(
    row_payoffs: list[list[Fraction]], column_payoffs: list[list[Fraction]]
) -> tuple[_Tableau, _Tableau]:
    row_count = len(row_payoffs)
    column_count = len(row_payoffs[0])

    # s_j = 1 - sum_i B[i][j] x_i   (column player's best-response polytope)
    x_rows = {}
    for j in range(column_count):
        coeffs = {
            f"x{i}": -column_payoffs[i][j]
            for i in range(row_count)
            if column_payoffs[i][j] != 0
        }
        x_rows[f"s{j}"] = (Fraction(1), coeffs)
    tableau_x = _Tableau(x_rows, {f"x{i}" for i in range(row_count)})

    # r_i = 1 - sum_j A[i][j] y_j   (row player's best-response polytope)
    y_rows = {}
    for i in range(row_count):
        coeffs = {
            f"y{j}": -row_payoffs[i][j]
            for j in range(column_count)
            if row_payoffs[i][j] != 0
        }
        y_rows[f"r{i}"] = (Fraction(1), coeffs)
    tableau_y = _Tableau(y_rows, {f"y{j}" for j in range(column_count)})

    return tableau_x, tableau_y


def _normalise(values: list[Fraction]) -> tuple[float, ...]:
    total = sum(values)
    if total == 0:
        raise ValueError("Lemke-Howson produced a zero strategy")
    return tuple(float(value / total) for value in values)


def lemke_howson(
    row_payoffs: list[list[float]],
    column_payoffs: list[list[float]],
    drop_label: int = 0,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """
    Find one Nash equilibrium of a 2-player game by dropping `drop_label`.

    Labels 0..m-1 are row strategies; m..m+n-1 are column strategies.
    """
    row_payoffs = _to_fraction_matrix(row_payoffs)
    column_payoffs = _to_fraction_matrix(column_payoffs)
    row_count = len(row_payoffs)
    column_count = len(row_payoffs[0])
    if row_count == 0 or column_count == 0:
        raise ValueError("payoff matrices must be non-empty")
    if any(len(row) != column_count for row in row_payoffs) or any(
        len(row) != column_count for row in column_payoffs
    ):
        raise ValueError("payoff matrices must be the same shape")
    if len(column_payoffs) != row_count:
        raise ValueError("payoff matrices must be the same shape")

    if row_count == 1 and column_count == 1:
        return (1.0,), (1.0,)

    row_payoffs, column_payoffs = _shift_positive(row_payoffs, column_payoffs)
    label_count = row_count + column_count
    drop_label = drop_label % label_count

    tableau_x, tableau_y = _build_tableaus(row_payoffs, column_payoffs)
    if drop_label < row_count:
        entering = f"x{drop_label}"
    else:
        entering = f"y{drop_label - row_count}"

    max_steps = max(50 * label_count, 200)
    for _ in range(max_steps):
        tableau = _tableau_for(entering, tableau_x, tableau_y)
        leaving = tableau.enter(entering)
        if _label(leaving, row_count) == drop_label:
            break
        entering = _complement(leaving)
    else:
        raise ValueError("Lemke-Howson did not terminate")

    row_mix = _normalise([tableau_x.value(f"x{i}") for i in range(row_count)])
    column_mix = _normalise([tableau_y.value(f"y{j}") for j in range(column_count)])
    return row_mix, column_mix


def _same_equilibrium(
    left: tuple[tuple[float, ...], tuple[float, ...]],
    right: tuple[tuple[float, ...], tuple[float, ...]],
    tol: float = 1e-8,
) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(left[0], right[0])) and all(
        abs(a - b) <= tol for a, b in zip(left[1], right[1])
    )


def lemke_howson_equilibria(
    row_payoffs: list[list[float]], column_payoffs: list[list[float]]
) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
    """Run Lemke–Howson from every label and collect distinct equilibria."""
    row_count = len(row_payoffs)
    column_count = len(row_payoffs[0])
    found: list[tuple[tuple[float, ...], tuple[float, ...]]] = []
    for drop_label in range(row_count + column_count):
        try:
            equilibrium = lemke_howson(row_payoffs, column_payoffs, drop_label)
        except ValueError:
            continue
        if not any(_same_equilibrium(equilibrium, existing) for existing in found):
            found.append(equilibrium)
    return found
