from pathlib import Path

import pygame
import pytest

from dawn_tactics.campaigns import Difficulty
from dawn_tactics.domain import Infantry, Position, Team
from dawn_tactics.game import (
    BACKGROUND,
    BATTLE_UNIT_IMAGE_SIZE,
    BLUE,
    CARD_UNIT_IMAGE_SIZE,
    GameApp,
    UNIT_ASSET_DIR,
    UNIT_ASSET_FILES,
    UNIT_KINDS,
    _load_unit_images,
)


@pytest.fixture
def pygame_display() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def app() -> GameApp:
    game = GameApp(Difficulty.NORMAL)
    yield game
    pygame.quit()


def test_unit_asset_registry_matches_every_unit_kind() -> None:
    assert UNIT_ASSET_FILES == {
        "infantry": "infantry.png",
        "anti_tank": "anti_tank.png",
        "tank": "tank.png",
        "artillery": "artillery.png",
        "machine_gun": "machine_gun.png",
        "cavalry": "cavalry.png",
    }
    assert tuple(UNIT_ASSET_FILES) == UNIT_KINDS
    assert all(
        (UNIT_ASSET_DIR / filename).is_file()
        for filename in UNIT_ASSET_FILES.values()
    )


@pytest.mark.parametrize("size", [BATTLE_UNIT_IMAGE_SIZE, CARD_UNIT_IMAGE_SIZE])
def test_load_unit_images_scales_every_asset(
    pygame_display: None,
    size: tuple[int, int],
) -> None:
    images = _load_unit_images(size)

    assert set(images) == set(UNIT_ASSET_FILES)
    assert all(image.get_size() == size for image in images.values())
    assert all(image.get_flags() & pygame.SRCALPHA for image in images.values())


def test_load_unit_images_skips_missing_and_invalid_files(
    pygame_display: None,
    tmp_path: Path,
) -> None:
    valid = pygame.Surface((12, 12), pygame.SRCALPHA)
    valid.fill((240, 220, 180, 255))
    pygame.image.save(valid, tmp_path / "tank.png")
    (tmp_path / "infantry.png").write_text("not a png", encoding="utf-8")

    images = _load_unit_images((8, 8), tmp_path)

    assert set(images) == {"tank"}
    assert images["tank"].get_size() == (8, 8)


def test_draw_unit_visual_blits_cached_image_over_team_plate(app: GameApp) -> None:
    marker = (17, 219, 83, 255)
    image = pygame.Surface(BATTLE_UNIT_IMAGE_SIZE, pygame.SRCALPHA)
    image.fill((0, 0, 0, 0))
    pygame.draw.rect(image, marker, pygame.Rect(20, 20, 8, 8))
    app.unit_images = {"infantry": image}
    unit = Infantry(1, Team.BLUE, Position(9, 3))
    center = (160, 200)
    app.screen.fill(BACKGROUND)

    used_image = app._draw_unit_visual(unit, center, BLUE)

    assert used_image
    assert app.screen.get_at(center) == marker
    assert app.screen.get_at((center[0] + 20, center[1])).b > 150


def test_draw_unit_visual_uses_shape_fallback_when_asset_is_missing(
    app: GameApp,
) -> None:
    app.unit_images = {}
    unit = Infantry(1, Team.BLUE, Position(9, 3))
    center = (160, 200)
    app.screen.fill(BACKGROUND)

    used_image = app._draw_unit_visual(unit, center, BLUE)

    assert not used_image
    assert app.screen.get_at(center) != BACKGROUND


def test_draw_unit_card_visual_blits_cached_image(app: GameApp) -> None:
    marker = (214, 137, 29, 255)
    image = pygame.Surface(CARD_UNIT_IMAGE_SIZE, pygame.SRCALPHA)
    image.fill(marker)
    app.unit_card_images = {"tank": image}
    card = pygame.Rect(100, 100, 174, 92)
    app.screen.fill(BACKGROUND)

    used_image = app._draw_unit_card_visual("tank", card)

    assert used_image
    assert app.screen.get_at((card.x + 27, card.centery)) == marker


def test_draw_unit_card_visual_uses_shape_fallback(app: GameApp) -> None:
    app.unit_card_images = {}
    card = pygame.Rect(100, 100, 174, 92)
    app.screen.fill(BACKGROUND)

    used_image = app._draw_unit_card_visual("tank", card)

    assert not used_image
    assert app.screen.get_at((card.x + 27, card.centery)) != BACKGROUND
