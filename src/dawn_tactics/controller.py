from __future__ import annotations

from dataclasses import dataclass

from .campaigns import CAMPAIGNS, Campaign, Difficulty
from .domain import (
    UNIT_REGISTRY,
    Battle,
    BattleEvent,
    BattleState,
    Position,
    Team,
)


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    message: str


class GameController:
    def __init__(self, difficulty: Difficulty = Difficulty.NORMAL) -> None:
        self.campaign_index: int | None = None
        self.campaign: Campaign | None = None
        self.difficulty = difficulty
        self.battle = Battle()
        self.remaining_budget = 0
        self._next_unit_id = 1

    def load_campaign(
        self,
        campaign_index: int,
        difficulty: Difficulty | None = None,
    ) -> None:
        if not 0 <= campaign_index < len(CAMPAIGNS):
            raise IndexError("Unknown campaign.")
        if difficulty is not None:
            self.difficulty = difficulty
        self.campaign_index = campaign_index
        self.campaign = CAMPAIGNS[campaign_index]
        self.battle = Battle()
        self.remaining_budget = self.campaign.budget_for(self.difficulty)
        self._next_unit_id = 1
        for deployment in self.campaign.enemies_for(self.difficulty):
            self._add_unit(
                deployment.unit_kind,
                Team.RED,
                deployment.position,
            )

    def place_blue_unit(self, unit_kind: str, position: Position) -> ActionResult:
        if self.campaign is None:
            return ActionResult(False, "Choose a campaign first.")
        if self.battle.state is not BattleState.SETUP:
            return ActionResult(False, "Deployment is locked during battle.")
        if unit_kind not in self.campaign.allowed_units:
            return ActionResult(False, "That unit is not available here.")
        unit_class = UNIT_REGISTRY.get(unit_kind)
        if unit_class is None:
            return ActionResult(False, "Unknown unit type.")
        if not self._inside(position):
            return ActionResult(False, "Choose a cell inside the grid.")
        if position.row < self.battle.height - 3:
            return ActionResult(False, "Deploy inside the blue zone.")
        if self.battle.unit_at(position) is not None:
            return ActionResult(False, "That cell is occupied.")
        if self.remaining_budget < unit_class.cost:
            return ActionResult(False, "Not enough budget.")

        self._add_unit(unit_kind, Team.BLUE, position)
        self.remaining_budget -= unit_class.cost
        return ActionResult(True, f"{unit_class.display_name} deployed.")

    def remove_blue_unit(self, position: Position) -> ActionResult:
        if self.battle.state is not BattleState.SETUP:
            return ActionResult(False, "Deployment is locked during battle.")
        removed = self.battle.remove_unit_at(position, Team.BLUE)
        if removed is None:
            return ActionResult(False, "Right-click a blue unit to refund it.")
        self.remaining_budget += removed.cost
        return ActionResult(True, f"{removed.display_name} refunded.")

    def start_battle(self) -> ActionResult:
        if self.campaign is None:
            return ActionResult(False, "Choose a campaign first.")
        blue_units = [
            unit
            for unit in self.battle.living_units
            if unit.team is Team.BLUE
        ]
        if not blue_units:
            return ActionResult(False, "Deploy at least one blue unit.")
        if not self.battle.start():
            return ActionResult(False, "The battle cannot start yet.")
        return ActionResult(True, "Battle started!")

    def restart(self) -> None:
        if self.campaign_index is not None:
            self.load_campaign(self.campaign_index, self.difficulty)

    def step(self) -> tuple[BattleEvent, ...]:
        return self.battle.step()

    def _add_unit(self, unit_kind: str, team: Team, position: Position) -> None:
        unit_class = UNIT_REGISTRY[unit_kind]
        if team is Team.BLUE:
            # A player's internal ID depends on the deployment cell, not the
            # order in which they clicked. Identical layouts therefore produce
            # identical battles, which keeps a difficult mission fair.
            unit_id = 1_000 + position.row * self.battle.width + position.column
        else:
            unit_id = self._next_unit_id
            self._next_unit_id += 1
        unit = unit_class(unit_id, team, position)
        self.battle.add_unit(unit)

    def _inside(self, position: Position) -> bool:
        return (
            0 <= position.row < self.battle.height
            and 0 <= position.column < self.battle.width
        )
