#!/usr/bin/env python3
from pyfiglet import figlet_format
from termcolor import colored

from .timewatcher import TimeWatcher


def main():
    print(colored(figlet_format("TimeWatcher", font="standard"), "green"), end="")
    print(colored("Welcome to TimeWatcher by Gal Birka!", "green"))
    timewatcher = TimeWatcher()
    timewatcher.fill()


if __name__ == "__main__":
    main()
