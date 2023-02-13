# Game solver


<a name="readme-top"></a>


## Background

I was taking the ECON 159 by Prof Ben Polak (<a href="https://oyc.yale.edu/economics/econ-159">link</a>) and thought, that it might be some good practice to implement the lessons learned there and combine it with the lesson learned taking the CS50P.

So I have implemented some classes and some algorithms to mimic the process of solving payoff matrices by iterated elimination of dominated strategies.


<!-- ABOUT THE PROJECT -->
## About The Project

The idea of this project has been to not only implement the algorithms, but build an object oriented structure above it. So we have a "game" which is played by two players, a "player" and an "opponent". The players have a common root in the DefaultPlayer which holds the strategy set. A strategy set is a list of "strategies" which themselves have a name and a list of payoffs.


### Built With

The little program is written entirely in Python and uses only the tabulate import for formatting the matrices output, and the configparser import to read and external init of the game.

* [![Python][Python.org]][Python-url]


### Installation

There is only one entry in the requirements.txt:

1. tabulate, which is used to pretty the output of the matrices

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

You only need to run the poject.py file with one argument, which is the *.ini file, that holds the payoffs for the different players:

python project.py prisoners-dilemma.ini

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Implementation details

Aside from the algorithms and classes, the even more important point for me was the usability. Running command-line programs requires often some input. In this case the input would be the payoffs for each player. As there a multiple ways to provide them, either as list, or separated, or ..., the chances are high to have them wrongly formatted. 

The most convenient way for the user is to have them written a file and then simply pass the filename. This makes also easy to run the same configuration multiple times. So in order to provide a common format, rather than inventing the wheel new, I went for the .ini configuration.

This gives you a lot of freedom setting up such configuration. 

   ```
   [players]
   player = (a, b), (c, d)
   opponent = (e, f), (a, b)
   ```

So I have prepared already some files in advance for myself:

```
1. prinoners-dilemma.ini
   The famous tell or not tell
2. beer.ini
   a well documented exercise on the web
3. hannibal.ini
   From the lecture ECON 159
```

Another point when it comes to iterated elimination is, that you can run the process not only for strictly dominated strategies, but also for weakly dominated. In the later case, you might delete some NASH equilibria, hence you might find some, but not all. Whereas eliminating only strictly dominated, you find the pure NE.

Therefore the method to solve the game, I have added an optional parameter, which limits the algorithm to only use strict dominance. And the default value is set to

   ```
   use_weakly = True
   ```


<!-- CONTACT -->
## Contact

email: CS50@stvwyman.com

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com
[Python.org]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
