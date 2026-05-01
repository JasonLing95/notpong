import curses

# Define the 12x9 "Wide" font for our digits
WIDE_NUMBERS = {
    "0": [
        "    0000    ",
        "  00    00  ",
        " 00      00 ",
        "00        00",
        "00        00",
        "00        00",
        " 00      00 ",
        "  00    00  ",
        "    0000    ",
    ],
    "1": [
        "     11     ",
        "   1111     ",
        "     11     ",
        "     11     ",
        "     11     ",
        "     11     ",
        "     11     ",
        "     11     ",
        " 1111111111 ",
    ],
    "2": [
        "   222222   ",
        " 22      22 ",
        "         22 ",
        "       22   ",
        "     222    ",
        "   222      ",
        " 22         ",
        " 22         ",
        " 2222222222 ",
    ],
    "3": [
        "   333333   ",
        " 33      33 ",
        "         33 ",
        "      3333  ",
        "         33 ",
        "         33 ",
        "         33 ",
        " 33      33 ",
        "   333333   ",
    ],
    "4": [
        "        44  ",
        "      4444  ",
        "    44  44  ",
        "  44    44  ",
        " 44     44  ",
        " 4444444444 ",
        "        44  ",
        "        44  ",
        "        44  ",
    ],
    "5": [
        " 5555555555 ",
        " 55         ",
        " 55         ",
        " 55555555   ",
        "         55 ",
        "         55 ",
        "         55 ",
        " 55      55 ",
        "   555555   ",
    ],
    "6": [
        "    66666   ",
        "  66        ",
        " 66         ",
        " 6666666    ",
        " 66     66  ",
        " 66     66  ",
        " 66     66  ",
        "  66   66   ",
        "    666     ",
    ],
    "7": [
        " 7777777777 ",
        "         77 ",
        "        77  ",
        "      77    ",
        "     77     ",
        "   77       ",
        "   77       ",
        "   77       ",
        "   77       ",
    ],
    "8": [
        "    8888    ",
        "  88    88  ",
        " 88      88 ",
        "  88    88  ",
        "    8888    ",
        "  88    88  ",
        " 88      88 ",
        "  88    88  ",
        "    8888    ",
    ],
    "9": [
        "    9999    ",
        "  99    99  ",
        " 99      99 ",
        " 99      99 ",
        "  99999999  ",
        "        99  ",
        "        99  ",
        "      99    ",
        "    999     ",
    ],
}


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def clear(self):
        self.stdscr.erase()

    def refresh(self):
        self.stdscr.refresh()

    def draw_borders(self, max_y, max_x):
        try:
            self.stdscr.addstr(0, 0, "+" + "-" * (max_x - 2) + "+")
            for y in range(1, max_y - 1):
                self.stdscr.addstr(y, 0, "|")
                self.stdscr.addstr(y, max_x - 1, "|")
        except curses.error:
            pass

    def draw_paddle(self, y, x, width):
        try:
            self.stdscr.addstr(round(y), round(x), "=" * width)
        except curses.error:
            pass

    def draw_ball(self, y, x):
        try:
            fractional_x = x - int(x)
            if fractional_x < 0.5:
                char = "▌"
            else:
                char = "▐"
            self.stdscr.addstr(int(y), int(x), char)
        except curses.error:
            pass

    def draw_score(self, score, max_y, max_x):
        try:
            score_str = str(score)
            digit_width = 12
            digit_height = 9
            spacing = 3

            total_width = (digit_width * len(score_str)) + (
                spacing * (len(score_str) - 1)
            )

            start_y = max_y // 2 - digit_height // 2
            start_x = max_x // 2 - total_width // 2

            for i, char in enumerate(score_str):
                lines = WIDE_NUMBERS[char]
                char_x = start_x + i * (digit_width + spacing)

                for row_offset, line in enumerate(lines):
                    self.stdscr.addstr(start_y + row_offset, char_x, line)
        except curses.error:
            pass

    def draw_game_over(self, score, max_y, max_x):
        try:
            msg1 = "GAME OVER"
            msg2 = f"Final Score: {score}"
            msg3 = "Press 'r' to Restart or 'q' to Quit"
            center_y = max_y // 2

            self.stdscr.addstr(center_y - 1, max_x // 2 - len(msg1) // 2, msg1)
            self.stdscr.addstr(center_y, max_x // 2 - len(msg2) // 2, msg2)
            self.stdscr.addstr(center_y + 1, max_x // 2 - len(msg3) // 2, msg3)
        except curses.error:
            pass

    def draw_warning(self, max_y, max_x):
        try:
            msg = "Terminal too small to fit the huge text!"
            self.stdscr.addstr(max_y // 2, max_x // 2 - len(msg) // 2, msg)
        except curses.error:
            pass
