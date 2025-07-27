import pygame, world, config
from texture import create_ground_texture

# unpack config
MARGIN_RATIO = config.TILE_MARGIN_RATIO
OUTLINE_COLOR = config.COLORS["outline"]
HIGHLIGHT_COLOR = config.COLORS["highlight"]
SIDE_COLOR1 = config.COLORS["side1"]
SIDE_COLOR2 = config.COLORS["side2"]
SHADE_FACTOR = config.SIDE_SHADE_FACTOR

_ground_tex = None
_ground_size = (0, 0)


def calculate_scaling(sw: int, sh: int):
    """Based on map dims & margin, compute tile w/h and origin."""
    mw, mh = config.MAP_WIDTH, config.MAP_HEIGHT
    usable_w = sw * (1 - 2 * MARGIN_RATIO)
    usable_h = sh * (1 - 2 * MARGIN_RATIO)
    tile_w = min(usable_w / mw, (usable_h / mh) * 2)
    tile_h = tile_w / 2
    grid_pw = (mw + mh) * tile_w / 2
    grid_ph = (mw + mh) * tile_h / 2
    ox = sw / 2 - tile_w / 2
    oy = (sh - grid_ph) / 2
    return int(tile_w), int(tile_h), int(ox), int(oy)


def grid_to_screen(x: int, y: int, tw: int, th: int, ox: int, oy: int):
    px = (x - y) * tw // 2 + ox
    py = (x + y) * th // 2 + oy
    return px, py


def point_in_diamond(mx, my, px, py, tw, th):
    dx = abs(mx - (px + tw / 2))
    dy = abs(my - (py + th / 2))
    return (dx / (tw / 2) + dy / (th / 2)) <= 1


def find_clicked_tile(mx, my, tw, th, ox, oy):
    """Brute-force map scan; uses config.MAP_* internally."""
    mw, mh = config.MAP_WIDTH, config.MAP_HEIGHT
    for yy in range(mh):
        for xx in range(mw):
            px, py = grid_to_screen(xx, yy, tw, th, ox, oy)
            if point_in_diamond(mx, my, px, py, tw, th):
                return xx, yy
    return None, None


def draw_block(screen, x, y, cell, tw, th, ox, oy):
    global _ground_tex, _ground_size
    px, py = grid_to_screen(x, y, tw, th, ox, oy)
    side_h = th // 2

    # regen ground texture if needed
    if _ground_size != (tw, th):
        _ground_tex = create_ground_texture(tw, th)
        _ground_size = (tw, th)

    top = (px + tw // 2, py)
    left = (px, py + th // 2)
    bottom = (px + tw // 2, py + th)
    right = (px + tw, py + th // 2)

    # draw either painted terrain or beveled ground
    if cell["terrain"]:
        t = world.TERRAINS[cell["terrain"]]
        col = t.color
        # 3D sides
        left_face = [
            left,
            bottom,
            (bottom[0], bottom[1] + side_h),
            (left[0], left[1] + side_h),
        ]
        right_face = [
            right,
            bottom,
            (bottom[0], bottom[1] + side_h),
            (right[0], right[1] + side_h),
        ]
        shade = tuple(max(int(c * SHADE_FACTOR), 0) for c in col)
        pygame.draw.polygon(screen, shade, left_face)
        pygame.draw.polygon(screen, col, right_face)
        pygame.draw.polygon(screen, col, [top, right, bottom, left])
    else:
        # default ground
        left_face = [
            left,
            bottom,
            (bottom[0], bottom[1] + side_h),
            (left[0], left[1] + side_h),
        ]
        right_face = [
            right,
            bottom,
            (bottom[0], bottom[1] + side_h),
            (right[0], right[1] + side_h),
        ]
        pygame.draw.polygon(screen, SIDE_COLOR1, left_face)
        pygame.draw.polygon(screen, SIDE_COLOR2, right_face)
        mask = pygame.Surface((tw, th), pygame.SRCALPHA)
        pygame.draw.polygon(
            mask,
            (255, 255, 255),
            [(0, th // 2), (tw // 2, 0), (tw, th // 2), (tw // 2, th)],
        )
        tex = _ground_tex.copy()
        tex.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(tex, (px, py))

    # outline
    pygame.draw.polygon(screen, OUTLINE_COLOR, [top, right, bottom, left], width=1)

    # building icon
    bld = cell["building"]
    if bld:
        cx, cy, sz = px + tw // 2, py + th // 2, tw // 4
        if bld.shape == "square":
            pygame.draw.rect(screen, bld.color, (cx - sz, cy - sz, 2 * sz, 2 * sz))
        elif bld.shape == "circle":
            pygame.draw.circle(screen, bld.color, (cx, cy), sz // 2)
        elif bld.shape == "triangle":
            pts = [(cx, cy - sz), (cx - sz, cy + sz), (cx + sz, cy + sz)]
            pygame.draw.polygon(screen, bld.color, pts)


def draw_grid(screen, tile_data, tw, th, ox, oy):
    for yy, row in enumerate(tile_data):
        for xx, cell in enumerate(row):
            draw_block(screen, xx, yy, cell, tw, th, ox, oy)


def draw_highlight(screen, x, y, tw, th, ox, oy):
    px, py = grid_to_screen(x, y, tw, th, ox, oy)
    pygame.draw.polygon(
        screen,
        HIGHLIGHT_COLOR,
        [
            (px + tw // 2, py),
            (px + tw, py + th // 2),
            (px + tw // 2, py + th),
            (px, py + th // 2),
        ],
        width=3,
    )
