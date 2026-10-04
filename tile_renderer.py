
import pygame
import os

class TileRenderer:
    def __init__(self, tile_size=48):
        self.tile_size = tile_size
        self.sprites = {}

        base_dir = os.path.dirname(os.path.abspath(__file__))
        asset_dir = os.path.join(base_dir, "assets")

        mapping = {
            '%': 'wall.png',
            ' ': 'floor.png',
            'D': 'target.png',

            'A': 'agent.png',

            '1': 'agent1.png',
            '2': 'agent2.png',

            'B': 'box.png',
            'C': 'box.png',
            'C1': 'box1.png',
            'C2': 'box2.png'
        }

        for key, filename in mapping.items():

            path = os.path.join(asset_dir, filename)

            if os.path.exists(path):

                try:
                    img = pygame.image.load(path).convert_alpha()

                    img = pygame.transform.scale(
                        img,
                        (self.tile_size, self.tile_size)
                    )

                    if key in ('C1', 'C2'):
                        tint = (
                            (40, 195, 85)
                            if key == 'C1'
                            else (220, 55, 65)
                        )

                        for x in range(img.get_width()):
                            for y in range(img.get_height()):
                                color = img.get_at((x, y))

                                if color.a:
                                    brightness = (
                                        color.r * 299
                                        + color.g * 587
                                        + color.b * 114
                                    ) / 255000
                                    shade = 0.38 + 0.62 * brightness

                                    img.set_at(
                                        (x, y),
                                        (
                                            int(tint[0] * shade),
                                            int(tint[1] * shade),
                                            int(tint[2] * shade),
                                            color.a
                                        )
                                    )

                    elif key == 'C':
                        for x in range(img.get_width()):
                            for y in range(img.get_height()):
                                color = img.get_at((x, y))

                                if color.a:
                                    brightness = (
                                        color.r * 299
                                        + color.g * 587
                                        + color.b * 114
                                    ) / 255000

                                    img.set_at(
                                        (x, y),
                                        (
                                            int(55 + 105 * brightness),
                                            int(30 + 66 * brightness),
                                            int(12 + 34 * brightness),
                                            color.a
                                        )
                                    )

                    self.sprites[key] = img

                except pygame.error as e:

                    print(f"[WARNING] Cannot load image: {path}")
                    print(e)

            else:

                if key not in ('C1', 'C2'):
                    print(f"[WARNING] Image not found: {path}")

                surf = pygame.Surface(
                    (self.tile_size, self.tile_size)
                )

                if key == '%':
                    surf.fill((100, 100, 100))

                elif key == 'C1':
                    surf.fill((40, 195, 85))

                elif key == 'C2':
                    surf.fill((220, 55, 65))

                elif key == 'B':
                    surf.fill((150, 100, 50))

                elif key == 'C':
                    surf.fill((200, 150, 50))

                elif key == 'D':
                    surf.fill((255, 255, 0))

                elif key == 'A':
                    surf.fill((0, 255, 0))

                elif key == '1':
                    surf.fill((40, 195, 85))

                elif key == '2':
                    surf.fill((220, 55, 65))

                else:
                    surf.fill((200, 200, 200))

                self.sprites[key] = surf

    def draw(self, screen, board, offset_x, offset_y):

        dynamic_tiles = {
            'A',
            '1',
            '2',
            'B',
            'C',
            'C1',
            'C2'
        }

        for r in range(board.rows):

            for c in range(board.cols):

                char = board.grid[r][c]

                x = (
                    offset_x
                    + c * self.tile_size
                )

                y = (
                    offset_y
                    + r * self.tile_size
                )

                if char in dynamic_tiles:

                    if (
                        hasattr(board, 'goals')
                        and (r, c) in board.goals
                    ):
                        sprite_key = 'D'

                    elif (
                        hasattr(board, 'targets')
                        and (r, c) in board.targets
                    ):
                        sprite_key = 'D'

                    else:
                        sprite_key = ' '

                else:

                    sprite_key = char

                if sprite_key not in self.sprites:
                    sprite_key = ' '

                if sprite_key == 'D':
                    screen.blit(
                        self.sprites[' '],
                        (x, y)
                    )

                screen.blit(
                    self.sprites[sprite_key],
                    (x, y)
                )

        if hasattr(board, 'neutral_boxes'):

            for box in board.neutral_boxes:

                x = (
                    offset_x
                    + box[1] * self.tile_size
                )

                y = (
                    offset_y
                    + box[0] * self.tile_size
                )

                screen.blit(
                    self.sprites['B'],
                    (x, y)
                )

            for box in board.b1:

                x = (
                    offset_x
                    + box[1] * self.tile_size
                )

                y = (
                    offset_y
                    + box[0] * self.tile_size
                )

                screen.blit(
                    self.sprites['C1'],
                    (x, y)
                )

            for box in board.b2:

                x = (
                    offset_x
                    + box[1] * self.tile_size
                )

                y = (
                    offset_y
                    + box[0] * self.tile_size
                )

                screen.blit(
                    self.sprites['C2'],
                    (x, y)
                )

            if (
                hasattr(board, 'agent1_pos')
                and board.agent1_pos is not None
            ):

                x = (
                    offset_x
                    + board.agent1_pos[1] * self.tile_size
                )

                y = (
                    offset_y
                    + board.agent1_pos[0] * self.tile_size
                )

                screen.blit(
                    self.sprites['1'],
                    (x, y)
                )

            if (
                hasattr(board, 'agent2_pos')
                and board.agent2_pos is not None
            ):

                x = (
                    offset_x
                    + board.agent2_pos[1] * self.tile_size
                )

                y = (
                    offset_y
                    + board.agent2_pos[0] * self.tile_size
                )

                screen.blit(
                    self.sprites['2'],
                    (x, y)
                )

        else:

            for box in board.boxes:

                x = (
                    offset_x
                    + box[1] * self.tile_size
                )

                y = (
                    offset_y
                    + box[0] * self.tile_size
                )

                if box in board.targets:
                    sprite_key = 'C'
                else:
                    sprite_key = 'B'

                screen.blit(
                    self.sprites[sprite_key],
                    (x, y)
                )

            if (
                hasattr(board, 'agent_pos')
                and board.agent_pos is not None
            ):

                x = (
                    offset_x
                    + board.agent_pos[1] * self.tile_size
                )

                y = (
                    offset_y
                    + board.agent_pos[0] * self.tile_size
                )

                screen.blit(
                    self.sprites['A'],
                    (x, y)
                )
