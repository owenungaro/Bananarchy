import pygame, sys
import config, world, resources
from world import init_world, update_tile, place_terrain
import render
from collections import defaultdict

pygame.init()
screen = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
pygame.display.set_caption("Bananarchy")

# initialize map
tile_data = init_world(config.MAP_WIDTH, config.MAP_HEIGHT)
clock, font = pygame.time.Clock(), pygame.font.SysFont(None, 24)

# tick every 2 seconds
TICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TICK_EVENT, 2000)

running = True
while running:
    sw, sh = screen.get_size()
    usable_sw = sw - config.PANEL_WIDTH
    tw, th, ox, oy = render.calculate_scaling(usable_sw, sh)

    mx, my = pygame.mouse.get_pos()
    # compute hover only when over map
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
            # sidebar click?
            if mx > usable_sw:
                idx = (my - config.PANEL_PADDING) // (
                    config.ICON_SIZE + config.PANEL_PADDING
                )
                if 0 <= idx < len(world.TOOLS):
                    world.set_selected_tool(idx)
            else:
                # map click: paint terrain or place building
                gx, gy = render.find_clicked_tile(mx, my, tw, th, ox, oy)
                if gx is not None:
                    kind, key = world.get_selected_tool()
                    cell = tile_data[gy][gx]
                    if kind == "building":
                        bld = world.BUILDINGS[key]
                        if cell["terrain"] in bld.allowed_terrains:
                            update_tile(tile_data, gx, gy, bld)
                        else:
                            print(f"Cannot place {bld.name} on '{cell['terrain']}'")
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

    # sidebar background
    pygame.draw.rect(
        screen,
        config.COLORS["panel_bg"],
        (usable_sw, 0, config.PANEL_WIDTH, sh),
    )

    # draw sidebar icons
    for i, (kind, key) in enumerate(world.TOOLS):
        x0 = usable_sw + config.PANEL_PADDING
        y0 = config.PANEL_PADDING + i * (config.ICON_SIZE + config.PANEL_PADDING)

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
                width=2,
            )

    # display mode text
    kind, key = world.get_selected_tool()
    name = world.BUILDINGS[key].name if kind == "building" else world.TERRAINS[key].name
    screen.blit(
        font.render(f"Mode: {kind.capitalize()} -> {name}", True, (255, 255, 255)),
        (10, 10),
    )

    # Display inventory
    totals = defaultdict(int)
    for row in tile_data:
        for cell in row:
            bld = cell["building"]
            if bld and bld.name == "Chimp Chest":
                for res, qty in cell["inventory"].items():
                    totals[res] += qty

    y_off = 10 + font.get_height() + 8
    for res_key, info in resources.RESOURCES.items():
        qty = totals.get(res_key, 0)
        text = f"{info['name']}: {qty}"
        screen.blit(font.render(text, True, (255, 255, 255)), (10, y_off))
        y_off += font.get_height() + 2

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
