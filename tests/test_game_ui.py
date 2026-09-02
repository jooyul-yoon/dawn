import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from pathlib import Path

import pygame
import pytest

from dawn_tactics.campaigns import VERIFIED_BLUE_LAYOUTS, Difficulty
from dawn_tactics.controller import MatchMode
from dawn_tactics.domain import Position, Team
from dawn_tactics.game import (
    BATTLE_HP_BAR_SIZE,
    BACKGROUND,
    BLUE_ZONE_COLOR,
    CELL_SIZE,
    ENEMY_ZONE_COLOR,
    GRID_HEIGHT,
    GRID_LEFT,
    GRID_TOP,
    GRID_WIDTH,
    HP_TEXT_OFFSET_Y,
    NEUTRAL_ZONE_COLOR,
    PANEL_HEIGHT,
    PANEL_LEFT,
    PANEL_WIDTH,
    WINDOW_SIZE,
    GameApp,
    _battle_hp_bar_rect,
    _deployment_zone_label_position,
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


def test_local_two_player_menu_card_fits_below_campaign_cards(app: GameApp) -> None:
    local_rect = app._local_two_player_rect()

    assert local_rect == pygame.Rect(180, 650, 920, 116)
    assert all(not local_rect.colliderect(rect) for rect in app._campaign_rects())
    assert local_rect.bottom < 838


def test_local_two_player_load_resets_setup_ui_state(app: GameApp) -> None:
    app.selected_kind = "tank"
    app.visual_events.append((object(), 0.0))  # type: ignore[arg-type]
    app.simulation_accumulator = 2.0

    app._load_local_two_player()

    assert app.mode == "game"
    assert app.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
    assert app.selected_kind == "infantry"
    assert app.status == "Blue's turn. Select a unit and deploy in the blue zone."
    assert app.visual_events == []
    assert app.simulation_accumulator == 0.0


def test_local_menu_click_starts_local_two_player_setup(app: GameApp) -> None:
    app._handle_click(app._local_two_player_rect().center, 1)

    assert app.mode == "game"
    assert app.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER


def test_local_start_and_pass_buttons_split_without_overlaps(app: GameApp) -> None:
    app._load_local_two_player()

    assert app._start_rect() == pygame.Rect(PANEL_LEFT + 24, 400, 168, 48)
    assert app._pass_rect() == pygame.Rect(PANEL_LEFT + 208, 400, 168, 48)
    assert not app._start_rect().colliderect(app._pass_rect())
    assert not app._start_rect().colliderect(app._restart_rect())
    assert not app._pass_rect().colliderect(app._menu_rect())


def test_local_grid_and_pass_inputs_follow_the_active_team(app: GameApp) -> None:
    app._load_local_two_player()
    blue_cell = app._cell_center(Position(7, 0))
    red_cell = app._cell_center(Position(4, 0))

    app._handle_click(blue_cell, 1)
    assert app.controller.battle.unit_at(Position(7, 0)).team is Team.BLUE
    assert app.controller.active_team is Team.RED
    assert app.status.endswith("Red's turn.")

    app._handle_click(blue_cell, 3)
    assert app.controller.active_team is Team.RED
    assert app.controller.battle.unit_at(Position(7, 0)).team is Team.BLUE

    app._handle_click(red_cell, 1)
    assert app.controller.battle.unit_at(Position(4, 0)).team is Team.RED
    assert app.controller.active_team is Team.BLUE

    app._handle_click(app._pass_rect().center, 1)
    assert app.controller.active_team is Team.RED
    app._handle_key(pygame.K_p)
    assert app.controller.active_team is Team.BLUE


def test_local_result_has_no_next_campaign_button(app: GameApp) -> None:
    app._load_local_two_player()

    _, _, next_rect = app._result_button_rects()

    assert next_rect is None


def test_local_two_player_setup_renders_dual_budget_panel(
    tmp_path: Path,
    app: GameApp,
) -> None:
    app._load_local_two_player()
    app._handle_click(app._cell_center(Position(7, 0)), 1)

    app.draw()
    output = tmp_path / "local-two-player-setup.png"
    pygame.image.save(app.screen, output)

    assert output.stat().st_size > 10_000
    assert app.screen.get_at((42, 26))[:3] != BACKGROUND
    assert app.controller.budget_for(Team.BLUE) == 1_900
    assert app.controller.budget_for(Team.RED) == 2_000


def test_five_row_window_grid_and_panel_geometry(app: GameApp) -> None:
    assert WINDOW_SIZE == (1280, 888)
    assert app.screen.get_size() == WINDOW_SIZE
    assert CELL_SIZE == 56
    assert GRID_WIDTH == 14 * CELL_SIZE == 784
    assert GRID_HEIGHT == 12 * CELL_SIZE == 672
    assert PANEL_LEFT == GRID_LEFT + GRID_WIDTH + 32 == 856
    assert PANEL_WIDTH == 400
    assert PANEL_HEIGHT == GRID_TOP + GRID_HEIGHT - 20 == 802
    assert PANEL_LEFT + PANEL_WIDTH <= WINDOW_SIZE[0]
    assert 20 + PANEL_HEIGHT == GRID_TOP + GRID_HEIGHT


def test_mouse_conversion_reaches_new_bottom_right_cell(app: GameApp) -> None:
    inside = (GRID_LEFT + GRID_WIDTH - 1, GRID_TOP + GRID_HEIGHT - 1)

    assert app._mouse_to_grid(inside) == Position(11, 13)
    assert app._mouse_to_grid((GRID_LEFT + GRID_WIDTH, inside[1])) is None
    assert app._mouse_to_grid((inside[0], GRID_TOP + GRID_HEIGHT)) is None


def test_grid_draws_five_red_two_neutral_and_five_blue_rows(app: GameApp) -> None:
    app._load_campaign(0)
    app.screen.fill((0, 0, 0))
    app._draw_grid()

    samples = tuple(
        app.screen.get_at(
            (
                GRID_LEFT + CELL_SIZE // 2,
                GRID_TOP + row * CELL_SIZE + CELL_SIZE // 2,
            )
        )[:3]
        for row in range(12)
    )

    assert samples == (
        *(ENEMY_ZONE_COLOR for _ in range(5)),
        *(NEUTRAL_ZONE_COLOR for _ in range(2)),
        *(BLUE_ZONE_COLOR for _ in range(5)),
    )


def test_deployment_zone_label_avoids_hard_campaign_three_units() -> None:
    app = GameApp(Difficulty.HARD)
    try:
        app._load_campaign(2)
        app.prepare_demo_layout()
        label_position = _deployment_zone_label_position(
            app.controller.battle.height
        )
        label_rect = app.fonts["tiny"].render(
            "YOUR DEPLOYMENT ZONE",
            True,
            (255, 255, 255),
        ).get_rect(topleft=label_position)
        blue_cells = []
        for unit in app.controller.battle.units:
            if unit.team is not Team.BLUE:
                continue
            center = app._cell_center(unit.position)
            blue_cells.append(
                pygame.Rect(
                    center[0] - CELL_SIZE // 2,
                    center[1] - CELL_SIZE // 2,
                    CELL_SIZE,
                    CELL_SIZE,
                )
            )

        assert all(not label_rect.colliderect(cell) for cell in blue_cells)
    finally:
        pygame.quit()


def test_hp_bar_and_text_fit_inside_a_fifty_six_pixel_cell(app: GameApp) -> None:
    center = app._cell_center(Position(11, 13))
    cell = pygame.Rect(
        center[0] - CELL_SIZE // 2,
        center[1] - CELL_SIZE // 2,
        CELL_SIZE,
        CELL_SIZE,
    )
    bar = _battle_hp_bar_rect(center)
    hp_text = app.fonts["tiny"].render("10", True, (255, 255, 255))
    hp_text_rect = hp_text.get_rect(
        center=(center[0], center[1] + HP_TEXT_OFFSET_Y)
    )

    assert BATTLE_HP_BAR_SIZE == (42, 5)
    assert cell.contains(bar)
    assert bar.top == cell.top + 1
    assert cell.contains(hp_text_rect)


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


@pytest.mark.parametrize("difficulty", (Difficulty.NORMAL, Difficulty.HARD))
@pytest.mark.parametrize("campaign_index", (0, 1, 2))
def test_prepare_demo_layout_uses_verified_campaign_data(
    difficulty: Difficulty,
    campaign_index: int,
) -> None:
    app = GameApp(difficulty)
    try:
        app._load_campaign(campaign_index)
        app.prepare_demo_layout()
        actual = tuple(
            (unit.kind, unit.position)
            for unit in app.controller.battle.units
            if unit.team is Team.BLUE
        )
        expected = tuple(
            (item.unit_kind, item.position)
            for item in VERIFIED_BLUE_LAYOUTS[difficulty][campaign_index]
        )

        assert actual == expected
    finally:
        pygame.quit()
