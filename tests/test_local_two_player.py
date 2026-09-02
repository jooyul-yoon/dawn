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
from dawn_tactics.local_match import (
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
