
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

        # Sokoban problem
        self.problem = SokobanProblem(
            self.map_file
        )

        self.path = []

        self.states = []

        self.current_step = 0

        self.auto_play = False

        self._solve_and_build_timeline()

    # =====================================================
    # SOLVE
    # =====================================================

    def _solve_and_build_timeline(self):

        print(
            f"AI đang tìm đường đi bằng "
            f"{self.algorithm}..."
        )

        if self.algorithm == "UCS":

            self.path, _, _ = solve_ucs(
                self.problem
            )

        else:

            self.path, _, _ = solve_astar(
                self.problem
            )

        if not self.path:

            print(
                "Không tìm thấy lời giải."
            )

            return

        # Initial state
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

        # Build timeline
        for act in self.path:

            dr, dc = ACTIONS[act]

            next_agent = (
                curr_agent[0] + dr,
                curr_agent[1] + dc
            )

            next_boxes = set(
                curr_boxes
            )

            # Agent pushes a box
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

    # =====================================================
    # HUD
    # =====================================================

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

        if not self.path:
            status_text = "NO SOLUTION"
            color_status = (231, 76, 60)
        elif self.current_step >= len(self.path):
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
            f"Mode: {self.algorithm}    Step: {self.current_step} / {len(self.path)}",
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
            "LEFT/RIGHT: Step   |   "
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

    # =====================================================
    # RUN GAME
    # =====================================================

    def run(self):

        clock = pygame.time.Clock()

        while True:

            for event in pygame.event.get():

                # Close window
                if event.type == pygame.QUIT:

                    return

                if event.type == pygame.KEYDOWN:

                    # ESC = back to menu
                    if event.key == pygame.K_ESCAPE:

                        return

                    # SPACE = play / pause
                    elif event.key == pygame.K_SPACE:

                        self.auto_play = (
                            not self.auto_play
                        )

                    # RIGHT = next step
                    elif event.key == pygame.K_RIGHT:

                        self.auto_play = False

                        if (
                            self.current_step
                            < len(self.path)
                        ):

                            self.current_step += 1

                    # LEFT = previous step
                    elif event.key == pygame.K_LEFT:

                        self.auto_play = False

                        if self.current_step > 0:

                            self.current_step -= 1

            # =================================================
            # AUTO PLAY
            # =================================================

            if (
                self.auto_play
                and
                self.current_step
                < len(self.path)
            ):

                self.current_step += 1

                pygame.time.wait(200)

            # =================================================
            # UPDATE BOARD
            # =================================================

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

            # =================================================
            # DRAW
            # =================================================

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


# =========================================================
# RUN GAME
# =========================================================

def run_game(algorithm="A*"):

    app = GameApp(
        algorithm=algorithm
    )

    app.run()


if __name__ == "__main__":

    selected_algorithm = (
        sys.argv[1].upper()
        if len(sys.argv) > 1
        else "A*"
    )

    if selected_algorithm not in {"A*", "UCS"}:
        raise SystemExit("Usage: python demo_single_agents.py [A*|UCS]")

    run_game(selected_algorithm)
