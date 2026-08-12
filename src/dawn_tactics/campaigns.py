from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from . import student_settings as settings
from .domain import Position


class Difficulty(str, Enum):
    NORMAL = "normal"
    HARD = "hard"


@dataclass(frozen=True)
class Deployment:
    unit_kind: str
    position: Position


@dataclass(frozen=True)
class Campaign:
    title: str
    objective: str
    history_note: str
    starting_budget: int
    enemies: tuple[Deployment, ...]
    hard_budget_penalty: int
    hard_reinforcements: tuple[Deployment, ...]
    allowed_units: tuple[str, ...] = (
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    )

    def budget_for(self, difficulty: Difficulty) -> int:
        if difficulty is Difficulty.HARD:
            return max(0, self.starting_budget - self.hard_budget_penalty)
        return self.starting_budget

    def enemies_for(self, difficulty: Difficulty) -> tuple[Deployment, ...]:
        if difficulty is Difficulty.HARD:
            return self.enemies + self.hard_reinforcements
        return self.enemies

    def objective_for(self, difficulty: Difficulty) -> str:
        return f"{self.objective} Budget: ${self.budget_for(difficulty):,}."

    def mode_note(self, difficulty: Difficulty) -> str:
        if difficulty is Difficulty.NORMAL:
            return "Normal rules: original budget and enemy force."
        reinforcement_count = len(self.hard_reinforcements)
        noun = "reinforcement" if reinforcement_count == 1 else "reinforcements"
        return (
            f"Hard rules: ${self.hard_budget_penalty:,} less budget and "
            f"{reinforcement_count} enemy {noun}."
        )


CAMPAIGNS: tuple[Campaign, ...] = (
    Campaign(
        title="First Deployment",
        objective="Defeat a light infantry line.",
        history_note="Combined roles are often stronger than one unit type alone.",
        starting_budget=settings.FIRST_DEPLOYMENT_BUDGET,
        enemies=(
            Deployment("infantry", Position(2, 4)),
            Deployment("infantry", Position(2, 7)),
            Deployment("infantry", Position(2, 10)),
        ),
        hard_budget_penalty=50,
        hard_reinforcements=(
            Deployment("anti_tank", Position(3, 6)),
        ),
    ),
    Campaign(
        title="Tank Breaker",
        objective="Destroy two tanks and their escort.",
        history_note="Anti-tank teams trade protection for specialized firepower.",
        starting_budget=settings.TANK_BREAKER_BUDGET,
        enemies=(
            Deployment("tank", Position(2, 5)),
            Deployment("tank", Position(2, 8)),
            Deployment("infantry", Position(3, 7)),
        ),
        hard_budget_penalty=100,
        hard_reinforcements=(
            Deployment("infantry", Position(3, 4)),
        ),
    ),
    Campaign(
        title="Combined Arms",
        objective="Build a balanced force against every enemy role.",
        history_note="Armored forces rely on support, positioning, and coordination.",
        starting_budget=settings.COMBINED_ARMS_BUDGET,
        enemies=(
            Deployment("artillery", Position(1, 7)),
            Deployment("infantry", Position(2, 4)),
            Deployment("infantry", Position(2, 9)),
            Deployment("anti_tank", Position(3, 4)),
            Deployment("tank", Position(3, 6)),
            Deployment("anti_tank", Position(3, 9)),
        ),
        hard_budget_penalty=200,
        hard_reinforcements=(
            Deployment("artillery", Position(1, 5)),
        ),
    ),
)
