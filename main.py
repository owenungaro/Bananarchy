import pygame, sys
import config, world, resources
from world import init_world, update_tile, place_terrain
import render
from collections import defaultdict

pygame.init()
screen = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
pygame.display.set_caption("Bananarchy")

tile_data = init_world(config.MAP_WIDTH, config.MAP_HEIGHT)
clock, font = pygame.time.Clock(), pygame.font.SysFont(None, 24)

TICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TICK_EVENT, 2000)

PAGE_TOOLS = 0
PAGE_ERASE = 1
PAGE_INFO = 2
PAGE_STATS = 3
current_page = PAGE_TOOLS
info_cell = None
expanded_resource = None

running = True
while running:
    sw, sh = screen.get_size()
    usable_sw = sw - config.PANEL_WIDTH
    tw, th, ox, oy = render.calculate_scaling(usable_sw, sh)

    mx, my = pygame.mouse.get_pos()
    if mx < usable_sw:
        hover = render.find_clicked_tile(mx, my, tw, th, ox, oy)
    else:
        hover = (None, None)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((ev.w, ev.h), pygame.RESIZABLE)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if mx > usable_sw:
                btn_y = config.PANEL_PADDING
                btn_h = font.get_height() + config.PANEL_PADDING
                btn_x = usable_sw + config.PANEL_PADDING

                if btn_y <= my < btn_y + btn_h:
                    current_page = PAGE_TOOLS
                elif btn_y + btn_h <= my < btn_y + 2 * btn_h:
                    current_page = PAGE_ERASE
                elif btn_y + 2 * btn_h <= my < btn_y + 3 * btn_h:
                    current_page = PAGE_INFO
                elif btn_y + 3 * btn_h <= my < btn_y + 4 * btn_h:
                    current_page = PAGE_STATS
                elif current_page == PAGE_INFO and info_cell:
                    line_count = 4
                    start_y = btn_y + 4 * btn_h
                    text_y = start_y + line_count * (font.get_height() + 2)
                    up_x = btn_x
                    up_y = text_y + config.PANEL_PADDING
                    up_w = config.PANEL_WIDTH - 2 * config.PANEL_PADDING
                    up_h = font.get_height() + config.PANEL_PADDING // 2
                    upgr_btn = pygame.Rect(up_x, up_y, up_w, up_h)
                    if upgr_btn.collidepoint(mx, my):
                        gx, gy = info_cell
                        world.upgrade_tile(tile_data, gx, gy)
                elif current_page == PAGE_TOOLS:
                    start_y = btn_y + 4 * btn_h
                    idx = (my - start_y) // (config.ICON_SIZE + config.PANEL_PADDING)
                    if 0 <= idx < len(world.TOOLS):
                        world.set_selected_tool(idx)
                elif current_page == PAGE_STATS:
                    # Detect which resource was clicked
                    y = btn_y + 4 * btn_h
                    for res_key in resources.RESOURCES:
                        rect = pygame.Rect(
                            btn_x, y, config.PANEL_WIDTH, font.get_height()
                        )
                        if rect.collidepoint(mx, my):
                            expanded_resource = (
                                res_key if expanded_resource != res_key else None
                            )
                        y += font.get_height() + 2
                        if expanded_resource == res_key:
                            for _ in range(3):  # space for a few lines of building info
                                y += font.get_height() + 2
            else:
                gx, gy = render.find_clicked_tile(mx, my, tw, th, ox, oy)
                if gx is not None:
                    if current_page == PAGE_ERASE:
                        tile_data[gy][gx]["building"] = None
                    elif current_page == PAGE_INFO:
                        info_cell = (gx, gy)
                    else:
                        kind, key = world.get_selected_tool()
                        cell = tile_data[gy][gx]
                        if kind == "building":
                            bld = world.BUILDINGS[key]
                            if cell["terrain"] in bld.allowed_terrains:
                                update_tile(tile_data, gx, gy, bld)
                        else:
                            place_terrain(tile_data, gx, gy, key)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_q:
                world.set_selected_tool(world._selected_tool - 1)
            elif ev.key == pygame.K_e:
                world.set_selected_tool(world._selected_tool + 1)
        elif ev.type == TICK_EVENT:
            world.simulate_tick(tile_data)

    screen.fill(config.COLORS["background"])
    render.draw_grid(screen, tile_data, tw, th, ox, oy)
    if hover[0] is not None:
        render.draw_highlight(screen, hover[0], hover[1], tw, th, ox, oy)

    pygame.draw.rect(
        screen, config.COLORS["panel_bg"], (usable_sw, 0, config.PANEL_WIDTH, sh)
    )

    btn_x = usable_sw + config.PANEL_PADDING
    btn_y = config.PANEL_PADDING
    btn_h = font.get_height() + config.PANEL_PADDING
    screen.blit(font.render("Tools", True, (255, 255, 255)), (btn_x, btn_y))
    screen.blit(font.render("Erase", True, (255, 255, 255)), (btn_x, btn_y + btn_h))
    screen.blit(font.render("Info", True, (255, 255, 255)), (btn_x, btn_y + 2 * btn_h))
    screen.blit(font.render("Stats", True, (255, 255, 255)), (btn_x, btn_y + 3 * btn_h))

    if current_page == PAGE_TOOLS:
        highlight_y = btn_y
    elif current_page == PAGE_ERASE:
        highlight_y = btn_y + btn_h
    elif current_page == PAGE_INFO:
        highlight_y = btn_y + 2 * btn_h
    else:
        highlight_y = btn_y + 3 * btn_h
    w = config.PANEL_WIDTH - 2 * config.PANEL_PADDING
    pygame.draw.rect(
        screen, config.COLORS["highlight"], (btn_x - 2, highlight_y - 2, w, btn_h), 2
    )

    if current_page == PAGE_TOOLS:
        start_y = btn_y + 4 * btn_h
        for i, (kind, key) in enumerate(world.TOOLS):
            x0 = usable_sw + config.PANEL_PADDING
            y0 = start_y + i * (config.ICON_SIZE + config.PANEL_PADDING)
            if kind == "terrain":
                col = world.TERRAINS[key].color
                pts = [
                    (x0 + config.ICON_SIZE // 2, y0),
                    (x0 + config.ICON_SIZE, y0 + config.ICON_SIZE // 2),
                    (x0 + config.ICON_SIZE // 2, y0 + config.ICON_SIZE),
                    (x0, y0 + config.ICON_SIZE // 2),
                ]
                pygame.draw.polygon(screen, col, pts)
            else:
                b = world.BUILDINGS[key]
                cx = x0 + config.ICON_SIZE // 2
                cy = y0 + config.ICON_SIZE // 2
                sz = config.ICON_SIZE // 2 - 4
                pygame.draw.rect(screen, b.color, (cx - sz, cy - sz, 2 * sz, 2 * sz))
            if i == world._selected_tool:
                pygame.draw.rect(
                    screen,
                    config.COLORS["highlight"],
                    (x0 - 2, y0 - 2, config.ICON_SIZE + 4, config.ICON_SIZE + 4),
                    2,
                )

    if current_page == PAGE_INFO and info_cell:
        gx, gy = info_cell
        cell = tile_data[gy][gx]
        terrain = cell["terrain"]
        bld = cell["building"]
        info_lines = [
            f"Tile ({gx},{gy})",
            f"Terrain: {terrain}",
        ]
        if bld:
            info_lines.append(f"Building: {bld.name}")
            info_lines.append(f"Level: {cell['level']}")
        else:
            info_lines.append("Building: None")
        text_y = btn_y + 4 * btn_h
        for line in info_lines:
            screen.blit(font.render(line, True, (255, 255, 255)), (btn_x, text_y))
            text_y += font.get_height() + 2
        if bld and bld.name not in ("Chimp Chest", "Conveyer Belt"):
            up_x = btn_x
            up_y = text_y + config.PANEL_PADDING
            up_w = config.PANEL_WIDTH - 2 * config.PANEL_PADDING
            up_h = font.get_height() + config.PANEL_PADDING // 2
            pygame.draw.rect(screen, config.COLORS["side1"], (up_x, up_y, up_w, up_h))
            screen.blit(
                font.render("Upgrade", True, (255, 255, 255)),
                (up_x + config.PANEL_PADDING // 2, up_y + config.PANEL_PADDING // 2),
            )

    elif current_page == PAGE_STATS:
        y = btn_y + 4 * btn_h
        totals = defaultdict(int)
        sources = defaultdict(list)
        for row in tile_data:
            for cell in row:
                b = cell["building"]
                lvl = cell["level"]
                if not b:
                    continue
                for res, amt in b.outputs.items():
                    net = amt * (2 ** (lvl - 1))
                    totals[res] += net
                    sources[res].append((b.name, lvl, net, "green"))
                for res, amt in b.inputs.items():
                    cost = amt * (2 ** (lvl - 1))
                    totals[res] -= cost
                    sources[res].append((b.name, lvl, -cost, "red"))

        for res_key in resources.RESOURCES:
            net = totals.get(res_key, 0)
            color = (
                (0, 255, 0)
                if net > 0
                else (255, 100, 100) if net < 0 else (255, 255, 255)
            )
            screen.blit(
                font.render(
                    f"{resources.RESOURCES[res_key]['name']}: {net:+}", True, color
                ),
                (btn_x, y),
            )
            y += font.get_height() + 2
            if res_key == expanded_resource:
                for bname, lvl, amt, tone in sources.get(res_key, []):
                    tone_col = (0, 255, 0) if tone == "green" else (255, 100, 100)
                    screen.blit(
                        font.render(f"  {bname} Lv{lvl}: {amt:+}", True, tone_col),
                        (btn_x + 10, y),
                    )
                    y += font.get_height() + 2

    # Top-left resource count
    totals = defaultdict(int)
    for row in tile_data:
        for cell in row:
            b = cell["building"]
            if b and b.name == "Chimp Chest":
                for res, qty in cell["inventory"].items():
                    totals[res] += qty
    y_off = 10 + font.get_height() + 8
    for res_key, info in resources.RESOURCES.items():
        qty = totals.get(res_key, 0)
        screen.blit(
            font.render(f"{info['name']}: {qty}", True, (255, 255, 255)), (10, y_off)
        )
        y_off += font.get_height() + 2

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
