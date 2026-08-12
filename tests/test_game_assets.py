from pathlib import Path

import pygame
import pytest

from dawn_tactics.game import (
    BATTLE_UNIT_IMAGE_SIZE,
    CARD_UNIT_IMAGE_SIZE,
    UNIT_ASSET_DIR,
    UNIT_ASSET_FILES,
    _load_unit_images,
)


@pytest.fixture
def pygame_display() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def test_unit_asset_registry_matches_every_unit_kind() -> None:
    assert UNIT_ASSET_FILES == {
        "infantry": "infantry.png",
        "anti_tank": "anti_tank.png",
        "tank": "tank.png",
        "artillery": "artillery.png",
    }
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
