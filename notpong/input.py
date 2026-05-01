import curses


class InputHandler:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.nodelay(True)  # Ensure non-blocking input
        self.stdscr.keypad(True)  # Enable special keys (arrows, etc.)

    def get_input(self):
        """Returns the next key in the buffer, or -1 if empty."""
        try:
            return self.stdscr.getch()
        except curses.error:
            return -1
