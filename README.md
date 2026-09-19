# Game solver

A little tool that could support you by solving game theory matrices, aka payoff matrices. In addition they could help underline the concepts that are available solving them such as:

1. finding pure Nash Equilibrium
2. iterated deletion of (weakly) dominated strategies
3. finding mixed Nash Equilibrium
  * support enumeration (Porter et al. 2004) for general-sum 2-player games of any size
  * Lemke–Howson complementary pivoting (`--lemke-howson`) — finds equilibria on the path from a dropped label
  * by oddments -> 2x2 and 3x3 (lecture algorithms, still available as helpers)
  * by formula -> 2x2
  * Williams fictitious play (`--zero-sum`) for zero-sum / constant-sum games

## Background

I was taking the ECON 159 by Prof Ben Polak and thought that it might be some good practice to implement the lessons learned there and combine it with the lesson learned taking the CS50P.

So I have implemented some classes and some algorithms to mimic the process of solving payoff matrices by iterated elimination of dominated strategies.

Further intro to [Game Theory](/SSRN-id1968579.pdf)

There are two famous algorithms for finding NE:

* LCP (Linear Complementarity) formulation — Lemke-Howson 1964 (`--lemke-howson`)
* Support Enumeration Method — Porter et al. 2004 (this is the default mixed-NE solver)

## About The Project

The idea of this project has been to not only implement the algorithms, but build an object oriented structure above it. So we have a "game" which is played by two players, a "player" and an "opponent". The players have a common root in the DefaultPlayer which holds the strategy set. A strategy set is a list of "strategies" which themselves have a name and a list of payoffs.

### Built With

The program is written in Python. Runtime dependency: `tabulate` (pretty-print matrices). Tests use `pytest`. `configparser` is in the standard library.

* [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)

### Installation

```sh
pip install -r requirements.txt
```

## Usage

Run `project.py` with the `*.ini` file that holds the payoffs:

```sh
python project.py -c games/tennis.ini
python project.py -c games/prisoners_dilemma.ini --use_weakly
python project.py -c games/rock_paper_scissors.ini --zero-sum
python project.py -c games/battle_of_the_sexes.ini --lemke-howson
```

```
usage: project.py [-h] [--use_weakly] [--zero-sum] [--lemke-howson]
                  [--drop-label K] [-c C]

Solve payoff matrices

optional arguments:
  -h, --help       show this help message and exit
  --use_weakly     also delete weakly dominated strategies during iterated
                   deletion; this may drop some NE
  --zero-sum       approximate mixed strategies with Williams fictitious play
                   (zero-sum / constant-sum games)
  --lemke-howson   find Nash equilibria with Lemke–Howson complementary pivoting
  --drop-label K   Lemke–Howson starting label (implies --lemke-howson)
  -c C             path to the *.ini file holding the payoffs
                   (default: games/default.ini)
```

If `-c` is omitted, only `games/default.ini` is loaded. A game file is never mixed with another file's payoffs.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Implementation details

Python files:

1. `project.py` — CLI and INI loading
2. `game.py` — game / player / strategy types and solvers
3. `lemke_howson.py` — complementary pivoting (Lemke–Howson 1964)
4. `williams.py` — fictitious play for zero-sum games
5. `test_game.py` — pytest suite

A game:

```python
class Game:
    def __init__(self, player: Player, opponent: Player):
        self._player = player
        self._opponent = opponent
        self._players = [self._player, self._opponent]
```

The players inherit from DefaultPlayer:

```python
class DefaultPlayer:
    def __init__(self, name: str, payoffs_str: str, strategy_prefix: str | None = None):
        self._name = name
        self._strategy_set = list()
```

A Strategy:

```python
class Strategy:
    def __init__(self, name: str, payoffs: list[int]):
        self._name = name
        self._payoffs = payoffs
```

Payoffs are read from an INI file so you can rerun the same game:

```ini
[names]
player = P
opponent = O

[strategies]
player = S
opponent = S

[payoffs]
player = (1, 1), (0, 0)
opponent = (0, 0), (2, 2)
```

`[names]` and `[strategies]` are optional. Missing names default to `P` / `O`. Missing strategy prefixes default to `{name}_S`, so strategies are named `P_S0`, `P_S1`, … If `[strategies] player = S`, strategies are named `S0`, `S1`, …

Prepared examples in `games/`:

1. `prisoners_dilemma.ini` — tell or not tell
2. `beer.ini` — dominated-strategy pricing exercise
3. `hannibal.ini` — from ECON 159
4. `tennis.ini` — mixed-strategy lecture example
5. `sharing.ini` — 4×4 general-sum game

Iterated elimination can use only strict dominance (the default) or also weakly dominated strategies (`--use_weakly`). Weak deletion can drop some Nash equilibria, so it may find some but not all.

```sh
use_weakly = False
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
