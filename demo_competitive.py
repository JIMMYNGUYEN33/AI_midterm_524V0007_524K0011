
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

        # =================================================
        # LOAD MAP
        # =================================================

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

        # Grid dùng cho TileRenderer
        self.grid = []

        self.walls = set()
        self.goals = set()

        self.agent1_pos = None
        self.agent2_pos = None

        self.agent1_boxes = set()
        self.agent2_boxes = set()
        self.neutral_boxes = set()

        # =================================================
        # PARSE MAP
        # =================================================

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

        # =================================================
        # SCREEN
        # =================================================

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

        # =================================================
        # TILE RENDERER
        # =================================================

        self.renderer = TileRenderer(
            self.tile_size
        )

        # =================================================
        # AGENTS
        # =================================================

        self.agent1 = Agent1Bot(
            self.walls,
            self.goals
        )

        self.agent2 = Agent2Bot(
            self.walls,
            self.goals
        )

        # =================================================
        # GAME STATE
        # =================================================

        self.step_count = 0

        self.max_steps = 25

        self.history = []

        self.game_over = False

        self.result_text = ""

        # =================================================
        # AUTO RUN
        # =================================================

        self.auto_run = True

        self.paused = False

        # Thời gian giữa mỗi bước
        # 500 ms = 0.5 giây
        self.step_delay = 500

        self.last_step_time = pygame.time.get_ticks()

        # =================================================
        # RENDERER COMPATIBILITY
        # =================================================

        self.update_renderer_boxes()

    # =====================================================
    # UPDATE BOX REFERENCES
    # =====================================================

    def update_renderer_boxes(self):

        # TileRenderer của bạn đang dùng:
        # board.b1
        # board.b2

        self.b1 = self.agent1_boxes
        self.b2 = self.agent2_boxes

    # =====================================================
    # SAVE STATE
    # =====================================================

    def save_state(self):

        state = {
            "agent1_pos": self.agent1_pos,
            "agent2_pos": self.agent2_pos,

            "agent1_boxes": set(
                self.agent1_boxes
            ),

            "agent2_boxes": set(
                self.agent2_boxes
            ),

            "neutral_boxes": set(
                self.neutral_boxes
            ),

            "step_count": self.step_count,

            "game_over": self.game_over,

            "result_text": self.result_text
        }

        self.history.append(state)

    # =====================================================
    # RESTORE STATE
    # =====================================================

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

        self.update_renderer_boxes()

    # =====================================================
    # SCORE
    # =====================================================

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

    # =====================================================
    # CHECK WIN
    # =====================================================

    def check_game_over(self):

        score1 = self.get_score1()
        score2 = self.get_score2()

        total_goals = len(
            self.goals
        )

        boxes_on_goals = (
            score1 + score2
        )

        # All goals filled
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

        # Maximum steps reached
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

    # =====================================================
    # MAKE ONE STEP
    # =====================================================

    def make_step(self):

        if self.game_over:
            return

        self.save_state()

        # -----------------------------
        # Agent 1 chooses action
        # -----------------------------

        action1 = self.agent1.get_action(
            self.agent1_pos,
            self.agent2_pos,
            self.agent1_boxes,
            self.agent2_boxes,
            self.neutral_boxes
        )

        # -----------------------------
        # Agent 2 chooses action
        # -----------------------------

        action2 = self.agent2.get_action(
            self.agent2_pos,
            self.agent1_pos,
            self.agent2_boxes,
            self.agent1_boxes,
            self.neutral_boxes
        )

        # -----------------------------
        # Simultaneous movement
        # -----------------------------

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
            self.goals
        )

        # -----------------------------
        # Update state
        # -----------------------------

        self.agent1_pos = new_p1
        self.agent2_pos = new_p2

        self.agent1_boxes = new_b1
        self.agent2_boxes = new_b2

        self.neutral_boxes = new_neutral

        self.step_count += 1

        # Cập nhật cho TileRenderer
        self.update_renderer_boxes()

        # Check winner
        self.check_game_over()

    # =====================================================
    # DRAW INFO
    # =====================================================

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

        # -----------------------------
        # GAME OVER
        # -----------------------------

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

    # =====================================================
    # DRAW BOARD
    # =====================================================

    def draw_board(self):

        # TileRenderer sẽ dùng:
        #
        # wall.png
        # floor.png
        # target.png
        # agent1.png
        # agent2.png
        # box.png
        # box1.png
        # box2.png

        self.renderer.draw(
            self.screen,
            self,
            0,
            0
        )

        self.draw_info()

        pygame.display.flip()

    # =====================================================
    # RESTART
    # =====================================================

    def restart(self):

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

        self.history = []

        self.game_over = False

        self.result_text = ""

        self.paused = False

        self.last_step_time = (
            pygame.time.get_ticks()
        )

        self.update_renderer_boxes()

    # =====================================================
    # BACKWARD
    # =====================================================

    def backward(self):

        if not self.history:
            return

        state = self.history.pop()

        self.restore_state(
            state
        )

        self.paused = True

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        running = True

        while running:

            # =============================================
            # EVENTS
            # =============================================

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                elif event.type == pygame.KEYDOWN:

                    # SPACE = PAUSE / RESUME
                    if event.key == pygame.K_SPACE:

                        self.paused = not self.paused

                        self.last_step_time = (
                            pygame.time.get_ticks()
                        )

                    # BACKWARD
                    elif event.key == pygame.K_LEFT:

                        self.backward()

                    # RESTART
                    elif event.key == pygame.K_r:

                        self.restart()

                    # ESC
                    elif event.key == pygame.K_ESCAPE:

                        running = False

            # =============================================
            # AUTO RUN
            # =============================================

            current_time = (
                pygame.time.get_ticks()
            )

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

            # =============================================
            # DRAW
            # =============================================

            self.draw_board()

            self.clock.tick(60)

        pygame.quit()


# =========================================================
# RUN GAME
# =========================================================

def run_game(n_steps=25):

    game = CompetitiveGame(
        "maps/competitive_map.txt"
    )

    game.max_steps = n_steps

    game.run()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_game()
