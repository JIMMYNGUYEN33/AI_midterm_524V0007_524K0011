import pygame
import os

class TileRenderer:
    def __init__(self, tile_size=48):
        self.tile_size = tile_size
        self.sprites = {}
        
        mapping = {
            '%': 'wall.png', ' ': 'floor.png',
            'A': 'agent.png', 'B': 'box.png',
            'D': 'target.png', 'C': 'box_target.png'
        }
        for key, filename in mapping.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.sprites[key] = pygame.transform.scale(img, (self.tile_size, self.tile_size))
            else:
                # Nếu thiếu hình nó sẽ tự vẽ ô màu thay thế
                surf = pygame.Surface((self.tile_size, self.tile_size))
                surf.fill((200, 200, 200))
                self.sprites[key] = surf

    def draw(self, screen, board, offset_x, offset_y):
        for r in range(board.rows):
            for c in range(board.cols):
                char = board.grid[r][c]
                x, y = offset_x + c * self.tile_size, offset_y + r * self.tile_size
                screen.blit(self.sprites.get(char, self.sprites[' ']), (x, y))
        
        for box in board.boxes:
            x, y = offset_x + box[1] * self.tile_size, offset_y + box[0] * self.tile_size
            sprite_key = 'C' if box in board.targets else 'B'
            screen.blit(self.sprites[sprite_key], (x, y))
            
        if board.agent_pos:
            x, y = offset_x + board.agent_pos[1] * self.tile_size, offset_y + board.agent_pos[0] * self.tile_size
            screen.blit(self.sprites['A'], (x, y))