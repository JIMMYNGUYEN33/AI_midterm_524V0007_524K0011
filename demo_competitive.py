import sys
import pygame
from engine import simultaneous_step
from agent1_controller import Agent1Bot
from agent2_controller import Agent2Bot

TILE_SIZE = 55
STEP_DELAY_MS = 300
ASSET_FILES = {
    'wall': 'wall.png', 'floor': 'floor.png', 'goal': 'target.png',
    'agent1': 'agent1.png', 'agent2': 'agent2.png',
    'box_neutral': 'box.png', 'box_agent1': 'box1.png', 'box_agent2': 'box2.png',
}


def draw_text(surface, text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y)) if center else surf.get_rect(topleft=(x, y))
    surface.blit(surf, rect)


class CompetitiveGUI:
    def __init__(self, max_steps=25):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Sokoban Competitive Mode")
        self.screen_w, self.screen_h = self.screen.get_size()
        self.font_title = pygame.font.SysFont('Impact', 32)
        self.font_info = pygame.font.SysFont('Arial', 22, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 16, bold=True)
        self.font_win = pygame.font.SysFont('Impact', 60)
        self.clock = pygame.time.Clock()

        self.rows, self.cols = 7, 7
        self.max_steps = max_steps
        self.current_step = 0
        self.offset_x = (self.screen_w - self.cols * TILE_SIZE) // 2
        self.offset_y = (self.screen_h - self.rows * TILE_SIZE) // 2 - 60

        self.assets = self._load_assets()

        self.walls = {(r, c) for r in range(self.rows) for c in range(self.cols)
                      if r in (0, self.rows - 1) or c in (0, self.cols - 1)}
        self.goals = {(1, 3), (5, 3)}
        self.neutral_boxes = {(3, 2), (3, 4)}
        self.agent1_boxes, self.agent2_boxes = set(), set()
        self.agent1_pos, self.agent2_pos = (1, 1), (5, 5)

        self.bot1 = Agent1Bot(self.walls, self.goals)
        self.bot2 = Agent2Bot(self.walls, self.goals)
        self.paused, self.game_over = True, False
        self.last_step_time = pygame.time.get_ticks()

    def _load_assets(self):
        assets = {}
        for key, name in ASSET_FILES.items():
            try:
                img = pygame.image.load(f'assets/{name}')
            except (FileNotFoundError, pygame.error):
                pygame.quit()
                sys.exit(f"Không tìm thấy assets/{name}")
            assets[key] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        return assets

    def step_game(self):
        if self.current_step >= self.max_steps:
            self.game_over = True
            return
        act1 = self.bot1.get_action(self.agent1_pos, self.agent2_pos,
                                    self.agent1_boxes, self.agent2_boxes, self.neutral_boxes)
        act2 = self.bot2.get_action(self.agent2_pos, self.agent1_pos,
                                    self.agent2_boxes, self.agent1_boxes, self.neutral_boxes)
        self.agent1_pos, self.agent2_pos = simultaneous_step(
            self.agent1_pos, self.agent2_pos,
            self.agent1_boxes, self.agent2_boxes, self.neutral_boxes,
            act1, act2, self.walls, self.goals,
            priority=1 if (self.current_step + 1) % 2 else 2)
        self.current_step += 1
        if self.current_step >= self.max_steps:
            self.game_over = True

    def _blit(self, key, cell):
        r, c = cell
        self.screen.blit(self.assets[key],
                         (c * TILE_SIZE + self.offset_x, r * TILE_SIZE + self.offset_y))

    def draw(self):
        self.screen.fill((135, 206, 235))
        for r in range(self.rows):
            for c in range(self.cols):
                self._blit('floor', (r, c))
        for cell in self.goals:
            self._blit('goal', cell)
        for cell in self.walls:
            self._blit('wall', cell)
        for cell in self.neutral_boxes:
            self._blit('box_neutral', cell)
        for cell in self.agent1_boxes:
            self._blit('box_agent1', cell)
        for cell in self.agent2_boxes:
            self._blit('box_agent2', cell)
        self._blit('agent1', self.agent1_pos)
        self._blit('agent2', self.agent2_pos)

        panel_w, panel_h = 760, 90
        panel_x = (self.screen_w - panel_w) // 2
        panel_y = self.screen_h - panel_h - 30
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, (100, 150, 180), panel.move(4, 4), border_radius=16)
        pygame.draw.rect(self.screen, (255, 255, 255), panel, border_radius=16)
        pygame.draw.rect(self.screen, (200, 200, 200), panel, width=3, border_radius=16)

        info = (f"STEP: {self.current_step}/{self.max_steps}   |   "
                f"P1 (Blue): {len(self.agent1_boxes)}   -   P2 (Orange): {len(self.agent2_boxes)}")
        status = "GAME OVER" if self.game_over else ("PAUSED" if self.paused else "PLAYING")
        guide = "[SPACE]: Play/Pause   |   [->]: Next Step   |   [ESC]: Quit"
        draw_text(self.screen, info, self.font_info, (20, 20, 20), panel_x + 30, panel_y + 15)
        color = (231, 76, 60) if (self.paused or self.game_over) else (46, 204, 113)
        draw_text(self.screen, status, self.font_title, color, panel_x + 600, panel_y + 12)
        draw_text(self.screen, guide, self.font_small, (120, 120, 120), panel_x + 30, panel_y + 55)

        if self.game_over:
            n1, n2 = len(self.agent1_boxes), len(self.agent2_boxes)
            text, color = "DRAW!", (241, 196, 15)
            if n1 > n2:
                text, color = "AGENT 1 WINS!", (41, 128, 185)
            elif n2 > n1:
                text, color = "AGENT 2 WINS!", (211, 84, 0)
            banner = pygame.Rect(0, 0, 400, 120)
            banner.center = (self.screen_w // 2, self.screen_h // 2)
            pygame.draw.rect(self.screen, (20, 20, 20), banner.move(6, 6), border_radius=20)
            pygame.draw.rect(self.screen, color, banner, border_radius=20)
            pygame.draw.rect(self.screen, (255, 255, 255), banner, width=5, border_radius=20)
            draw_text(self.screen, text, self.font_win, (255, 255, 255),
                      self.screen_w // 2, self.screen_h // 2, center=True)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if self.game_over:
                        continue
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                        self.last_step_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_RIGHT:
                        self.step_game()

            now = pygame.time.get_ticks()
            if not self.paused and not self.game_over and now - self.last_step_time >= STEP_DELAY_MS:
                self.step_game()
                self.last_step_time = now

            self.draw()
            pygame.display.flip()
            self.clock.tick(30)


def run_game(n_steps=25):
    CompetitiveGUI(max_steps=n_steps).run()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else int(input("Số bước n: ") or 25)
    run_game(n)