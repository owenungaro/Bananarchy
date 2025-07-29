import pygame, world, config

# unpack config
MARGIN_RATIO = config.TILE_MARGIN_RATIO
OUTLINE_COLOR = config.COLORS["outline"]
HIGHLIGHT_COLOR = config.COLORS["highlight"]
SHADE_FACTOR = config.SIDE_SHADE_FACTOR


def calculate_scaling(sw: int, sh: int):
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
    mw, mh = config.MAP_WIDTH, config.MAP_HEIGHT
    for yy in range(mh):
        for xx in range(mw):
            px, py = grid_to_screen(xx, yy, tw, th, ox, oy)
            if point_in_diamond(mx, my, px, py, tw, th):
                return xx, yy
    return None, None


def draw_block(screen, x, y, cell, tw, th, ox, oy):
    px, py = grid_to_screen(x, y, tw, th, ox, oy)
    side_h = th // 2

    # corners of the diamond
    top = (px + tw // 2, py)
    right = (px + tw, py + th // 2)
    bottom = (px + tw // 2, py + th)
    left = (px, py + th // 2)

    # center point for splitting
    cx, cy = px + tw // 2, py + th // 2

    # get base color
    terrain = world.TERRAINS[cell["terrain"]]
    base_col = terrain.color

    # choose facet multipliers (light from top-left)
    # order: top→right→bottom→left
    # top facet faces the light best, bottom faces it least
    fac_mul = [1.00, 0.85, 0.75, 0.90]

    # build facets
    facets = [
        ([top, (cx, cy), right], fac_mul[0]),
        ([right, (cx, cy), bottom], fac_mul[1]),
        ([bottom, (cx, cy), left], fac_mul[2]),
        ([left, (cx, cy), top], fac_mul[3]),
    ]

    # draw side faces
    left_col = tuple(int(c * SHADE_FACTOR) for c in base_col)
    right_col = tuple(int(c * (SHADE_FACTOR + 0.1)) for c in base_col)
    bottom_left_face = [
        left,
        bottom,
        (bottom[0], bottom[1] + side_h),
        (left[0], left[1] + side_h),
    ]
    bottom_right_face = [
        right,
        bottom,
        (bottom[0], bottom[1] + side_h),
        (right[0], right[1] + side_h),
    ]
    pygame.draw.polygon(screen, left_col, bottom_left_face)
    pygame.draw.polygon(screen, right_col, bottom_right_face)

    # draw top‑face facets
    for pts, m in facets:
        col = tuple(int(c * m) for c in base_col)
        pygame.draw.polygon(screen, col, pts)

    # outline
    pygame.draw.polygon(screen, OUTLINE_COLOR, [top, right, bottom, left], width=1)

    # building icon (unchanged)
    bld = cell["building"]
    if bld:
        icon_cx = px + tw // 2
        icon_cy = py + th // 2
        sz = tw // 4
        if bld.shape == "square":
            h = sz // 2
            pygame.draw.rect(
                screen, bld.color, (icon_cx - h, icon_cy - h, 2 * h, 2 * h)
            )
        elif bld.shape == "circle":
            pygame.draw.circle(screen, bld.color, (icon_cx, icon_cy), sz // 2)
        elif bld.shape == "triangle":
            pts = [
                (icon_cx, icon_cy - sz),
                (icon_cx - sz, icon_cy + sz),
                (icon_cx + sz, icon_cy + sz),
            ]
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
