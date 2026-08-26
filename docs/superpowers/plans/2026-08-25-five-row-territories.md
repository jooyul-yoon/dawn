# Five-Row Territories Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand Dawn Tactics to a 14-column by 12-row battlefield with equal 5×14 Red and Blue territories separated by a 2×14 neutral strip, while keeping combat rules, budgets, unit assets, and lesson files unchanged.

**Architecture:** `domain.py` owns the authoritative board width, height, and shared territory depth. `controller.py` and `game.py` import that depth so deployment validation and territory rendering cannot drift apart; `campaigns.py` owns both the new enemy coordinates and six verified player/demo layouts. Pygame renders the larger board with 56-pixel cells in a fixed 1280×888 window and derives every grid, panel, HP-bar, and mouse boundary from named constants.

**Tech Stack:** Python 3.12, pygame-ce 2.5.7, pytest, headless SDL rendering

---

## File Map

- Modify `src/dawn_tactics/domain.py`: define authoritative board and territory constants; make `Battle()` default to 14×12.
- Modify `src/dawn_tactics/controller.py`: validate Blue deployment against the shared five-row territory depth.
- Modify `src/dawn_tactics/campaigns.py`: install the approved enemy formations and six verified Blue layouts.
- Modify `src/dawn_tactics/game.py`: render 14×12 at 56 pixels per cell, align the panel, fit HP UI inside cells, and consume verified layouts.
- Modify `tests/test_domain.py`: cover boundaries, deployment rows, campaign signatures, budgets, winning layouts, exact ticks, and click-order determinism.
- Modify `tests/test_game_ui.py`: cover window/grid/panel geometry, zone colors, HP containment, click conversion, and demo placement.
- Inspect without changing `src/dawn_tactics/student_settings.py`, `src/dawn_tactics/student_rules.py`, `src/dawn_tactics/student_rules_validation.py`, and `src/dawn_tactics/assets/units/*.png`.
- Create for visual inspection `screenshots/five-row-territories-final.png`.

## Verified Layout Reference

The following results were observed against the approved enemy coordinates with the current default lesson balance. Blue IDs were derived from positions, and every forward/reverse deployment pair produced an identical `BattleState`, tick count, and complete `BattleEvent` history.

| Campaign | Difficulty | Blue layout | Result |
|---|---|---|---|
| 1 | Normal | Infantry `(9,4)`, Tank `(8,8)` | Blue win, tick 9 |
| 2 | Normal | Anti-Tank `(8,4)`, `(8,7)`, `(8,10)`; Infantry `(10,5)`, `(10,9)` | Blue win, tick 6 |
| 3 | Normal | Tank `(10,6)`, Anti-Tank `(10,4)`, Artillery `(10,9)`, Infantry `(11,5)`, `(11,8)` | Blue win, tick 15 |
| 1 | Hard | Infantry `(8,6)`, Artillery `(9,8)` | Blue win, tick 13 |
| 2 | Hard | Infantry `(8,3)`, `(8,7)`, `(10,7)`; Artillery `(11,7)`; Anti-Tank `(8,10)` | Blue win, tick 14 |
| 3 | Hard | Machine Gun `(11,4)`, Tank `(11,1)`, Infantry `(10,1)`, Cavalry `(9,1)` | Blue win, tick 21 |

The Hard Campaign 3 layout deliberately includes Machine Gun and Cavalry so the final screenshot exercises their already-created battlefield assets.

### Task 0: Preserve and record the current worktree state

**Files:**
- Inspect: all tracked files in `/Users/mygenbio/Documents/Dawn/.worktrees/expand-battlefield`

- [ ] **Step 1: Record the starting branch and dirty files**

Run:

```bash
git status -sb
git diff -- docs/superpowers/plans/2026-08-11-expand-battlefield.md docs/superpowers/specs/2026-08-11-expand-battlefield-design.md src/dawn_tactics/controller.py src/dawn_tactics/game.py tests/test_domain.py
```

Expected: branch `codex/expand-battlefield`; the two August 11 documents plus `controller.py`, `game.py`, and `test_domain.py` are modified. These are existing user/worktree changes. Do not reset, restore, stash, or delete them. The new source and test implementation supersedes the incomplete three-row source/test edits; the two older documents stay unstaged.

- [ ] **Step 2: Confirm the known failing baseline**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: 5 failures and 64 passes. The failures are the stale Hard Campaign 2/3 loadouts, the Campaign 3 click-order expected result, and two stale Campaign 1 tank-damage tick values. Record any different failure set before changing code.

- [ ] **Step 3: Confirm the approved specification is the implementation source**

Run:

```bash
git show HEAD:docs/superpowers/specs/2026-08-25-five-row-territories-design.md | sed -n '1,220p'
```

Expected: the committed design states 14×12, Red rows 0–4, neutral rows 5–6, Blue rows 7–11, 56-pixel cells, a 1280×888 window, and the exact enemy positions used below.

### Task 1: Make board and territory geometry authoritative with TDD

**Files:**
- Modify: `tests/test_domain.py`
- Modify: `src/dawn_tactics/domain.py:12-20,260-270`
- Modify: `src/dawn_tactics/controller.py:5-15,62-66`

- [ ] **Step 1: Replace the old default-board boundary tests**

Import the new constants from `dawn_tactics.domain` and replace the old 14×10, corner, outside-border, and three-row deployment tests with:

```python
from dawn_tactics.domain import (
    DEFAULT_BATTLE_HEIGHT,
    DEFAULT_BATTLE_WIDTH,
    TERRITORY_DEPTH,
    AntiTank,
    Artillery,
    Battle,
    BattleEvent,
    BattleState,
    Cavalry,
    EventKind,
    Infantry,
    MachineGun,
    Position,
    Tank,
    Team,
    UNIT_REGISTRY,
)


def test_default_battle_is_fourteen_by_twelve() -> None:
    battle = Battle()

    assert DEFAULT_BATTLE_WIDTH == 14
    assert DEFAULT_BATTLE_HEIGHT == 12
    assert TERRITORY_DEPTH == 5
    assert (battle.width, battle.height) == (
        DEFAULT_BATTLE_WIDTH,
        DEFAULT_BATTLE_HEIGHT,
    )


def test_expanded_battle_accepts_all_four_corners() -> None:
    battle = Battle()
    positions = (
        Position(0, 0),
        Position(0, 13),
        Position(11, 0),
        Position(11, 13),
    )

    for unit_id, position in enumerate(positions, start=1):
        battle.add_unit(Infantry(unit_id, Team.BLUE, position))

    assert tuple(unit.position for unit in battle.units) == positions


@pytest.mark.parametrize(
    "position",
    (Position(-1, 0), Position(0, -1), Position(12, 0), Position(0, 14)),
)
def test_expanded_battle_rejects_positions_beyond_new_border(
    position: Position,
) -> None:
    with pytest.raises(ValueError, match="outside the battlefield"):
        Battle().add_unit(Infantry(1, Team.BLUE, position))


def test_blue_deployment_zone_is_bottom_five_rows() -> None:
    controller = GameController()
    controller.load_campaign(0)
    controller.remaining_budget = Infantry.cost * 6

    assert not controller.place_blue_unit("infantry", Position(6, 1)).ok
    for column, row in enumerate((7, 8, 9, 10, 11), start=1):
        assert controller.place_blue_unit("infantry", Position(row, column)).ok
```

- [ ] **Step 2: Run the focused tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_domain.py::test_default_battle_is_fourteen_by_twelve \
  tests/test_domain.py::test_expanded_battle_accepts_all_four_corners \
  tests/test_domain.py::test_expanded_battle_rejects_positions_beyond_new_border \
  tests/test_domain.py::test_blue_deployment_zone_is_bottom_five_rows -q
```

Expected: collection fails because the three constants do not exist, proving the tests precede implementation.

- [ ] **Step 3: Add authoritative constants and use them in `Battle`**

Add immediately after the imports in `src/dawn_tactics/domain.py`:

```python
DEFAULT_BATTLE_WIDTH = 14
DEFAULT_BATTLE_HEIGHT = 12
TERRITORY_DEPTH = 5
```

Change the constructor signature to:

```python
class Battle:
    def __init__(
        self,
        width: int = DEFAULT_BATTLE_WIDTH,
        height: int = DEFAULT_BATTLE_HEIGHT,
        max_ticks: int = 180,
    ) -> None:
```

Do not modify `Unit`, its subclasses, targeting, movement, attacks, simultaneous damage, or victory logic.

- [ ] **Step 4: Use the shared territory depth in controller validation**

Add `TERRITORY_DEPTH` to the `from .domain import (...)` list in `src/dawn_tactics/controller.py`, then replace the boundary check with:

```python
        if position.row < self.battle.height - TERRITORY_DEPTH:
            return ActionResult(False, "Deploy inside the blue zone.")
```

Keep coordinate-derived Blue IDs unchanged:

```python
            unit_id = 1_000 + position.row * self.battle.width + position.column
```

- [ ] **Step 5: Run the focused tests to verify GREEN**

Run the command from Step 2 again.

Expected: all parameter cases pass; rows 7–11 deploy and row 6 is rejected.

- [ ] **Step 6: Commit the authoritative geometry**

Run:

```bash
git add src/dawn_tactics/domain.py src/dawn_tactics/controller.py
git diff --cached --check
git diff --cached --name-only
git commit -m "Expand battlefield domain to twelve rows"
```

Expected staged names: only `domain.py` and `controller.py`. Keep the focused
tests in the working tree, but defer staging `tests/test_domain.py` until Task 4
because it already contains pre-existing, partially migrated layout hunks that
must not enter an intermediate commit. The two older dirty documentation files
also remain unstaged.

### Task 2: Install approved enemy formations with TDD

**Files:**
- Modify: `tests/test_domain.py`
- Modify: `src/dawn_tactics/campaigns.py:63-112`

- [ ] **Step 1: Replace the old campaign migration test with exact signatures**

Use this test:

```python
def test_campaign_deployments_use_five_row_red_territory() -> None:
    expected = (
        (
            ("infantry", Position(3, 2)),
            ("infantry", Position(3, 7)),
            ("infantry", Position(3, 12)),
            ("anti_tank", Position(2, 7)),
        ),
        (
            ("tank", Position(3, 4)),
            ("tank", Position(3, 10)),
            ("infantry", Position(4, 7)),
            ("infantry", Position(4, 2)),
        ),
        (
            ("artillery", Position(1, 7)),
            ("infantry", Position(3, 2)),
            ("infantry", Position(3, 12)),
            ("anti_tank", Position(4, 4)),
            ("anti_tank", Position(4, 10)),
            ("tank", Position(4, 7)),
            ("artillery", Position(1, 11)),
        ),
    )
    actual = tuple(
        tuple(
            (deployment.unit_kind, deployment.position)
            for deployment in campaign.enemies + campaign.hard_reinforcements
        )
        for campaign in CAMPAIGNS
    )

    assert actual == expected
```

The last element in each campaign tuple is the Hard reinforcement. Existing budget and allowed-unit tests continue proving no campaign economy or roster change.

- [ ] **Step 2: Run the signature test to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_domain.py::test_campaign_deployments_use_five_row_red_territory -q
```

Expected: one assertion failure showing the previous enemy coordinates.

- [ ] **Step 3: Replace only deployment positions in `CAMPAIGNS`**

Use these exact deployment blocks while retaining all existing titles, objectives, history notes, settings-backed budgets, difficulty penalties, and allowed units:

```python
        enemies=(
            Deployment("infantry", Position(3, 2)),
            Deployment("infantry", Position(3, 7)),
            Deployment("infantry", Position(3, 12)),
        ),
        hard_budget_penalty=50,
        hard_reinforcements=(
            Deployment("anti_tank", Position(2, 7)),
        ),
```

```python
        enemies=(
            Deployment("tank", Position(3, 4)),
            Deployment("tank", Position(3, 10)),
            Deployment("infantry", Position(4, 7)),
        ),
        hard_budget_penalty=100,
        hard_reinforcements=(
            Deployment("infantry", Position(4, 2)),
        ),
```

```python
        enemies=(
            Deployment("artillery", Position(1, 7)),
            Deployment("infantry", Position(3, 2)),
            Deployment("infantry", Position(3, 12)),
            Deployment("anti_tank", Position(4, 4)),
            Deployment("anti_tank", Position(4, 10)),
            Deployment("tank", Position(4, 7)),
        ),
        hard_budget_penalty=200,
        hard_reinforcements=(
            Deployment("artillery", Position(1, 11)),
        ),
```

- [ ] **Step 4: Verify signature, composition, budget, and allowed roster**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_domain.py::test_campaign_deployments_use_five_row_red_territory \
  tests/test_domain.py::test_campaigns_use_student_budget_settings \
  tests/test_domain.py::test_hard_mode_has_less_budget_and_visible_reinforcements \
  tests/test_domain.py::test_all_campaigns_allow_six_player_unit_types -q
```

Expected: all pass.

- [ ] **Step 5: Commit the enemy formations**

Run:

```bash
git add src/dawn_tactics/campaigns.py
git diff --cached --check
git commit -m "Deploy enemies across five-row territory"
```

Keep `tests/test_domain.py` unstaged for the same preservation reason recorded
in Task 1 Step 6; Task 4 makes every pending domain-test hunk coherent before
staging that file.

### Task 3: Fit the 14×12 presentation and interaction with TDD

**Files:**
- Modify: `tests/test_game_ui.py`
- Modify: `src/dawn_tactics/game.py:8-45,377-435,565-570,784-797`

- [ ] **Step 1: Replace the old geometry test and add zone/HP containment tests**

Import the following names from `dawn_tactics.game`:

```python
from dawn_tactics.game import (
    BATTLE_HP_BAR_SIZE,
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
    unit_rule_text,
)
```

Replace the old 14×10 UI geometry and mouse tests and add the new render checks:

```python
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
```

- [ ] **Step 2: Run the new UI tests to verify RED**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m pytest \
  tests/test_game_ui.py::test_five_row_window_grid_and_panel_geometry \
  tests/test_game_ui.py::test_mouse_conversion_reaches_new_bottom_right_cell \
  tests/test_game_ui.py::test_grid_draws_five_red_two_neutral_and_five_blue_rows \
  tests/test_game_ui.py::test_hp_bar_and_text_fit_inside_a_fifty_six_pixel_cell -q
```

Expected: collection fails for the new constants/helper before presentation implementation.

- [ ] **Step 3: Derive presentation geometry from domain constants**

Add `DEFAULT_BATTLE_HEIGHT`, `DEFAULT_BATTLE_WIDTH`, and `TERRITORY_DEPTH` to the `from .domain import (...)` list. Replace the presentation constant block with:

```python
WINDOW_SIZE = (1280, 888)
FPS = 60
GRID_LEFT = 40
GRID_TOP = 150
CELL_SIZE = 56
GRID_WIDTH = DEFAULT_BATTLE_WIDTH * CELL_SIZE
GRID_HEIGHT = DEFAULT_BATTLE_HEIGHT * CELL_SIZE
PANEL_LEFT = GRID_LEFT + GRID_WIDTH + 32
PANEL_WIDTH = 400
PANEL_HEIGHT = GRID_TOP + GRID_HEIGHT - 20
SIMULATION_SECONDS = settings.BATTLE_STEP_SECONDS
BATTLE_UNIT_IMAGE_SIZE = (48, 48)
CARD_UNIT_IMAGE_SIZE = (44, 44)
BATTLE_HP_BAR_SIZE = (42, 5)
HP_TEXT_OFFSET_Y = 19

ENEMY_ZONE_COLOR = (51, 31, 42)
NEUTRAL_ZONE_COLOR = (28, 36, 50)
BLUE_ZONE_COLOR = (25, 45, 67)
```

Keep `GRID_LEFT`, `GRID_TOP`, `PANEL_WIDTH`, battlefield image size, card image size, card rectangles, buttons, and panel-internal text positions unchanged.

- [ ] **Step 4: Add HP geometry helper and apply it**

Add this module-level helper before `GameApp`:

```python
def _battle_hp_bar_rect(center: tuple[int, int]) -> pygame.Rect:
    width, height = BATTLE_HP_BAR_SIZE
    return pygame.Rect(
        center[0] - width // 2,
        center[1] - CELL_SIZE // 2 + 1,
        width,
        height,
    )
```

Replace the HP bar and HP text offsets in `_draw_units()` with:

```python
            bar = _battle_hp_bar_rect(center)
            pygame.draw.rect(self.screen, (54, 24, 31), bar, border_radius=3)
            pygame.draw.rect(
                self.screen,
                GREEN,
                (bar.x, bar.y, round(bar.width * hp_ratio), bar.height),
                border_radius=3,
            )
            self._draw_text(
                str(unit.hp),
                self.fonts["tiny"],
                TEXT,
                (center[0], center[1] + HP_TEXT_OFFSET_Y),
                center=True,
            )
```

- [ ] **Step 5: Render zones from shared depth and align the panel**

Replace the row-color branch in `_draw_grid()` with:

```python
                if row < TERRITORY_DEPTH:
                    color = ENEMY_ZONE_COLOR
                elif row >= battle.height - TERRITORY_DEPTH:
                    color = BLUE_ZONE_COLOR
                else:
                    color = NEUTRAL_ZONE_COLOR
```

Retain `ENEMY ZONE` at `(GRID_LEFT + 10, GRID_TOP + 8)`. Retain `YOUR DEPLOYMENT ZONE` at `(GRID_LEFT + 10, GRID_TOP + GRID_HEIGHT - 24)` so it stays within the last Blue row.

Replace the side-panel rectangle with:

```python
        panel_rect = pygame.Rect(PANEL_LEFT, 20, PANEL_WIDTH, PANEL_HEIGHT)
```

- [ ] **Step 6: Verify UI geometry, existing cards, assets, and setup render**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m pytest tests/test_game_ui.py tests/test_game_assets.py -q
```

Expected: all UI and asset tests pass. The six cards and buttons remain outside the grid, the bottom-right maps to `(11,13)`, and both 48-pixel battlefield and 44-pixel card images retain their tested sizes.

- [ ] **Step 7: Commit presentation geometry**

Run:

```bash
git add src/dawn_tactics/game.py tests/test_game_ui.py
git diff --cached --check
git commit -m "Fit twelve-row battlefield in game window"
```

### Task 4: Add shared verified player layouts and deterministic outcomes

**Files:**
- Modify: `src/dawn_tactics/campaigns.py`
- Modify: `src/dawn_tactics/game.py:870-918`
- Modify: `tests/test_domain.py:267-305,405-529`
- Modify: `tests/test_game_ui.py`

- [ ] **Step 1: Write exact layout and deterministic-result tests**

Import `VERIFIED_BLUE_LAYOUTS` beside `CAMPAIGNS` and `Difficulty`, then replace the old Normal/Hard winning-layout parameterizations and single Campaign 3 click-order test with:

```python
EXPECTED_VERIFIED_LAYOUTS = {
    Difficulty.NORMAL: (
        (
            ("infantry", Position(9, 4)),
            ("tank", Position(8, 8)),
        ),
        (
            ("anti_tank", Position(8, 4)),
            ("anti_tank", Position(8, 7)),
            ("anti_tank", Position(8, 10)),
            ("infantry", Position(10, 5)),
            ("infantry", Position(10, 9)),
        ),
        (
            ("tank", Position(10, 6)),
            ("anti_tank", Position(10, 4)),
            ("artillery", Position(10, 9)),
            ("infantry", Position(11, 5)),
            ("infantry", Position(11, 8)),
        ),
    ),
    Difficulty.HARD: (
        (
            ("infantry", Position(8, 6)),
            ("artillery", Position(9, 8)),
        ),
        (
            ("infantry", Position(8, 3)),
            ("infantry", Position(8, 7)),
            ("artillery", Position(11, 7)),
            ("anti_tank", Position(8, 10)),
            ("infantry", Position(10, 7)),
        ),
        (
            ("machine_gun", Position(11, 4)),
            ("tank", Position(11, 1)),
            ("infantry", Position(10, 1)),
            ("cavalry", Position(9, 1)),
        ),
    ),
}


def test_verified_blue_layout_data_matches_approved_positions() -> None:
    actual = {
        difficulty: tuple(
            tuple((item.unit_kind, item.position) for item in layout)
            for layout in layouts
        )
        for difficulty, layouts in VERIFIED_BLUE_LAYOUTS.items()
    }

    assert actual == EXPECTED_VERIFIED_LAYOUTS


@pytest.mark.parametrize(
    ("difficulty", "expected_ticks"),
    (
        (Difficulty.NORMAL, (9, 6, 15)),
        (Difficulty.HARD, (13, 14, 21)),
    ),
)
@pytest.mark.skipif(
    not DEFAULT_BALANCE_IS_ACTIVE,
    reason="Restore Lesson 01 defaults to verify the original campaign balance.",
)
def test_each_verified_layout_wins_and_ignores_click_order(
    difficulty: Difficulty,
    expected_ticks: tuple[int, int, int],
) -> None:
    for campaign_index, (layout, tick) in enumerate(
        zip(EXPECTED_VERIFIED_LAYOUTS[difficulty], expected_ticks, strict=True)
    ):
        forward = _run_campaign_layout(campaign_index, difficulty, layout)
        backward = _run_campaign_layout(
            campaign_index,
            difficulty,
            tuple(reversed(layout)),
        )

        assert forward == backward
        assert forward[:2] == (BattleState.BLUE_WIN, tick)
```

- [ ] **Step 2: Update the Campaign 1 tank-damage experiment**

Use the verified Campaign 1 Normal positions and freshly observed exact ticks:

```python
@pytest.mark.parametrize(
    ("tank_damage", "expected_state", "expected_ticks"),
    (
        (3, BattleState.BLUE_WIN, 9),
        (1, BattleState.RED_WIN, 10),
        (6, BattleState.BLUE_WIN, 8),
    ),
)
@pytest.mark.skipif(
    not DEFAULT_BALANCE_IS_ACTIVE,
    reason="Restore Lesson 01 defaults to verify its baseline experiment.",
)
def test_lesson_one_normal_mode_damage_experiment_stays_reproducible(
    monkeypatch: pytest.MonkeyPatch,
    tank_damage: int,
    expected_state: BattleState,
    expected_ticks: int,
) -> None:
    monkeypatch.setattr(Tank, "base_damage", tank_damage)
    controller = GameController(Difficulty.NORMAL)
    controller.load_campaign(0)
    assert controller.place_blue_unit("infantry", Position(9, 4)).ok
    assert controller.place_blue_unit("tank", Position(8, 8)).ok
    assert controller.start_battle().ok

    while controller.battle.state is BattleState.RUNNING:
        controller.step()

    assert controller.battle.state is expected_state
    assert controller.battle.tick == expected_ticks
```

- [ ] **Step 3: Run the new layout tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_domain.py::test_verified_blue_layout_data_matches_approved_positions \
  tests/test_domain.py::test_each_verified_layout_wins_and_ignores_click_order \
  tests/test_domain.py::test_lesson_one_normal_mode_damage_experiment_stays_reproducible -q
```

Expected: collection fails because `VERIFIED_BLUE_LAYOUTS` does not exist.

- [ ] **Step 4: Define the layouts as pure campaign data**

Append this constant after `CAMPAIGNS` in `src/dawn_tactics/campaigns.py`:

```python
VERIFIED_BLUE_LAYOUTS: dict[
    Difficulty,
    tuple[tuple[Deployment, ...], ...],
] = {
    Difficulty.NORMAL: (
        (
            Deployment("infantry", Position(9, 4)),
            Deployment("tank", Position(8, 8)),
        ),
        (
            Deployment("anti_tank", Position(8, 4)),
            Deployment("anti_tank", Position(8, 7)),
            Deployment("anti_tank", Position(8, 10)),
            Deployment("infantry", Position(10, 5)),
            Deployment("infantry", Position(10, 9)),
        ),
        (
            Deployment("tank", Position(10, 6)),
            Deployment("anti_tank", Position(10, 4)),
            Deployment("artillery", Position(10, 9)),
            Deployment("infantry", Position(11, 5)),
            Deployment("infantry", Position(11, 8)),
        ),
    ),
    Difficulty.HARD: (
        (
            Deployment("infantry", Position(8, 6)),
            Deployment("artillery", Position(9, 8)),
        ),
        (
            Deployment("infantry", Position(8, 3)),
            Deployment("infantry", Position(8, 7)),
            Deployment("artillery", Position(11, 7)),
            Deployment("anti_tank", Position(8, 10)),
            Deployment("infantry", Position(10, 7)),
        ),
        (
            Deployment("machine_gun", Position(11, 4)),
            Deployment("tank", Position(11, 1)),
            Deployment("infantry", Position(10, 1)),
            Deployment("cavalry", Position(9, 1)),
        ),
    ),
}
```

The six costs are exactly Normal `$500/$950/$1,200` and Hard `$450/$900/$1,000`, each within its campaign budget. No budget value changes.

- [ ] **Step 5: Make screenshot/demo preparation consume the shared layouts**

Import `VERIFIED_BLUE_LAYOUTS` from `campaigns.py`, then replace the full local `normal_layouts`/`hard_layouts` block in `prepare_demo_layout()` with:

```python
    def prepare_demo_layout(self) -> None:
        if self.controller.campaign_index is None:
            return
        layout = VERIFIED_BLUE_LAYOUTS[self.controller.difficulty][
            self.controller.campaign_index
        ]
        for deployment in layout:
            self.controller.place_blue_unit(
                deployment.unit_kind,
                deployment.position,
            )
```

- [ ] **Step 6: Prove `prepare_demo_layout()` places exactly the shared data**

Add to `tests/test_game_ui.py` and import `VERIFIED_BLUE_LAYOUTS` and `Team`:

```python
@pytest.mark.parametrize("difficulty", (Difficulty.NORMAL, Difficulty.HARD))
@pytest.mark.parametrize("campaign_index", (0, 1, 2))
def test_prepare_demo_layout_uses_verified_campaign_data(
    difficulty: Difficulty,
    campaign_index: int,
) -> None:
    app = GameApp(difficulty)
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
    pygame.quit()
```

- [ ] **Step 7: Verify layouts three times and run all domain/UI tests**

Run:

```bash
for run_number in 1 2 3; do
  .venv/bin/python -m pytest \
    tests/test_domain.py::test_each_verified_layout_wins_and_ignores_click_order -q || exit 1
done
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m pytest tests/test_domain.py tests/test_game_ui.py -q
```

Expected: every repetition passes with Normal ticks `(9,6,15)` and Hard ticks `(13,14,21)`; the full event histories match after reversing placement order.

- [ ] **Step 8: Commit verified layouts**

Run:

```bash
git add src/dawn_tactics/campaigns.py src/dawn_tactics/game.py tests/test_domain.py tests/test_game_ui.py
git diff --cached --check
git commit -m "Add verified twelve-row campaign layouts"
```

### Task 5: Run full regression and inspect the final frame

**Files:**
- Verify: all Python source and tests
- Create: `screenshots/five-row-territories-final.png`
- Inspect: `src/dawn_tactics/assets/units/machine_gun.png`
- Inspect: `src/dawn_tactics/assets/units/cavalry.png`

- [ ] **Step 1: Confirm no stale geometry literals remain in active code/tests**

Run:

```bash
rg -n "height - 3|row < 3|14, 10|1408, 888|10 \* CELL_SIZE|Position\(9, 13\)" src tests
```

Expected: no matches. Historical August 11 plan/spec documents are excluded because they describe the superseded design and remain preserved as pre-existing unstaged changes.

- [ ] **Step 2: Run compilation and the complete test suite**

Run:

```bash
.venv/bin/python -m compileall -q src tests
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q
```

Expected: compilation exits 0 and all tests pass.

- [ ] **Step 3: Render the exact final screenshot**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m dawn_tactics \
  --screenshot screenshots/five-row-territories-final.png \
  --campaign 3 --difficulty hard --simulate-ticks 0
.venv/bin/python - <<'PY'
from pathlib import Path
import pygame

image_path = Path("screenshots/five-row-territories-final.png")
image = pygame.image.load(image_path)
assert image.get_size() == (1280, 888)
assert image_path.stat().st_size > 10_000
print(image.get_size(), image_path.stat().st_size)
PY
```

Expected: the image is exactly `(1280, 888)` and larger than 10 KB.

- [ ] **Step 4: Inspect the screenshot at original resolution**

Open `screenshots/five-row-territories-final.png` at original size and verify all of the following:

- fourteen complete columns and twelve complete rows are visible;
- Red occupies five rows, neutral occupies two rows, and Blue occupies five rows;
- outer grid borders at row 11 and column 13 are uncropped;
- the panel begins 32 pixels after the grid and its background ends level with the grid;
- cards, buttons, labels, objective text, history note, and panel text are readable and do not overlap;
- the Machine Gun at `(11,4)` and Cavalry at `(9,1)` use their created images on Blue plates;
- 48-pixel unit images, 42×5 HP bars, and HP text stay inside 56-pixel cells.

If any visual item fails, return to Task 3, add a focused failing geometry test that reproduces that exact overlap/clipping condition, apply the smallest presentation-only correction, rerun Task 3 Step 6, and render this same screenshot again.

- [ ] **Step 5: Audit scope boundaries**

Run:

```bash
git diff 2436619..HEAD -- \
  src/dawn_tactics/student_settings.py \
  src/dawn_tactics/student_rules.py \
  src/dawn_tactics/student_rules_validation.py \
  src/dawn_tactics/assets/units
git diff 2436619..HEAD --stat
git status -sb
```

Expected: the first command has no output. Only board geometry, campaign positions/layout data, presentation geometry, tests, and the screenshot changed in implementation commits. The two pre-existing older plan/spec modifications may still appear unstaged and must not be silently included.

- [ ] **Step 6: Commit the verified screenshot only if it is repository-tracked evidence**

First run:

```bash
git check-ignore -q screenshots/five-row-territories-final.png
```

If exit status is 0, leave the ignored screenshot uncommitted. If exit status is 1, run:

```bash
git add screenshots/five-row-territories-final.png
git diff --cached --check
git commit -m "Add twelve-row battlefield preview"
```

- [ ] **Step 7: Final verification immediately before completion**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
git log --oneline -6
git status -sb
```

Expected: all tests and compilation pass; the implementation commits are visible; no student rules, settings, stats, budgets, assets, or unrelated files were changed by this implementation.
