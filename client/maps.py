import pygame
from blocks import Block


class Map:
    """Map class to generate the map based on a layout"""

    def __init__(self, name: str, layout: list[list[dict]]):
        self.name = name
        self.layout = layout

    def generate_map(self):
        """Generate the map based on the layout"""
        blocks = pygame.sprite.Group()
        for y, row in enumerate(self.layout):
            for x, block_data in enumerate(row):
                block = Block(
                    x * Block.BLOCK_SIZE,
                    y * Block.BLOCK_SIZE,
                    block_data["image_name"],
                    solid=block_data["solid"],
                )
                blocks.add(block)
        return blocks
