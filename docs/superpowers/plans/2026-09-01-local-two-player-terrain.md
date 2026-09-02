# Local Two-Player and Terrain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Add a same-screen local two-player mode with $2,000 per team, alternating one-unit deployment turns, and symmetric blocking sea/building terrain.

**Architecture:** Keep campaigns backward-compatible while extending GameController with a separate local-match state. Add a pygame-independent Terrain class and a fixed local map to Battle; pygame renders assets and routes current-player input but owns no terrain or budget rules.

**Tech Stack:** Python 3.12, pygame-ce 2.5.7, pytest, Pillow for asset inspection only, headless SDL verification.

---

## File Structure

- Modify src/dawn_tactics/domain.py: Terrain model, terrain validation, collision, and pathfinding.
- Create src/dawn_tactics/local_match.py: local budget and exact symmetric terrain layout.
- Modify src/dawn_tactics/controller.py: match mode, team budgets, alternating deployment, pass/refund/restart.
- Modify src/dawn_tactics/game.py: menu entry, local setup flow, dual-budget panel, terrain rendering.
- Create src/dawn_tactics/assets/terrain/sea.png: top-down water tile.
- Create src/dawn_tactics/assets/terrain/building.png: top-down blocked-building tile.
- Modify src/dawn_tactics/__init__.py: export Terrain for the pure-Python teaching API.
- Modify pyproject.toml: package terrain PNG files.
- Create tests/test_local_two_player.py: domain/controller local-match contract.
- Create tests/test_terrain_assets.py: terrain image registry, alpha, scaling, and fallback contract.
- Modify tests/test_game_ui.py: local menu, panel, input, labels, terrain, and result geometry.
- Modify README.md: local-mode controls and terrain rules.

### Task 1: Terrain domain and fixed local map

**Files:**
- Modify: src/dawn_tactics/domain.py
- Create: src/dawn_tactics/local_match.py
- Modify: src/dawn_tactics/__init__.py
- Create: tests/test_local_two_player.py

- [ ] **Step 1: Write failing terrain-model tests**

Create tests/test_local_two_player.py with the imports and terrain tests below:

~~~python
import pytest

from dawn_tactics.domain import Battle, Infantry, Position, Team, Terrain
from dawn_tactics.local_match import (
    LOCAL_TWO_PLAYER_BUDGET,
    build_local_terrain,
)


def test_local_map_is_symmetric_and_uses_two_thousand_dollars() -> None:
    terrain = build_local_terrain()
    actual = {(tile.kind, tile.position) for tile in terrain}
    rotated = {
        (tile.kind, Position(11 - tile.position.row, 13 - tile.position.column))
        for tile in terrain
    }

    assert LOCAL_TWO_PLAYER_BUDGET == 2_000
    assert actual == rotated
    assert sum(tile.kind == "sea" for tile in terrain) == 20
    assert sum(tile.kind == "building" for tile in terrain) == 4


def test_terrain_rejects_unknown_kind_and_duplicate_position() -> None:
    with pytest.raises(ValueError, match="Unknown terrain kind"):
        Terrain("forest", Position(1, 1))

    duplicate = (
        Terrain("sea", Position(5, 0)),
        Terrain("building", Position(5, 0)),
    )
    with pytest.raises(ValueError, match="duplicate"):
        Battle(terrain=duplicate)

    with pytest.raises(ValueError, match="outside"):
        Battle(terrain=(Terrain("sea", Position(12, 0)),))


def test_terrain_blocks_deployment() -> None:
    battle = Battle(terrain=(Terrain("building", Position(3, 4)),))

    with pytest.raises(ValueError, match="blocked by terrain"):
        battle.add_unit(Infantry(1, Team.RED, Position(3, 4)))
~~~

- [ ] **Step 2: Run the terrain tests and observe RED**

Run:

~~~bash
.venv/bin/python -m pytest tests/test_local_two_player.py -q
~~~

Expected: collection fails because Terrain and dawn_tactics.local_match do not exist.

- [ ] **Step 3: Implement Terrain and terrain-aware Battle setup**

In src/dawn_tactics/domain.py, add after Position:

~~~python
TERRAIN_KINDS = frozenset({"sea", "building"})


class Terrain:
    """One blocked battlefield feature with no pygame dependency."""

    def __init__(
        self,
        kind: str,
        position: Position,
        *,
        blocks_movement: bool = True,
        blocks_deployment: bool = True,
    ) -> None:
        if kind not in TERRAIN_KINDS:
            raise ValueError(f"Unknown terrain kind: {kind}")
        self.kind = kind
        self.position = position
        self.blocks_movement = blocks_movement
        self.blocks_deployment = blocks_deployment
~~~

Change Battle.__init__ to accept terrain: Iterable[Terrain] = (), store it as a tuple, reject outside-map terrain, and reject duplicate positions:

~~~python
self.terrain = tuple(terrain)
terrain_positions: set[Position] = set()
for tile in self.terrain:
    if not self._inside(tile.position):
        raise ValueError("Terrain position is outside the battlefield.")
    if tile.position in terrain_positions:
        raise ValueError("Terrain positions must not contain duplicates.")
    terrain_positions.add(tile.position)
~~~

Add these Battle methods:

~~~python
def terrain_at(self, position: Position) -> Terrain | None:
    return next(
        (tile for tile in self.terrain if tile.position == position),
        None,
    )

def blocks_deployment(self, position: Position) -> bool:
    tile = self.terrain_at(position)
    return tile is not None and tile.blocks_deployment

def blocks_movement(self, position: Position) -> bool:
    tile = self.terrain_at(position)
    return tile is not None and tile.blocks_movement
~~~

In Battle.add_unit, after the bounds check and before the occupied-cell check, raise ValueError("Unit position is blocked by terrain.") when blocks_deployment returns true.

In Battle._find_next_step, skip a neighbor when self.blocks_movement(neighbor) is true:

~~~python
if (
    neighbor in parent
    or neighbor in occupied
    or self.blocks_movement(neighbor)
):
    continue
~~~

- [ ] **Step 4: Create the fixed local map**

Create src/dawn_tactics/local_match.py:

~~~python
from __future__ import annotations

from .domain import Position, Terrain


LOCAL_TWO_PLAYER_BUDGET = 2_000
OPEN_CROSSING_COLUMNS = frozenset({2, 6, 7, 11})
BUILDING_POSITIONS = (
    Position(3, 4),
    Position(3, 9),
    Position(8, 4),
    Position(8, 9),
)


def build_local_terrain() -> tuple[Terrain, ...]:
    sea = tuple(
        Terrain("sea", Position(row, column))
        for row in (5, 6)
        for column in range(14)
        if column not in OPEN_CROSSING_COLUMNS
    )
    buildings = tuple(
        Terrain("building", position)
        for position in BUILDING_POSITIONS
    )
    return sea + buildings
~~~

Export Terrain from src/dawn_tactics/__init__.py by adding it to the domain import and __all__.

- [ ] **Step 5: Add and pass a pathfinding test**

Append:

~~~python
def test_units_route_through_open_crossings_without_entering_terrain() -> None:
    battle = Battle(terrain=build_local_terrain(), max_ticks=40)
    blue = Infantry(1_111, Team.BLUE, Position(7, 5))
    red = Infantry(2_042, Team.RED, Position(4, 5))
    battle.add_unit(blue)
    battle.add_unit(red)
    assert battle.start()

    for _ in range(20):
        battle.step()
        assert all(
            not battle.blocks_movement(unit.position)
            for unit in battle.living_units
        )
        if blue.position.row <= 6 or red.position.row >= 5:
            break

    assert blue.position.column in {2, 6, 7, 11}
    assert red.position.column in {2, 6, 7, 11}
~~~

Run:

~~~bash
.venv/bin/python -m pytest tests/test_local_two_player.py -q
~~~

Expected: all Task 1 tests pass.

- [ ] **Step 6: Run campaign-domain regression tests**

Run:

~~~bash
.venv/bin/python -m pytest tests/test_domain.py -q
~~~

Expected: all existing domain tests pass with terrain defaulting to empty.

- [ ] **Step 7: Commit the terrain domain**

~~~bash
git add src/dawn_tactics/domain.py src/dawn_tactics/local_match.py src/dawn_tactics/__init__.py tests/test_local_two_player.py
git commit -m "Add blocking terrain domain model"
~~~

### Task 2: Alternating local two-player controller

**Files:**
- Modify: src/dawn_tactics/controller.py
- Modify: tests/test_local_two_player.py

- [ ] **Step 1: Write failing local-controller setup and alternation tests**

Append:

~~~python
from dawn_tactics.controller import GameController, MatchMode
from dawn_tactics.domain import Cavalry, Infantry


def test_local_match_starts_empty_with_two_budgets_and_blue_turn() -> None:
    controller = GameController()
    controller.load_local_two_player()

    assert controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
    assert controller.campaign is None
    assert controller.battle.units == []
    assert controller.budget_for(Team.BLUE) == 2_000
    assert controller.budget_for(Team.RED) == 2_000
    assert controller.active_team is Team.BLUE


def test_successful_local_placements_spend_and_alternate() -> None:
    controller = GameController()
    controller.load_local_two_player()

    blue = controller.place_current_unit("infantry", Position(9, 2))
    assert blue.ok
    assert controller.budget_for(Team.BLUE) == 2_000 - Infantry.cost
    assert controller.budget_for(Team.RED) == 2_000
    assert controller.active_team is Team.RED

    red = controller.place_current_unit("cavalry", Position(2, 2))
    assert red.ok
    assert controller.budget_for(Team.RED) == 2_000 - Cavalry.cost
    assert controller.active_team is Team.BLUE


@pytest.mark.parametrize(
    ("position", "message"),
    (
        (Position(2, 2), "blue zone"),
        (Position(5, 2), "blue zone"),
        (Position(8, 4), "terrain"),
        (Position(-1, 2), "inside"),
    ),
)
def test_failed_local_placement_preserves_budget_and_turn(
    position: Position,
    message: str,
) -> None:
    controller = GameController()
    controller.load_local_two_player()
    before = dict(controller.team_budgets)

    result = controller.place_current_unit("infantry", position)

    assert not result.ok
    assert message in result.message.lower()
    assert controller.team_budgets == before
    assert controller.active_team is Team.BLUE


def test_local_placement_rejects_unknown_occupied_and_unaffordable() -> None:
    controller = GameController()
    controller.load_local_two_player()

    unknown = controller.place_current_unit("zeppelin", Position(9, 2))
    assert not unknown.ok
    assert controller.active_team is Team.BLUE

    controller.team_budgets[Team.BLUE] = 0
    poor = controller.place_current_unit("infantry", Position(9, 2))
    assert not poor.ok
    assert controller.active_team is Team.BLUE

    controller.team_budgets[Team.BLUE] = 2_000
    assert controller.place_current_unit("infantry", Position(9, 2)).ok
    assert controller.place_current_unit("infantry", Position(2, 2)).ok
    occupied = controller.place_current_unit("infantry", Position(9, 2))
    assert not occupied.ok
    assert controller.active_team is Team.BLUE


def test_red_uses_top_five_rows_and_rejects_neutral_or_blue_rows() -> None:
    controller = GameController()
    controller.load_local_two_player()
    assert controller.pass_turn().ok

    for position in (Position(5, 3), Position(9, 3)):
        result = controller.place_current_unit("infantry", position)
        assert not result.ok
        assert controller.active_team is Team.RED

    assert controller.place_current_unit("infantry", Position(4, 3)).ok
    assert controller.active_team is Team.BLUE
~~~

- [ ] **Step 2: Run the new controller tests and observe RED**

Run:

~~~bash
.venv/bin/python -m pytest tests/test_local_two_player.py -q
~~~

Expected: import or attribute failures for MatchMode and local controller APIs.

- [ ] **Step 3: Add match state and local loading**

In src/dawn_tactics/controller.py, import Enum, LOCAL_TWO_PLAYER_BUDGET, and build_local_terrain, then add:

~~~python
class MatchMode(str, Enum):
    CAMPAIGN = "campaign"
    LOCAL_TWO_PLAYER = "local_two_player"
~~~

Initialize these fields without removing remaining_budget:

~~~python
self.match_mode = MatchMode.CAMPAIGN
self.team_budgets = {Team.BLUE: 0, Team.RED: 0}
self.active_team = Team.BLUE
~~~

At the start of load_campaign set match_mode to CAMPAIGN. After calculating remaining_budget, synchronize team_budgets:

~~~python
self.team_budgets = {
    Team.BLUE: self.remaining_budget,
    Team.RED: 0,
}
self.active_team = Team.BLUE
~~~

Add:

~~~python
def load_local_two_player(self) -> None:
    self.match_mode = MatchMode.LOCAL_TWO_PLAYER
    self.campaign_index = None
    self.campaign = None
    self.battle = Battle(terrain=build_local_terrain())
    self.remaining_budget = 0
    self.team_budgets = {
        Team.BLUE: LOCAL_TWO_PLAYER_BUDGET,
        Team.RED: LOCAL_TWO_PLAYER_BUDGET,
    }
    self.active_team = Team.BLUE
    self._next_unit_id = 1

def budget_for(self, team: Team) -> int:
    if self.match_mode is MatchMode.LOCAL_TWO_PLAYER:
        return self.team_budgets[team]
    return self.remaining_budget if team is Team.BLUE else 0

@property
def active_budget(self) -> int:
    return self.budget_for(self.active_team)
~~~

- [ ] **Step 4: Implement one-placement turn switching**

Add:

~~~python
def place_current_unit(
    self,
    unit_kind: str,
    position: Position,
) -> ActionResult:
    if self.match_mode is not MatchMode.LOCAL_TWO_PLAYER:
        return ActionResult(False, "Choose Local 2 Player first.")
    if self.battle.state is not BattleState.SETUP:
        return ActionResult(False, "Deployment is locked during battle.")
    unit_class = UNIT_REGISTRY.get(unit_kind)
    if unit_class is None:
        return ActionResult(False, "Unknown unit type.")
    if not self._inside(position):
        return ActionResult(False, "Choose a cell inside the grid.")
    if not self._inside_deployment_zone(self.active_team, position):
        team_name = self.active_team.value
        return ActionResult(False, f"Deploy inside the {team_name} zone.")
    if self.battle.blocks_deployment(position):
        return ActionResult(False, "That cell is blocked by terrain.")
    if self.battle.unit_at(position) is not None:
        return ActionResult(False, "That cell is occupied.")
    if self.active_budget < unit_class.cost:
        return ActionResult(False, "Not enough budget.")

    team = self.active_team
    self._add_unit(unit_kind, team, position)
    self.team_budgets[team] -= unit_class.cost
    self._switch_active_team()
    return ActionResult(
        True,
        f"{team.value.title()} deployed {unit_class.display_name}.",
    )

def _inside_deployment_zone(self, team: Team, position: Position) -> bool:
    if team is Team.RED:
        return position.row < TERRITORY_DEPTH
    return position.row >= self.battle.height - TERRITORY_DEPTH

def _switch_active_team(self) -> None:
    self.active_team = (
        Team.RED if self.active_team is Team.BLUE else Team.BLUE
    )
~~~

In _add_unit, keep the old campaign ID behavior and use team/position IDs only in local mode:

~~~python
if self.match_mode is MatchMode.LOCAL_TWO_PLAYER:
    prefix = 1_000 if team is Team.BLUE else 2_000
    unit_id = prefix + position.row * self.battle.width + position.column
elif team is Team.BLUE:
    unit_id = 1_000 + position.row * self.battle.width + position.column
else:
    unit_id = self._next_unit_id
    self._next_unit_id += 1
~~~

- [ ] **Step 5: Add failing refund, pass, start, stable-ID, and restart tests**

Append:

~~~python
def test_local_refund_pass_start_and_restart() -> None:
    controller = GameController()
    controller.load_local_two_player()
    assert controller.place_current_unit("infantry", Position(9, 2)).ok
    assert controller.active_team is Team.RED

    wrong_team = controller.remove_current_unit(Position(9, 2))
    assert not wrong_team.ok
    assert controller.active_team is Team.RED

    passed = controller.pass_turn()
    assert passed.ok
    assert controller.active_team is Team.BLUE

    refunded = controller.remove_current_unit(Position(9, 2))
    assert refunded.ok
    assert controller.budget_for(Team.BLUE) == 2_000
    assert controller.active_team is Team.BLUE

    no_teams = controller.start_battle()
    assert not no_teams.ok

    assert controller.place_current_unit("infantry", Position(9, 2)).ok
    assert controller.place_current_unit("infantry", Position(2, 2)).ok
    assert controller.start_battle().ok

    controller.restart()
    assert controller.battle.state.value == "setup"
    assert controller.battle.units == []
    assert controller.active_team is Team.BLUE
    assert controller.team_budgets == {
        Team.BLUE: 2_000,
        Team.RED: 2_000,
    }


def test_local_ids_depend_on_team_and_position_not_click_history() -> None:
    first = GameController()
    first.load_local_two_player()
    first.place_current_unit("infantry", Position(9, 2))
    first.place_current_unit("infantry", Position(2, 2))

    second = GameController()
    second.load_local_two_player()
    second.pass_turn()
    second.place_current_unit("infantry", Position(2, 2))
    second.place_current_unit("infantry", Position(9, 2))

    first_ids = {
        (unit.team, unit.position): unit.unit_id
        for unit in first.battle.units
    }
    second_ids = {
        (unit.team, unit.position): unit.unit_id
        for unit in second.battle.units
    }
    assert first_ids == second_ids
~~~

Run and confirm these fail before the new APIs exist.

- [ ] **Step 6: Implement refund, pass, local start, and restart**

Add:

~~~python
def remove_current_unit(self, position: Position) -> ActionResult:
    if self.match_mode is not MatchMode.LOCAL_TWO_PLAYER:
        return ActionResult(False, "Choose Local 2 Player first.")
    if self.battle.state is not BattleState.SETUP:
        return ActionResult(False, "Deployment is locked during battle.")
    removed = self.battle.remove_unit_at(position, self.active_team)
    if removed is None:
        return ActionResult(
            False,
            f"Right-click a {self.active_team.value} unit to refund it.",
        )
    self.team_budgets[self.active_team] += removed.cost
    return ActionResult(True, f"{removed.display_name} refunded.")

def pass_turn(self) -> ActionResult:
    if (
        self.match_mode is not MatchMode.LOCAL_TWO_PLAYER
        or self.battle.state is not BattleState.SETUP
    ):
        return ActionResult(False, "Passing is only available during local setup.")
    team = self.active_team
    self._switch_active_team()
    return ActionResult(True, f"{team.value.title()} passed.")
~~~

Replace start_battle and restart with the mode-aware versions below:

~~~python
def start_battle(self) -> ActionResult:
    if (
        self.match_mode is MatchMode.CAMPAIGN
        and self.campaign is None
    ):
        return ActionResult(False, "Choose a campaign first.")

    living_teams = {
        unit.team
        for unit in self.battle.living_units
    }
    if self.match_mode is MatchMode.LOCAL_TWO_PLAYER:
        if living_teams != {Team.BLUE, Team.RED}:
            return ActionResult(
                False,
                "Both Blue and Red must deploy at least one unit.",
            )
    elif Team.BLUE not in living_teams:
        return ActionResult(False, "Deploy at least one blue unit.")

    if not self.battle.start():
        return ActionResult(False, "The battle cannot start yet.")
    return ActionResult(True, "Battle started!")

def restart(self) -> None:
    if self.match_mode is MatchMode.LOCAL_TWO_PLAYER:
        self.load_local_two_player()
    elif self.campaign_index is not None:
        self.load_campaign(self.campaign_index, self.difficulty)
~~~

- [ ] **Step 7: Run controller and campaign regression tests**

Run:

~~~bash
.venv/bin/python -m pytest tests/test_local_two_player.py tests/test_domain.py -q
~~~

Expected: all tests pass.

- [ ] **Step 8: Commit local controller behavior**

~~~bash
git add src/dawn_tactics/controller.py tests/test_local_two_player.py
git commit -m "Add alternating local two-player deployment"
~~~

### Task 3: Local menu, dual-budget UI, and team-aware input

**Files:**
- Modify: src/dawn_tactics/game.py
- Modify: tests/test_game_ui.py

- [ ] **Step 1: Write failing menu and local-layout geometry tests**

Add imports for MatchMode and terrain constants, then append:

~~~python
def test_local_two_player_menu_card_does_not_overlap_campaigns(app: GameApp) -> None:
    local = app._local_two_player_rect()
    assert all(not local.colliderect(rect) for rect in app._campaign_rects())
    assert local.bottom < WINDOW_SIZE[1] - 34


def test_local_panel_shows_split_actions_without_overlap(app: GameApp) -> None:
    app._load_local_two_player()
    start = app._start_rect()
    passed = app._pass_rect()
    assert app.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
    assert not start.colliderect(passed)
    assert start.union(passed).width <= PANEL_WIDTH - 48
    assert not start.colliderect(app._restart_rect())
    assert not passed.colliderect(app._restart_rect())
~~~

Run:

~~~bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_ui.py -q
~~~

Expected: failures for missing local UI methods.

- [ ] **Step 2: Add and draw the local menu card**

In GameApp, add _local_two_player_rect returning pygame.Rect(180, 650, 920, 116). Move the footer to y=838. In _draw_menu, draw the local card after campaign cards with:

~~~text
LOCAL 2 PLAYER
$2,000 EACH • ALTERNATE ONE UNIT AT A TIME
SEA + BUILDING TERRAIN • SAME-SCREEN PLAY
~~~

In menu click handling, check the local rect after campaign rects and call _load_local_two_player.

Add:

~~~python
def _load_local_two_player(self) -> None:
    self.controller.load_local_two_player()
    self.mode = "game"
    self.selected_kind = "infantry"
    self.status = "Blue turn: select one unit and deploy it."
    self.visual_events.clear()
    self.simulation_accumulator = 0.0
~~~

- [ ] **Step 3: Route local clicks and keys through current-player APIs**

Replace the grid-action branch with:

~~~python
if button == 1 and self.selected_kind is not None:
    if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
        result = self.controller.place_current_unit(
            self.selected_kind,
            grid_position,
        )
    else:
        result = self.controller.place_blue_unit(
            self.selected_kind,
            grid_position,
        )
    self.status = self._local_turn_status(result.message)
elif button == 3:
    if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
        result = self.controller.remove_current_unit(grid_position)
    else:
        result = self.controller.remove_blue_unit(grid_position)
    self.status = self._local_turn_status(result.message)
~~~

Use these action rectangles:

~~~python
def _start_rect(self) -> pygame.Rect:
    width = (
        168
        if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
        else PANEL_WIDTH - 48
    )
    return pygame.Rect(PANEL_LEFT + 24, 400, width, 48)

def _pass_rect(self) -> pygame.Rect:
    return pygame.Rect(PANEL_LEFT + 208, 400, 168, 48)
~~~

In click handling, before Restart, add:

~~~python
if (
    self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
    and self._pass_rect().collidepoint(mouse_position)
):
    result = self.controller.pass_turn()
    self.status = self._local_turn_status(result.message)
    return
~~~

In _handle_key add:

~~~python
elif (
    key == pygame.K_p
    and self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
):
    result = self.controller.pass_turn()
    self.status = self._local_turn_status(result.message)
~~~

After every successful placement, refund, or pass, use a helper to append the next active team to status:

~~~python
def _local_turn_status(self, message: str) -> str:
    if self.controller.match_mode is not MatchMode.LOCAL_TWO_PLAYER:
        return message
    team = self.controller.active_team.value.title()
    return f"{message} {team} turn."
~~~

- [ ] **Step 4: Draw local headers, labels, budgets, and actions**

Start _draw_game with this exact header selection so local mode does not require
a Campaign:

~~~python
def _draw_game(self) -> None:
    campaign = self.controller.campaign
    if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
        title = "LOCAL 2 PLAYER"
        objective = "Build both forces, then start the automatic battle."
        note = (
            "Map Rule: terrain blocks movement and deployment, "
            "not ranged fire."
        )
        mode_color = (
            BLUE if self.controller.active_team is Team.BLUE else RED
        )
    else:
        if campaign is None:
            return
        difficulty = self.controller.difficulty
        title = f"{campaign.title}  •  {difficulty.value.upper()}"
        objective = campaign.objective_for(difficulty)
        note = f"History Note: {campaign.history_note}"
        mode_color = RED if difficulty is Difficulty.HARD else GREEN

    self._draw_text(title, self.fonts["h1"], mode_color, (40, 24))
    self._draw_text(objective, self.fonts["body"], MUTED, (40, 66))
    if (
        self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
        or settings.SHOW_HISTORY_NOTE
    ):
        self._draw_text(
            note,
            self.fonts["small"],
            (180, 192, 218),
            (40, 101),
        )
    self._draw_grid()
    self._draw_units()
    self._draw_visual_events()
    self._draw_side_panel()

    if self.controller.battle.state in {
        BattleState.BLUE_WIN,
        BattleState.RED_WIN,
        BattleState.DRAW,
    }:
        self._draw_result_overlay()
~~~

The local header copy is:

~~~text
LOCAL 2 PLAYER
Build both forces, then start the automatic battle.
Map Rule: terrain blocks movement and deployment, not ranged fire.
~~~

In _draw_grid, use RED DEPLOYMENT ZONE and BLUE DEPLOYMENT ZONE for local play. Highlight the hovered valid active-team zone with the active team color.

In _draw_side_panel local branch:

- draw BLUE TURN or RED TURN at y=42;
- draw Blue $X and Red $Y on one line at y=78;
- draw the active-team instruction at y=116;
- determine card affordability from controller.active_budget;
- draw START BATTLE and PASS TURN in the split action row;
- draw the terrain legend in the existing lower panel space.

Keep the campaign panel text, budget property, buttons, and geometry unchanged.

Change _result_button_rects so local mode always returns next_rect=None.

- [ ] **Step 5: Write and pass team-aware click tests**

Append:

~~~python
def test_local_grid_clicks_alternate_blue_and_red(app: GameApp) -> None:
    app._load_local_two_player()
    app.selected_kind = "infantry"

    app._handle_click(app._cell_center(Position(9, 2)), 1)
    assert app.controller.active_team is Team.RED
    app._handle_click(app._cell_center(Position(2, 2)), 1)
    assert app.controller.active_team is Team.BLUE

    teams = {(unit.team, unit.position) for unit in app.controller.battle.units}
    assert teams == {
        (Team.BLUE, Position(9, 2)),
        (Team.RED, Position(2, 2)),
    }


def test_local_result_has_no_next_campaign_button(app: GameApp) -> None:
    app._load_local_two_player()
    _, _, next_rect = app._result_button_rects()
    assert next_rect is None
~~~

Run:

~~~bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_ui.py tests/test_local_two_player.py -q
~~~

Expected: all local UI/controller tests pass.

- [ ] **Step 6: Commit local-mode UI**

~~~bash
git add src/dawn_tactics/game.py tests/test_game_ui.py
git commit -m "Add local two-player setup interface"
~~~

### Task 4: Terrain images and rendering

**Files:**
- Create: src/dawn_tactics/assets/terrain/sea.png
- Create: src/dawn_tactics/assets/terrain/building.png
- Create: tests/test_terrain_assets.py
- Modify: src/dawn_tactics/game.py
- Modify: pyproject.toml

- [ ] **Step 1: Write failing terrain-asset registry tests**

Create tests/test_terrain_assets.py:

~~~python
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from dawn_tactics.game import (
    CELL_SIZE,
    TERRAIN_ASSET_FILES,
    GameApp,
    _load_terrain_images,
)


@pytest.fixture
def display() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def test_terrain_asset_registry_has_sea_and_building() -> None:
    assert TERRAIN_ASSET_FILES == {
        "sea": "sea.png",
        "building": "building.png",
    }


def test_terrain_assets_load_with_alpha_and_scale(display: None) -> None:
    images = _load_terrain_images()
    assert set(images) == {"sea", "building"}
    assert all(image.get_size() == (CELL_SIZE - 2, CELL_SIZE - 2) for image in images.values())
    assert all(image.get_flags() & pygame.SRCALPHA for image in images.values())


def test_terrain_image_loader_skips_missing_files(
    tmp_path: Path,
    display: None,
) -> None:
    assert _load_terrain_images(tmp_path) == {}
~~~

- [ ] **Step 2: Run asset tests and observe RED**

Run:

~~~bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_terrain_assets.py -q
~~~

Expected: import failures because the registry and loader do not exist.

- [ ] **Step 3: Generate the two terrain tiles**

Use the imagegen skill with one square-tile request per asset. The sea prompt must request a seamless top-down 1930s-1940s tactical-map water tile, slate-blue water, subtle waves, no text, no units, no shoreline, centered orthographic view. The building prompt must request a top-down compact stone-and-brick military-era town building footprint, intact roof silhouette, muted brown/gray palette, no text, no people, no vehicles, centered with a small transparent margin.

Save the selected outputs at the exact asset paths. Preserve RGBA and resize to a square source between 256 and 1024 pixels; pygame performs final 54x54 scaling. Visually inspect both originals and a 54x54 contact sheet before continuing.

- [ ] **Step 4: Implement loading and procedural fallbacks**

In src/dawn_tactics/game.py add:

~~~python
TERRAIN_ASSET_DIR = Path(__file__).resolve().parent / "assets" / "terrain"
TERRAIN_ASSET_FILES = {
    "sea": "sea.png",
    "building": "building.png",
}
TERRAIN_IMAGE_SIZE = (CELL_SIZE - 2, CELL_SIZE - 2)


def _load_terrain_images(
    asset_dir: Path = TERRAIN_ASSET_DIR,
) -> dict[str, pygame.Surface]:
    images: dict[str, pygame.Surface] = {}
    for kind, filename in TERRAIN_ASSET_FILES.items():
        try:
            source = pygame.image.load(asset_dir / filename).convert_alpha()
        except (FileNotFoundError, pygame.error):
            continue
        images[kind] = pygame.transform.smoothscale(source, TERRAIN_IMAGE_SIZE)
    return images
~~~

Load self.terrain_images in GameApp.__init__.

Add _draw_terrain_tile(tile, rect), which blits the cached image inset by one pixel. When no image exists:

- sea: fill with slate blue and draw three short light-blue wave strokes;
- building: fill with muted brown and draw a dark roof rectangle plus two diagonal roof lines.

Draw every battle terrain tile inside _draw_grid after the territory fill but before the grid border. Add a high-contrast blocked border that does not cover the image.

- [ ] **Step 5: Package the terrain assets**

Change pyproject.toml:

~~~toml
[tool.setuptools.package-data]
dawn_tactics = ["assets/units/*.png", "assets/terrain/*.png"]
~~~

- [ ] **Step 6: Pass assets, fallback, and UI tests**

Append these exact rendering tests:

~~~python
from dawn_tactics.domain import Position
from dawn_tactics.game import GameApp, TERRAIN_IMAGE_SIZE


def _terrain_sample(app: GameApp, position: Position) -> tuple[int, int, int]:
    center = app._cell_center(position)
    return tuple(app.screen.get_at(center)[:3])


def test_draw_local_terrain_blits_cached_images(display: None) -> None:
    app = GameApp()
    try:
        app._load_local_two_player()
        sea = pygame.Surface(TERRAIN_IMAGE_SIZE, pygame.SRCALPHA)
        sea.fill((12, 90, 150, 255))
        building = pygame.Surface(TERRAIN_IMAGE_SIZE, pygame.SRCALPHA)
        building.fill((150, 90, 40, 255))
        app.terrain_images = {"sea": sea, "building": building}
        app._draw_grid()

        assert _terrain_sample(app, Position(5, 0)) == (12, 90, 150)
        assert _terrain_sample(app, Position(3, 4)) == (150, 90, 40)
    finally:
        pygame.quit()


def test_draw_local_terrain_has_procedural_fallbacks(display: None) -> None:
    app = GameApp()
    try:
        app._load_local_two_player()
        app.terrain_images = {}
        app._draw_grid()

        assert _terrain_sample(app, Position(5, 0)) != (28, 36, 50)
        assert _terrain_sample(app, Position(3, 4)) != (51, 31, 42)
    finally:
        pygame.quit()
~~~

Run:

~~~bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_terrain_assets.py tests/test_game_ui.py -q
~~~

Expected: all tests pass.

- [ ] **Step 7: Commit terrain rendering**

~~~bash
git add src/dawn_tactics/assets/terrain src/dawn_tactics/game.py pyproject.toml tests/test_terrain_assets.py tests/test_game_ui.py
git commit -m "Render sea and building terrain"
~~~

### Task 5: Documentation, screenshot QA, and complete regression

**Files:**
- Modify: README.md
- Create: screenshots/local-two-player-setup.png

- [ ] **Step 1: Document local play**

Add a Local 2 Player section to README.md covering:

- click LOCAL 2 PLAYER on the main menu;
- Blue moves first;
- each side starts with $2,000;
- every successful placement changes turn;
- invalid clicks do not consume turn or budget;
- P or PASS TURN changes team;
- right-click refunds only the active team's unit and does not change turn;
- Space or START BATTLE begins automatic combat after both teams deploy;
- sea and buildings block movement and deployment;
- ranged fire is not blocked;
- R resets the local match and Esc returns to menu.

- [ ] **Step 2: Add a deterministic screenshot setup helper**

Extend screenshot CLI with --local-two-player. When present:

1. call _load_local_two_player;
2. place Blue Infantry at (9, 2);
3. place Red Infantry at (2, 2);
4. place Blue Tank at (9, 7);
5. place Red Anti-Tank at (2, 7);
6. draw without starting combat unless --simulate-ticks is positive.

Keep existing --campaign and --difficulty behavior when the flag is absent.

- [ ] **Step 3: Render and inspect the local setup**

Run:

~~~bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m dawn_tactics --local-two-player --screenshot screenshots/local-two-player-setup.png
~~~

Expected: a non-empty 1280x888 PNG with two Blue units, two Red units, twenty sea tiles, four buildings, both budgets, and an active Blue turn after four alternating placements.

Inspect the PNG at original resolution. Correct overlaps, unreadable labels, indistinct terrain, or clipped controls before proceeding.

- [ ] **Step 4: Run focused verification**

~~~bash
.venv/bin/python -m pytest tests/test_local_two_player.py -q
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_ui.py tests/test_terrain_assets.py tests/test_game_assets.py -q
~~~

Expected: all focused tests pass.

- [ ] **Step 5: Run full verification**

~~~bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
git diff --check
~~~

Expected: the full clean-worktree suite passes, compileall emits no errors, and git diff --check emits no output.

- [ ] **Step 6: Build and inspect package contents**

Build a wheel using the available project build tool, then list its contents and confirm both terrain PNGs and all six unit PNGs are present. Do not add a new runtime dependency solely for this check.

- [ ] **Step 7: Commit docs and verified screenshot**

~~~bash
git add README.md src/dawn_tactics/game.py tests/test_game_ui.py screenshots/local-two-player-setup.png
git commit -m "Document and verify local two-player mode"
~~~
