# Touhou LNB simulator

This is a Python program for answering a question posed in the Touhou Discord server: if you're aiming to minimize time to achieve a no-bomb (NB) clear, should you start a new run or continue with your current run? If your current run is doing poorly and you are unlikely to clear given the situation, it may be better to restart instead of wasting time on an attempt that doesn't succeed. This program provides exact probabilities of whether restarting will make you spend more time achieving a NB clear compared to continuing.

## How to use this program

The program takes the section and life count (of the current run) and a list of game sections as input. The list contains the following information about each section:
- **cap rate**: the empirical probability of completing the section without losing any lives
  - must be a float from `0.0` to `1.0`
- **time**: the time needed to complete the section; arbitrary unit
  - must be a non-negative int or float
- **lives gained**: the number of lives gained upon completing the section
  - must be a non-negative int

You can also customize the number of starting lives for a run, the maximum number of lives that can be held at a time, and the simulation depth. The simulation depth affects the accuracy of the result and the time needed to compute it.

The entrypoint is the `main()` function in `main.py`. You can specify the section and life count of the current run as parameters of `main()` and tweak constants for the remaining configuration values.

## How to run this program

1. Make sure `numpy` is installed
2. Run `main.py`

Alternatively, if you have [`uv`](https://github.com/astral-sh/uv) installed, you can simply use `uv run --with numpy main.py`.

## See also...

This work is heavily related to a previous project I did on calculating gacha probabilities. The repository for that project is available [here](https://github.com/astral4/aksim).

## Acknowledgements

Special thanks to Taprus and Rose from the Touhou Discord server for the motivation behind this program.
