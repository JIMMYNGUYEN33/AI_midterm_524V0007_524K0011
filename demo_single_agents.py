
import pygame
import sys

from board import Board
from tile_renderer import TileRenderer
from sokoban_solver import SokobanProblem, solve_astar, solve_ucs, ACTIONS

def draw_text(
    surface,
    text,
    font,
    color,
    x,
    y,
    center=False
):
    text_surf = font.render(
        text,
        True,
        color
    )

    if center:
        text_rect = text_surf.get_rect(
            center=(x, y)
        )
    else:
        text_rect = text_surf.get_rect(
            topleft=(x, y)
        )

    surface.blit(
        text_surf,
        text_rect
    )

class GameApp:

    def __init__(self, algorithm="A*"):

        pygame.init()
        pygame.font.init()

        self.algorithm = algorithm

        self.map_file = "maps/example_map.txt"

        self.board = Board(
            self.map_file
        )

        self.tile_size = 64
        self.margin = 0
        self.hud_gap = 0
        self.hud_height = 80

        board_width = self.board.cols * self.tile_size
        board_height = self.board.rows * self.tile_size

        self.screen_w = board_width + 2 * self.margin
        self.screen_h = (
            board_height
            + 2 * self.margin
            + self.hud_gap
            + self.hud_height
        )

        self.screen = pygame.display.set_mode(
            (self.screen_w, self.screen_h)
        )

        pygame.display.set_caption(
            f"Sokoban TDTU - {algorithm}"
        )

        self.renderer = TileRenderer(
            tile_size=self.tile_size
        )

        self.font_title = pygame.font.SysFont(
            "Impact",
            24
        )

        self.font = pygame.font.SysFont(
            "Arial",
            22,
            bold=True
        )

        self.small_font = pygame.font.SysFont(
            "Arial",
            14,
            bold=True
        )

        self.offset_x = self.margin
        self.offset_y = self.margin

        self.problem = SokobanProblem(
            self.map_file
        )

        self.path = None

        self.states = []

        self.current_step = 0

        self.auto_play = False

        self._solve_and_build_timeline()

    def _solve_and_build_timeline(self):

        print(
            f"AI is searching with "
            f"{self.algorithm}..."
        )

        if self.algorithm == "UCS":

            self.path, nodes_expanded, elapsed = solve_ucs(
                self.problem
            )

        else:

            self.path, nodes_expanded, elapsed = solve_astar(
                self.problem
            )

        print("Nodes:", nodes_expanded)
        print(f"Time: {elapsed:.3f} seconds")

        if self.path is None:

            print(
                "No solution found."
            )

            return

        print("Actions:", self.path)
        print("Total cost:", len(self.path))

        curr_agent = (
            self.problem.initial_agent
        )

        curr_boxes = set(
            self.problem.initial_boxes
        )

        self.states.append(
            (
                curr_agent,
                curr_boxes.copy()
            )
        )

        for act in self.path:

            dr, dc = ACTIONS[act]

            next_agent = (
                curr_agent[0] + dr,
                curr_agent[1] + dc
            )

            next_boxes = set(
                curr_boxes
            )

            if next_agent in next_boxes:

                box_next = (
                    next_agent[0] + dr,
                    next_agent[1] + dc
                )

                next_boxes.remove(
                    next_agent
                )

                next_boxes.add(
                    box_next
                )

            self.states.append(
                (
                    next_agent,
                    next_boxes.copy()
                )
            )

            curr_agent = next_agent

            curr_boxes = next_boxes

    def draw_hud(self):

        y = (
            self.offset_y
            + self.board.rows * self.tile_size
            + self.hud_gap
        )
        pygame.draw.rect(
            self.screen,
            (245, 245, 245),
            (0, y, self.screen_w, self.hud_height)
        )

        path_length = len(self.path) if self.path is not None else 0

        if self.path is None:
            status_text = "NO SOLUTION"
            color_status = (231, 76, 60)
        elif self.current_step >= path_length:
            status_text = "FINISHED"
            color_status = (46, 204, 113)
        elif self.auto_play:
            status_text = "PLAYING"
            color_status = (46, 204, 113)
        else:
            status_text = "PAUSED"
            color_status = (231, 76, 60)

        draw_text(
            self.screen,
            f"Mode: {self.algorithm}    Step: {self.current_step} / {path_length}",
            self.font,
            (20, 20, 20),
            10,
            y + 5
        )

        draw_text(
            self.screen,
            f"Status: {status_text}",
            self.font,
            color_status,
            10,
            y + 30
        )

        guide_text = (
            "SPACE: Play/Pause   |   "
            "Hold LEFT/RIGHT: Rewind/Forward   |   "
            "ESC: Exit"
        )
        self.screen.blit(
            self.small_font.render(
                guide_text,
                True,
                (120, 120, 120)
            ),
            (10, y + 55)
        )

    def run(self):

        clock = pygame.time.Clock()
        left_held = False
        right_held = False
        manual_step_delay = 180
        last_manual_step_time = 0

        while True:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    return

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        return

                    elif event.key == pygame.K_SPACE:

                        self.auto_play = (
                            not self.auto_play
                        )

                    elif event.key == pygame.K_RIGHT:

                        self.auto_play = False

                        if (
                            self.path is not None
                            and
                            self.current_step
                            < len(self.path)
                        ):

                            self.current_step += 1

                        right_held = True
                        last_manual_step_time = pygame.time.get_ticks()

                    elif event.key == pygame.K_LEFT:

                        self.auto_play = False

                        if self.current_step > 0:

                            self.current_step -= 1

                        left_held = True
                        last_manual_step_time = pygame.time.get_ticks()

                elif event.type == pygame.KEYUP:

                    if event.key == pygame.K_LEFT:
                        left_held = False

                    elif event.key == pygame.K_RIGHT:
                        right_held = False

            current_time = pygame.time.get_ticks()

            if (
                (left_held or right_held)
                and current_time - last_manual_step_time
                >= manual_step_delay
            ):
                self.auto_play = False

                if left_held:
                    if self.current_step > 0:
                        self.current_step -= 1
                elif self.path is not None and self.current_step < len(self.path):
                    self.current_step += 1

                last_manual_step_time = current_time

            if (
                self.auto_play
                and self.path is not None
                and
                self.current_step
                < len(self.path)
            ):

                self.current_step += 1

                pygame.time.wait(200)

            if self.states:

                agent_pos, boxes = (
                    self.states[
                        self.current_step
                    ]
                )

                self.board.agent_pos = (
                    agent_pos
                )

                self.board.boxes = set(
                    boxes
                )

            self.screen.fill(
                (135, 206, 235)
            )

            self.renderer.draw(
                self.screen,
                self.board,
                self.offset_x,
                self.offset_y
            )

            self.draw_hud()

            pygame.display.flip()

            clock.tick(30)

def run_game(algorithm="A*"):

    app = GameApp(
        algorithm=algorithm
    )

    app.run()

def select_algorithm():

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((560, 380))
    pygame.display.set_caption("Sokoban TDTU - Select Algorithm")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("Impact", 36)
    font = pygame.font.SysFont("Arial", 22, bold=True)
    small_font = pygame.font.SysFont("Arial", 16)

    algorithms = ["A*", "UCS"]
    selected_index = 0
    algorithm_buttons = [
        pygame.Rect(105, 190, 155, 64),
        pygame.Rect(300, 190, 155, 64)
    ]
    start_button = pygame.Rect(180, 285, 200, 54)
    background = (135, 206, 235)
    ink = (34, 54, 75)
    accent = (49, 112, 164)

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return None

                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    selected_index = 1 - selected_index

                elif event.key == pygame.K_1:
                    selected_index = 0

                elif event.key == pygame.K_2:
                    selected_index = 1

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    pygame.quit()
                    return algorithms[selected_index]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                for index, button in enumerate(algorithm_buttons):
                    if button.collidepoint(event.pos):
                        selected_index = index

                if start_button.collidepoint(event.pos):
                    pygame.quit()
                    return algorithms[selected_index]

        screen.fill(background)

        pygame.draw.rect(
            screen,
            (248, 250, 252),
            (40, 35, 480, 310),
            border_radius=20
        )

        title = title_font.render("SOKOBAN", True, ink)
        screen.blit(title, title.get_rect(center=(280, 88)))

        subtitle = font.render("Choose a search algorithm", True, ink)
        screen.blit(subtitle, subtitle.get_rect(center=(280, 140)))

        for index, (algorithm, button) in enumerate(
            zip(algorithms, algorithm_buttons)
        ):
            selected = index == selected_index
            pygame.draw.rect(
                screen,
                accent if selected else (224, 233, 241),
                button,
                border_radius=12
            )
            label = font.render(
                algorithm,
                True,
                (255, 255, 255) if selected else ink
            )
            screen.blit(label, label.get_rect(center=button.center))

        pygame.draw.rect(
            screen,
            (53, 145, 101),
            start_button,
            border_radius=12
        )
        start_label = font.render("START GAME", True, (255, 255, 255))
        screen.blit(start_label, start_label.get_rect(center=start_button.center))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        selected_algorithm = sys.argv[1].upper()

        if selected_algorithm not in {"A*", "UCS"}:
            raise SystemExit("Usage: python demo_single_agents.py [A*|UCS]")

        run_game(selected_algorithm)
    else:
        selected_algorithm = select_algorithm()

        if selected_algorithm is not None:
            run_game(selected_algorithm)
