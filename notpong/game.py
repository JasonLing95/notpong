import curses
import time
from .render import Renderer, WIDE_NUMBERS
from .input import InputHandler


class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.renderer = Renderer(stdscr)
        self.input_handler = InputHandler(stdscr)
        self.running = True
        self.state = "PLAYING"
        self.init_game_state()

    def init_game_state(self):
        self.max_y, self.max_x = self.stdscr.getmaxyx()
        self.score = 0

        self.paddle_width = 10
        self.paddle_y = self.max_y - 2
        self.paddle_x = self.max_x // 2 - self.paddle_width // 2

        self.paddle_speed = 4.0

        self.ball_y = self.max_y // 2.0 - 8.0
        self.ball_x = self.max_x // 2.0

        self.ball_dy = 15.0
        self.ball_dx = 5.0
        self.speed_multiplier = 1.03
        self.state = "PLAYING"

    def handle_resize(self):
        self.max_y, self.max_x = self.stdscr.getmaxyx()
        self.paddle_y = self.max_y - 2

        if self.paddle_x + self.paddle_width >= self.max_x:
            self.paddle_x = max(1, self.max_x - self.paddle_width - 1)

        if self.ball_x >= self.max_x:
            self.ball_x = self.max_x - 2
        if self.ball_y >= self.max_y and self.state == "PLAYING":
            self.ball_y = self.max_y - 3

    def process_input(self):
        while True:
            key = self.input_handler.get_input()
            if key == -1:
                break
            if key == curses.KEY_RESIZE:
                self.handle_resize()
            elif key in [ord("q"), ord("Q")]:
                self.running = False

            if self.state == "PLAYING":
                if key in [curses.KEY_LEFT, ord("a"), ord("A")]:
                    self.paddle_x -= self.paddle_speed
                elif key in [curses.KEY_RIGHT, ord("d"), ord("D")]:
                    self.paddle_x += self.paddle_speed
            elif self.state == "GAME_OVER":
                if key in [ord("r"), ord("R")]:
                    self.init_game_state()

        if self.paddle_x < 1:
            self.paddle_x = 1
        if self.paddle_x > self.max_x - self.paddle_width - 1:
            self.paddle_x = self.max_x - self.paddle_width - 1

    def update_physics(self, dt):
        if self.state != "PLAYING":
            return

        prev_x = self.ball_x
        prev_y = self.ball_y

        self.ball_x += self.ball_dx * dt
        self.ball_y += self.ball_dy * dt

        # Left & Right wall collisions
        if self.ball_x <= 1:
            self.ball_x = 1
            self.ball_dx *= -1
        elif self.ball_x >= self.max_x - 2:
            self.ball_x = self.max_x - 2
            self.ball_dx *= -1

        # Top wall collision
        if self.ball_y <= 1:
            self.ball_y = 1
            self.ball_dy *= -1

        # --- SCORE OBSTACLE COLLISION (Character-Perfect Hitboxes) ---
        score_str = str(self.score)
        digit_width = 12
        digit_height = 9
        spacing = 3

        total_width = (digit_width * len(score_str)) + (spacing * (len(score_str) - 1))

        score_y_start = self.max_y // 2 - digit_height // 2
        score_y_end = score_y_start + digit_height

        base_x_start = self.max_x // 2 - total_width // 2

        # Check collision against EACH digit individually
        for i, char in enumerate(score_str):
            char_x_start = base_x_start + i * (digit_width + spacing)
            char_x_end = char_x_start + digit_width

            # 1. Quick AABB (Bounding Box) check to see if we are inside this digit's grid
            if (
                score_y_start <= self.ball_y < score_y_end
                and char_x_start <= self.ball_x < char_x_end
            ):

                # 2. Translate ball coordinates to local grid coordinates (0-8 row, 0-11 col)
                local_row = int(self.ball_y) - score_y_start
                local_col = int(self.ball_x) - char_x_start

                # 3. Ensure we are within bounds, then check if we hit a solid character
                if 0 <= local_row < digit_height and 0 <= local_col < digit_width:
                    if WIDE_NUMBERS[char][local_row][local_col] != " ":
                        # HIT! We touched a painted part of the number.

                        # Treat this specific 1x1 character cell as the solid obstacle
                        cell_y_top = score_y_start + local_row
                        cell_y_bottom = cell_y_top + 1
                        cell_x_left = char_x_start + local_col
                        cell_x_right = cell_x_left + 1

                        crossed_y = prev_y < cell_y_top or prev_y >= cell_y_bottom
                        crossed_x = prev_x < cell_x_left or prev_x >= cell_x_right

                        if crossed_y and not crossed_x:
                            self.ball_dy *= -1
                            self.ball_y = prev_y  # Push out to prevent tunneling
                        elif crossed_x and not crossed_y:
                            self.ball_dx *= -1
                            self.ball_x = prev_x
                        else:
                            # Corner hit or diagonal cross
                            self.ball_dy *= -1
                            self.ball_dx *= -1
                            self.ball_y = prev_y
                            self.ball_x = prev_x

                        # Break out immediately after bouncing
                        break

        # --- PADDLE COLLISION ---
        if int(self.ball_y) >= self.paddle_y and self.ball_dy > 0:
            if self.paddle_x <= int(self.ball_x) <= self.paddle_x + self.paddle_width:
                self.ball_y = self.paddle_y - 1
                self.ball_dy *= -1

                self.ball_dy *= self.speed_multiplier
                self.ball_dx *= self.speed_multiplier
                self.paddle_speed *= self.speed_multiplier

                scale_factor = self.paddle_speed / 4.0
                hit_position = (self.ball_x - self.paddle_x) / self.paddle_width
                deflection = (hit_position - 0.5) * 2.0

                self.ball_dx += deflection * (5.0 * scale_factor)

                self.score += 1

        # Bottom fall-through
        if self.ball_y >= self.max_y:
            self.state = "GAME_OVER"

    def run(self):
        last_time = time.perf_counter()
        target_fps = 60
        frame_time = 1.0 / target_fps

        while self.running:
            current_time = time.perf_counter()
            dt = current_time - last_time
            last_time = current_time

            if dt > 0.1:
                dt = 0.1

            self.process_input()
            self.update_physics(dt)

            self.renderer.clear()

            if self.max_y < 24 or self.max_x < 50:
                self.renderer.draw_warning(self.max_y, self.max_x)
            else:
                if self.state == "PLAYING":
                    self.renderer.draw_borders(self.max_y, self.max_x)

                    # 1. Draw the score FIRST (background layer)
                    self.renderer.draw_score(self.score, self.max_y, self.max_x)

                    # 2. Draw the paddle and ball LAST (foreground layer)
                    self.renderer.draw_paddle(
                        self.paddle_y, self.paddle_x, self.paddle_width
                    )
                    self.renderer.draw_ball(self.ball_y, self.ball_x)

                elif self.state == "GAME_OVER":
                    self.renderer.draw_game_over(self.score, self.max_y, self.max_x)

            self.renderer.refresh()

            sleep_time = frame_time - (time.perf_counter() - current_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
