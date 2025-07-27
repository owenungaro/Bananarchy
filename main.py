import pygame
import sys
import world  # <— import the module
from world import init_world, update_tile, BUILDINGS, set_selected_building
from render import draw_grid, calculate_scaling, find_clicked_tile, draw_highlight

# Pygame init
pygame.init()
screen = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
pygame.display.set_caption("Isometric Grid Game")

# World setup
MAP_WIDTH, MAP_HEIGHT = 10, 10
tile_data = init_world(MAP_WIDTH, MAP_HEIGHT)

# Build list and cycling index
build_list = sorted(BUILDINGS.keys())
current_idx = build_list.index(
    world.selected_building
)  # <— use world.selected_building

clock = pygame.time.Clock()
running = True

# Font for UI
font = pygame.font.SysFont(None, 24)

while running:
    # Resize & recalc
    sw, sh = screen.get_size()
    tile_w, tile_h, origin_x, origin_y = calculate_scaling(
        sw, sh, MAP_WIDTH, MAP_HEIGHT
    )

    # Mouse hover
    mx, my = pygame.mouse.get_pos()
    hover_x, hover_y = find_clicked_tile(
        mx, my, tile_w, tile_h, origin_x, origin_y, MAP_WIDTH, MAP_HEIGHT
    )

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            gx, gy = find_clicked_tile(
                mx, my, tile_w, tile_h, origin_x, origin_y, MAP_WIDTH, MAP_HEIGHT
            )
            if gx is not None:
                # place the building using the up‑to‑date world.selected_building
                update_tile(tile_data, gx, gy, BUILDINGS[world.selected_building])

        elif event.type == pygame.KEYDOWN:
            # Cycle backwards: Q
            if event.key == pygame.K_q:
                current_idx = (current_idx - 1) % len(build_list)
                set_selected_building(build_list[current_idx])

            # Cycle forwards: E
            elif event.key == pygame.K_e:
                current_idx = (current_idx + 1) % len(build_list)
                set_selected_building(build_list[current_idx])

            # Direct number keys 1–9
            elif pygame.K_1 <= event.key <= pygame.K_9:
                key_num = event.key - pygame.K_0
                if key_num in BUILDINGS:
                    set_selected_building(key_num)
                    current_idx = build_list.index(key_num)

    # Draw world
    screen.fill((50, 50, 50))
    draw_grid(screen, tile_data, tile_w, tile_h, origin_x, origin_y)

    # Highlight hover
    if hover_x is not None:
        draw_highlight(screen, hover_x, hover_y, tile_w, tile_h, origin_x, origin_y)

    # Draw UI: current selection (read from world.selected_building)
    sel_id = world.selected_building
    sel_name = BUILDINGS[sel_id]["name"]
    txt = font.render(f"Selected [{sel_id}]: {sel_name}", True, (255, 255, 255))
    screen.blit(txt, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
