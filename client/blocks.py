import pygame


class BlockTypes:
    """Collection of predefined block types"""

    GRASS_BACKGROUND = {
        "image_name": "tileGrass1.png",
        "solid": False,
    }
    SAND_BACKGROUND = {
        "image_name": "tileSand1.png",
        "solid": False,
    }
    GREEN_TREE = {
        "image_name": "treeGreen_large.png",
        "solid": True,
    }
    BROWN_TREE = {
        "image_name": "treeBrown_large.png",
        "solid": True,
    }


class Block(pygame.sprite.Sprite):
    """Block class"""

    BLOCK_SIZE = 64  # Size of the block in pixels

    def __init__(self, x: int, y: int, image_name: str, solid: bool = True):
        """
        Block constructor

        Note that `image_name` will be prefixed by `assets/Retina/`, and should include file format
        """
        super().__init__()
        # For collisions
        self.solid = solid

        # Load image
        self.image = pygame.image.load(f"assets/Retina/{image_name}").convert_alpha()
        self.image = pygame.transform.scale(
            self.image, (self.BLOCK_SIZE, self.BLOCK_SIZE)
        )

        # Block position
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
