import pygame


def create_ground_texture(tile_w, tile_h):
    """
    Beveled, smooth vertical gradient—from a light pastel top
    to a slightly darker base.
    """
    base = (200, 230, 240)
    dark = (160, 200, 220)
    surf = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
    for y in range(tile_h):
        t = y / tile_h
        color = (
            int(base[0] * (1 - t) + dark[0] * t),
            int(base[1] * (1 - t) + dark[1] * t),
            int(base[2] * (1 - t) + dark[2] * t),
        )
        pygame.draw.line(surf, color, (0, y), (tile_w, y))
    return surf
