
import pygame
import os


class TileRenderer:
    def __init__(self, tile_size=48):
        self.tile_size = tile_size
        self.sprites = {}

        # Lấy đúng thư mục chứa tile_renderer.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        asset_dir = os.path.join(base_dir, "assets")

        mapping = {
            # Map
            '%': 'wall.png',
            ' ': 'floor.png',
            'D': 'target.png',

            # Single Agent
            'A': 'agent.png',

            # Competitive Agents
            '1': 'agent1.png',
            '2': 'agent2.png',

            # Boxes
            'B': 'box.png',
            'C': 'box_target.png',
            'C1': 'box1.png',
            'C2': 'box2.png'
        }

        # ==============================
        # LOAD SPRITES
        # ==============================

        for key, filename in mapping.items():

            path = os.path.join(asset_dir, filename)

            if os.path.exists(path):

                try:
                    img = pygame.image.load(path).convert_alpha()

                    img = pygame.transform.scale(
                        img,
                        (self.tile_size, self.tile_size)
                    )

                    self.sprites[key] = img

                except pygame.error as e:

                    print(f"[WARNING] Cannot load image: {path}")
                    print(e)

            else:

                print(f"[WARNING] Image not found: {path}")

                # Fallback
                surf = pygame.Surface(
                    (self.tile_size, self.tile_size)
                )

                if key == '%':
                    surf.fill((100, 100, 100))

                elif key == 'C1':
                    surf.fill((0, 0, 255))

                elif key == 'C2':
                    surf.fill((255, 165, 0))

                elif key == 'B':
                    surf.fill((150, 100, 50))

                elif key == 'C':
                    surf.fill((200, 150, 50))

                elif key == 'D':
                    surf.fill((255, 255, 0))

                elif key == 'A':
                    surf.fill((0, 255, 0))

                elif key == '1':
                    surf.fill((0, 0, 255))

                elif key == '2':
                    surf.fill((255, 165, 0))

                else:
                    surf.fill((200, 200, 200))

                self.sprites[key] = surf

    # =========================================================
    # DRAW BOARD
    # =========================================================

    def draw(self, screen, board, offset_x, offset_y):

        # =====================================================
        # 1. DRAW BASE MAP ONLY
        # =====================================================
        #
        # QUAN TRỌNG:
        # Không lấy agent/box trong board.grid để vẽ.
        #
        # board.grid là map ban đầu.
        # Agent và box đã di chuyển nên vị trí trong grid
        # có thể là vị trí CŨ.
        #
        # Vì vậy:
        # A, 1, 2, B, C, C1, C2
        # -> chỉ vẽ nền bên dưới.
        # =====================================================

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

                # ---------------------------------------------
                # Dynamic object
                # ---------------------------------------------

                if char in dynamic_tiles:

                    # Nếu vị trí này là goal
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

                    # Static tile
                    sprite_key = char

                # Nếu không có sprite
                if sprite_key not in self.sprites:
                    sprite_key = ' '

                screen.blit(
                    self.sprites[sprite_key],
                    (x, y)
                )

        # =====================================================
        # 2. COMPETITIVE MODE
        # =====================================================

        if hasattr(board, 'neutral_boxes'):

            # ---------------------------------------------
            # Neutral boxes
            # ---------------------------------------------

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

            # ---------------------------------------------
            # Agent 1 boxes
            # ---------------------------------------------

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

            # ---------------------------------------------
            # Agent 2 boxes
            # ---------------------------------------------

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

            # ---------------------------------------------
            # Agent 1
            # ---------------------------------------------

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

            # ---------------------------------------------
            # Agent 2
            # ---------------------------------------------

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

        # =====================================================
        # 3. SINGLE AGENT MODE
        # =====================================================

        else:

            # ---------------------------------------------
            # Boxes
            # ---------------------------------------------

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

            # ---------------------------------------------
            # Agent
            # ---------------------------------------------

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
