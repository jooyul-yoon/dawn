import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from pathlib import Path

import pygame
import pytest

from dawn_tactics.campaigns import Difficulty
from dawn_tactics.domain import Position
from dawn_tactics.game import (
    CELL_SIZE,
    GRID_HEIGHT,
    GRID_LEFT,
    GRID_TOP,
    GRID_WIDTH,
    PANEL_LEFT,
    WINDOW_SIZE,
    GameApp,
    unit_rule_text,
)


@pytest.fixture
def app() -> GameApp:
    game = GameApp(Difficulty.NORMAL)
    yield game
    pygame.quit()


def test_game_startup_validates_student_rules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "dawn_tactics.game.validate_student_rules",
        lambda: calls.append("validated"),
    )
    game = GameApp(Difficulty.NORMAL)
    assert calls == ["validated"]
    pygame.quit()


def test_unit_cards_show_six_non_overlapping_choices(app: GameApp) -> None:
    rects = app._unit_card_rects()
    values = tuple(rects.values())
    assert tuple(rects) == (
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    )
    assert all(
        not first.colliderect(second)
        for index, first in enumerate(values)
        for second in values[index + 1 :]
    )
    assert all(not rect.colliderect(app._start_rect()) for rect in values)
    assert not app._start_rect().colliderect(app._restart_rect())
    assert not app._start_rect().colliderect(app._menu_rect())
    assert not app._restart_rect().colliderect(app._status_rect())
    assert not app._menu_rect().colliderect(app._status_rect())
    grid_rect = pygame.Rect(GRID_LEFT, GRID_TOP, GRID_WIDTH, GRID_HEIGHT)
    assert all(not rect.colliderect(grid_rect) for rect in values)


def test_expanded_window_grid_and_panel_geometry(app: GameApp) -> None:
    assert WINDOW_SIZE == (1408, 888)
    assert app.screen.get_size() == WINDOW_SIZE
    assert GRID_WIDTH == 14 * CELL_SIZE == 896
    assert GRID_HEIGHT == 10 * CELL_SIZE == 640
    assert PANEL_LEFT == GRID_LEFT + GRID_WIDTH + 32 == 968


def test_mouse_conversion_reaches_new_bottom_right_cell(app: GameApp) -> None:
    inside = (GRID_LEFT + GRID_WIDTH - 1, GRID_TOP + GRID_HEIGHT - 1)

    assert app._mouse_to_grid(inside) == Position(9, 13)
    assert app._mouse_to_grid((GRID_LEFT + GRID_WIDTH, inside[1])) is None
    assert app._mouse_to_grid((inside[0], GRID_TOP + GRID_HEIGHT)) is None


def test_number_keys_five_and_six_select_new_units(app: GameApp) -> None:
    app._load_campaign(0)
    app._handle_key(pygame.K_5)
    assert app.selected_kind == "machine_gun"
    app._handle_key(pygame.K_6)
    assert app.selected_kind == "cavalry"


def test_special_rule_text_does_not_claim_one_fixed_damage() -> None:
    assert unit_rule_text("machine_gun") == "DMG BY ARMOR  RNG 3"
    assert unit_rule_text("cavalry") == "DMG BY TYPE  RNG 1"


def test_rule_text_fits_beside_each_card_visual(app: GameApp) -> None:
    for kind, rect in app._unit_card_rects().items():
        text_width = app.fonts["card_rule"].size(unit_rule_text(kind))[0]
        assert text_width <= rect.right - (rect.x + 56)


def test_six_card_setup_screen_renders(tmp_path: Path, app: GameApp) -> None:
    app._load_campaign(0)
    assert app.controller.place_blue_unit("machine_gun", Position(9, 5)).ok
    assert app.controller.place_blue_unit("cavalry", Position(9, 7)).ok
    app.draw()
    output = tmp_path / "day-2-setup.png"
    pygame.image.save(app.screen, output)
    assert output.stat().st_size > 10_000
