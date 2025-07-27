# world.py

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
    Building(
        id=4,
        name="Chimp Chest",
        shape="circle",
        color=(255, 0, 0),
        inputs={},
        outputs={},
        allowed_terrains=["base"],
    ),
    Building(
        id=1,
        name="Banana Grove",
        shape="circle",
        color=(255, 255, 100),
        inputs={},
        outputs={"raw_banana": 100},
        allowed_terrains=["forest"],
    ),
    Building(
        id=2,
        name="Bamboo Thicket",
        shape="circle",
        color=(50, 200, 50),
        inputs={},
        outputs={"bamboo": 80},
        allowed_terrains=["forest"],
    ),
    Building(
        id=3,
        name="Clay Pit",
        shape="circle",
        color=(200, 160, 130),
        inputs={},
        outputs={"clay": 40},
        allowed_terrains=["rock"],
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


# World Grid Management


def init_world(width: int, height: int):
    """
    Returns a height x width grid of cells. Each cell:
      - 'building': None or Building
      - 'terrain' : starts as 'base'
      - 'inventory': defaultdict(int)
      - 'level'   : int
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


def update_tile(world, x: int, y: int, b: Building):
    cell = world[y][x]
    cell["building"] = b
    cell["level"] = 1


def place_terrain(world, x: int, y: int, terrain_key: str):
    """
    Paint a terrain type—and if an existing building
    isn't allowed on it, drop that building.
    """
    cell = world[y][x]
    cell["terrain"] = terrain_key
    bld = cell["building"]
    if bld and terrain_key not in bld.allowed_terrains:
        cell["building"] = None


def upgrade_tile(world, x: int, y: int):
    cell = world[y][x]
    if cell["building"] and cell["level"] == 1:
        cell["level"] = 2


def simulate_tick(world):
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
                for res, req in bld.inputs.items():
                    inv[res] -= req * lvl
                for res, prod in bld.outputs.items():
                    inv[res] += prod * lvl
