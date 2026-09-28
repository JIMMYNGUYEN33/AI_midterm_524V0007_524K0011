import pygame
import sys
import time
from agent1_controller import Agent1Bot
from agent2_controller import Agent2Bot

TILE_SIZE = 55
ACTIONS = {'North': (-1, 0), 'South': (1, 0), 'West': (0, -1), 'East': (0, 1)}

# --- HÀM HỖ TRỢ VẼ UI ---
def draw_text_with_shadow(surface, text, font, color, x, y, center=False):
    shadow = font.render(text, True, (40, 40, 40))
    text_surf = font.render(text, True, color)
    if center:
        shadow_rect = shadow.get_rect(center=(x + 2, y + 2))
        text_rect = text_surf.get_rect(center=(x, y))
    else:
        shadow_rect = shadow.get_rect(topleft=(x + 2, y + 2))
        text_rect = text_surf.get_rect(topleft=(x, y))
    
    surface.blit(shadow, shadow_rect)
    surface.blit(text_surf, text_rect)

def move_agent(pos, act, walls, opp_pos, my_boxes, opp_boxes, neutral_boxes, goals):
    dr, dc = ACTIONS.get(act, (0, 0))
    nxt = (pos[0] + dr, pos[1] + dc)
    all_boxes = set(my_boxes) | set(opp_boxes) | set(neutral_boxes)

    if nxt in walls or nxt == opp_pos: return pos
    if nxt in all_boxes:
        box_nxt = (nxt[0] + dr, nxt[1] + dc)
        if box_nxt in walls or box_nxt in all_boxes or box_nxt == opp_pos:
            return pos
        if nxt in my_boxes: my_boxes.remove(nxt)
        elif nxt in opp_boxes: opp_boxes.remove(nxt)
        elif nxt in neutral_boxes: neutral_boxes.remove(nxt)
        
        if box_nxt in goals: my_boxes.add(box_nxt)
        else: neutral_boxes.add(box_nxt)
    return nxt

class CompetitiveGUI:
    def __init__(self, max_steps=25):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Sokoban Competitive Mode")
        
        self.screen_w, self.screen_h = self.screen.get_size()
        self.font_title = pygame.font.SysFont('Impact', 32)
        self.font_info = pygame.font.SysFont('Arial', 22, bold=True)
        self.clock = pygame.time.Clock()

        self.rows, self.cols = 7, 7
        self.max_steps = max_steps
        self.current_step = 0
        
        # Tính toán offset để căn giữa Map
        self.offset_x = (self.screen_w - self.cols * TILE_SIZE) // 2
        self.offset_y = (self.screen_h - self.rows * TILE_SIZE) // 2 - 60

        # --- LOAD ASSETS ---
        self.assets = {}
        try:
            self.assets['wall'] = pygame.transform.scale(pygame.image.load('assets/wall.png'), (TILE_SIZE, TILE_SIZE))
            self.assets['floor'] = pygame.transform.scale(pygame.image.load('assets/floor.png'), (TILE_SIZE, TILE_SIZE))
            self.assets['goal'] = pygame.transform.scale(pygame.image.load('assets/target.png'), (TILE_SIZE, TILE_SIZE))
            self.assets['agent1'] = pygame.transform.scale(pygame.image.load('assets/agent1.png'), (TILE_SIZE, TILE_SIZE))
            self.assets['agent2'] = pygame.transform.scale(pygame.image.load('assets/agent2.png'), (TILE_SIZE, TILE_SIZE))
            self.assets['box_neutral'] = pygame.transform.scale(pygame.image.load('assets/box.png'), (TILE_SIZE, TILE_SIZE))
            self.assets['box_agent1'] = pygame.transform.scale(pygame.image.load('assets/box1.png'), (TILE_SIZE, TILE_SIZE))
            self.assets['box_agent2'] = pygame.transform.scale(pygame.image.load('assets/box2.png'), (TILE_SIZE, TILE_SIZE))
        except FileNotFoundError:
            self.game_over = True

        self.walls = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1:
                    self.walls.add((r, c))

        self.goals = {(1, 3), (5, 3)}
        self.neutral_boxes = {(3, 2), (3, 4)}
        self.agent1_boxes, self.agent2_boxes = set(), set()
        self.agent1_pos, self.agent2_pos = (1, 1), (5, 5)

        self.bot1 = Agent1Bot(self.walls, self.goals)
        self.bot2 = Agent2Bot(self.walls, self.goals)
        self.paused, self.game_over = True, False

    def step_game(self):
        if self.current_step >= self.max_steps:
            self.game_over = True
            return

        act1 = self.bot1.get_action(self.agent1_pos, self.agent2_pos, self.agent1_boxes, self.agent2_boxes, self.neutral_boxes)
        act2 = self.bot2.get_action(self.agent2_pos, self.agent1_pos, self.agent2_boxes, self.agent1_boxes, self.neutral_boxes)

        self.agent1_pos = move_agent(self.agent1_pos, act1, self.walls, self.agent2_pos, self.agent1_boxes, self.agent2_boxes, self.neutral_boxes, self.goals)
        self.agent2_pos = move_agent(self.agent2_pos, act2, self.walls, self.agent1_pos, self.agent2_boxes, self.agent1_boxes, self.neutral_boxes, self.goals)
        self.current_step += 1

    def draw(self):
        self.screen.fill((135, 206, 235)) # Sky Blue Theme
        
        # Vẽ Map kèm Offset X, Y
        for r in range(self.rows):
            for c in range(self.cols):
                self.screen.blit(self.assets['floor'], (c * TILE_SIZE + self.offset_x, r * TILE_SIZE + self.offset_y))

        for r, c in self.goals: self.screen.blit(self.assets['goal'], (c * TILE_SIZE + self.offset_x, r * TILE_SIZE + self.offset_y))
        for r, c in self.walls: self.screen.blit(self.assets['wall'], (c * TILE_SIZE + self.offset_x, r * TILE_SIZE + self.offset_y))
        
        for r, c in self.neutral_boxes: self.screen.blit(self.assets['box_neutral'], (c * TILE_SIZE + self.offset_x, r * TILE_SIZE + self.offset_y))
        for r, c in self.agent1_boxes: self.screen.blit(self.assets['box_agent1'], (c * TILE_SIZE + self.offset_x, r * TILE_SIZE + self.offset_y))
        for r, c in self.agent2_boxes: self.screen.blit(self.assets['box_agent2'], (c * TILE_SIZE + self.offset_x, r * TILE_SIZE + self.offset_y))

        r1, c1 = self.agent1_pos
        self.screen.blit(self.assets['agent1'], (c1 * TILE_SIZE + self.offset_x, r1 * TILE_SIZE + self.offset_y))
        r2, c2 = self.agent2_pos
        self.screen.blit(self.assets['agent2'], (c2 * TILE_SIZE + self.offset_x, r2 * TILE_SIZE + self.offset_y))

        # Vẽ HUD Panel bo góc lơ lửng
        panel_w, panel_h = 760, 90
        panel_x = (self.screen_w - panel_w) // 2
        panel_y = self.screen_h - panel_h - 30
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, (100, 150, 180), panel_rect.move(4, 4), border_radius=16)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, border_radius=16)
        pygame.draw.rect(self.screen, (200, 200, 200), panel_rect, width=3, border_radius=16)

        info1 = f"STEP: {self.current_step}/{self.max_steps}   |   P1 (Blue): {len(self.agent1_boxes)}   -   P2 (Orange): {len(self.agent2_boxes)}"
        status = "GAME OVER" if self.game_over else ("PAUSED" if self.paused else "PLAYING")
        guide = "[SPACE]: Play/Pause   |   [->]: Next Step   |   [ESC]: Menu"

        draw_text_with_shadow(self.screen, info1, self.font_info, (20, 20, 20), panel_x + 30, panel_y + 15)
        
        status_color = (231, 76, 60) if (self.paused or self.game_over) else (46, 204, 113)
        draw_text_with_shadow(self.screen, status, self.font_title, status_color, panel_x + 600, panel_y + 12)
        
        self.screen.blit(pygame.font.SysFont('Arial', 16, bold=True).render(guide, True, (120, 120, 120)), (panel_x + 30, panel_y + 55))

        # Bảng thông báo Winner lớn giữa màn hình
        if self.game_over:
            res_text = "DRAW!"
            res_color = (241, 196, 15) # Vàng
            if len(self.agent1_boxes) > len(self.agent2_boxes):
                res_text = "AGENT 1 WINS!"
                res_color = (41, 128, 185) # Xanh
            elif len(self.agent2_boxes) > len(self.agent1_boxes):
                res_text = "AGENT 2 WINS!"
                res_color = (211, 84, 0) # Cam
            
            # Khối nổi kết quả
            font_win = pygame.font.SysFont('Impact', 60)
            banner_rect = pygame.Rect(0, 0, 400, 120)
            banner_rect.center = (self.screen_w // 2, self.screen_h // 2)
            
            pygame.draw.rect(self.screen, (20, 20, 20), banner_rect.move(6, 6), border_radius=20)
            pygame.draw.rect(self.screen, res_color, banner_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 255, 255), banner_rect, width=5, border_radius=20)
            
            draw_text_with_shadow(self.screen, res_text, font_win, (255, 255, 255), self.screen_w // 2, self.screen_h // 2, center=True)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 
                    elif event.key == pygame.K_SPACE and not self.game_over:
                        self.paused = not self.paused
                    elif event.key == pygame.K_RIGHT and not self.game_over:
                        self.step_game()

            if not self.paused and not self.game_over:
                self.step_game()
                time.sleep(0.3)

            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

def run_game(n_steps=25):
    app = CompetitiveGUI(max_steps=n_steps)
    app.run()

if __name__ == "__main__":
    run_game(25)