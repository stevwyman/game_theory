# Game solver

A little tool that could support you by solving game theory matrices, aka payoff matrices. In addition they could help underline the concepts that are available solving them such as:

1. finding pure Nash Equilibrium
2. iterated deletion of (weakly) dominated strategies
3. finding mixed Nash Equilibrium
    by oddments -> 2x2 and 3x3
    by formula -> 2x2
    by an algorithm that iterates simply n-times over the matrix and they identifies the oddments
Note: the last algorithm is still subject of work

## Background

I was taking the ECON 159 by Prof Ben Polak (link) and thought, that it might be some good practice to implement the lessons learned there and combine it with the lesson learned taking the CS50P.

So I have implemented some classes and some algorithms to mimic the process of solving payoff matrices by iterated elimination of dominated strategies.

<!-- ABOUT THE PROJECT -->

## About The Project

The idea of this project has been to not only implement the algorithms, but build an object oriented structure above it. So we have a "game" which is played by two players, a "player" and an "opponent". The players have a common root in the DefaultPlayer which holds the strategy set. A strategy set is a list of "strategies" which themselves have a name and a list of payoffs.

### Built With

The little program is written entirely in Python and uses only the tabulate import for formatting the matrices output, and the configparser import to read and external init of the game.

* [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)

### Installation

There is only one entry in the requirements.txt:

1. tabulate, which is used to pretty the output of the matrices

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

You only need to run the poject.py file with one argument, which is the *.ini file, that holds the payoffs for the different players:

```sh
usage: project.py [-h] [--use_weakly] [-c C]

Solve payoff matrices

optional arguments:
  -h, --help    show this help message and exit
  --use_weakly  use also weakly dominated strategies when using iterate deletion, note that this methode might
                not find all NE
  -c C          path to the *.ini file holding the payoffs, should be located in a folder called games
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Implementation details

Aside from the algorithms and classes, the even more important point for me was the usability. Running command-line programs requires often some input. In this case the input would be the payoffs for each player. As there a multiple ways to provide them, either as list, or separated, or ..., the chances are high to have them wrongly formatted.

The most convenient way for the user is to have them written a file and then simply pass the filename. This makes also easy to run the same configuration multiple times. So in order to provide a common format, rather than inventing the wheel new, I went for the .ini configuration.

This gives you a lot of freedom setting up such configuration.

```hs
[players]
player = (a, b), (c, d)
opponent = (e, f), (a, b)
```

So I have prepared already some files in advance for myself:

```ini
1. prinoners-dilemma.ini
   The famous tell or not tell
2. beer.ini
   a well documented exercise on the web
3. hannibal.ini
   From the lecture ECON 159
```

Another point when it comes to iterated elimination is, that you can run the process not only for strictly dominated strategies, but also for weakly dominated. In the later case, you might delete some NASH equilibria, hence you might find some, but not all. Whereas eliminating only strictly dominated, you find the pure NE.

Therefore the method to solve the game, I have added an optional parameter, which limits the algorithm to only use strict dominance. And the default value is set to

```sh
use_weakly = True
```

<!-- CONTACT -->

## Contact

email: CS50@stvwyman.com

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

