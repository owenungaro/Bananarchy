import pygame
from texture import create_ground_texture

MARGIN_RATIO = 0.1
OUTLINE_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 0)

# Side‐face tints
SIDE_COLOR1 = (160, 200, 220)  # left face
SIDE_COLOR2 = (120, 170, 200)  # right face

# Cache for procedural texture
_ground_tex = None
_ground_size = (0, 0)


def calculate_scaling(sw, sh, map_w, map_h):
    usable_w = sw * (1 - 2 * MARGIN_RATIO)
    usable_h = sh * (1 - 2 * MARGIN_RATIO)
    tile_w = min(usable_w / map_w, (usable_h / map_h) * 2)
    tile_h = tile_w / 2

    grid_pw = (map_w + map_h) * tile_w / 2
    grid_ph = (map_w + map_h) * tile_h / 2

    origin_x = sw / 2 - tile_w / 2
    origin_y = (sh - grid_ph) / 2

    return int(tile_w), int(tile_h), int(origin_x), int(origin_y)


def grid_to_screen(x, y, tile_w, tile_h, ox, oy):
    px = (x - y) * tile_w // 2 + ox
    py = (x + y) * tile_h // 2 + oy
    return px, py


def point_in_diamond(mx, my, px, py, tile_w, tile_h):
    dx = abs(mx - (px + tile_w / 2))
    dy = abs(my - (py + tile_h / 2))
    return (dx / (tile_w / 2) + dy / (tile_h / 2)) <= 1


def find_clicked_tile(mx, my, tile_w, tile_h, ox, oy, mw, mh):
    for yy in range(mh):
        for xx in range(mw):
            px, py = grid_to_screen(xx, yy, tile_w, tile_h, ox, oy)
            if point_in_diamond(mx, my, px, py, tile_w, tile_h):
                return xx, yy
    return None, None


def draw_grid(screen, tile_data, tile_w, tile_h, ox, oy):
    """
    tile_data is your world grid of cells:
    each cell = {"building": <dict> or None, ...}
    """
    for yy, row in enumerate(tile_data):
        for xx, cell in enumerate(row):
            building = cell["building"]
            draw_block(screen, xx, yy, building, tile_w, tile_h, ox, oy)


def draw_block(screen, x, y, building, tile_w, tile_h, ox, oy):
    global _ground_tex, _ground_size

    px, py = grid_to_screen(x, y, tile_w, tile_h, ox, oy)
    side_h = tile_h // 2

    # Regenerate texture if size changed
    if _ground_size != (tile_w, tile_h):
        _ground_tex = create_ground_texture(tile_w, tile_h)
        _ground_size = (tile_w, tile_h)

    # Diamond corners
    top = (px + tile_w // 2, py)
    left = (px, py + tile_h // 2)
    bottom = (px + tile_w // 2, py + tile_h)
    right = (px + tile_w, py + tile_h // 2)

    # Draw left side face
    left_face = [
        left,
        bottom,
        (bottom[0], bottom[1] + side_h),
        (left[0], left[1] + side_h),
    ]
    pygame.draw.polygon(screen, SIDE_COLOR1, left_face)

    # Draw right side face
    right_face = [
        right,
        bottom,
        (bottom[0], bottom[1] + side_h),
        (right[0], right[1] + side_h),
    ]
    pygame.draw.polygon(screen, SIDE_COLOR2, right_face)

    # Draw top face (textured)
    mask = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
    pygame.draw.polygon(
        mask,
        (255, 255, 255),
        [
            (0, tile_h // 2),
            (tile_w // 2, 0),
            (tile_w, tile_h // 2),
            (tile_w // 2, tile_h),
        ],
    )
    tex = _ground_tex.copy()
    tex.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(tex, (px, py))

    # Outline top edges
    pygame.draw.polygon(screen, OUTLINE_COLOR, [top, right, bottom, left], width=1)

    # Draw building if present
    if building:
        cx, cy = px + tile_w // 2, py + tile_h // 2
        sz = tile_w // 4
        color = building["color"]
        shape = building["shape"]

        if shape == "square":
            pygame.draw.rect(screen, color, (cx - sz // 2, cy - sz // 2, sz, sz))
        elif shape == "circle":
            pygame.draw.circle(screen, color, (cx, cy), sz // 2)
        elif shape == "triangle":
            tri = [(cx, cy - sz), (cx - sz, cy + sz), (cx + sz, cy + sz)]
            pygame.draw.polygon(screen, color, tri)


def draw_highlight(screen, x, y, tile_w, tile_h, ox, oy):
    px, py = grid_to_screen(x, y, tile_w, tile_h, ox, oy)
    pygame.draw.polygon(
        screen,
        HIGHLIGHT_COLOR,
        [
            (px + tile_w // 2, py),
            (px + tile_w, py + tile_h // 2),
            (px + tile_w // 2, py + tile_h),
            (px, py + tile_h // 2),
        ],
        width=3,
    )
