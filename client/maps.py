import pygame
from blocks import Block, BlockTypes
from config import Config

TOP_BORDER_ROW = [BlockTypes.SAND_BACKGROUND] * Config.WIDTH_IN_BLOCKS

SIDE_BORDER_ROW = (
    [BlockTypes.SAND_BACKGROUND]
    + [None] * (Config.WIDTH_IN_BLOCKS - 2)
    + [BlockTypes.SAND_BACKGROUND]
)

MAP_1_LAYOUT = [
    TOP_BORDER_ROW,
    *[SIDE_BORDER_ROW for _ in range(Config.HEIGHT_IN_BLOCKS - 2)],
    TOP_BORDER_ROW,
]


class Map:
    """Map class to generate the map based on a layout"""

    def __init__(self, id: int, layout: list[list[dict]]):
        self.id = id
        self.layout = layout

    def generate_map(self):
        """Generate the map based on the layout"""
        blocks = pygame.sprite.Group()
        for y, row in enumerate(self.layout):
            for x, block_data in enumerate(row):
                if block_data is not None:
                    block = Block(
                        x * Block.BLOCK_SIZE,
                        y * Block.BLOCK_SIZE,
                        block_data["image_name"],
                        solid=block_data["solid"],
                    )
                    blocks.add(block)
        return blocks
