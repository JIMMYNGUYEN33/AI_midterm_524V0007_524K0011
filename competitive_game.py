import time
import sys
import pygame
from engine import simultaneous_step
from agent1_controller import Agent1Bot
from agent2_controller import Agent2Bot
from tile_renderer import TileRenderer

class CompetitiveBoard:
    def __init__(self, map_path):
        self.grid = []
        self.agent1_pos = None
        self.agent2_pos = None
        self.neutral_boxes = set()
        self.b1 = set()
        self.b2 = set()
        self.targets = set()
        self.walls = set()
        self._load_map(map_path)
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0

    def _load_map(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
        max_len = max(len(line.strip('\n')) for line in lines)
        for r, line in enumerate(lines):
            row = list(line.strip('\n').ljust(max_len, ' '))
            for c, char in enumerate(row):
                if char == '%':
                    self.walls.add((r, c))
                elif char == '1':
                    self.agent1_pos = (r, c)
                    row[c] = ' '
                elif char == '2':
                    self.agent2_pos = (r, c)
                    row[c] = ' '
                elif char == 'B':
                    self.neutral_boxes.add((r, c))
                    row[c] = ' '
                elif char == 'D':
                    self.targets.add((r, c))
                    row[c] = 'D'
            self.grid.append(row)

def play_competitive(map_path, n_steps=25):
    pygame.init()
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Sokoban Competitive AI")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)

    board = CompetitiveBoard(map_path)
    renderer = TileRenderer(tile_size=48)
    
    offset_x = (screen_w - board.cols * 48) // 2
    offset_y = (screen_h - board.rows * 48) // 2 + 40

    bot1 = Agent1Bot(board.walls, board.targets)
    bot2 = Agent2Bot(board.walls, board.targets)

    step = 0
    is_paused = True
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    is_paused = not is_paused
                elif event.key == pygame.K_RIGHT and is_paused and not game_over:
                    step += 1
                    take_turn(board, bot1, bot2, step)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if not is_paused and not game_over:
            step += 1
            take_turn(board, bot1, bot2, step)
            pygame.time.delay(300)
            
        if step >= n_steps:
            game_over = True
            is_paused = True

        screen.fill((40, 40, 40))
        
        score_text = f"STEP: {step}/{n_steps} | P1 (Blue): {len(board.b1)} - P2 (Orange): {len(board.b2)}"
        text_surface = font.render(score_text, True, (255, 255, 255))
        screen.blit(text_surface, (20, 15))
        
        if game_over:
            result_str = "DRAW!"
            if len(board.b1) > len(board.b2): result_str = "P1 WINS!"
            elif len(board.b2) > len(board.b1): result_str = "P2 WINS!"
            res_surface = font.render(f"GAME OVER - {result_str}", True, (255, 100, 100))
            screen.blit(res_surface, (screen_w - 300, 15))

        renderer.draw(screen, board, offset_x, offset_y)
        pygame.display.flip()
        clock.tick(30)


def take_turn(board, bot1, bot2, step):
    t_start = time.time()
    a1 = bot1.get_action(board.agent1_pos, board.agent2_pos, board.b1, board.b2, board.neutral_boxes)
    if (time.time() - t_start) * 1000 > 1000:
        a1 = "Wait"

    t_start = time.time()
    a2 = bot2.get_action(board.agent2_pos, board.agent1_pos, board.b2, board.b1, board.neutral_boxes)
    if (time.time() - t_start) * 1000 > 1000:
        a2 = "Wait"

    priority = 1 if step % 2 != 0 else 2
    
    # Cập nhật để nhận lại 5 giá trị từ hàm engine mới
    new_p1, new_p2, new_b1, new_b2, new_neutral = simultaneous_step(
        board.agent1_pos, board.agent2_pos, 
        board.b1, board.b2, board.neutral_boxes, 
        a1, a2, board.walls, board.targets, priority
    )
    
    board.agent1_pos = new_p1
    board.agent2_pos = new_p2
    board.b1 = new_b1
    board.b2 = new_b2
    board.neutral_boxes = new_neutral


if __name__ == "__main__":
    n_input = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    play_competitive("maps/competitive_map.txt", n_steps=n_input)