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
        Terrain("building", position) for position in BUILDING_POSITIONS
    )
    return sea + buildings
