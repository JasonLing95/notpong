import curses
from .game import Game


def main(stdscr):
    # Initialize colors, hide cursor, etc.
    curses.curs_set(0)
    stdscr.nodelay(True)

    # Start the game loop
    game = Game(stdscr)
    game.run()


def run():
    # wrapper automatically handles curses initialization and teardown (restoring terminal state)
    curses.wrapper(main)


if __name__ == "__main__":
    run()
