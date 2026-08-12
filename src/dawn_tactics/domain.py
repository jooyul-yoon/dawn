from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Iterable

from . import student_settings as settings
from .student_rules_validation import cavalry_damage_for, machine_gun_damage_for


class Team(str, Enum):
    BLUE = "blue"
    RED = "red"


class BattleState(str, Enum):
    SETUP = "setup"
    RUNNING = "running"
    BLUE_WIN = "blue_win"
    RED_WIN = "red_win"
    DRAW = "draw"


class EventKind(str, Enum):
    MOVE = "move"
    ATTACK = "attack"
    DESTROY = "destroy"
    RESULT = "result"


@dataclass(frozen=True, order=True)
class Position:
    row: int
    column: int

    def distance_to(self, other: Position) -> int:
        return abs(self.row - other.row) + abs(self.column - other.column)

    def neighbors(self, width: int, height: int) -> tuple[Position, ...]:
        candidates = (
            Position(self.row - 1, self.column),
            Position(self.row, self.column - 1),
            Position(self.row, self.column + 1),
            Position(self.row + 1, self.column),
        )
        return tuple(
            point
            for point in candidates
            if 0 <= point.row < height and 0 <= point.column < width
        )


@dataclass(frozen=True)
class BattleEvent:
    kind: EventKind
    unit_id: int | None = None
    target_id: int | None = None
    from_position: Position | None = None
    to_position: Position | None = None
    amount: int = 0
    result: BattleState | None = None


@dataclass(frozen=True)
class MoveAction:
    unit_id: int
    destination: Position


@dataclass(frozen=True)
class AttackAction:
    unit_id: int
    target_id: int
    damage: int
    source_position: Position
    target_position: Position


# ---------------------------------------------------------------------------
# STUDENT LAB START: edit Unit and its subclasses to change the game rules.
# ---------------------------------------------------------------------------


class Unit:
    """Base class for every unit in the simulation.

    This class intentionally contains no pygame code. Students can change the
    rules here and immediately see the result in the game.
    """

    kind: ClassVar[str] = "unit"
    display_name: ClassVar[str] = "Unit"
    short_name: ClassVar[str] = "U"
    cost: ClassVar[int] = 0
    max_hp: ClassVar[int] = 1
    base_damage: ClassVar[int] = 1
    attack_range: ClassVar[int] = 1
    attack_every: ClassVar[int] = 1
    move_every: ClassVar[int] = 1
    armor: ClassVar[str] = "LIGHT"

    def __init__(
        self,
        unit_id: int,
        team: Team,
        position: Position,
    ) -> None:
        self.unit_id = unit_id
        self.team = team
        self.position = position
        self.hp = self.max_hp
        self.last_attack_tick = -self.attack_every
        self.last_move_tick = -self.move_every

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def distance_to(self, other: Unit) -> int:
        return self.position.distance_to(other.position)

    def choose_target(self, enemies: Iterable[Unit]) -> Unit | None:
        living_enemies = [enemy for enemy in enemies if enemy.is_alive]
        if not living_enemies:
            return None
        return min(
            living_enemies,
            key=lambda enemy: (
                self.distance_to(enemy),
                enemy.hp,
                enemy.unit_id,
            ),
        )

    def can_attack(self, target: Unit) -> bool:
        return self.distance_to(target) <= self.attack_range

    def ready_to_attack(self, tick: int) -> bool:
        return tick - self.last_attack_tick >= self.attack_every

    def ready_to_move(self, tick: int) -> bool:
        return tick - self.last_move_tick >= self.move_every

    def damage_against(self, target: Unit) -> int:
        return self.base_damage

    def take_damage(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        self.hp = max(0, self.hp - amount)


class Infantry(Unit):
    kind = "infantry"
    display_name = "Infantry"
    short_name = "I"
    cost = 100
    max_hp = 5
    base_damage = 1
    attack_range = 1
    attack_every = 1
    move_every = 1
    armor = "LIGHT"


class AntiTank(Unit):
    kind = "anti_tank"
    display_name = "Anti-Tank"
    short_name = "AT"
    cost = 250
    max_hp = 4
    base_damage = 1
    attack_range = 2
    attack_every = 2
    move_every = 1
    armor = "LIGHT"

    def damage_against(self, target: Unit) -> int:
        return (
            settings.ANTI_TANK_DAMAGE_VS_HEAVY
            if target.armor == "HEAVY"
            else self.base_damage
        )


class Tank(Unit):
    kind = "tank"
    display_name = settings.TANK_NAME
    short_name = "T"
    cost = settings.TANK_COST
    max_hp = settings.TANK_MAX_HP
    base_damage = settings.TANK_DAMAGE
    attack_range = settings.TANK_RANGE
    attack_every = 2
    move_every = 1
    armor = "HEAVY"


class Artillery(Unit):
    kind = "artillery"
    display_name = "Artillery"
    short_name = "A"
    cost = 350
    max_hp = 4
    base_damage = 4
    attack_range = 5
    attack_every = 3
    move_every = 2
    armor = "LIGHT"


class MachineGun(Unit):
    kind = "machine_gun"
    display_name = "Machine Gun"
    short_name = "MG"
    cost = 300
    max_hp = 5
    base_damage = 1
    attack_range = 3
    attack_every = 2
    move_every = 1
    armor = "LIGHT"

    def damage_against(self, target: Unit) -> int:
        return machine_gun_damage_for(target.armor)


class Cavalry(Unit):
    kind = "cavalry"
    display_name = "Cavalry"
    short_name = "C"
    cost = 200
    max_hp = 6
    base_damage = 1
    attack_range = 1
    attack_every = 1
    move_every = 1
    armor = "LIGHT"

    def damage_against(self, target: Unit) -> int:
        return cavalry_damage_for(target.kind)


UNIT_REGISTRY: dict[str, type[Unit]] = {
    Infantry.kind: Infantry,
    AntiTank.kind: AntiTank,
    Tank.kind: Tank,
    Artillery.kind: Artillery,
    MachineGun.kind: MachineGun,
    Cavalry.kind: Cavalry,
}


# ---------------------------------------------------------------------------
# STUDENT LAB END: the Battle engine below resolves movement and combat.
# ---------------------------------------------------------------------------


class Battle:
    def __init__(
        self,
        width: int = 12,
        height: int = 8,
        max_ticks: int = 180,
    ) -> None:
        if width < 2 or height < 2:
            raise ValueError("The battlefield must be at least 2 x 2.")
        self.width = width
        self.height = height
        self.max_ticks = max_ticks
        self.units: list[Unit] = []
        self.state = BattleState.SETUP
        self.tick = 0
        self.history: list[BattleEvent] = []

    @property
    def living_units(self) -> list[Unit]:
        return [unit for unit in self.units if unit.is_alive]

    def unit_at(self, position: Position) -> Unit | None:
        return next(
            (
                unit
                for unit in self.units
                if unit.is_alive and unit.position == position
            ),
            None,
        )

    def unit_by_id(self, unit_id: int) -> Unit | None:
        return next((unit for unit in self.units if unit.unit_id == unit_id), None)

    def add_unit(self, unit: Unit) -> None:
        if self.state is not BattleState.SETUP:
            raise RuntimeError("Units can only be added during setup.")
        if not self._inside(unit.position):
            raise ValueError("Unit position is outside the battlefield.")
        if self.unit_at(unit.position) is not None:
            raise ValueError("That cell is already occupied.")
        if self.unit_by_id(unit.unit_id) is not None:
            raise ValueError("Unit IDs must be unique.")
        self.units.append(unit)

    def remove_unit_at(self, position: Position, team: Team) -> Unit | None:
        if self.state is not BattleState.SETUP:
            return None
        unit = self.unit_at(position)
        if unit is None or unit.team is not team:
            return None
        self.units.remove(unit)
        return unit

    def start(self) -> bool:
        if self.state is not BattleState.SETUP:
            return False
        teams = {unit.team for unit in self.living_units}
        if teams != {Team.BLUE, Team.RED}:
            return False
        self.state = BattleState.RUNNING
        return True

    def step(self) -> tuple[BattleEvent, ...]:
        if self.state is not BattleState.RUNNING:
            return ()
        if self.tick >= self.max_ticks:
            return self._finish(BattleState.DRAW)

        actors = sorted(self.living_units, key=lambda unit: unit.unit_id)
        attack_actions: list[AttackAction] = []
        move_actions: list[MoveAction] = []

        for actor in actors:
            enemies = [unit for unit in actors if unit.team is not actor.team]
            target = actor.choose_target(enemies)
            if target is None:
                continue

            if actor.can_attack(target):
                if actor.ready_to_attack(self.tick):
                    attack_actions.append(
                        AttackAction(
                            unit_id=actor.unit_id,
                            target_id=target.unit_id,
                            damage=actor.damage_against(target),
                            source_position=actor.position,
                            target_position=target.position,
                        )
                    )
                continue

            if actor.ready_to_move(self.tick):
                destination = self._find_next_step(actor, target)
                if destination is not None:
                    move_actions.append(MoveAction(actor.unit_id, destination))

        events: list[BattleEvent] = []
        occupied = {unit.position for unit in self.living_units}
        reserved: set[Position] = set()
        for action in sorted(move_actions, key=lambda item: item.unit_id):
            actor = self.unit_by_id(action.unit_id)
            if actor is None or not actor.is_alive:
                continue
            if action.destination in occupied or action.destination in reserved:
                continue
            old_position = actor.position
            occupied.remove(old_position)
            actor.position = action.destination
            actor.last_move_tick = self.tick
            occupied.add(action.destination)
            reserved.add(action.destination)
            events.append(
                BattleEvent(
                    EventKind.MOVE,
                    unit_id=actor.unit_id,
                    from_position=old_position,
                    to_position=action.destination,
                )
            )

        damage_by_target: dict[int, int] = {}
        for action in sorted(attack_actions, key=lambda item: item.unit_id):
            actor = self.unit_by_id(action.unit_id)
            target = self.unit_by_id(action.target_id)
            if actor is None or target is None:
                continue
            actor.last_attack_tick = self.tick
            damage_by_target[target.unit_id] = (
                damage_by_target.get(target.unit_id, 0) + action.damage
            )
            events.append(
                BattleEvent(
                    EventKind.ATTACK,
                    unit_id=actor.unit_id,
                    target_id=target.unit_id,
                    from_position=action.source_position,
                    to_position=action.target_position,
                    amount=action.damage,
                )
            )

        for target_id in sorted(damage_by_target):
            target = self.unit_by_id(target_id)
            if target is None:
                continue
            target.take_damage(damage_by_target[target_id])
            if not target.is_alive:
                events.append(
                    BattleEvent(
                        EventKind.DESTROY,
                        unit_id=target.unit_id,
                        from_position=target.position,
                    )
                )

        self.tick += 1
        self.history.extend(events)

        blue_alive = any(
            unit.is_alive and unit.team is Team.BLUE for unit in self.units
        )
        red_alive = any(
            unit.is_alive and unit.team is Team.RED for unit in self.units
        )
        if not blue_alive and not red_alive:
            result_events = self._finish(BattleState.DRAW)
            return tuple(events) + result_events
        if not red_alive:
            result_events = self._finish(BattleState.BLUE_WIN)
            return tuple(events) + result_events
        if not blue_alive:
            result_events = self._finish(BattleState.RED_WIN)
            return tuple(events) + result_events
        if self.tick >= self.max_ticks:
            result_events = self._finish(BattleState.DRAW)
            return tuple(events) + result_events
        return tuple(events)

    def _finish(self, result: BattleState) -> tuple[BattleEvent, ...]:
        self.state = result
        event = BattleEvent(EventKind.RESULT, result=result)
        self.history.append(event)
        return (event,)

    def _inside(self, position: Position) -> bool:
        return (
            0 <= position.row < self.height
            and 0 <= position.column < self.width
        )

    def _find_next_step(self, actor: Unit, target: Unit) -> Position | None:
        occupied = {
            unit.position
            for unit in self.living_units
            if unit.unit_id != actor.unit_id
        }
        frontier: deque[Position] = deque([actor.position])
        parent: dict[Position, Position | None] = {actor.position: None}
        destination: Position | None = None

        while frontier:
            current = frontier.popleft()
            if (
                current != actor.position
                and current.distance_to(target.position) <= actor.attack_range
            ):
                destination = current
                break
            for neighbor in current.neighbors(self.width, self.height):
                if neighbor in parent or neighbor in occupied:
                    continue
                parent[neighbor] = current
                frontier.append(neighbor)

        if destination is None:
            return None

        step = destination
        while parent[step] != actor.position:
            previous = parent[step]
            if previous is None:
                return None
            step = previous
        return step
