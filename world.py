# world.py
from collections import defaultdict
from resources import RESOURCES

BUILDINGS = {
    # ── Tier I: Gatherers ───────────────────────────────────────────────────────
    1: {
        "name": "Banana Grove",
        "color": (255, 255, 100),
        "shape": "circle",
        "inputs": {},
        "outputs": {"raw_banana": 100},
    },
    2: {
        "name": "Bamboo Thicket",
        "color": (50, 200, 50),
        "shape": "square",
        "inputs": {},
        "outputs": {"bamboo": 80},
    },
    3: {
        "name": "Clay Pit",
        "color": (200, 160, 130),
        "shape": "triangle",
        "inputs": {},
        "outputs": {"clay": 40},
    },
    # 4: {
    #     "name": "Coconut Grove",
    #     "color": (200, 200, 150),
    #     "shape": "circle",
    #     "inputs": {"clay": 80},
    #     "outputs": {"coconut": 50},
    # },
    # 5: {
    #     "name": "Jungle Quarry",
    #     "color": (120, 120, 120),
    #     "shape": "square",
    #     "inputs": {"clay": 40},
    #     "outputs": {"jungle_stone": 30},
    # },
    # 6: {
    #     "name": "River Mine",
    #     "color": (100, 100, 120),
    #     "shape": "square",
    #     "inputs": {"clay": 60, "jungle_stone": 60},
    #     "outputs": {"ore": 20},
    # },
}

selected_building = 1


def set_selected_building(bid):
    global selected_building
    selected_building = bid


def init_world(width, height):
    """
    Each tile holds:
      - 'building': None or a BUILDINGS entry
      - 'inventory': resource counts
      - 'level': upgrade level (1 or 2)
    """
    return [
        [
            {"building": None, "inventory": defaultdict(int), "level": 1}
            for _ in range(width)
        ]
        for _ in range(height)
    ]


def update_tile(world, x, y, building):
    """Place a building and reset its level to 1."""
    cell = world[y][x]
    cell["building"] = building
    cell["level"] = 1


def upgrade_tile(world, x, y):
    """Upgrade a building once (level 1→2), doubling its I/O."""
    cell = world[y][x]
    if cell["building"] and cell["level"] == 1:
        cell["level"] = 2


def simulate_tick(world):
    """
    Each tick, every building that has enough inputs will:
      - consume (inputs × level)
      - produce (outputs × level)
    """
    H, W = len(world), len(world[0])
    for y in range(H):
        for x in range(W):
            cell = world[y][x]
            bld = cell["building"]
            lvl = cell["level"]
            if not bld:
                continue

            inv = cell["inventory"]
            # Check inputs
            for res, req in bld["inputs"].items():
                if inv[res] < req * lvl:
                    break
            else:
                # Consume inputs
                for res, req in bld["inputs"].items():
                    inv[res] -= req * lvl
                # Produce outputs
                for res, prod in bld["outputs"].items():
                    inv[res] += prod * lvl
