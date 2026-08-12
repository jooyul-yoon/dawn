# Expanded Battlefield Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the default battlefield from 12×8 to 14×10, adding one playable cell around every side while preserving 64-pixel cells, three-row deployment zones, and combat rules.

**Architecture:** `Battle` owns the authoritative 14×10 default. Campaign enemies migrate by `(row + 1, column + 1)` to center old formations; player/demo layouts migrate into the new bottom-three-row zone. Pygame derives a 896×640 grid, moves the unchanged command panel right, and enlarges the window to 1408×888.

**Tech Stack:** Python 3.12, pygame-ce 2.5.7, pytest, headless SDL rendering

---

## File Map

- Modify `src/dawn_tactics/domain.py`: authoritative default dimensions.
- Modify `src/dawn_tactics/campaigns.py`: centered enemy deployments.
- Modify `src/dawn_tactics/game.py`: canvas geometry and demo layouts.
- Modify `tests/test_domain.py`: geometry, campaigns, layouts, determinism.
- Modify `tests/test_game_ui.py`: canvas, clicks, layout, rendering.
- Modify `tests/test_game_assets.py`: default-board rendering coordinates.
- Create for inspection only `screenshots/expanded-battlefield-final.png`.

### Task 1: Implement domain and campaign geometry with TDD

**Files:**
- Modify: `tests/test_domain.py`
- Modify: `src/dawn_tactics/domain.py:260-265`
- Modify: `src/dawn_tactics/campaigns.py:63-112`

- [ ] **Step 1: Write failing geometry tests**

Add:

```python
def test_default_battle_is_fourteen_by_ten() -> None:
    battle = Battle()
    assert (battle.width, battle.height) == (14, 10)


def test_expanded_battle_accepts_every_new_corner() -> None:
    battle = Battle()
    positions = (Position(0, 0), Position(0, 13), Position(9, 0), Position(9, 13))
    for unit_id, position in enumerate(positions, start=1):
        battle.add_unit(Infantry(unit_id, Team.BLUE, position))
    assert tuple(unit.position for unit in battle.units) == positions


@pytest.mark.parametrize(
    "position",
    (Position(-1, 0), Position(0, -1), Position(10, 0), Position(0, 14)),
)
def test_expanded_battle_rejects_positions_beyond_new_border(
    position: Position,
) -> None:
    with pytest.raises(ValueError, match="outside the battlefield"):
        Battle().add_unit(Infantry(1, Team.BLUE, position))


def test_blue_deployment_zone_is_bottom_three_rows_after_expansion() -> None:
    controller = GameController()
    controller.load_campaign(0)
    controller.remaining_budget = Infantry.cost * 4
    assert not controller.place_blue_unit("infantry", Position(6, 1)).ok
    for column, row in enumerate((7, 8, 9), start=1):
        assert controller.place_blue_unit("infantry", Position(row, column)).ok
```

- [ ] **Step 2: Write the exact failing campaign migration test**

```python
def test_campaign_deployments_shift_one_cell_down_and_right() -> None:
    expected = (
        (("infantry", Position(2, 4)), ("infantry", Position(2, 7)),
         ("infantry", Position(2, 10)), ("anti_tank", Position(3, 6))),
        (("tank", Position(2, 5)), ("tank", Position(2, 8)),
         ("infantry", Position(3, 7)), ("infantry", Position(3, 4))),
        (("artillery", Position(1, 7)), ("infantry", Position(2, 4)),
         ("infantry", Position(2, 9)), ("anti_tank", Position(3, 4)),
         ("tank", Position(3, 6)), ("anti_tank", Position(3, 9)),
         ("artillery", Position(1, 5))),
    )
    actual = tuple(
        tuple((item.unit_kind, item.position)
              for item in campaign.enemies + campaign.hard_reinforcements)
        for campaign in CAMPAIGNS
    )
    assert actual == expected
```

- [ ] **Step 3: Verify RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_domain.py::test_default_battle_is_fourteen_by_ten \
  tests/test_domain.py::test_expanded_battle_accepts_every_new_corner \
  tests/test_domain.py::test_expanded_battle_rejects_positions_beyond_new_border \
  tests/test_domain.py::test_blue_deployment_zone_is_bottom_three_rows_after_expansion \
  tests/test_domain.py::test_campaign_deployments_shift_one_cell_down_and_right -q
```

Expected: failures identify the old 12×8 default, old blue boundary, and old
campaign signatures.

- [ ] **Step 4: Implement the minimum production change**

Change `Battle.__init__` defaults to `width: int = 14` and `height: int = 10`.
Replace every campaign position with the exact signatures above. Do not change
budgets, allowed units, stats, objectives, or combat behavior.

- [ ] **Step 5: Verify GREEN and commit**

Re-run the five focused tests, then:

```bash
git add src/dawn_tactics/domain.py src/dawn_tactics/campaigns.py tests/test_domain.py
git diff --cached --check
git commit -m "Expand battlefield domain to fourteen by ten"
```

### Task 2: Expand pygame canvas and grid interaction with TDD

**Files:**
- Modify: `tests/test_game_ui.py`
- Modify: `src/dawn_tactics/game.py:25-33`

- [ ] **Step 1: Import the geometry constants in `tests/test_game_ui.py`**

Import `CELL_SIZE`, `GRID_HEIGHT`, `GRID_LEFT`, `GRID_TOP`, `GRID_WIDTH`,
`PANEL_LEFT`, and `WINDOW_SIZE` alongside `GameApp` and `unit_rule_text`.

- [ ] **Step 2: Write failing window and click tests**

```python
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
```

Extend the card-layout test:

```python
    grid_rect = pygame.Rect(GRID_LEFT, GRID_TOP, GRID_WIDTH, GRID_HEIGHT)
    assert all(not rect.colliderect(grid_rect) for rect in values)
```

Move the setup-render placements to Machine Gun `Position(9, 5)` and Cavalry
`Position(9, 7)`.

- [ ] **Step 3: Verify RED**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m pytest tests/test_game_ui.py -q
```

Expected: old window/grid/panel values, bottom-right mapping, and row-9 setup
placements fail.

- [ ] **Step 4: Change only presentation constants**

```python
WINDOW_SIZE = (1408, 888)
FPS = 60
GRID_LEFT = 40
GRID_TOP = 150
CELL_SIZE = 64
GRID_WIDTH = 14 * CELL_SIZE
GRID_HEIGHT = 10 * CELL_SIZE
PANEL_LEFT = GRID_LEFT + GRID_WIDTH + 32
PANEL_WIDTH = 400
```

Keep panel internal rectangles, cards, cell size, and unit image sizes unchanged.

- [ ] **Step 5: Verify GREEN and commit**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m pytest tests/test_game_ui.py tests/test_game_assets.py -q
git add src/dawn_tactics/game.py tests/test_game_ui.py
git diff --cached --check
git commit -m "Expand battlefield presentation"
```

### Task 3: Migrate player layouts and deterministic outcomes

**Files:**
- Modify: `tests/test_domain.py`
- Modify: `tests/test_game_assets.py`
- Modify: `src/dawn_tactics/game.py:870-918`

- [ ] **Step 1: Apply the default-board player-coordinate mapping**

Use this mapping only in default `GameController`/`Battle` scenarios:

```text
old row 5 -> new row 7
old row 6 -> new row 8
old row 7 -> new row 9
old column C -> new column C + 1
```

Do not alter explicit custom-size `Battle(width=..., height=...)` tests. Examples:
`(7,4)->(9,5)`, `(7,6)->(9,7)`, `(7,2)->(9,3)`.

- [ ] **Step 2: Use these exact normal winning/demo layouts**

```python
(
    (0, (("infantry", Position(9, 5)), ("tank", Position(9, 7)))),
    (1, (("anti_tank", Position(9, 4)), ("anti_tank", Position(9, 6)),
         ("anti_tank", Position(9, 8)), ("infantry", Position(8, 5)),
         ("infantry", Position(8, 7)))),
    (2, (("tank", Position(9, 6)), ("anti_tank", Position(9, 4)),
         ("artillery", Position(9, 9)), ("infantry", Position(8, 5)),
         ("infantry", Position(8, 8)))),
)
```

- [ ] **Step 3: Use these exact hard winning/demo layouts**

```python
(
    (0, (("infantry", Position(7, 12)), ("artillery", Position(9, 1)))),
    (1, (("infantry", Position(9, 9)), ("infantry", Position(7, 4)),
         ("artillery", Position(9, 12)), ("anti_tank", Position(8, 5)),
         ("infantry", Position(8, 11)))),
    (2, (("anti_tank", Position(9, 5)), ("infantry", Position(8, 2)),
         ("anti_tank", Position(7, 6)), ("infantry", Position(8, 10)),
         ("infantry", Position(8, 4)), ("infantry", Position(8, 8)),
         ("infantry", Position(7, 4)))),
)
```

Use the same six layouts in `GameApp.prepare_demo_layout`.

- [ ] **Step 4: Run domain tests and verify placements**

```bash
.venv/bin/python -m pytest tests/test_domain.py -q
```

Expected: placements are legal. Any remaining failures are stale exact outcome
literals caused by the added travel space.

- [ ] **Step 5: Encode freshly verified deterministic outcomes**

Run each exact-outcome failure three times and update only its expected
state/tick after all runs agree. The click-order test must retain identical
forward/reversed histories. Winning-loadout tests must remain `BLUE_WIN`. Do not
change stats, movement, targeting, budgets, layouts, or `max_ticks` merely to
recover old tick counts.

- [ ] **Step 6: Verify full GREEN and commit**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest \
  tests/test_domain.py::test_deployment_click_order_does_not_change_the_battle -q
git add src/dawn_tactics/game.py tests/test_domain.py tests/test_game_assets.py
git diff --cached --check
git commit -m "Migrate layouts to expanded battlefield"
```

### Task 4: Render and audit the enlarged interface

**Files:**
- Create for inspection only: `screenshots/expanded-battlefield-final.png`
- No tracked changes expected

- [ ] **Step 1: Render the final headless screenshot**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python - <<'PY'
from pathlib import Path
import pygame
from dawn_tactics.campaigns import Difficulty
from dawn_tactics.domain import Position
from dawn_tactics.game import GameApp

output = Path("screenshots/expanded-battlefield-final.png")
output.parent.mkdir(parents=True, exist_ok=True)
app = GameApp(Difficulty.NORMAL)
app._load_campaign(2)
assert app.controller.place_blue_unit("machine_gun", Position(9, 5)).ok
assert app.controller.place_blue_unit("cavalry", Position(9, 7)).ok
app.status = "Expanded 14 x 10 battlefield check."
app.draw()
pygame.image.save(app.screen, output)
pygame.quit()
print(output)
PY
file screenshots/expanded-battlefield-final.png
```

Expected: a 1408×888 PNG.

- [ ] **Step 2: Inspect at original resolution**

Confirm 14 columns and 10 rows; all four borders; red/blue zone labels;
Machine Gun and Cavalry inside their cells with plates and HP bars; a 32-pixel
grid/panel gap; six readable cards; readable buttons/status/learning text; and
no overlap or clipping. If a defect exists, add a failing geometry test before
changing a constant.

- [ ] **Step 3: Run final verification**

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest \
  tests/test_domain.py::test_deployment_click_order_does_not_change_the_battle -q
git diff --check
```

Expected: compilation, full suite, and determinism pass; diff check is silent.

- [ ] **Step 4: Audit learner scope and repository state**

```bash
base_sha=$(git merge-base HEAD main)
git diff --exit-code "$base_sha"..HEAD -- \
  src/dawn_tactics/student_rules.py \
  src/dawn_tactics/student_rules_validation.py \
  src/dawn_tactics/student_settings.py \
  src/dawn_tactics/settings_validation.py
git diff "$base_sha"..HEAD -- src/dawn_tactics/domain.py
git status --short
git log -6 --oneline --decorate
```

Expected: learner files have no changes; the production `domain.py` diff changes
only default width/height; status is clean; ignored screenshot remains available.
