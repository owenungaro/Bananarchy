from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, List, Tuple
import config


@dataclass
class Building:
    id: int
    name: str
    shape: str  # "circle", "square", "triangle", etc.
    color: Tuple[int, int, int]
    inputs: Dict[str, int]
    outputs: Dict[str, int]


@dataclass
class Terrain:
    key: str  # unique string ID
    name: str
    color: Tuple[int, int, int]


TERRAINS_LIST: List[Terrain] = [
    Terrain("forest", "Forest", (34, 139, 34)),
    Terrain("rock", "Rock", (128, 128, 128)),
]

BUILDINGS_LIST: List[Building] = [
    Building(1, "Banana Grove", "circle", (255, 255, 100), {}, {"raw_banana": 100}),
    Building(2, "Bamboo Thicket", "circle", (50, 200, 50), {}, {"bamboo": 80}),
    Building(3, "Clay Pit", "circle", (200, 160, 130), {}, {"clay": 40}),
]

# lookup dicts
TERRAINS: Dict[str, Terrain] = {t.key: t for t in TERRAINS_LIST}
BUILDINGS: Dict[int, Building] = {b.id: b for b in BUILDINGS_LIST}

# unified tool list for sidebar: each entry is ("terrain", terrain_key) or ("building", building_id)
TOOLS: List[Tuple[str, object]] = [("terrain", t.key) for t in TERRAINS_LIST] + [
    ("building", b.id) for b in BUILDINGS_LIST
]

_selected_tool: int = 0


def set_selected_tool(idx: int):
    global _selected_tool
    _selected_tool = idx % len(TOOLS)


def get_selected_tool():
    """Returns (kind, key) for the current sidebar selection."""
    return TOOLS[_selected_tool]


# World state management


def init_world(width: int, height: int):
    """
    Create a 2D array of cells. Each cell is a dict:
      - 'building': None or a Building
      - 'terrain' : None or a terrain key
      - 'inventory': defaultdict(int)
      - 'level'   : int
    """
    return [
        [
            {
                "building": None,
                "terrain": None,
                "inventory": defaultdict(int),
                "level": 1,
            }
            for _ in range(width)
        ]
        for _ in range(height)
    ]


def update_tile(world, x: int, y: int, b: Building):
    """Place/replace a building and reset its level."""
    cell = world[y][x]
    cell["building"] = b
    cell["level"] = 1


def place_terrain(world, x: int, y: int, terrain_key: str):
    """Paint a terrain type onto this cell."""
    cell = world[y][x]
    cell["terrain"] = terrain_key


def upgrade_tile(world, x: int, y: int):
    """Example upgrade logic (level 1→2)."""
    cell = world[y][x]
    if cell["building"] and cell["level"] == 1:
        cell["level"] = 2


def simulate_tick(world):
    """Example production logic."""
    for row in world:
        for cell in row:
            bld = cell["building"]
            lvl = cell["level"]
            if not bld:
                continue
            inv = cell["inventory"]
            # check inputs
            for res, req in bld.inputs.items():
                if inv[res] < req * lvl:
                    break
            else:
                # consume & produce
                for res, req in bld.inputs.items():
                    inv[res] -= req * lvl
                for res, prod in bld.outputs.items():
                    inv[res] += prod * lvl
