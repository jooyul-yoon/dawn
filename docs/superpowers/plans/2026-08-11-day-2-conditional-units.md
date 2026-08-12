# Day 2 Conditional Units Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add player-only Machine Gun and Cavalry units whose damage decisions are safely editable through a Day 2 `student_rules.py` lesson on `if`, `elif`, and `else`.

**Architecture:** Keep student-authored conditional functions separate from fixed unit classes and pygame. A dedicated validator evaluates every supported branch at startup and wraps runtime results, while the presentation layer expands to six compact cards without changing existing enemy forces or deterministic combat rules.

**Tech Stack:** Python 3.12, pygame-ce 2.5.7, pytest, Jupyter Notebook JSON, Markdown

---

## File Map

- Create `src/dawn_tactics/student_rules.py`: Day 2 student edit surface.
- Create `src/dawn_tactics/student_rules_validation.py`: friendly branch-result validation.
- Modify `src/dawn_tactics/domain.py`: Machine Gun and Cavalry classes.
- Modify `src/dawn_tactics/campaigns.py`: player availability in all campaigns.
- Modify `src/dawn_tactics/__init__.py`: public exports.
- Modify `src/dawn_tactics/game.py`: startup validation, keys, six cards, and icons.
- Create `tests/test_student_rules.py`, `tests/test_game_ui.py`, and `tests/test_lesson_materials.py`.
- Modify `tests/test_domain.py` for domain and regression coverage.
- Create two Day 2 notebooks and the Korean teacher guide under `lessons/`.
- Modify `README.md` for controls and lesson links.

### Task 1: Student Rules and Friendly Validation

**Files:**
- Create: `tests/test_student_rules.py`
- Create: `src/dawn_tactics/student_rules.py`
- Create: `src/dawn_tactics/student_rules_validation.py`

- [ ] **Step 1: Write the first failing default-rule test**

Create `tests/test_student_rules.py`:

```python
from dawn_tactics import student_rules as rules


def test_default_student_rules_cover_if_elif_and_else_branches() -> None:
    assert rules.machine_gun_damage("LIGHT") == 4
    assert rules.machine_gun_damage("HEAVY") == 1
    assert rules.cavalry_damage("artillery") == 5
    assert rules.cavalry_damage("infantry") == 3
    assert rules.cavalry_damage("tank") == 1
```

- [ ] **Step 2: Verify RED for the missing student module**

Run:

```bash
.venv/bin/python -m pytest tests/test_student_rules.py -q
```

Expected: collection fails because `dawn_tactics.student_rules` does not exist.

- [ ] **Step 3: Add the minimal student edit surface**

Create `src/dawn_tactics/student_rules.py`:

```python
"""Lesson 02 — Conditionals

Change the conditions and returned damage values, then restart the game.
Keep each possible target covered by an if, elif, or else branch.
"""


def machine_gun_damage(target_armor):
    """Choose Machine Gun damage from the target's armor."""
    if target_armor == "LIGHT":
        return 4
    else:
        return 1


def cavalry_damage(target_kind):
    """Choose Cavalry damage from the target's unit kind."""
    if target_kind == "artillery":
        return 5
    elif target_kind == "infantry":
        return 3
    else:
        return 1
```

- [ ] **Step 4: Verify GREEN for the default branches**

Run:

```bash
.venv/bin/python -m pytest tests/test_student_rules.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Add failing validation tests**

Extend `tests/test_student_rules.py` to this complete form:

```python
import pytest

from dawn_tactics import student_rules as rules
from dawn_tactics.student_rules_validation import (
    StudentRulesError,
    cavalry_damage_for,
    machine_gun_damage_for,
    validate_student_rules,
)


def test_default_student_rules_cover_if_elif_and_else_branches() -> None:
    assert rules.machine_gun_damage("LIGHT") == 4
    assert rules.machine_gun_damage("HEAVY") == 1
    assert rules.cavalry_damage("artillery") == 5
    assert rules.cavalry_damage("infantry") == 3
    assert rules.cavalry_damage("tank") == 1


def test_default_student_rules_are_safe() -> None:
    validate_student_rules()


def test_startup_validation_evaluates_every_supported_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_armors: list[str] = []
    seen_kinds: list[str] = []
    monkeypatch.setattr(
        rules,
        "machine_gun_damage",
        lambda armor: seen_armors.append(armor) or 1,
    )
    monkeypatch.setattr(
        rules,
        "cavalry_damage",
        lambda kind: seen_kinds.append(kind) or 1,
    )

    validate_student_rules()

    assert seen_armors == ["LIGHT", "HEAVY"]
    assert seen_kinds == [
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    ]


@pytest.mark.parametrize("bad_result", (None, "4", True, -1, 1_000))
def test_machine_gun_rule_rejects_invalid_damage(
    monkeypatch: pytest.MonkeyPatch,
    bad_result: object,
) -> None:
    monkeypatch.setattr(
        rules,
        "machine_gun_damage",
        lambda target_armor: bad_result,
    )
    with pytest.raises(
        StudentRulesError,
        match=r"MACHINE_GUN_DAMAGE.*target_armor='LIGHT'",
    ):
        machine_gun_damage_for("LIGHT")


def test_missing_cavalry_else_has_a_helpful_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def incomplete_rule(target_kind):
        if target_kind == "artillery":
            return 5

    monkeypatch.setattr(rules, "cavalry_damage", incomplete_rule)
    with pytest.raises(
        StudentRulesError,
        match=r"CAVALRY_DAMAGE.*target_kind='tank'.*None",
    ):
        cavalry_damage_for("tank")


def test_zero_damage_is_a_valid_student_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rules, "cavalry_damage", lambda target_kind: 0)
    assert cavalry_damage_for("tank") == 0
```

- [ ] **Step 6: Verify RED for the missing validator**

Run:

```bash
.venv/bin/python -m pytest tests/test_student_rules.py -q
```

Expected: collection fails with `ModuleNotFoundError` for
`student_rules_validation`.

- [ ] **Step 7: Implement the validator**

Create `src/dawn_tactics/student_rules_validation.py`:

```python
from __future__ import annotations

from . import student_rules as rules


SUPPORTED_TARGET_ARMORS = ("LIGHT", "HEAVY")
SUPPORTED_TARGET_KINDS = (
    "infantry",
    "anti_tank",
    "tank",
    "artillery",
    "machine_gun",
    "cavalry",
)


class StudentRulesError(ValueError):
    """Raised when a Day 2 conditional rule returns unsafe damage."""


def _checked_damage(
    rule_name: str,
    input_name: str,
    input_value: str,
    result: object,
) -> int:
    if type(result) is not int or not 0 <= result <= 999:
        raise StudentRulesError(
            f"{rule_name} must return a whole-number damage from 0 to 999 "
            f"for {input_name}={input_value!r}; got {result!r}."
        )
    return result


def machine_gun_damage_for(target_armor: str) -> int:
    return _checked_damage(
        "MACHINE_GUN_DAMAGE",
        "target_armor",
        target_armor,
        rules.machine_gun_damage(target_armor),
    )


def cavalry_damage_for(target_kind: str) -> int:
    return _checked_damage(
        "CAVALRY_DAMAGE",
        "target_kind",
        target_kind,
        rules.cavalry_damage(target_kind),
    )


def validate_student_rules() -> None:
    for armor in SUPPORTED_TARGET_ARMORS:
        machine_gun_damage_for(armor)
    for kind in SUPPORTED_TARGET_KINDS:
        cavalry_damage_for(kind)
```

- [ ] **Step 8: Verify validation and the full suite**

Run:

```bash
.venv/bin/python -m pytest tests/test_student_rules.py -q
.venv/bin/python -m pytest -q
```

Expected: all rule tests and all pre-existing tests pass.

- [ ] **Step 9: Commit the rule boundary**

```bash
git add \
  src/dawn_tactics/student_rules.py \
  src/dawn_tactics/student_rules_validation.py \
  tests/test_student_rules.py
git commit -m "Add safe Day 2 conditional rules"
```

### Task 2: Domain Classes and Campaign Availability

**Files:**
- Modify: `tests/test_domain.py`
- Modify: `src/dawn_tactics/domain.py:6-8,199-217`
- Modify: `src/dawn_tactics/campaigns.py:30-35`
- Modify: `src/dawn_tactics/__init__.py:3-27`

- [ ] **Step 1: Add failing unit tests**

Import `student_rules as rules`, `Artillery`, `Cavalry`, `MachineGun`, and
`UNIT_REGISTRY` in `tests/test_domain.py`, then add:

```python
def test_machine_gun_and_cavalry_stats_and_registry() -> None:
    assert UNIT_REGISTRY["machine_gun"] is MachineGun
    assert (
        MachineGun.display_name,
        MachineGun.short_name,
        MachineGun.cost,
        MachineGun.max_hp,
        MachineGun.base_damage,
        MachineGun.attack_range,
        MachineGun.attack_every,
        MachineGun.move_every,
        MachineGun.armor,
    ) == ("Machine Gun", "MG", 300, 5, 1, 3, 2, 1, "LIGHT")

    assert UNIT_REGISTRY["cavalry"] is Cavalry
    assert (
        Cavalry.display_name,
        Cavalry.short_name,
        Cavalry.cost,
        Cavalry.max_hp,
        Cavalry.base_damage,
        Cavalry.attack_range,
        Cavalry.attack_every,
        Cavalry.move_every,
        Cavalry.armor,
    ) == ("Cavalry", "C", 200, 6, 1, 1, 1, 1, "LIGHT")


def test_new_units_delegate_damage_to_student_rules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    machine_gun = MachineGun(1, Team.BLUE, Position(2, 2))
    cavalry = Cavalry(2, Team.BLUE, Position(2, 3))
    tank = Tank(3, Team.RED, Position(1, 2))
    artillery = Artillery(4, Team.RED, Position(1, 3))
    monkeypatch.setattr(rules, "machine_gun_damage", lambda armor: 7)
    monkeypatch.setattr(rules, "cavalry_damage", lambda kind: 8)

    assert machine_gun.damage_against(tank) == 7
    assert cavalry.damage_against(artillery) == 8
```

- [ ] **Step 2: Verify RED for missing classes**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_domain.py::test_machine_gun_and_cavalry_stats_and_registry \
  tests/test_domain.py::test_new_units_delegate_damage_to_student_rules -q
```

Expected: collection fails because `MachineGun` and `Cavalry` do not exist.

- [ ] **Step 3: Implement and register both units**

Import the wrappers in `domain.py`:

```python
from .student_rules_validation import cavalry_damage_for, machine_gun_damage_for
```

Insert after `Artillery`:

```python
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
```

Extend the registry in this order:

```python
UNIT_REGISTRY: dict[str, type[Unit]] = {
    Infantry.kind: Infantry,
    AntiTank.kind: AntiTank,
    Tank.kind: Tank,
    Artillery.kind: Artillery,
    MachineGun.kind: MachineGun,
    Cavalry.kind: Cavalry,
}
```

In `src/dawn_tactics/__init__.py`, add both classes inside the existing
parenthesized domain import:

```python
    Cavalry,
    MachineGun,
```

Add these public names inside `__all__`:

```python
    "Cavalry",
    "MachineGun",
```

- [ ] **Step 4: Verify GREEN for the classes**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_domain.py::test_machine_gun_and_cavalry_stats_and_registry \
  tests/test_domain.py::test_new_units_delegate_damage_to_student_rules -q
```

Expected: both tests pass.

- [ ] **Step 5: Add failing availability and purchase tests**

Append to `tests/test_domain.py`:

```python
def test_all_campaigns_allow_six_player_unit_types() -> None:
    expected = (
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    )
    assert all(campaign.allowed_units == expected for campaign in CAMPAIGNS)


def test_campaign_one_can_buy_and_refund_both_day_two_units() -> None:
    controller = GameController(Difficulty.NORMAL)
    controller.load_campaign(0)
    assert controller.place_blue_unit("machine_gun", Position(7, 4)).ok
    assert controller.remaining_budget == 200
    assert controller.place_blue_unit("cavalry", Position(7, 6)).ok
    assert controller.remaining_budget == 0
    assert controller.remove_blue_unit(Position(7, 4)).ok
    assert controller.remaining_budget == 300
```

- [ ] **Step 6: Verify RED for campaign availability**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_domain.py::test_all_campaigns_allow_six_player_unit_types \
  tests/test_domain.py::test_campaign_one_can_buy_and_refund_both_day_two_units -q
```

Expected: failures because the campaign still permits four kinds.

- [ ] **Step 7: Extend `Campaign.allowed_units` only**

Use this tuple in `campaigns.py`:

```python
    allowed_units: tuple[str, ...] = (
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    )
```

Do not change budgets, Red units, Hard reinforcements, or campaign text.

- [ ] **Step 8: Run focused and full regression suites**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_domain.py::test_all_campaigns_allow_six_player_unit_types \
  tests/test_domain.py::test_campaign_one_can_buy_and_refund_both_day_two_units -q
.venv/bin/python -m pytest -q
```

Expected: new tests pass; Day 1 damage results, Normal/Hard winning layouts,
and click-order histories remain green.

- [ ] **Step 9: Commit the domain feature**

```bash
git add \
  src/dawn_tactics/domain.py \
  src/dawn_tactics/campaigns.py \
  src/dawn_tactics/__init__.py \
  tests/test_domain.py
git commit -m "Add Machine Gun and Cavalry units"
```

### Task 3: Startup Validation and Six-Card UI

**Files:**
- Create: `tests/test_game_ui.py`
- Modify: `src/dawn_tactics/game.py:21-66,91-105,385-416,444-553,596-617`

- [ ] **Step 1: Write failing dummy-SDL UI tests**

Create `tests/test_game_ui.py`:

```python
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from pathlib import Path

import pygame
import pytest

from dawn_tactics.campaigns import Difficulty
from dawn_tactics.domain import Position
from dawn_tactics.game import GameApp, unit_rule_text


@pytest.fixture
def app() -> GameApp:
    game = GameApp(Difficulty.NORMAL)
    yield game
    pygame.quit()


def test_game_startup_validates_student_rules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "dawn_tactics.game.validate_student_rules",
        lambda: calls.append("validated"),
    )
    game = GameApp(Difficulty.NORMAL)
    assert calls == ["validated"]
    pygame.quit()


def test_unit_cards_show_six_non_overlapping_choices(app: GameApp) -> None:
    rects = app._unit_card_rects()
    values = tuple(rects.values())
    assert tuple(rects) == (
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    )
    assert all(
        not first.colliderect(second)
        for index, first in enumerate(values)
        for second in values[index + 1 :]
    )
    assert all(not rect.colliderect(app._start_rect()) for rect in values)
    assert not app._start_rect().colliderect(app._restart_rect())
    assert not app._start_rect().colliderect(app._menu_rect())
    assert not app._restart_rect().colliderect(app._status_rect())
    assert not app._menu_rect().colliderect(app._status_rect())


def test_number_keys_five_and_six_select_new_units(app: GameApp) -> None:
    app._load_campaign(0)
    app._handle_key(pygame.K_5)
    assert app.selected_kind == "machine_gun"
    app._handle_key(pygame.K_6)
    assert app.selected_kind == "cavalry"


def test_special_rule_text_does_not_claim_one_fixed_damage() -> None:
    assert unit_rule_text("machine_gun") == "DMG BY ARMOR  RNG 3"
    assert unit_rule_text("cavalry") == "DMG BY TYPE  RNG 1"


def test_six_card_setup_screen_renders(tmp_path: Path, app: GameApp) -> None:
    app._load_campaign(0)
    assert app.controller.place_blue_unit("machine_gun", Position(7, 4)).ok
    assert app.controller.place_blue_unit("cavalry", Position(7, 6)).ok
    app.draw()
    output = tmp_path / "day-2-setup.png"
    pygame.image.save(app.screen, output)
    assert output.stat().st_size > 10_000
```

- [ ] **Step 2: Run UI tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_game_ui.py -q
```

Expected: collection fails because `unit_rule_text` is missing. After adding
that symbol, remaining assertions stay red until startup validation, keys, and
six-card rectangles are implemented.

- [ ] **Step 3: Add startup validation and shared unit metadata**

Import and call the validator in `game.py`:

```python
from .student_rules_validation import validate_student_rules
```

```python
        validate_student_settings()
        validate_student_rules()
```

Add near the UI constants:

```python
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
```

Replace the number-key mapping with:

```python
        number_keys = {
            pygame.K_1: "infantry",
            pygame.K_2: "anti_tank",
            pygame.K_3: "tank",
            pygame.K_4: "artillery",
            pygame.K_5: "machine_gun",
            pygame.K_6: "cavalry",
        }
```

- [ ] **Step 4: Implement compact rectangle helpers and text positions**

Use these helpers:

```python
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
        return pygame.Rect(PANEL_LEFT + 24, 400, PANEL_WIDTH - 48, 48)

    def _restart_rect(self) -> pygame.Rect:
        return pygame.Rect(PANEL_LEFT + 24, 456, 168, 40)

    def _menu_rect(self) -> pygame.Rect:
        return pygame.Rect(PANEL_LEFT + 208, 456, 168, 40)

    def _status_rect(self) -> pygame.Rect:
        return pygame.Rect(PANEL_LEFT + 24, 508, PANEL_WIDTH - 48, 52)
```

In `_draw_side_panel`:

- change the setup instruction to
  `1–6 select • Left-click place • Right-click refund`;
- place card name, stats, and rule text at `rect.y + 7`, `rect.y + 30`, and
  `rect.y + 53`;
- use `rule_text = unit_rule_text(kind)`;
- use `self._status_rect()` rather than an inline status rectangle;
- draw tick text at y `574`, `LEARN BY EDITING` at y `610`, and
  `Day 2 rules live in student_rules.py` at y `637`.

- [ ] **Step 5: Draw distinct geometric fallback icons**

Insert before the Artillery branch in `_draw_unit_shape`:

```python
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
```

Make the existing triangle an explicit `elif unit.kind == "artillery"` branch.
Add a final fallback `else` that draws a 20-pixel circle so unknown future
units do not look like Artillery:

```python
        else:
            pygame.draw.circle(self.screen, color, center, 20)
            pygame.draw.circle(self.screen, outline, center, 20, width=2)
```

- [ ] **Step 6: Verify UI and regressions**

Run:

```bash
.venv/bin/python -m pytest tests/test_game_ui.py -q
.venv/bin/python -m pytest -q
```

Expected: all dummy-SDL tests and the complete suite pass.

- [ ] **Step 7: Commit the interface**

```bash
git add src/dawn_tactics/game.py tests/test_game_ui.py
git commit -m "Add six-unit Day 2 interface"
```

### Task 4: Day 2 Lesson Artifacts

**Files:**
- Create: `tests/test_lesson_materials.py`
- Create: `lessons/lesson_02_conditionals.ipynb`
- Create: `lessons/lesson_02_conditionals_en.ipynb`
- Create: `lessons/lesson_02_curriculum_ko.md`

- [ ] **Step 1: Write failing artifact tests**

Create `tests/test_lesson_materials.py`:

```python
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KOREAN_NOTEBOOK = ROOT / "lessons" / "lesson_02_conditionals.ipynb"
ENGLISH_NOTEBOOK = ROOT / "lessons" / "lesson_02_conditionals_en.ipynb"
TEACHER_GUIDE = ROOT / "lessons" / "lesson_02_curriculum_ko.md"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _code_sources(notebook: dict[str, object]) -> list[list[str]]:
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return [cell["source"] for cell in cells if cell["cell_type"] == "code"]


def test_day_two_lesson_artifacts_exist_and_parse() -> None:
    assert _load(KOREAN_NOTEBOOK)["nbformat"] == 4
    assert _load(ENGLISH_NOTEBOOK)["nbformat"] == 4
    assert TEACHER_GUIDE.read_text(encoding="utf-8").startswith(
        "# Lesson 02 — Conditionals"
    )


def test_day_two_notebooks_share_identical_code_cells() -> None:
    assert _code_sources(_load(KOREAN_NOTEBOOK)) == _code_sources(
        _load(ENGLISH_NOTEBOOK)
    )


def test_day_two_materials_cover_rules_and_reset() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (KOREAN_NOTEBOOK, ENGLISH_NOTEBOOK, TEACHER_GUIDE)
    )
    for required in (
        "student_rules.py",
        "machine_gun_damage",
        "cavalry_damage",
        "if",
        "elif",
        "else",
        "Predict",
        "Restore",
    ):
        assert required in combined
```

- [ ] **Step 2: Verify RED for missing lesson files**

Run:

```bash
.venv/bin/python -m pytest tests/test_lesson_materials.py -q
```

Expected: failures with `FileNotFoundError` for the Day 2 artifacts.

- [ ] **Step 3: Create the Korean-led notebook**

Use `apply_patch` to create both notebooks as nbformat `4.5` JSON with the
Python 3.12 kernel metadata copied from Lesson 1. Use these cell IDs in order:

```text
title, goals, compare-intro, compare-code, if-else-intro, if-else-code,
elif-intro, elif-code, real-rules, preview-rules, experiment-cycle,
experiment-map, exit-ticket, defaults
```

The four code cells in both notebooks must be byte-for-byte equivalent to:

```python
target_armor = "LIGHT"

print("Is LIGHT armor?", target_armor == "LIGHT")
print("Is HEAVY armor?", target_armor == "HEAVY")
```

```python
target_armor = "LIGHT"

if target_armor == "LIGHT":
    damage = 4
else:
    damage = 1

print("Machine Gun damage:", damage)
```

```python
target_kind = "artillery"

if target_kind == "artillery":
    damage = 5
elif target_kind == "infantry":
    damage = 3
else:
    damage = 1

print("Cavalry damage:", damage)
```

```python
from dawn_tactics import student_rules as rules

print("Machine Gun vs LIGHT:", rules.machine_gun_damage("LIGHT"))
print("Machine Gun vs HEAVY:", rules.machine_gun_damage("HEAVY"))
print("Cavalry vs Artillery:", rules.cavalry_damage("artillery"))
print("Cavalry vs Infantry:", rules.cavalry_damage("infantry"))
print("Cavalry vs Tank:", rules.cavalry_damage("tank"))
```

Use these Korean-led markdown cells around the shared code:

```markdown
# Lesson 02 — Conditionals: 유닛이 상황을 판단하게 만들기

Today's mission: teach Machine Gun and Cavalry to choose damage with `if`, `elif`, and `else`.
```

```markdown
## Mission goals

1. Explain that a condition becomes `True` or `False`.
2. Predict which branch Python will run.
3. Use indentation to show which code belongs to a branch.
4. Change one real rule in `student_rules.py`, observe it, and Restore it.
```

```markdown
## 1. Comparison은 질문이다

`target_armor == "LIGHT"` asks a yes/no question. Predict both answers before running the next cell, then change `LIGHT` to `HEAVY`.
```

```markdown
## 2. `if` and `else`

Python checks `if` first. If it is false, Python runs `else`. Exactly one branch runs.
```

```markdown
## 3. Add another choice with `elif`

`elif` means “if the earlier condition was false, check this condition.” Try `artillery`, `infantry`, and `tank`.
```

```markdown
## 4. Read the real game rules

The game reads `src/dawn_tactics/student_rules.py`. The function shell is supplied; today edit only its conditions and returned damage values.
```

```markdown
## 5. Preview every branch

Every preview must return a whole-number damage from 0 to 999 before launching the game.
```

```markdown
## Scientist loop

1. **Predict:** Which branch will run?
2. **Change:** Edit one condition or one returned number.
3. **Preview:** Run all five previews.
4. **Observe:** Restart the game with the same deployment.
5. **Explain:** Connect the result to one branch.
6. **Reset:** Restore the default.
```

```markdown
## Game experiments

- Change Machine Gun's `LIGHT` condition to `HEAVY`.
- Or change Cavalry's Artillery damage from `5` to `1`.
- Or change the Cavalry `elif` target from `infantry` to `anti_tank`.

Use Normal Campaign 1 and change only one line per experiment.
```

```markdown
## Exit ticket

1. What does an `if` condition decide?
2. When does `else` run?
3. Why does branch order matter?
4. Which game rule changed, and what happened?
```

````markdown
## Restore these defaults after class

```python
def machine_gun_damage(target_armor):
    if target_armor == "LIGHT":
        return 4
    else:
        return 1


def cavalry_damage(target_kind):
    if target_kind == "artillery":
        return 5
    elif target_kind == "infantry":
        return 3
    else:
        return 1
```
````

- [ ] **Step 4: Create the English notebook**

Use these exact four code cells in the English notebook:

```python
target_armor = "LIGHT"

print("Is LIGHT armor?", target_armor == "LIGHT")
print("Is HEAVY armor?", target_armor == "HEAVY")
```

```python
target_armor = "LIGHT"

if target_armor == "LIGHT":
    damage = 4
else:
    damage = 1

print("Machine Gun damage:", damage)
```

```python
target_kind = "artillery"

if target_kind == "artillery":
    damage = 5
elif target_kind == "infantry":
    damage = 3
else:
    damage = 1

print("Cavalry damage:", damage)
```

```python
from dawn_tactics import student_rules as rules

print("Machine Gun vs LIGHT:", rules.machine_gun_damage("LIGHT"))
print("Machine Gun vs HEAVY:", rules.machine_gun_damage("HEAVY"))
print("Cavalry vs Artillery:", rules.cavalry_damage("artillery"))
print("Cavalry vs Infantry:", rules.cavalry_damage("infantry"))
print("Cavalry vs Tank:", rules.cavalry_damage("tank"))
```

Use these exact markdown cells:

```markdown
# Lesson 02 — Conditionals: Teaching Units to Decide

Today's mission: teach Machine Gun and Cavalry to choose damage with `if`, `elif`, and `else`.
```

```markdown
## Mission goals

1. Explain that a condition becomes `True` or `False`.
2. Predict which branch Python will run.
3. Use indentation to show which code belongs to a branch.
4. Change one real rule in `student_rules.py`, observe it, and Restore it.
```

```markdown
## 1. A comparison is a question

`target_armor == "LIGHT"` asks a yes/no question. Predict both answers before running the next cell, then change `LIGHT` to `HEAVY`.
```

```markdown
## 2. `if` and `else`

Python checks `if` first. If it is false, Python runs `else`. Exactly one branch runs.
```

```markdown
## 3. Add another choice with `elif`

`elif` means “if the earlier condition was false, check this condition.” Try `artillery`, `infantry`, and `tank`.
```

```markdown
## 4. Read the real game rules

The game reads `src/dawn_tactics/student_rules.py`. The function shell is supplied; today edit only its conditions and returned damage values.
```

```markdown
## 5. Preview every branch

Every preview must return a whole-number damage from 0 to 999 before launching the game.
```

```markdown
## Scientist loop

1. **Predict:** Which branch will run?
2. **Change:** Edit one condition or one returned number.
3. **Preview:** Run all five previews.
4. **Observe:** Restart the game with the same deployment.
5. **Explain:** Connect the result to one branch.
6. **Reset:** Restore the default.
```

```markdown
## Game experiments

- Change Machine Gun's `LIGHT` condition to `HEAVY`.
- Or change Cavalry's Artillery damage from `5` to `1`.
- Or change the Cavalry `elif` target from `infantry` to `anti_tank`.

Use Normal Campaign 1 and change only one line per experiment.
```

```markdown
## Exit ticket

1. What does an `if` condition decide?
2. When does `else` run?
3. Why does branch order matter?
4. Which game rule changed, and what happened?
```

````markdown
## Restore these defaults after class

```python
def machine_gun_damage(target_armor):
    if target_armor == "LIGHT":
        return 4
    else:
        return 1


def cavalry_damage(target_kind):
    if target_kind == "artillery":
        return 5
    elif target_kind == "infantry":
        return 3
    else:
        return 1
```
````

- [ ] **Step 5: Create the Korean 90-minute teacher guide**

Create `lessons/lesson_02_curriculum_ko.md` with this content:

````markdown
# Lesson 02 — Conditionals: 유닛이 상황을 판단하게 만들기

## 수업 개요

- 시간: 90분
- 설명 언어: 한국어
- 코드·UI·핵심 용어: 영어
- 학생 편집 파일: `src/dawn_tactics/student_rules.py`
- 중심 문장: A condition is a question that becomes `True` or `False`.

Day 2는 `if`, `elif`, `else`에 집중한다. `def`와 `return`은 준비된 규칙
상자의 입구와 출구로만 설명하고 function 수업은 Day 3로 미룬다.

## 학습 목표

1. 비교식 결과를 `True` 또는 `False`로 예측한다.
2. 주어진 입력에서 실행될 branch를 가리킨다.
3. indentation이 branch 범위를 나타낸다고 설명한다.
4. `if/else`와 `if/elif/else`를 구분한다.
5. 한 조건 또는 return value만 바꾸고 게임 결과와 연결한다.
6. 실험 뒤 기본 규칙을 Restore한다.

## 수업 전 준비

1. 게임과 두 notebook을 실행한다.
2. `student_rules.py`가 기본값인지 확인한다.
3. Normal Campaign 1에서 Machine Gun과 Cavalry를 함께 구매한다.
4. preview 결과가 `4, 1, 5, 3, 1`인지 확인한다.
5. `python -m pytest`가 통과하는지 확인한다.

## 90분 진행안

### 0–10분 — Day 1 variable 복습
`target_armor`, `target_kind`, `damage`에서 name과 value를 찾는다.

### 10–25분 — 비교식은 yes/no 질문
`target_armor == "LIGHT"`의 결과를 실행 전에 예상한다. `=`는 저장,
`==`는 질문이라는 차이를 확인한다.

### 25–40분 — if와 else
LIGHT와 HEAVY 카드를 Machine Gun의 두 갈래 규칙에 넣고 실행 branch를
학생이 손으로 가리킨 뒤 코드를 실행한다.

### 40–52분 — elif로 세 번째 선택
Artillery, Infantry, Tank 카드를 Cavalry 규칙에 차례로 넣는다. Python이
위에서 아래로 확인하고 첫 번째 참인 branch 뒤에는 멈춤을 관찰한다.

### 52–60분 — 실제 규칙 읽기
`student_rules.py`를 열고 function 구조는 제공된 것이라고 설명한다.

### 60–75분 — 통제된 게임 실험
Normal Campaign 1에서 두 유닛 위치를 고정한다. 기본 전투를 기록한 뒤
Machine Gun의 `LIGHT`를 `HEAVY`로 한 줄만 바꾸고 같은 배치를 비교한다.

### 75–83분 — 학생 선택 실험
- Cavalry의 Artillery damage를 5에서 1로 변경
- Cavalry의 `elif` target을 Infantry에서 Anti-Tank로 변경
- Machine Gun의 HEAVY damage를 1에서 0으로 변경

### 83–88분 — Exit ticket
`if`가 묻는 질문, `else`가 실행되는 때, branch order가 중요한 이유,
바꾼 규칙과 관찰 결과를 답한다.

### 88–90분 — 기본값 복구
두 함수를 기본값과 대조하고 preview `4, 1, 5, 3, 1`을 확인한다.

## 문제 해결표

| 증상 | 먼저 확인할 것 |
|---|---|
| `SyntaxError` | 조건 끝의 `:` 또는 따옴표 |
| `IndentationError` | branch 안의 네 칸 들여쓰기 |
| `StudentRulesError`와 `None` | 모든 입력을 처리하는 `else` |
| 게임 결과가 그대로 | 저장 후 게임을 완전히 재시작했는가? |
| 원인을 설명하기 어려움 | 한 번에 두 줄 이상 바꾸지 않았는가? |

## 기본 규칙

```python
def machine_gun_damage(target_armor):
    if target_armor == "LIGHT":
        return 4
    else:
        return 1


def cavalry_damage(target_kind):
    if target_kind == "artillery":
        return 5
    elif target_kind == "infantry":
        return 3
    else:
        return 1
```

## 다음 수업 연결

Day 3에서는 오늘 사용한 규칙 상자를 통해 `function`, parameter,
argument, return을 정식으로 배운다.
````

- [ ] **Step 6: Verify lesson files**

Run:

```bash
.venv/bin/python -m pytest tests/test_lesson_materials.py -q
jq empty lessons/lesson_02_conditionals.ipynb lessons/lesson_02_conditionals_en.ipynb
```

Expected: all artifact tests pass and `jq` exits silently.

- [ ] **Step 7: Commit lesson materials**

```bash
git add \
  lessons/lesson_02_conditionals.ipynb \
  lessons/lesson_02_conditionals_en.ipynb \
  lessons/lesson_02_curriculum_ko.md \
  tests/test_lesson_materials.py
git commit -m "Add Day 2 conditionals lesson materials"
```

### Task 5: README and Final Verification

**Files:**
- Modify: `tests/test_lesson_materials.py`
- Modify: `README.md:7-14,70-77,88-111`

- [ ] **Step 1: Add a failing README test**

Append to `tests/test_lesson_materials.py`:

```python
def test_readme_links_day_two_student_materials() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "`1`–`6`" in readme
    assert "Machine Gun" in readme
    assert "Cavalry" in readme
    assert "lessons/lesson_02_conditionals.ipynb" in readme
    assert "lessons/lesson_02_conditionals_en.ipynb" in readme
    assert "lessons/lesson_02_curriculum_ko.md" in readme
    assert "src/dawn_tactics/student_rules.py" in readme
```

- [ ] **Step 2: Verify RED for stale documentation**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_lesson_materials.py::test_readme_links_day_two_student_materials -q
```

Expected: failure because README still documents four units and Lesson 1 only.

- [ ] **Step 3: Update README with exact Day 2 content**

Replace the four-subclass feature bullet with:

```markdown
- six Python subclasses: `Infantry`, `AntiTank`, `Tank`, `Artillery`,
  `MachineGun`, and `Cavalry`;
```

Change the control to:

```markdown
- `1`–`6`: select a unit
```

Insert after the Lesson 1 section:

```markdown
## Lesson 02: Conditionals

Lesson 02 adds Machine Gun and Cavalry. Their damage decisions live in a small
student file so `if`, `elif`, and `else` visibly change real battles.

- Korean/bilingual student notebook: `lessons/lesson_02_conditionals.ipynb`
- English student notebook: `lessons/lesson_02_conditionals_en.ipynb`
- Korean teacher guide: `lessons/lesson_02_curriculum_ko.md`
- Safe conditional rules: `src/dawn_tactics/student_rules.py`

Use Normal Campaign 1 for the core experiment. Machine Gun costs $300 and
Cavalry costs $200, so both fit the original $500 budget. Restore the default
rules printed at the end of the notebook after class.
```

Replace the Teaching Boundary paragraph with:

```markdown
In Lesson 01 students edit `student_settings.py`; in Lesson 02 they edit
`student_rules.py`. Both files keep early lessons away from pygame and class
internals. Later OOP lessons move into `domain.py`, where the `Unit` base class
and six subclasses expose state, methods, inheritance, and overridden damage
rules.
```

- [ ] **Step 4: Verify README and full tests**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_lesson_materials.py::test_readme_links_day_two_student_materials -q
.venv/bin/python -m pytest -q
```

Expected: focused and complete suites pass.

- [ ] **Step 5: Render a deterministic Day 2 screenshot**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python - <<'PY'
from pathlib import Path

import pygame

from dawn_tactics.campaigns import Difficulty
from dawn_tactics.domain import Position
from dawn_tactics.game import GameApp

output = Path("screenshots/day-2-conditional-units.png")
output.parent.mkdir(parents=True, exist_ok=True)
app = GameApp(Difficulty.NORMAL)
app._load_campaign(0)
assert app.controller.place_blue_unit("machine_gun", Position(7, 4)).ok
assert app.controller.place_blue_unit("cavalry", Position(7, 6)).ok
app.draw()
pygame.image.save(app.screen, output)
pygame.quit()
print(output)
PY
```

Expected: the command prints `screenshots/day-2-conditional-units.png`.
Inspect it for six readable cards, distinct new icons, and no overlap among
cards, buttons, status, tick, and footer text.

- [ ] **Step 6: Run final verification**

Run each command separately:

```bash
.venv/bin/python -m compileall -q src
.venv/bin/python -m pytest -q
jq empty lessons/lesson_01_variables.ipynb lessons/lesson_01_variables_en.ipynb
jq empty lessons/lesson_02_conditionals.ipynb lessons/lesson_02_conditionals_en.ipynb
bash -n RUN_GAME_MAC.command
git diff --check
git status --short
```

Expected: compilation and JSON checks are silent, pytest is green, shell syntax
is valid, whitespace checking is silent, and status lists only the intended
Task 5 README and test changes before commit.

- [ ] **Step 7: Commit documentation**

```bash
git add README.md tests/test_lesson_materials.py
git commit -m "Document Day 2 conditional units"
```

- [ ] **Step 8: Confirm a clean branch**

Run:

```bash
git status --short --branch
git log --oneline --decorate -10
```

Expected: no uncommitted files and one focused implementation commit per task
after the approved design and plan commits.
