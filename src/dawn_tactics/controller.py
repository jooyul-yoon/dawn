from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .campaigns import CAMPAIGNS, Campaign, Difficulty
from .domain import (
    TERRITORY_DEPTH,
    UNIT_REGISTRY,
    Battle,
    BattleEvent,
    BattleState,
    Position,
    Team,
)
from .local_match import LOCAL_TWO_PLAYER_BUDGET, build_local_terrain


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    message: str


class MatchMode(str, Enum):
    CAMPAIGN = "campaign"
    LOCAL_TWO_PLAYER = "local_two_player"


class GameController:
    def __init__(self, difficulty: Difficulty = Difficulty.NORMAL) -> None:
        self.campaign_index: int | None = None
        self.campaign: Campaign | None = None
        self.difficulty = difficulty
        self.battle = Battle()
        self.match_mode = MatchMode.CAMPAIGN
        self.team_budgets = {Team.BLUE: 0, Team.RED: 0}
        self.active_team = Team.BLUE
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
        self.match_mode = MatchMode.CAMPAIGN
        self.campaign_index = campaign_index
        self.campaign = CAMPAIGNS[campaign_index]
        self.battle = Battle()
        self.remaining_budget = self.campaign.budget_for(self.difficulty)
        self.team_budgets = {Team.BLUE: self.remaining_budget, Team.RED: 0}
        self.active_team = Team.BLUE
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
        if position.row < self.battle.height - TERRITORY_DEPTH:
            return ActionResult(False, "Deploy inside the blue zone.")
        if self.battle.unit_at(position) is not None:
            return ActionResult(False, "That cell is occupied.")
        if self.remaining_budget < unit_class.cost:
            return ActionResult(False, "Not enough budget.")

        self._add_unit(unit_kind, Team.BLUE, position)
        self.remaining_budget -= unit_class.cost
        self.team_budgets[Team.BLUE] = self.remaining_budget
        return ActionResult(True, f"{unit_class.display_name} deployed.")

    def remove_blue_unit(self, position: Position) -> ActionResult:
        if self.battle.state is not BattleState.SETUP:
            return ActionResult(False, "Deployment is locked during battle.")
        removed = self.battle.remove_unit_at(position, Team.BLUE)
        if removed is None:
            return ActionResult(False, "Right-click a blue unit to refund it.")
        self.remaining_budget += removed.cost
        self.team_budgets[Team.BLUE] = self.remaining_budget
        return ActionResult(True, f"{removed.display_name} refunded.")

    def load_local_two_player(self) -> None:
        self.match_mode = MatchMode.LOCAL_TWO_PLAYER
        self.campaign_index = None
        self.campaign = None
        self.battle = Battle(terrain=build_local_terrain())
        self.team_budgets = {
            Team.BLUE: LOCAL_TWO_PLAYER_BUDGET,
            Team.RED: LOCAL_TWO_PLAYER_BUDGET,
        }
        self.active_team = Team.BLUE
        self._sync_remaining_budget()
        self._next_unit_id = 1

    def budget_for(self, team: Team) -> int:
        if self.match_mode is MatchMode.CAMPAIGN and team is Team.BLUE:
            return self.remaining_budget
        return self.team_budgets[team]

    @property
    def active_budget(self) -> int:
        return self.budget_for(self.active_team)

    def place_current_unit(
        self,
        unit_kind: str,
        position: Position,
    ) -> ActionResult:
        if self.match_mode is not MatchMode.LOCAL_TWO_PLAYER:
            return ActionResult(False, "Start a local two-player match first.")
        if self.battle.state is not BattleState.SETUP:
            return ActionResult(False, "Deployment is locked during battle.")
        unit_class = UNIT_REGISTRY.get(unit_kind)
        if unit_class is None:
            return ActionResult(False, "Unknown unit type.")
        if not self._inside(position):
            return ActionResult(False, "Choose a cell inside the grid.")
        if not self._in_local_zone(self.active_team, position):
            return ActionResult(False, f"Deploy inside the {self.active_team.value} zone.")
        if self.battle.blocks_deployment(position):
            return ActionResult(False, "That cell is blocked by terrain.")
        if self.battle.unit_at(position) is not None:
            return ActionResult(False, "That cell is occupied.")
        if self.active_budget < unit_class.cost:
            return ActionResult(False, "Not enough budget.")

        self._add_unit(unit_kind, self.active_team, position)
        self.team_budgets[self.active_team] -= unit_class.cost
        deployed_team = self.active_team
        self._flip_active_team()
        return ActionResult(
            True,
            f"{unit_class.display_name} deployed for {deployed_team.value}.",
        )

    def remove_current_unit(self, position: Position) -> ActionResult:
        if self.match_mode is not MatchMode.LOCAL_TWO_PLAYER:
            return ActionResult(False, "Start a local two-player match first.")
        if self.battle.state is not BattleState.SETUP:
            return ActionResult(False, "Deployment is locked during battle.")
        removed = self.battle.remove_unit_at(position, self.active_team)
        if removed is None:
            return ActionResult(
                False,
                f"Choose a {self.active_team.value} unit to refund.",
            )
        self.team_budgets[self.active_team] += removed.cost
        self._sync_remaining_budget()
        return ActionResult(True, f"{removed.display_name} refunded.")

    def pass_turn(self) -> ActionResult:
        if self.match_mode is not MatchMode.LOCAL_TWO_PLAYER:
            return ActionResult(False, "Start a local two-player match first.")
        if self.battle.state is not BattleState.SETUP:
            return ActionResult(False, "Deployment is locked during battle.")
        self._flip_active_team()
        return ActionResult(True, f"{self.active_team.value.title()}'s turn.")

    def start_battle(self) -> ActionResult:
        if self.match_mode is MatchMode.LOCAL_TWO_PLAYER:
            teams = {unit.team for unit in self.battle.living_units}
            if teams != {Team.BLUE, Team.RED}:
                return ActionResult(False, "Deploy at least one unit for each team.")
            if not self.battle.start():
                return ActionResult(False, "The battle cannot start yet.")
            return ActionResult(True, "Battle started!")
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
        if self.match_mode is MatchMode.LOCAL_TWO_PLAYER:
            self.load_local_two_player()
            return
        if self.campaign_index is not None:
            self.load_campaign(self.campaign_index, self.difficulty)

    def step(self) -> tuple[BattleEvent, ...]:
        return self.battle.step()

    def _add_unit(self, unit_kind: str, team: Team, position: Position) -> None:
        unit_class = UNIT_REGISTRY[unit_kind]
        if self.match_mode is MatchMode.LOCAL_TWO_PLAYER:
            team_base = 1_000 if team is Team.BLUE else 2_000
            unit_id = team_base + position.row * self.battle.width + position.column
        elif team is Team.BLUE:
            # A player's internal ID depends on the deployment cell, not the
            # order in which they clicked. Identical layouts therefore produce
            # identical battles, which keeps a difficult mission fair.
            unit_id = 1_000 + position.row * self.battle.width + position.column
        else:
            unit_id = self._next_unit_id
            self._next_unit_id += 1
        unit = unit_class(unit_id, team, position)
        self.battle.add_unit(unit)

    def _in_local_zone(self, team: Team, position: Position) -> bool:
        if team is Team.RED:
            return position.row < TERRITORY_DEPTH
        return position.row >= self.battle.height - TERRITORY_DEPTH

    def _flip_active_team(self) -> None:
        self.active_team = (
            Team.RED if self.active_team is Team.BLUE else Team.BLUE
        )
        self._sync_remaining_budget()

    def _sync_remaining_budget(self) -> None:
        self.remaining_budget = self.team_budgets[self.active_team]

    def _inside(self, position: Position) -> bool:
        return (
            0 <= position.row < self.battle.height
            and 0 <= position.column < self.battle.width
        )
