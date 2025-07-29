import pygame


def create_ground_texture(tile_w, tile_h):
    """
    Stub for compatibility: Polytopia‑style is flat, so we return
    a fully transparent surface (no texture).
    """
    return pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
