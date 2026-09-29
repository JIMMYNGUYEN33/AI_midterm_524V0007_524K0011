import pygame
import sys
from board import Board
from tile_renderer import TileRenderer
from sokoban_solver import SokobanProblem, solve_astar, solve_ucs, ACTIONS

def draw_text(surface, text, font, color, x, y, center=False):
    text_surf = font.render(text, True, color)
    if center:
        text_rect = text_surf.get_rect(center=(x, y))
    else:
        text_rect = text_surf.get_rect(topleft=(x, y))
    surface.blit(text_surf, text_rect)

class GameApp:
    def __init__(self, algorithm="A*"):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption(f"Sokoban TDTU - {algorithm}")
        pygame.font.init()
        
        self.screen_w, self.screen_h = self.screen.get_size()
        
        self.algorithm = algorithm
        self.map_file = "example_map.txt"
        self.board = Board(self.map_file)
        self.renderer = TileRenderer(tile_size=48)
        
        self.font_title = pygame.font.SysFont('Impact', 32)
        self.font = pygame.font.SysFont('Arial', 22, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 18, bold=True)
        
        self.offset_x = (self.screen_w - self.board.cols * 48) // 2
        self.offset_y = (self.screen_h - self.board.rows * 48) // 2 - 60
        
        self.problem = SokobanProblem(self.map_file)
        self.path = []
        self.states = [] 
        self.current_step = 0
        self.auto_play = False
        
        self._solve_and_build_timeline()

    def _solve_and_build_timeline(self):
        print(f"AI đang tìm đường đi bằng {self.algorithm}...")
        if self.algorithm == 'UCS':
            self.path, _, _ = solve_ucs(self.problem)
        else:
            self.path, _, _ = solve_astar(self.problem)

        if not self.path:
            return

        curr_agent = self.problem.initial_agent
        curr_boxes = set(self.problem.initial_boxes)
        self.states.append((curr_agent, curr_boxes))

        for act in self.path:
            dr, dc = ACTIONS[act]
            next_agent = (curr_agent[0] + dr, curr_agent[1] + dc)
            next_boxes = set(curr_boxes)
            
            if next_agent in next_boxes:
                box_next = (next_agent[0] + dr, next_agent[1] + dc)
                next_boxes.remove(next_agent)
                next_boxes.add(box_next)
                
            self.states.append((next_agent, next_boxes))
            curr_agent = next_agent
            curr_boxes = next_boxes
            
    def draw_hud(self):
        panel_w, panel_h = 760, 90
        panel_x = (self.screen_w - panel_w) // 2
        panel_y = self.screen_h - panel_h - 30
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, (100, 150, 180), panel_rect.move(4, 4), border_radius=16)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, border_radius=16)
        pygame.draw.rect(self.screen, (200, 200, 200), panel_rect, width=3, border_radius=16)
        
        # Chữ
        step_text = f"MODE: {self.algorithm}   |   STEPS: {self.current_step} / {len(self.path)}"
        status_text = "PLAYING" if self.auto_play else "PAUSED"
        guide_text = "[SPACE]: Play/Pause   |   [<-] [->]: Move   |   [ESC]: Menu"
        
        draw_text(self.screen, step_text, self.font_title, (41, 128, 185), panel_x + 30, panel_y + 15)
        
        color_status = (46, 204, 113) if self.auto_play else (231, 76, 60)
        draw_text(self.screen, status_text, self.font_title, color_status, panel_x + 550, panel_y + 15)
        
        self.screen.blit(self.small_font.render(guide_text, True, (120, 120, 120)), (panel_x + 30, panel_y + 55))

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 
                    elif event.key == pygame.K_SPACE:
                        self.auto_play = not self.auto_play
                    elif event.key == pygame.K_RIGHT:
                        self.auto_play = False
                        if self.current_step < len(self.path):
                            self.current_step += 1
                    elif event.key == pygame.K_LEFT:
                        self.auto_play = False
                        if self.current_step > 0:
                            self.current_step -= 1

            if self.auto_play and self.current_step < len(self.path):
                self.current_step += 1
                pygame.time.wait(200)

            if self.states:
                self.board.agent_pos, self.board.boxes = self.states[self.current_step]

            self.screen.fill((135, 206, 235)) 
            self.renderer.draw(self.screen, self.board, self.offset_x, self.offset_y)
            self.draw_hud()
            
            pygame.display.flip()
            clock.tick(30)

def run_game(algorithm="A*"):
    app = GameApp(algorithm=algorithm)
    app.run()

if __name__ == "__main__":
    run_game("A*")
    
    