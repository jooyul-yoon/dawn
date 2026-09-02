from __future__ import annotations

import argparse
import time
from pathlib import Path

import pygame

from . import student_settings as settings
from .campaigns import CAMPAIGNS, VERIFIED_BLUE_LAYOUTS, Difficulty
from .controller import ActionResult, GameController, MatchMode
from .domain import (
    DEFAULT_BATTLE_HEIGHT,
    DEFAULT_BATTLE_WIDTH,
    TERRITORY_DEPTH,
    UNIT_REGISTRY,
    BattleEvent,
    BattleState,
    EventKind,
    Position,
    Team,
    Unit,
)
from .settings_validation import validate_student_settings
from .student_rules_validation import validate_student_rules


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
UNIT_ASSET_DIR = Path(__file__).resolve().parent / "assets" / "units"
UNIT_ASSET_FILES = {
    "infantry": "infantry.png",
    "anti_tank": "anti_tank.png",
    "tank": "tank.png",
    "artillery": "artillery.png",
    "machine_gun": "machine_gun.png",
    "cavalry": "cavalry.png",
}
BATTLE_UNIT_IMAGE_SIZE = (48, 48)
CARD_UNIT_IMAGE_SIZE = (44, 44)
BATTLE_HP_BAR_SIZE = (42, 5)
HP_TEXT_OFFSET_Y = 19

BACKGROUND = (13, 18, 30)
PANEL = (25, 33, 50)
PANEL_LIGHT = (36, 47, 68)
TEXT = (235, 240, 248)
MUTED = (157, 170, 191)
ACCENT = (255, 199, 92)
BLUE = (74, 151, 255)
RED = (237, 91, 105)
GREEN = (83, 204, 142)
ENEMY_ZONE_COLOR = (51, 31, 42)
NEUTRAL_ZONE_COLOR = (28, 36, 50)
BLUE_ZONE_COLOR = (25, 45, 67)

UNIT_KINDS = (
    "infantry",
    "anti_tank",
    "tank",
    "artillery",
    "machine_gun",
    "cavalry",
)


def unit_rule_text(kind: str) -> str:
    unit_class = UNIT_REGISTRY[kind]
    if kind == "anti_tank":
        return (
            f"DMG {unit_class.base_damage} / "
            f"{settings.ANTI_TANK_DAMAGE_VS_HEAVY} vs TANK"
        )
    if kind == "machine_gun":
        return f"DMG BY ARMOR  RNG {unit_class.attack_range}"
    if kind == "cavalry":
        return f"DMG BY TYPE  RNG {unit_class.attack_range}"
    return f"DMG {unit_class.base_damage}  RNG {unit_class.attack_range}"


def _load_unit_images(
    size: tuple[int, int],
    asset_dir: Path = UNIT_ASSET_DIR,
) -> dict[str, pygame.Surface]:
    images: dict[str, pygame.Surface] = {}
    for kind, filename in UNIT_ASSET_FILES.items():
        try:
            source = pygame.image.load(asset_dir / filename).convert_alpha()
        except (FileNotFoundError, pygame.error):
            continue
        images[kind] = pygame.transform.smoothscale(source, size)
    return images


def _battle_hp_bar_rect(center: tuple[int, int]) -> pygame.Rect:
    width, height = BATTLE_HP_BAR_SIZE
    return pygame.Rect(
        center[0] - width // 2,
        center[1] - CELL_SIZE // 2 + 1,
        width,
        height,
    )


def _deployment_zone_label_position(battle_height: int) -> tuple[int, int]:
    return (
        GRID_LEFT + 10,
        GRID_TOP + (battle_height - TERRITORY_DEPTH) * CELL_SIZE + 8,
    )


class GameApp:
    def __init__(
        self,
        default_difficulty: Difficulty = Difficulty.HARD,
    ) -> None:
        validate_student_settings()
        validate_student_rules()
        pygame.init()
        pygame.display.set_caption(settings.GAME_TITLE.title())
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.unit_images = _load_unit_images(BATTLE_UNIT_IMAGE_SIZE)
        self.unit_card_images = _load_unit_images(CARD_UNIT_IMAGE_SIZE)
        self.clock = pygame.time.Clock()
        self.fonts = {
            "title": pygame.font.Font(None, 64),
            "h1": pygame.font.Font(None, 40),
            "h2": pygame.font.Font(None, 30),
            "body": pygame.font.Font(None, 24),
            "small": pygame.font.Font(None, 20),
            "tiny": pygame.font.Font(None, 17),
            "card_rule": pygame.font.Font(None, 14),
        }
        self.controller = GameController(default_difficulty)
        self.selected_difficulty = default_difficulty
        self.mode = "menu"
        self.selected_kind: str | None = None
        self.status = "Choose a campaign to begin."
        self.running = True
        self.simulation_accumulator = 0.0
        self.visual_events: list[tuple[BattleEvent, float]] = []

    def run(self) -> None:
        while self.running:
            elapsed = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(elapsed)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event.pos, event.button)

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self._go_to_menu()
            return
        if self.mode != "game":
            return
        number_keys = {
            pygame.K_1: "infantry",
            pygame.K_2: "anti_tank",
            pygame.K_3: "tank",
            pygame.K_4: "artillery",
            pygame.K_5: "machine_gun",
            pygame.K_6: "cavalry",
        }
        if key in number_keys:
            self.selected_kind = number_keys[key]
            self.status = f"Selected {UNIT_REGISTRY[self.selected_kind].display_name}."
        elif key == pygame.K_SPACE:
            result = self.controller.start_battle()
            self.status = result.message
        elif (
            key == pygame.K_p
            and self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
            and self.controller.battle.state is BattleState.SETUP
        ):
            self._set_local_status(self.controller.pass_turn())
        elif key == pygame.K_r:
            self._restart()

    def _handle_click(self, mouse_position: tuple[int, int], button: int) -> None:
        if self.mode == "menu":
            if button != 1:
                return
            for difficulty, rect in self._difficulty_button_rects().items():
                if rect.collidepoint(mouse_position):
                    self.selected_difficulty = difficulty
                    return
            for index, rect in enumerate(self._campaign_rects()):
                if rect.collidepoint(mouse_position):
                    self._load_campaign(index)
                    return
            if self._local_two_player_rect().collidepoint(mouse_position):
                self._load_local_two_player()
            return

        state = self.controller.battle.state
        if state in {
            BattleState.BLUE_WIN,
            BattleState.RED_WIN,
            BattleState.DRAW,
        }:
            restart_rect, menu_rect, next_rect = self._result_button_rects()
            if button == 1 and restart_rect.collidepoint(mouse_position):
                self._restart()
            elif button == 1 and menu_rect.collidepoint(mouse_position):
                self._go_to_menu()
            elif button == 1 and next_rect and next_rect.collidepoint(mouse_position):
                next_index = (self.controller.campaign_index or 0) + 1
                self._load_campaign(next_index)
            return

        if button == 1:
            for kind, rect in self._unit_card_rects().items():
                if rect.collidepoint(mouse_position):
                    self.selected_kind = kind
                    self.status = f"Selected {UNIT_REGISTRY[kind].display_name}."
                    return
            if self._start_rect().collidepoint(mouse_position):
                result = self.controller.start_battle()
                self.status = result.message
                return
            if (
                self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER
                and self.controller.battle.state is BattleState.SETUP
                and self._pass_rect().collidepoint(mouse_position)
            ):
                self._set_local_status(self.controller.pass_turn())
                return
            if self._restart_rect().collidepoint(mouse_position):
                self._restart()
                return
            if self._menu_rect().collidepoint(mouse_position):
                self._go_to_menu()
                return

        grid_position = self._mouse_to_grid(mouse_position)
        if grid_position is None:
            return
        if button == 1 and self.selected_kind is not None:
            if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
                self._set_local_status(
                    self.controller.place_current_unit(
                        self.selected_kind,
                        grid_position,
                    )
                )
            else:
                result = self.controller.place_blue_unit(
                    self.selected_kind,
                    grid_position,
                )
                self.status = result.message
        elif button == 3:
            if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
                self._set_local_status(
                    self.controller.remove_current_unit(grid_position)
                )
            else:
                result = self.controller.remove_blue_unit(grid_position)
                self.status = result.message

    def _update(self, elapsed: float) -> None:
        now = time.monotonic()
        self.visual_events = [
            item for item in self.visual_events if item[1] > now
        ]
        if self.mode != "game":
            return
        if self.controller.battle.state is BattleState.RUNNING:
            self.simulation_accumulator += elapsed
            while self.simulation_accumulator >= SIMULATION_SECONDS:
                self.simulation_accumulator -= SIMULATION_SECONDS
                events = self.controller.step()
                self._remember_visual_events(events)
                if self.controller.battle.state is not BattleState.RUNNING:
                    self.status = self._result_text()
                    self.simulation_accumulator = 0.0
                    break

    def _remember_visual_events(self, events: tuple[BattleEvent, ...]) -> None:
        expiry = time.monotonic() + 0.32
        for event in events:
            if event.kind in {EventKind.ATTACK, EventKind.DESTROY}:
                self.visual_events.append((event, expiry))

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        if self.mode == "menu":
            self._draw_menu()
        else:
            self._draw_game()

    def _draw_menu(self) -> None:
        self._draw_text(settings.GAME_TITLE, self.fonts["title"], TEXT, (640, 54), center=True)
        self._draw_text(
            "Build a force. Test a strategy. Learn Python OOP.",
            self.fonts["h2"],
            MUTED,
            (640, 108),
            center=True,
        )
        self._draw_text("MODE", self.fonts["tiny"], MUTED, (1020, 22))
        for difficulty, rect in self._difficulty_button_rects().items():
            selected = difficulty is self.selected_difficulty
            if difficulty is Difficulty.HARD:
                selected_color = RED
            else:
                selected_color = GREEN
            self._draw_button(
                rect,
                difficulty.value.upper(),
                selected_color if selected else (58, 70, 91),
                dark_text=selected,
            )
        for index, (campaign, rect) in enumerate(
            zip(CAMPAIGNS, self._campaign_rects(), strict=True)
        ):
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            mode_color = (
                RED if self.selected_difficulty is Difficulty.HARD else GREEN
            )
            pygame.draw.rect(
                self.screen,
                PANEL_LIGHT if hovered else PANEL,
                rect,
                border_radius=14,
            )
            pygame.draw.rect(
                self.screen,
                mode_color if hovered else (63, 78, 105),
                rect,
                width=2,
                border_radius=14,
            )
            badge = pygame.Rect(rect.x + 20, rect.y + 20, 54, 54)
            pygame.draw.rect(self.screen, (45, 61, 89), badge, border_radius=12)
            self._draw_text(
                str(index + 1), self.fonts["h1"], ACCENT, badge.center, center=True
            )
            self._draw_text(
                campaign.title,
                self.fonts["h1"],
                TEXT,
                (rect.x + 92, rect.y + 16),
            )
            self._draw_text(
                campaign.objective_for(self.selected_difficulty),
                self.fonts["body"],
                MUTED,
                (rect.x + 92, rect.y + 56),
            )
            self._draw_text(
                f"{self.selected_difficulty.value.upper()}   |   "
                f"{len(campaign.enemies_for(self.selected_difficulty))} enemy units",
                self.fonts["small"],
                mode_color,
                (rect.x + 92, rect.y + 88),
            )
            play_rect = pygame.Rect(rect.right - 145, rect.y + 42, 112, 42)
            self._draw_button(
                play_rect,
                f"PLAY {self.selected_difficulty.value.upper()}",
                mode_color,
                dark_text=True,
            )

        local_rect = self._local_two_player_rect()
        hovered = local_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(
            self.screen,
            PANEL_LIGHT if hovered else PANEL,
            local_rect,
            border_radius=14,
        )
        pygame.draw.rect(
            self.screen,
            ACCENT if hovered else (63, 78, 105),
            local_rect,
            width=2,
            border_radius=14,
        )
        self._draw_text(
            "LOCAL 2 PLAYER",
            self.fonts["h1"],
            TEXT,
            (local_rect.x + 28, local_rect.y + 14),
        )
        self._draw_text(
            "$2,000 EACH • ALTERNATE ONE UNIT AT A TIME",
            self.fonts["body"],
            ACCENT,
            (local_rect.x + 28, local_rect.y + 48),
        )
        self._draw_text(
            "SEA + BUILDING TERRAIN • SAME-SCREEN PLAY",
            self.fonts["small"],
            MUTED,
            (local_rect.x + 28, local_rect.y + 78),
        )
        self._draw_button(
            pygame.Rect(local_rect.right - 145, local_rect.y + 37, 112, 42),
            "PLAY LOCAL",
            ACCENT,
            dark_text=True,
        )

        self._draw_text(
            "Fictional teams • Abstract combat • No graphic violence",
            self.fonts["small"],
            MUTED,
            (640, 838),
            center=True,
        )

    def _draw_game(self) -> None:
        campaign = self.controller.campaign
        if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
            active_color = (
                BLUE if self.controller.active_team is Team.BLUE else RED
            )
            self._draw_text(
                "LOCAL 2 PLAYER",
                self.fonts["h1"],
                active_color,
                (40, 24),
            )
            self._draw_text(
                "Build both forces, then start the automatic battle.",
                self.fonts["body"],
                MUTED,
                (40, 66),
            )
            self._draw_text(
                "Map Rule: terrain blocks movement and deployment, not ranged fire.",
                self.fonts["small"],
                (180, 192, 218),
                (40, 101),
            )
        elif campaign is not None:
            difficulty = self.controller.difficulty
            mode_color = RED if difficulty is Difficulty.HARD else GREEN
            self._draw_text(
                f"{campaign.title}  •  {difficulty.value.upper()}",
                self.fonts["h1"],
                mode_color,
                (40, 24),
            )
            self._draw_text(
                campaign.objective_for(difficulty),
                self.fonts["body"],
                MUTED,
                (40, 66),
            )
            if settings.SHOW_HISTORY_NOTE:
                self._draw_text(
                    f"History Note: {campaign.history_note}",
                    self.fonts["small"],
                    (180, 192, 218),
                    (40, 101),
                )
        else:
            return
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

    def _draw_grid(self) -> None:
        battle = self.controller.battle
        hover = self._mouse_to_grid(pygame.mouse.get_pos())
        for row in range(battle.height):
            for column in range(battle.width):
                rect = pygame.Rect(
                    GRID_LEFT + column * CELL_SIZE,
                    GRID_TOP + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                if row < TERRITORY_DEPTH:
                    color = ENEMY_ZONE_COLOR
                elif row >= battle.height - TERRITORY_DEPTH:
                    color = BLUE_ZONE_COLOR
                else:
                    color = NEUTRAL_ZONE_COLOR
                active_zone = (
                    self.controller.match_mode is not MatchMode.LOCAL_TWO_PLAYER
                )
                if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
                    if self.controller.active_team is Team.RED:
                        active_zone = row < TERRITORY_DEPTH
                    else:
                        active_zone = row >= battle.height - TERRITORY_DEPTH
                if (
                    hover == Position(row, column)
                    and battle.state is BattleState.SETUP
                    and active_zone
                ):
                    color = tuple(min(255, value + 22) for value in color)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (59, 70, 88), rect, width=1)

        if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
            self._draw_text(
                "RED DEPLOYMENT ZONE",
                self.fonts["tiny"],
                (184, 105, 118),
                (GRID_LEFT + 10, GRID_TOP + 8),
            )
            self._draw_text(
                "BLUE DEPLOYMENT ZONE",
                self.fonts["tiny"],
                (105, 157, 205),
                _deployment_zone_label_position(battle.height),
            )
        else:
            self._draw_text(
                "ENEMY ZONE",
                self.fonts["tiny"],
                (184, 105, 118),
                (GRID_LEFT + 10, GRID_TOP + 8),
            )
            self._draw_text(
                "YOUR DEPLOYMENT ZONE",
                self.fonts["tiny"],
                (105, 157, 205),
                _deployment_zone_label_position(battle.height),
            )

    def _draw_units(self) -> None:
        for unit in self.controller.battle.living_units:
            center = self._cell_center(unit.position)
            color = BLUE if unit.team is Team.BLUE else RED
            self._draw_unit_visual(unit, center, color)
            hp_ratio = unit.hp / unit.max_hp
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

    def _draw_unit_visual(
        self,
        unit: Unit,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> bool:
        image = self.unit_images.get(unit.kind)
        if image is None:
            pygame.draw.circle(
                self.screen,
                (8, 12, 20),
                (center[0] + 3, center[1] + 4),
                24,
            )
            self._draw_unit_shape(unit, center, color)
            return False

        pygame.draw.circle(
            self.screen,
            (8, 12, 20),
            (center[0] + 3, center[1] + 4),
            25,
        )
        pygame.draw.circle(self.screen, color, center, 24)
        pygame.draw.circle(self.screen, (238, 243, 250), center, 24, width=2)
        self.screen.blit(image, image.get_rect(center=center))
        return True

    def _draw_unit_shape(
        self,
        unit: Unit,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        x, y = center
        outline = (238, 243, 250)
        if unit.kind == "infantry":
            pygame.draw.circle(self.screen, color, center, 20)
            pygame.draw.circle(self.screen, outline, center, 20, width=2)
        elif unit.kind == "anti_tank":
            points = [(x, y - 23), (x + 23, y), (x, y + 23), (x - 23, y)]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, outline, points, width=2)
        elif unit.kind == "tank":
            body = pygame.Rect(x - 24, y - 17, 48, 34)
            pygame.draw.rect(self.screen, color, body, border_radius=7)
            pygame.draw.rect(self.screen, outline, body, width=2, border_radius=7)
            pygame.draw.circle(self.screen, outline, center, 8, width=2)
            pygame.draw.line(self.screen, outline, (x + 5, y - 5), (x + 27, y - 21), width=4)
        elif unit.kind == "machine_gun":
            base = pygame.Rect(x - 22, y - 13, 38, 26)
            pygame.draw.rect(self.screen, color, base, border_radius=8)
            pygame.draw.rect(self.screen, outline, base, width=2, border_radius=8)
            pygame.draw.line(
                self.screen, outline, (x + 5, y - 3), (x + 28, y - 16), width=4
            )
            pygame.draw.line(
                self.screen, outline, (x - 8, y + 10), (x - 17, y + 23), width=3
            )
            pygame.draw.line(
                self.screen, outline, (x + 4, y + 10), (x + 13, y + 23), width=3
            )
        elif unit.kind == "cavalry":
            points = [
                (x - 22, y - 14),
                (x + 4, y - 21),
                (x + 23, y),
                (x + 4, y + 21),
                (x - 22, y + 14),
                (x - 8, y),
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, outline, points, width=2)
        elif unit.kind == "artillery":
            points = [(x, y - 24), (x + 24, y + 20), (x - 24, y + 20)]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, outline, points, width=2)
            pygame.draw.line(self.screen, outline, (x, y - 5), (x, y - 29), width=4)
        else:
            pygame.draw.circle(self.screen, color, center, 20)
            pygame.draw.circle(self.screen, outline, center, 20, width=2)

        self._draw_text(
            unit.short_name,
            self.fonts["small"],
            TEXT,
            (x, y),
            center=True,
        )

    def _draw_visual_events(self) -> None:
        now = time.monotonic()
        for event, expiry in self.visual_events:
            alpha = max(0.0, min(1.0, (expiry - now) / 0.32))
            if event.kind is EventKind.ATTACK and event.from_position and event.to_position:
                color = (
                    255,
                    round(120 + 90 * alpha),
                    round(80 + 80 * alpha),
                )
                pygame.draw.line(
                    self.screen,
                    color,
                    self._cell_center(event.from_position),
                    self._cell_center(event.to_position),
                    width=max(2, round(5 * alpha)),
                )
            elif event.kind is EventKind.DESTROY and event.from_position:
                pygame.draw.circle(
                    self.screen,
                    ACCENT,
                    self._cell_center(event.from_position),
                    round(18 + 16 * (1 - alpha)),
                    width=3,
                )

    def _draw_unit_card_visual(self, kind: str, rect: pygame.Rect) -> bool:
        center = (rect.x + 27, rect.centery)
        pygame.draw.circle(self.screen, (18, 25, 39), center, 25)
        image = self.unit_card_images.get(kind)
        if image is not None:
            self.screen.blit(image, image.get_rect(center=center))
            return True

        unit_class = UNIT_REGISTRY[kind]
        preview = unit_class(0, Team.BLUE, Position(0, 0))
        self._draw_unit_shape(preview, center, BLUE)
        return False

    def _draw_side_panel(self) -> None:
        panel_rect = pygame.Rect(PANEL_LEFT, 20, PANEL_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(self.screen, PANEL, panel_rect, border_radius=16)
        pygame.draw.rect(self.screen, (50, 65, 91), panel_rect, width=2, border_radius=16)

        if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
            self._draw_local_side_panel()
            return

        state = self.controller.battle.state
        difficulty = self.controller.difficulty
        mode_color = RED if difficulty is Difficulty.HARD else GREEN
        self._draw_text(
            f"COMMAND • {difficulty.value.upper()}",
            self.fonts["h2"],
            mode_color,
            (PANEL_LEFT + 24, 42),
        )
        self._draw_text(
            f"Budget  ${self.controller.remaining_budget:,}",
            self.fonts["h1"],
            mode_color,
            (PANEL_LEFT + 24, 76),
        )
        if state is BattleState.RUNNING:
            instruction = "Units act automatically • R restarts this mission"
        elif state is BattleState.SETUP:
            instruction = "1–6 select • Left-click place • Right-click refund"
        else:
            instruction = "Battle complete • Review the result or try again"
        self._draw_text(
            instruction,
            self.fonts["tiny"],
            MUTED,
            (PANEL_LEFT + 24, 120),
        )

        for kind, rect in self._unit_card_rects().items():
            unit_class = UNIT_REGISTRY[kind]
            selected = kind == self.selected_kind
            affordable = self.controller.remaining_budget >= unit_class.cost
            fill = (42, 55, 79) if affordable else (35, 39, 51)
            pygame.draw.rect(self.screen, fill, rect, border_radius=10)
            pygame.draw.rect(
                self.screen,
                ACCENT if selected else (71, 84, 108),
                rect,
                width=3 if selected else 1,
                border_radius=10,
            )
            self._draw_unit_card_visual(kind, rect)
            text_x = rect.x + 56
            name_color = TEXT if affordable else (113, 121, 137)
            self._draw_text(
                unit_class.display_name,
                self.fonts["body"],
                name_color,
                (text_x, rect.y + 7),
            )
            self._draw_text(
                f"${unit_class.cost}  HP {unit_class.max_hp}",
                self.fonts["small"],
                GREEN if affordable else (99, 106, 119),
                (text_x, rect.y + 30),
            )
            rule_text = unit_rule_text(kind)
            self._draw_text(
                rule_text,
                self.fonts["card_rule"],
                MUTED,
                (text_x, rect.y + 53),
            )

        start_rect = self._start_rect()
        has_blue = any(
            unit.team is Team.BLUE
            for unit in self.controller.battle.living_units
        )
        start_enabled = state is BattleState.SETUP and has_blue
        if state is BattleState.RUNNING:
            start_label = "BATTLE RUNNING"
        elif state is BattleState.SETUP:
            start_label = "START BATTLE"
        else:
            start_label = "BATTLE COMPLETE"
        self._draw_button(
            start_rect,
            start_label,
            GREEN if start_enabled else (75, 83, 96),
            dark_text=start_enabled,
        )
        self._draw_button(self._restart_rect(), "RESTART", (73, 92, 124))
        self._draw_button(self._menu_rect(), "CAMPAIGNS", (73, 92, 124))

        status_rect = self._status_rect()
        pygame.draw.rect(self.screen, (19, 25, 39), status_rect, border_radius=8)
        self._draw_wrapped(
            self.status,
            self.fonts["small"],
            TEXT,
            status_rect.inflate(-18, -12),
        )
        self._draw_text(
            f"Battle tick: {self.controller.battle.tick} / {self.controller.battle.max_ticks}",
            self.fonts["tiny"],
            MUTED,
            (PANEL_LEFT + 24, 574),
        )
        self._draw_text(
            "LEARN BY EDITING",
            self.fonts["small"],
            ACCENT,
            (PANEL_LEFT + 24, 610),
        )
        self._draw_text(
            "Day 2 rules live in student_rules.py",
            self.fonts["tiny"],
            MUTED,
            (PANEL_LEFT + 24, 637),
        )

    def _draw_local_side_panel(self) -> None:
        state = self.controller.battle.state
        active_team = self.controller.active_team
        active_color = BLUE if active_team is Team.BLUE else RED
        self._draw_text(
            f"{active_team.value.upper()} TURN",
            self.fonts["h2"],
            active_color,
            (PANEL_LEFT + 24, 42),
        )
        self._draw_text(
            f"BLUE  ${self.controller.budget_for(Team.BLUE):,}",
            self.fonts["body"],
            BLUE,
            (PANEL_LEFT + 24, 76),
        )
        self._draw_text(
            f"RED  ${self.controller.budget_for(Team.RED):,}",
            self.fonts["body"],
            RED,
            (PANEL_LEFT + 208, 76),
        )
        if state is BattleState.RUNNING:
            instruction = "Units act automatically • R restarts this match"
        elif state is BattleState.SETUP:
            instruction = "1–6 select • Place one unit, then pass turns"
        else:
            instruction = "Battle complete • Review the result or try again"
        self._draw_text(
            instruction,
            self.fonts["tiny"],
            MUTED,
            (PANEL_LEFT + 24, 112),
        )

        for kind, rect in self._unit_card_rects().items():
            unit_class = UNIT_REGISTRY[kind]
            selected = kind == self.selected_kind
            affordable = self.controller.active_budget >= unit_class.cost
            fill = (42, 55, 79) if affordable else (35, 39, 51)
            pygame.draw.rect(self.screen, fill, rect, border_radius=10)
            pygame.draw.rect(
                self.screen,
                active_color if selected else (71, 84, 108),
                rect,
                width=3 if selected else 1,
                border_radius=10,
            )
            self._draw_unit_card_visual(kind, rect)
            text_x = rect.x + 56
            name_color = TEXT if affordable else (113, 121, 137)
            self._draw_text(
                unit_class.display_name,
                self.fonts["body"],
                name_color,
                (text_x, rect.y + 7),
            )
            self._draw_text(
                f"${unit_class.cost}  HP {unit_class.max_hp}",
                self.fonts["small"],
                GREEN if affordable else (99, 106, 119),
                (text_x, rect.y + 30),
            )
            self._draw_text(
                unit_rule_text(kind),
                self.fonts["card_rule"],
                MUTED,
                (text_x, rect.y + 53),
            )

        teams = {unit.team for unit in self.controller.battle.living_units}
        start_enabled = state is BattleState.SETUP and teams == {Team.BLUE, Team.RED}
        if state is BattleState.RUNNING:
            start_label = "BATTLE RUNNING"
        elif state is BattleState.SETUP:
            start_label = "START BATTLE"
        else:
            start_label = "BATTLE COMPLETE"
        self._draw_button(
            self._start_rect(),
            start_label,
            GREEN if start_enabled else (75, 83, 96),
            dark_text=start_enabled,
        )
        self._draw_button(
            self._pass_rect(),
            "PASS (P)",
            active_color if state is BattleState.SETUP else (75, 83, 96),
            dark_text=state is BattleState.SETUP,
        )
        self._draw_button(self._restart_rect(), "RESTART", (73, 92, 124))
        self._draw_button(self._menu_rect(), "CAMPAIGNS", (73, 92, 124))

        status_rect = self._status_rect()
        pygame.draw.rect(self.screen, (19, 25, 39), status_rect, border_radius=8)
        self._draw_wrapped(
            self.status,
            self.fonts["small"],
            TEXT,
            status_rect.inflate(-18, -12),
        )
        self._draw_text(
            f"Battle tick: {self.controller.battle.tick} / {self.controller.battle.max_ticks}",
            self.fonts["tiny"],
            MUTED,
            (PANEL_LEFT + 24, 574),
        )
        self._draw_text(
            "TERRAIN RULES",
            self.fonts["small"],
            ACCENT,
            (PANEL_LEFT + 24, 610),
        )
        self._draw_text(
            "Sea + buildings block movement and deployment.",
            self.fonts["tiny"],
            MUTED,
            (PANEL_LEFT + 24, 637),
        )
        self._draw_text(
            "Ranged fire crosses terrain.",
            self.fonts["tiny"],
            MUTED,
            (PANEL_LEFT + 24, 659),
        )

    def _draw_result_overlay(self) -> None:
        overlay = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 9, 16, 210))
        self.screen.blit(overlay, (GRID_LEFT, GRID_TOP))
        result = self._result_text()
        color = BLUE if self.controller.battle.state is BattleState.BLUE_WIN else RED
        if self.controller.battle.state is BattleState.DRAW:
            color = ACCENT
        center_x = GRID_LEFT + GRID_WIDTH // 2
        self._draw_text(result, self.fonts["title"], color, (center_x, 292), center=True)
        self._draw_text(
            f"Resolved in {self.controller.battle.tick} simulation ticks",
            self.fonts["body"],
            TEXT,
            (center_x, 346),
            center=True,
        )
        restart_rect, menu_rect, next_rect = self._result_button_rects()
        self._draw_button(restart_rect, "RESTART", (73, 92, 124))
        self._draw_button(menu_rect, "CAMPAIGNS", (73, 92, 124))
        if next_rect:
            self._draw_button(next_rect, "NEXT", ACCENT, dark_text=True)

    def _campaign_rects(self) -> list[pygame.Rect]:
        return [pygame.Rect(180, 160 + index * 170, 920, 130) for index in range(3)]

    def _local_two_player_rect(self) -> pygame.Rect:
        return pygame.Rect(180, 650, 920, 116)

    def _difficulty_button_rects(self) -> dict[Difficulty, pygame.Rect]:
        return {
            Difficulty.NORMAL: pygame.Rect(1010, 44, 92, 38),
            Difficulty.HARD: pygame.Rect(1110, 44, 92, 38),
        }

    def _unit_card_rects(self) -> dict[str, pygame.Rect]:
        result: dict[str, pygame.Rect] = {}
        for index, kind in enumerate(UNIT_KINDS):
            column = index % 2
            row = index // 2
            result[kind] = pygame.Rect(
                PANEL_LEFT + 22 + column * 185,
                142 + row * 84,
                174,
                76,
            )
        return result

    def _start_rect(self) -> pygame.Rect:
        if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
            return pygame.Rect(PANEL_LEFT + 24, 400, 168, 48)
        return pygame.Rect(PANEL_LEFT + 24, 400, PANEL_WIDTH - 48, 48)

    def _pass_rect(self) -> pygame.Rect:
        return pygame.Rect(PANEL_LEFT + 208, 400, 168, 48)

    def _restart_rect(self) -> pygame.Rect:
        return pygame.Rect(PANEL_LEFT + 24, 456, 168, 40)

    def _menu_rect(self) -> pygame.Rect:
        return pygame.Rect(PANEL_LEFT + 208, 456, 168, 40)

    def _status_rect(self) -> pygame.Rect:
        return pygame.Rect(PANEL_LEFT + 24, 508, PANEL_WIDTH - 48, 52)

    def _result_button_rects(
        self,
    ) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect | None]:
        y = 402
        restart = pygame.Rect(GRID_LEFT + 154, y, 140, 48)
        menu = pygame.Rect(GRID_LEFT + 314, y, 140, 48)
        next_rect = None
        campaign_index = self.controller.campaign_index or 0
        if (
            self.controller.match_mode is MatchMode.CAMPAIGN
            and campaign_index + 1 < len(CAMPAIGNS)
        ):
            next_rect = pygame.Rect(GRID_LEFT + 474, y, 140, 48)
        return restart, menu, next_rect

    def _load_campaign(self, index: int) -> None:
        self.controller.load_campaign(index, self.selected_difficulty)
        self.mode = "game"
        self.selected_kind = "infantry"
        campaign = self.controller.campaign
        self.status = (
            campaign.mode_note(self.controller.difficulty)
            if campaign
            else "Select a unit, then deploy inside the blue zone."
        )
        self.visual_events.clear()
        self.simulation_accumulator = 0.0

    def _load_local_two_player(self) -> None:
        self.controller.load_local_two_player()
        self.mode = "game"
        self.selected_kind = "infantry"
        self.status = "Blue's turn. Select a unit and deploy in the blue zone."
        self.visual_events.clear()
        self.simulation_accumulator = 0.0

    def _set_local_status(self, result: ActionResult) -> None:
        message = result.message
        active_turn = f"{self.controller.active_team.value.title()}'s turn."
        self.status = message if message == active_turn else f"{message} {active_turn}"

    def _restart(self) -> None:
        self.controller.restart()
        self.selected_kind = "infantry"
        if self.controller.match_mode is MatchMode.LOCAL_TWO_PLAYER:
            self.status = "Local setup reset. Blue's turn."
        else:
            self.status = "Campaign reset. Try a new strategy."
        self.visual_events.clear()
        self.simulation_accumulator = 0.0

    def _go_to_menu(self) -> None:
        self.mode = "menu"
        self.selected_kind = None
        self.status = "Choose a campaign to begin."
        self.visual_events.clear()

    def _mouse_to_grid(
        self,
        mouse_position: tuple[int, int],
    ) -> Position | None:
        x, y = mouse_position
        if not (
            GRID_LEFT <= x < GRID_LEFT + GRID_WIDTH
            and GRID_TOP <= y < GRID_TOP + GRID_HEIGHT
        ):
            return None
        return Position(
            row=(y - GRID_TOP) // CELL_SIZE,
            column=(x - GRID_LEFT) // CELL_SIZE,
        )

    def _cell_center(self, position: Position) -> tuple[int, int]:
        return (
            GRID_LEFT + position.column * CELL_SIZE + CELL_SIZE // 2,
            GRID_TOP + position.row * CELL_SIZE + CELL_SIZE // 2,
        )

    def _result_text(self) -> str:
        state = self.controller.battle.state
        if state is BattleState.BLUE_WIN:
            return "BLUE VICTORY"
        if state is BattleState.RED_WIN:
            return "RED VICTORY"
        return "DRAW"

    def _draw_button(
        self,
        rect: pygame.Rect,
        label: str,
        color: tuple[int, int, int],
        *,
        dark_text: bool = False,
    ) -> None:
        pygame.draw.rect(self.screen, color, rect, border_radius=9)
        pygame.draw.rect(self.screen, (115, 129, 151), rect, width=1, border_radius=9)
        self._draw_text(
            label,
            self.fonts["small"],
            (20, 28, 38) if dark_text else TEXT,
            rect.center,
            center=True,
        )

    def _draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
        *,
        center: bool = False,
    ) -> None:
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = position
        else:
            rect.topleft = position
        self.screen.blit(surface, rect)

    def _draw_wrapped(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
    ) -> None:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= rect.width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        for index, line in enumerate(lines[:2]):
            self._draw_text(
                line,
                font,
                color,
                (rect.x, rect.y + index * (font.get_height() + 2)),
            )

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Dawn Tactics demo.")
    parser.add_argument(
        "--screenshot",
        type=Path,
        help="Save one rendered demo frame and exit.",
    )
    parser.add_argument(
        "--campaign",
        type=int,
        choices=(1, 2, 3),
        default=2,
        help="Campaign used by screenshot mode (default: 2).",
    )
    parser.add_argument(
        "--difficulty",
        choices=(Difficulty.NORMAL.value, Difficulty.HARD.value),
        default=Difficulty.HARD.value,
        help="Difficulty used by the game and screenshot mode (default: hard).",
    )
    parser.add_argument(
        "--simulate-ticks",
        type=int,
        default=0,
        help="Advance the prepared screenshot battle by N ticks.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    app = GameApp(Difficulty(args.difficulty))
    if args.screenshot:
        app._load_campaign(args.campaign - 1)
        app.prepare_demo_layout()
        if args.simulate_ticks > 0:
            app.controller.start_battle()
            app.status = "Battle started! Units now act automatically."
            for _ in range(args.simulate_ticks):
                events = app.controller.step()
                app._remember_visual_events(events)
                if app.controller.battle.state is not BattleState.RUNNING:
                    break
            if app.controller.battle.state is not BattleState.RUNNING:
                app.status = app._result_text()
        app.draw()
        args.screenshot.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(app.screen, args.screenshot)
        pygame.quit()
        return
    app.run()


if __name__ == "__main__":
    main()
