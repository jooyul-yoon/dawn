from collections import Counter

import pytest

from dawn_tactics.domain import (
    Battle,
    BattleState,
    EventKind,
    Infantry,
    Position,
    Team,
    Terrain,
)
from dawn_tactics.controller import GameController, MatchMode
from dawn_tactics.campaigns import CAMPAIGNS, Difficulty
from dawn_tactics.local_match import (
    BUILDING_POSITIONS,
    LOCAL_TWO_PLAYER_BUDGET,
    OPEN_CROSSING_COLUMNS,
    build_local_terrain,
)


def test_local_two_player_budget_is_two_thousand() -> None:
    assert LOCAL_TWO_PLAYER_BUDGET == 2_000


def test_local_terrain_is_180_degree_symmetric() -> None:
    terrain_by_position = {
        terrain.position: terrain.kind for terrain in build_local_terrain()
    }

    for position, kind in terrain_by_position.items():
        rotated = Position(11 - position.row, 13 - position.column)
        assert terrain_by_position[rotated] == kind


def test_local_terrain_has_expected_tile_counts() -> None:
    counts = Counter(terrain.kind for terrain in build_local_terrain())

    assert counts == {"sea": 20, "building": 4}


def test_local_terrain_has_the_expected_crossings_and_buildings() -> None:
    terrain = build_local_terrain()
    sea_positions = {
        tile.position
        for tile in terrain
        if tile.kind == "sea"
    }
    building_positions = {
        tile.position
        for tile in terrain
        if tile.kind == "building"
    }

    assert OPEN_CROSSING_COLUMNS == {2, 6, 7, 11}
    assert BUILDING_POSITIONS == (
        Position(3, 4),
        Position(3, 9),
        Position(8, 4),
        Position(8, 9),
    )
    assert all(
        Position(row, column) not in sea_positions
        for row in (5, 6)
        for column in OPEN_CROSSING_COLUMNS
    )
    assert building_positions == set(BUILDING_POSITIONS)


def test_load_local_two_player_initializes_empty_symmetric_setup() -> None:
    controller = GameController()

    controller.load_local_two_player()

    assert controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
    assert controller.campaign is None
    assert controller.campaign_index is None
    assert controller.battle.units == []
    assert [
        (tile.kind, tile.position) for tile in controller.battle.terrain
    ] == [
        (tile.kind, tile.position) for tile in build_local_terrain()
    ]
    assert controller.team_budgets == {
        Team.BLUE: LOCAL_TWO_PLAYER_BUDGET,
        Team.RED: LOCAL_TWO_PLAYER_BUDGET,
    }
    assert controller.active_team is Team.BLUE
    assert controller.active_budget == LOCAL_TWO_PLAYER_BUDGET


def test_load_campaign_resets_local_mode_and_synchronizes_blue_budget() -> None:
    controller = GameController()
    controller.load_local_two_player()

    controller.load_campaign(0, Difficulty.NORMAL)

    campaign_budget = CAMPAIGNS[0].budget_for(Difficulty.NORMAL)
    assert controller.match_mode is MatchMode.CAMPAIGN
    assert controller.active_team is Team.BLUE
    assert controller.remaining_budget == campaign_budget
    assert controller.team_budgets == {Team.BLUE: campaign_budget, Team.RED: 0}


def test_local_deployment_alternates_teams_and_spends_active_budget() -> None:
    controller = GameController()
    controller.load_local_two_player()

    blue = controller.place_current_unit("infantry", Position(7, 0))

    assert blue.ok
    assert controller.active_team is Team.RED
    assert controller.budget_for(Team.BLUE) == 1_900
    assert controller.budget_for(Team.RED) == 2_000
    assert controller.active_budget == 2_000

    red = controller.place_current_unit("cavalry", Position(4, 0))

    assert red.ok
    assert controller.active_team is Team.BLUE
    assert controller.budget_for(Team.BLUE) == 1_900
    assert controller.budget_for(Team.RED) == 1_800


def test_local_deployment_allows_every_registered_unit_type() -> None:
    controller = GameController()
    controller.load_local_two_player()

    for column, unit_kind in enumerate(
        ("infantry", "anti_tank", "tank", "artillery", "machine_gun", "cavalry")
    ):
        row = 7 if controller.active_team is Team.BLUE else 4
        assert controller.place_current_unit(unit_kind, Position(row, column)).ok

    assert {unit.kind for unit in controller.battle.units} == {
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    }


@pytest.mark.parametrize(
    ("team", "allowed", "disallowed"),
    (
        (Team.BLUE, Position(7, 1), Position(6, 1)),
        (Team.RED, Position(4, 1), Position(5, 1)),
    ),
)
def test_local_deployment_enforces_each_teams_five_row_zone(
    team: Team,
    allowed: Position,
    disallowed: Position,
) -> None:
    controller = GameController()
    controller.load_local_two_player()
    if team is Team.RED:
        assert controller.pass_turn().ok

    budget = controller.active_budget
    invalid = controller.place_current_unit("infantry", disallowed)

    assert not invalid.ok
    assert controller.active_team is team
    assert controller.active_budget == budget
    assert controller.place_current_unit("infantry", allowed).ok


@pytest.mark.parametrize(
    ("kind", "position"),
    (
        ("infantry", Position(-1, 0)),
        ("infantry", Position(12, 0)),
        ("infantry", Position(6, 0)),
        ("infantry", Position(8, 4)),
        ("unknown", Position(7, 0)),
    ),
)
def test_invalid_local_deployments_do_not_change_budget_turn_or_units(
    kind: str,
    position: Position,
) -> None:
    controller = GameController()
    controller.load_local_two_player()
    before_budgets = dict(controller.team_budgets)

    result = controller.place_current_unit(kind, position)

    assert not result.ok
    assert controller.team_budgets == before_budgets
    assert controller.active_team is Team.BLUE
    assert controller.battle.units == []


def test_local_deployment_rejects_occupied_cell_and_insufficient_budget() -> None:
    controller = GameController()
    controller.load_local_two_player()
    assert controller.place_current_unit("infantry", Position(7, 0)).ok
    assert controller.place_current_unit("infantry", Position(4, 0)).ok
    before_budgets = dict(controller.team_budgets)

    occupied = controller.place_current_unit("infantry", Position(7, 0))
    assert not occupied.ok
    assert controller.team_budgets == before_budgets
    assert controller.active_team is Team.BLUE

    controller.team_budgets[Team.BLUE] = 0
    before_units = list(controller.battle.units)
    insufficient = controller.place_current_unit("infantry", Position(7, 1))

    assert not insufficient.ok
    assert controller.team_budgets[Team.BLUE] == 0
    assert controller.active_team is Team.BLUE
    assert controller.battle.units == before_units


def test_local_refund_only_removes_the_active_teams_unit_without_switching() -> None:
    controller = GameController()
    controller.load_local_two_player()
    blue_position = Position(7, 0)
    red_position = Position(4, 0)
    assert controller.place_current_unit("infantry", blue_position).ok
    assert controller.place_current_unit("cavalry", red_position).ok

    before_budgets = dict(controller.team_budgets)
    wrong_team = controller.remove_current_unit(red_position)

    assert not wrong_team.ok
    assert controller.team_budgets == before_budgets
    assert controller.active_team is Team.BLUE

    refunded = controller.remove_current_unit(blue_position)

    assert refunded.ok
    assert controller.budget_for(Team.BLUE) == LOCAL_TWO_PLAYER_BUDGET
    assert controller.active_team is Team.BLUE
    assert controller.battle.unit_at(blue_position) is None

    before_budgets = dict(controller.team_budgets)
    empty = controller.remove_current_unit(blue_position)
    assert not empty.ok
    assert controller.team_budgets == before_budgets
    assert controller.active_team is Team.BLUE


def test_local_pass_keeps_budgets_and_switches_active_team() -> None:
    controller = GameController()
    controller.load_local_two_player()
    before_budgets = dict(controller.team_budgets)

    result = controller.pass_turn()

    assert result.ok
    assert controller.active_team is Team.RED
    assert controller.team_budgets == before_budgets
    assert controller.remaining_budget == controller.active_budget


def test_local_start_requires_each_team_then_starts_battle() -> None:
    controller = GameController()
    controller.load_local_two_player()

    assert not controller.start_battle().ok
    assert controller.place_current_unit("infantry", Position(7, 0)).ok
    assert not controller.start_battle().ok
    assert controller.place_current_unit("infantry", Position(4, 0)).ok

    assert controller.start_battle().ok
    assert controller.battle.state is BattleState.RUNNING


def test_local_restart_restores_empty_blue_setup_and_full_budgets() -> None:
    controller = GameController()
    controller.load_local_two_player()
    assert controller.place_current_unit("infantry", Position(7, 0)).ok

    controller.restart()

    assert controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
    assert controller.battle.units == []
    assert controller.active_team is Team.BLUE
    assert controller.team_budgets == {
        Team.BLUE: LOCAL_TWO_PLAYER_BUDGET,
        Team.RED: LOCAL_TWO_PLAYER_BUDGET,
    }


def test_local_unit_ids_are_stable_for_team_and_position() -> None:
    first = GameController()
    first.load_local_two_player()
    assert first.place_current_unit("infantry", Position(7, 0)).ok
    assert first.place_current_unit("infantry", Position(4, 0)).ok
    first_ids = {
        (unit.team, unit.position): unit.unit_id
        for unit in first.battle.units
    }

    second = GameController()
    second.load_local_two_player()
    assert second.pass_turn().ok
    assert second.place_current_unit("infantry", Position(4, 0)).ok
    assert second.place_current_unit("infantry", Position(7, 0)).ok
    second_ids = {
        (unit.team, unit.position): unit.unit_id
        for unit in second.battle.units
    }

    assert second_ids == first_ids


def test_terrain_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="Unknown terrain kind"):
        Terrain("forest", Position(1, 1))


def test_battle_rejects_duplicate_terrain_positions() -> None:
    terrain = (
        Terrain("sea", Position(1, 1)),
        Terrain("building", Position(1, 1)),
    )

    with pytest.raises(ValueError, match="duplicate"):
        Battle(terrain=terrain)


def test_battle_rejects_terrain_outside_map() -> None:
    with pytest.raises(ValueError, match="outside"):
        Battle(terrain=(Terrain("sea", Position(12, 0)),))


def test_deployment_rejects_building_terrain() -> None:
    blocked_position = Position(1, 1)
    battle = Battle(terrain=(Terrain("building", blocked_position),))

    with pytest.raises(ValueError, match="blocked by terrain"):
        battle.add_unit(Infantry(1, Team.BLUE, blocked_position))


def test_infantry_routes_through_open_sea_crossing() -> None:
    battle = Battle(terrain=build_local_terrain())
    battle.add_unit(Infantry(1, Team.BLUE, Position(10, 4)))
    battle.add_unit(Infantry(2, Team.RED, Position(1, 4)))
    assert battle.start()

    crossing_columns: set[int] = set()
    while battle.state is BattleState.RUNNING:
        events = battle.step()
        assert all(
            not battle.blocks_movement(unit.position)
            for unit in battle.living_units
        )
        crossing_columns.update(
            event.to_position.column
            for event in events
            if event.kind is EventKind.MOVE
            and event.to_position is not None
            and event.to_position.row in {5, 6}
        )

    assert crossing_columns
    assert crossing_columns <= OPEN_CROSSING_COLUMNS
