
import sys
import time

import pygame

from agent1_controller import Agent1Bot
from agent2_controller import Agent2Bot
from engine import simultaneous_step
from tile_renderer import TileRenderer

class CompetitiveGame:

    def __init__(
        self,
        map_file="maps/competitive_map.txt"
    ):

        pygame.init()

        self.map_file = map_file

        with open(
            map_file,
            "r",
            encoding="utf-8"
        ) as f:

            self.map_lines = [
                line.rstrip("\n\r")
                for line in f
            ]

        self.rows = len(self.map_lines)

        self.cols = max(
            len(line)
            for line in self.map_lines
        )

        self.grid = []

        self.walls = set()
        self.goals = set()

        self.agent1_pos = None
        self.agent2_pos = None

        self.agent1_boxes = set()
        self.agent2_boxes = set()
        self.neutral_boxes = set()

        for r, line in enumerate(
            self.map_lines
        ):

            row = list(
                line.ljust(
                    self.cols,
                    " "
                )
            )

            self.grid.append(row)

            for c, char in enumerate(row):

                pos = (r, c)

                if char == "%":

                    self.walls.add(pos)

                elif char == "D":

                    self.goals.add(pos)

                elif char == "1":

                    self.agent1_pos = pos

                elif char == "2":

                    self.agent2_pos = pos

                elif char == "B":

                    self.neutral_boxes.add(pos)

                elif char == "A":

                    self.agent1_pos = pos

                elif char == "C":

                    self.neutral_boxes.add(pos)
                    self.goals.add(pos)

        self.tile_size = 64

        self.screen_width = (
            self.cols
            * self.tile_size
        )

        self.screen_height = (
            self.rows
            * self.tile_size
            + 80
        )

        self.screen = pygame.display.set_mode(
            (
                self.screen_width,
                self.screen_height
            )
        )

        pygame.display.set_caption(
            "Sokoban - Competitive Mode"
        )

        self.clock = pygame.time.Clock()

        self.renderer = TileRenderer(
            self.tile_size
        )

        self.agent1 = Agent1Bot(
            self.walls,
            self.goals
        )

        self.agent2 = Agent2Bot(
            self.walls,
            self.goals
        )

        self.step_count = 0

        self.max_steps = 25

        self.history = []
        self.future_states = []

        self.game_over = False

        self.result_text = ""
        self.analysis_log = []

        self.auto_run = True

        self.paused = True

        self.step_delay = 500

        self.last_step_time = pygame.time.get_ticks()

        self.update_renderer_boxes()

    def update_renderer_boxes(self):

        self.b1 = self.agent1_boxes
        self.b2 = self.agent2_boxes

    def save_state(self):

        self.history.append(self.capture_state())
        self.future_states.clear()

    def capture_state(self):

        return {
            "agent1_pos": self.agent1_pos,
            "agent2_pos": self.agent2_pos,
            "agent1_boxes": set(self.agent1_boxes),
            "agent2_boxes": set(self.agent2_boxes),
            "neutral_boxes": set(self.neutral_boxes),
            "step_count": self.step_count,
            "game_over": self.game_over,
            "result_text": self.result_text,
            "analysis_log": [
                entry.copy()
                for entry in self.analysis_log
            ]
        }

    def restore_state(self, state):

        self.agent1_pos = (
            state["agent1_pos"]
        )

        self.agent2_pos = (
            state["agent2_pos"]
        )

        self.agent1_boxes = set(
            state["agent1_boxes"]
        )

        self.agent2_boxes = set(
            state["agent2_boxes"]
        )

        self.neutral_boxes = set(
            state["neutral_boxes"]
        )

        self.step_count = (
            state["step_count"]
        )

        self.game_over = (
            state["game_over"]
        )

        self.result_text = (
            state["result_text"]
        )
        self.analysis_log = [
            entry.copy()
            for entry in state["analysis_log"]
        ]

        self.update_renderer_boxes()

    def get_score1(self):

        return len(
            self.agent1_boxes
            & self.goals
        )

    def get_score2(self):

        return len(
            self.agent2_boxes
            & self.goals
        )

    def print_analysis(self):

        print("\nMap 2 match analysis")
        print(f"Result: {self.result_text}")
        print(f"Game steps / total cost: {self.step_count}")

        for agent_id in (1, 2):
            actions = [
                entry[f"agent{agent_id}_action"]
                for entry in self.analysis_log
            ]
            nodes = sum(
                entry[f"agent{agent_id}_nodes"]
                for entry in self.analysis_log
            )
            total_time = sum(
                entry[f"agent{agent_id}_time"]
                for entry in self.analysis_log
            )
            max_time = max(
                (
                    entry[f"agent{agent_id}_time"]
                    for entry in self.analysis_log
                ),
                default=0.0
            )
            timeouts = sum(
                entry[f"agent{agent_id}_time"] > 1.0
                for entry in self.analysis_log
            )
            average_time = (
                total_time / len(actions)
                if actions
                else 0.0
            )
            score = (
                self.get_score1()
                if agent_id == 1
                else self.get_score2()
            )

            print(f"\nAgent {agent_id}")
            print("Actions:", actions)
            print("Total cost:", len(actions))
            print("Expanded nodes:", nodes)
            print(f"Total search time: {total_time:.3f} seconds")
            print(f"Average decision time: {average_time * 1000:.2f} ms")
            print(f"Max decision time: {max_time * 1000:.2f} ms")
            print("Decisions over 1 second:", timeouts)
            print(f"Goals secured: {score}/{len(self.goals)}")

    def check_game_over(self):

        score1 = self.get_score1()
        score2 = self.get_score2()

        total_goals = len(
            self.goals
        )

        boxes_on_goals = (
            score1 + score2
        )

        if boxes_on_goals == total_goals:

            self.game_over = True

            if score1 > score2:

                self.result_text = (
                    "Agent 1 wins!"
                )

            elif score2 > score1:

                self.result_text = (
                    "Agent 2 wins!"
                )

            else:

                self.result_text = (
                    "Draw!"
                )

            return

        if self.step_count >= self.max_steps:

            self.game_over = True

            if score1 > score2:

                self.result_text = (
                    "Agent 1 wins!"
                )

            elif score2 > score1:

                self.result_text = (
                    "Agent 2 wins!"
                )

            else:

                self.result_text = (
                    "Draw!"
                )

    def make_step(self):

        if self.game_over:
            return

        self.save_state()

        started = time.perf_counter()
        action1 = self.agent1.get_action(
            self.agent1_pos,
            self.agent2_pos,
            self.agent1_boxes,
            self.agent2_boxes,
            self.neutral_boxes
        )
        elapsed1 = time.perf_counter() - started
        if elapsed1 > 1.0:
            action1 = "Wait"

        started = time.perf_counter()
        action2 = self.agent2.get_action(
            self.agent2_pos,
            self.agent1_pos,
            self.agent2_boxes,
            self.agent1_boxes,
            self.neutral_boxes
        )
        elapsed2 = time.perf_counter() - started
        if elapsed2 > 1.0:
            action2 = "Wait"

        (
            new_p1,
            new_p2,
            new_b1,
            new_b2,
            new_neutral
        ) = simultaneous_step(

            self.agent1_pos,
            self.agent2_pos,

            self.agent1_boxes,
            self.agent2_boxes,

            self.neutral_boxes,

            action1,
            action2,

            self.walls,
            self.goals,
            priority=1 if self.step_count % 2 == 0 else 2
        )

        self.agent1_pos = new_p1
        self.agent2_pos = new_p2

        self.agent1_boxes = new_b1
        self.agent2_boxes = new_b2

        self.neutral_boxes = new_neutral

        self.step_count += 1
        self.analysis_log.append({
            "agent1_action": action1,
            "agent1_nodes": self.agent1.last_nodes_expanded,
            "agent1_time": elapsed1,
            "agent2_action": action2,
            "agent2_nodes": self.agent2.last_nodes_expanded,
            "agent2_time": elapsed2
        })
        print(
            f"Step {self.step_count}: "
            f"Agent 1={action1} ({self.agent1.last_nodes_expanded} nodes, "
            f"{elapsed1 * 1000:.2f} ms); "
            f"Agent 2={action2} ({self.agent2.last_nodes_expanded} nodes, "
            f"{elapsed2 * 1000:.2f} ms)"
        )

        self.update_renderer_boxes()

        self.check_game_over()
        if self.game_over:
            self.print_analysis()

    def draw_info(self):

        y = (
            self.rows
            * self.tile_size
        )

        pygame.draw.rect(
            self.screen,
            (245, 245, 245),
            (
                0,
                y,
                self.screen_width,
                80
            )
        )

        font = pygame.font.SysFont(
            None,
            22
        )

        text1 = (
            f"Step: {self.step_count}"
            f"/{self.max_steps}"
        )

        text2 = (
            f"Agent 1: {self.get_score1()}    "
            f"Agent 2: {self.get_score2()}"
        )

        if self.paused:

            text3 = (
                "PAUSED - SPACE = Resume    "
                "R = Restart    ESC = Exit"
            )

        else:

            text3 = (
                "AUTO RUN    "
                "SPACE = Pause    "
                "LEFT = Backward    "
                "R = Restart"
            )

        surface1 = font.render(
            text1,
            True,
            (20, 20, 20)
        )

        surface2 = font.render(
            text2,
            True,
            (20, 20, 20)
        )

        surface3 = font.render(
            text3,
            True,
            (20, 20, 20)
        )

        self.screen.blit(
            surface1,
            (10, y + 5)
        )

        self.screen.blit(
            surface2,
            (10, y + 30)
        )

        self.screen.blit(
            surface3,
            (10, y + 55)
        )

        if self.game_over:

            big_font = pygame.font.SysFont(
                None,
                48
            )

            result = big_font.render(
                self.result_text,
                True,
                (0, 120, 0)
            )

            rect = result.get_rect(
                center=(
                    self.screen_width // 2,
                    self.screen_height // 2
                )
            )

            self.screen.blit(
                result,
                rect
            )

    def draw_board(self):

        self.renderer.draw(
            self.screen,
            self,
            0,
            0
        )

        self.draw_info()

        pygame.display.flip()

    def restart(self):

        max_steps = self.max_steps
        new_game = CompetitiveGame(
            self.map_file
        )

        self.agent1_pos = (
            new_game.agent1_pos
        )

        self.agent2_pos = (
            new_game.agent2_pos
        )

        self.agent1_boxes = set(
            new_game.agent1_boxes
        )

        self.agent2_boxes = set(
            new_game.agent2_boxes
        )

        self.neutral_boxes = set(
            new_game.neutral_boxes
        )

        self.step_count = 0
        self.max_steps = max_steps

        self.history = []
        self.future_states = []

        self.game_over = False

        self.result_text = ""
        self.analysis_log = []

        self.paused = True

        self.last_step_time = (
            pygame.time.get_ticks()
        )

        self.update_renderer_boxes()

    def backward(self):

        if not self.history:
            return

        self.future_states.append(
            self.capture_state()
        )
        state = self.history.pop()

        self.restore_state(
            state
        )

        self.paused = True

    def forward(self):

        if self.future_states:
            self.history.append(
                self.capture_state()
            )
            self.restore_state(
                self.future_states.pop()
            )
        elif not self.game_over:
            self.make_step()

        self.paused = True
        self.last_step_time = pygame.time.get_ticks()

    def run(self):

        running = True
        left_held = False
        right_held = False
        manual_step_delay = 180
        last_manual_step_time = 0

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:

                        self.paused = not self.paused

                        self.last_step_time = (
                            pygame.time.get_ticks()
                        )

                    elif event.key == pygame.K_LEFT:

                        if not left_held:
                            self.backward()
                            last_manual_step_time = (
                                pygame.time.get_ticks()
                            )

                        left_held = True

                    elif event.key == pygame.K_RIGHT:

                        if not right_held:
                            self.forward()
                            last_manual_step_time = (
                                pygame.time.get_ticks()
                            )

                        right_held = True

                    elif event.key == pygame.K_r:

                        self.restart()

                    elif event.key == pygame.K_ESCAPE:

                        running = False

                elif event.type == pygame.KEYUP:

                    if event.key == pygame.K_LEFT:
                        left_held = False

                    elif event.key == pygame.K_RIGHT:
                        right_held = False
            
            current_time = (
                pygame.time.get_ticks()
            )

            if (
                (left_held or right_held)
                and current_time - last_manual_step_time >= manual_step_delay
            ):
                if left_held:
                    self.backward()
                else:
                    self.forward()

                last_manual_step_time = current_time

            if (
                self.auto_run
                and not self.paused
                and not self.game_over
            ):

                if (
                    current_time
                    - self.last_step_time
                    >= self.step_delay
                ):

                    self.make_step()

                    self.last_step_time = (
                        current_time
                    )

            self.draw_board()

            self.clock.tick(60)

        pygame.quit()

def run_game(n_steps=25):
    game = CompetitiveGame(
        "maps/competitive_map.txt"
    )

    game.max_steps = n_steps

    game.run()

def select_max_steps():

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((560, 400))
    pygame.display.set_caption("Sokoban - Map 2 Setup")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("Impact", 34)
    font = pygame.font.SysFont("Arial", 21, bold=True)
    small_font = pygame.font.SysFont("Arial", 16)

    step_field = pygame.Rect(165, 190, 230, 56)
    start_button = pygame.Rect(180, 285, 200, 54)
    steps_text = "25"
    field_focused = True
    error_text = ""
    background = (135, 206, 235)
    ink = (34, 54, 75)
    accent = (49, 112, 164)
    pygame.key.start_text_input()

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.key.stop_text_input()
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.key.stop_text_input()
                    pygame.quit()
                    return None

                if event.key == pygame.K_RETURN:
                    try:
                        steps = int(steps_text)
                    except ValueError:
                        steps = 0

                    if steps > 0:
                        pygame.key.stop_text_input()
                        pygame.quit()
                        return steps

                    error_text = "Enter a number of steps greater than 0."

                elif event.key == pygame.K_BACKSPACE and field_focused:
                    steps_text = steps_text[:-1]
                    error_text = ""

            elif event.type == pygame.TEXTINPUT and field_focused:
                digits = "".join(
                    character
                    for character in event.text
                    if character.isdecimal()
                )
                if digits and len(steps_text) + len(digits) <= 6:
                    steps_text += digits
                    error_text = ""

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                field_focused = step_field.collidepoint(event.pos)
                if field_focused:
                    pygame.key.start_text_input()
                else:
                    pygame.key.stop_text_input()

                if start_button.collidepoint(event.pos):
                    try:
                        steps = int(steps_text)
                    except ValueError:
                        steps = 0

                    if steps > 0:
                        pygame.key.stop_text_input()
                        pygame.quit()
                        return steps

                    error_text = "Enter a number of steps greater than 0."

        screen.fill(background)

        pygame.draw.rect(
            screen,
            (248, 250, 252),
            (40, 35, 480, 330),
            border_radius=20
        )

        title = title_font.render("SOKOBAN - MAP 2", True, ink)
        screen.blit(title, title.get_rect(center=(280, 91)))

        subtitle = font.render("Enter the step limit", True, ink)
        screen.blit(subtitle, subtitle.get_rect(center=(280, 145)))

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            step_field,
            border_radius=10
        )
        pygame.draw.rect(
            screen,
            accent if field_focused else (190, 204, 216),
            step_field,
            width=2,
            border_radius=10
        )
        steps_label = font.render(steps_text, True, ink)
        steps_rect = steps_label.get_rect(center=step_field.center)
        screen.blit(steps_label, steps_rect)

        if field_focused and (pygame.time.get_ticks() // 500) % 2 == 0:
            caret_x = steps_rect.right + 2
            pygame.draw.line(
                screen,
                accent,
                (caret_x, step_field.centery - 13),
                (caret_x, step_field.centery + 13),
                2
            )

        pygame.draw.rect(
            screen,
            (53, 145, 101),
            start_button,
            border_radius=12
        )
        start_label = font.render("START GAME", True, (255, 255, 255))
        screen.blit(start_label, start_label.get_rect(center=start_button.center))

        if error_text:
            error = small_font.render(error_text, True, (190, 58, 50))
            screen.blit(error, error.get_rect(center=(280, 260)))
        else:
            hint = small_font.render(
                "Press Enter or click the button to start",
                True,
                (104, 119, 132)
            )
            screen.blit(hint, hint.get_rect(center=(280, 260)))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        try:
            steps = int(sys.argv[1])
        except ValueError as error:
            raise SystemExit(
                "Usage: python demo_competitive.py [number_of_steps]"
            ) from error

        if steps < 1:
            raise SystemExit("The number of steps must be positive.")

        run_game(steps)
    else:
        steps = select_max_steps()

        if steps is not None:
            run_game(steps)
