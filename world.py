from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List, Tuple
import config


@dataclass
class Building:
    id: int
    name: str
    shape: str
    color: Tuple[int, int, int]
    inputs: Dict[str, int]
    outputs: Dict[str, int]
    allowed_terrains: List[str] = field(default_factory=list)


@dataclass
class Terrain:
    key: str
    name: str
    color: Tuple[int, int, int]


TERRAINS_LIST: List[Terrain] = [
    Terrain("base", "Base", (240, 240, 240)),
    Terrain("forest", "Forest", (34, 139, 34)),
    Terrain("rock", "Rock", (128, 128, 128)),
]
TERRAINS: Dict[str, Terrain] = {t.key: t for t in TERRAINS_LIST}

BUILDINGS_LIST: List[Building] = [
    Building(1, "Chimp Chest", "circle", (255, 0, 0), {}, {}, ["base"]),
    Building(2, "Conveyer Belt", "square", (0, 0, 0), {}, {}, ["base"]),
    Building(
        3, "Banana Grove", "circle", (255, 255, 100), {}, {"raw_banana": 1}, ["forest"]
    ),
    Building(
        4, "Bamboo Thicket", "circle", (50, 200, 50), {}, {"bamboo": 1}, ["forest"]
    ),
    Building(5, "Clay Pit", "circle", (200, 160, 130), {}, {"clay": 1}, ["rock"]),
    Building(
        6,
        "Splinter Shack",
        "square",
        (180, 120, 40),
        {"bamboo": 1},
        {"split_bamboo": 2},
        ["forest"],
    ),
    Building(
        7,
        "Sticky Press",
        "circle",
        (255, 230, 60),
        {"raw_banana": 2},
        {"banana_pulp": 2},
        ["base"],
    ),
    Building(
        8,
        "Mud Kiln",
        "triangle",
        (170, 100, 80),
        {"clay": 2},
        {"ceramic_shard": 2},
        ["base"],
    ),
    Building(
        9,
        "Rope Twister",
        "circle",
        (100, 180, 100),
        {"raw_banana": 1, "bamboo": 1},
        {"jungle_rope": 2},
        ["base"],
    ),
    Building(
        10,
        "Brick Smusher",
        "square",
        (150, 70, 50),
        {"clay": 2, "split_bamboo": 2},
        {"mudbrick": 2},
        ["base"],
    ),
]
BUILDINGS: Dict[int, Building] = {b.id: b for b in BUILDINGS_LIST}

TOOLS: List[Tuple[str, object]] = [("terrain", t.key) for t in TERRAINS_LIST] + [
    ("building", b.id) for b in BUILDINGS_LIST
]
_selected_tool: int = 0


def set_selected_tool(idx: int):
    global _selected_tool
    _selected_tool = idx % len(TOOLS)


def get_selected_tool() -> Tuple[str, object]:
    return TOOLS[_selected_tool]


# World Grid management
def init_world(width: int, height: int):
    """
    Create a height X width grid of cells. Each cell is a dict:
      - 'building': None or a Building
      - 'terrain': starts as 'base'
      - 'inventory': defaultdict(int)
      - 'level': int
    """
    default = TERRAINS_LIST[0].key  # "base"
    return [
        [
            {
                "building": None,
                "terrain": default,
                "inventory": defaultdict(int),
                "level": 1,
            }
            for _ in range(width)
        ]
        for _ in range(height)
    ]


def update_tile(world_grid, x: int, y: int, b: Building):
    cell = world_grid[y][x]
    cell["building"] = b
    cell["level"] = 1


def place_terrain(world_grid, x: int, y: int, terrain_key: str):
    """
    Paint a terrain type—and if an existing building
    isn't allowed on it, remove that building.
    """
    cell = world_grid[y][x]
    cell["terrain"] = terrain_key
    bld = cell["building"]
    if bld and terrain_key not in bld.allowed_terrains:
        cell["building"] = None


def upgrade_tile(world_grid, x, y):
    cell = world_grid[y][x]
    cell["level"] += 1


def simulate_tick(world_grid):
    H = len(world_grid)
    W = len(world_grid[0]) if H else 0

    for y in range(H):
        for x in range(W):
            cell = world_grid[y][x]
            bld = cell["building"]
            lvl = cell["level"]
            if not bld or not bld.outputs:
                continue

            # Step 1: Find reachable chimp chests
            visited = set()
            queue = [(x, y)]
            reachable_chests = []

            while queue:
                cx, cy = queue.pop(0)
                if (cx, cy) in visited:
                    continue
                visited.add((cx, cy))

                for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                    nx, ny = cx + dx, cy + dy
                    if not (0 <= nx < W and 0 <= ny < H):
                        continue
                    neighbor = world_grid[ny][nx]
                    nbld = neighbor["building"]

                    if (nx, ny) in visited:
                        continue
                    if nbld:
                        if nbld.name == "Chimp Chest":
                            reachable_chests.append((nx, ny))
                        elif nbld.name == "Conveyer Belt":
                            queue.append((nx, ny))

            # Step 2: Check if all inputs are available in any single chimp chest
            for chest_x, chest_y in reachable_chests:
                chest = world_grid[chest_y][chest_x]
                inventory = chest["inventory"]
                if all(inventory[res] >= req * lvl for res, req in bld.inputs.items()):
                    # Step 3: Deduct from chest
                    for res, req in bld.inputs.items():
                        inventory[res] -= req * lvl

                    # Step 4: Produce + deposit output
                    for res, prod in bld.outputs.items():
                        amount = prod * (2 ** (lvl - 1))
                        chest["inventory"][res] += amount
                    break  # only produce once per tick
