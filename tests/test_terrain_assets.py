import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from pathlib import Path

import pygame
import pytest

from dawn_tactics.campaigns import Difficulty
from dawn_tactics.domain import Position, Terrain
from dawn_tactics.game import (
    BLUE_ZONE_COLOR,
    CELL_SIZE,
    PANEL,
    PANEL_LEFT,
    TERRAIN_ASSET_DIR,
    TERRAIN_ASSET_FILES,
    TERRAIN_IMAGE_SIZE,
    GameApp,
    _load_terrain_images,
)


@pytest.fixture(autouse=True)
def pygame_display() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def app() -> GameApp:
    game = GameApp(Difficulty.NORMAL)
    yield game


def test_terrain_asset_registry_names_the_packaged_files() -> None:
    assert TERRAIN_ASSET_FILES == {"sea": "sea.png", "building": "building.png"}


def test_terrain_assets_load_as_scaled_alpha_surfaces() -> None:
    images = _load_terrain_images()

    assert set(images) == {"sea", "building"}
    assert all((TERRAIN_ASSET_DIR / filename).is_file() for filename in TERRAIN_ASSET_FILES.values())
    assert all(image.get_size() == (CELL_SIZE - 2, CELL_SIZE - 2) for image in images.values())
    assert all(image.get_flags() & pygame.SRCALPHA for image in images.values())


def test_terrain_image_loader_skips_missing_and_invalid_files(tmp_path: Path) -> None:
    (tmp_path / "sea.png").write_bytes(b"not a png")

    assert _load_terrain_images(asset_dir=tmp_path) == {}


@pytest.mark.parametrize(
    ("kind", "color"),
    (("sea", (20, 120, 220)), ("building", (190, 105, 45))),
)
def test_draw_terrain_tile_blits_cached_image_at_the_tile_center(
    app: GameApp,
    kind: str,
    color: tuple[int, int, int],
) -> None:
    image = pygame.Surface(TERRAIN_IMAGE_SIZE, pygame.SRCALPHA)
    image.fill(color)
    app.terrain_images = {kind: image}
    rect = pygame.Rect(100, 100, CELL_SIZE, CELL_SIZE)

    app._draw_terrain_tile(Terrain(kind, Position(0, 0)), rect)

    assert app.screen.get_at(rect.center)[:3] == color


@pytest.mark.parametrize("kind", ("sea", "building"))
def test_draw_terrain_tile_uses_a_visible_procedural_fallback(
    app: GameApp,
    kind: str,
) -> None:
    app.terrain_images = {}
    rect = pygame.Rect(100, 100, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(app.screen, BLUE_ZONE_COLOR, rect)

    app._draw_terrain_tile(Terrain(kind, Position(0, 0)), rect)

    assert app.screen.get_at(rect.center)[:3] != BLUE_ZONE_COLOR


def test_local_game_render_keeps_terrain_tiles_and_units_in_their_layers(
    app: GameApp,
) -> None:
    sea_color = (20, 120, 220)
    building_color = (190, 105, 45)
    unit_color = (236, 72, 153)
    app.terrain_images = {
        "sea": pygame.Surface(TERRAIN_IMAGE_SIZE, pygame.SRCALPHA),
        "building": pygame.Surface(TERRAIN_IMAGE_SIZE, pygame.SRCALPHA),
    }
    app.terrain_images["sea"].fill(sea_color)
    app.terrain_images["building"].fill(building_color)
    unit_image = pygame.Surface((48, 48), pygame.SRCALPHA)
    unit_image.fill(unit_color)
    app.unit_images = {"infantry": unit_image}
    app._load_local_two_player()
    assert app.controller.place_current_unit("infantry", Position(7, 0)).ok

    app._draw_game()

    for terrain in app.controller.battle.terrain:
        expected_color = sea_color if terrain.kind == "sea" else building_color
        assert app.screen.get_at(app._cell_center(terrain.position))[:3] == expected_color
    assert app.screen.get_at(app._cell_center(Position(7, 0)))[:3] == unit_color
    assert app.screen.get_at((PANEL_LEFT + 10, 30))[:3] == PANEL
