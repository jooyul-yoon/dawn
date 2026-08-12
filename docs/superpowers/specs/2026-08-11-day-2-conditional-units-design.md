# Day 2 Conditional Units Design

## Goal

Add `Machine Gun` and `Cavalry` as player-only units in every Dawn Tactics
campaign, and give the student one small English-language file where changing
`if`, `elif`, and `else` visibly changes those units' damage rules.

The lesson must build directly on Day 1 variables without requiring the
student to understand classes, `self`, inheritance, or pygame. Existing enemy
forces, campaign budgets, deterministic battle behavior, and Day 1 baseline
results remain unchanged.

## Success Criteria

- All six units are selectable with the mouse and number keys `1` through `6`.
- A Machine Gun and Cavalry can be purchased together with Campaign 1's normal
  `$500` budget.
- The student edits only `src/dawn_tactics/student_rules.py` during the core
  exercise.
- The default Machine Gun rule demonstrates `if/else`.
- The default Cavalry rule demonstrates `if/elif/else`.
- Saving the rules file and restarting the game changes real battle damage.
- Missing branches and invalid return values produce a short error naming the
  rule and the input that failed.
- All existing campaign and Day 1 regression tests continue to pass.

## Student Learning Boundary

Day 2 teaches Boolean comparisons, branch selection, indentation, and the idea
that exactly one branch runs. Function syntax is treated as a supplied
container: `def` and `return` receive only the minimum explanation needed to
use the file. Functions as a general abstraction remain a Day 3 topic.

The student-facing code and game UI remain in English. Teacher explanations
and the primary notebook instructions remain in Korean, matching the existing
lesson structure.

## Student Rules File

Create `src/dawn_tactics/student_rules.py` with this default editable surface:

```python
"""Lesson 02 — Conditionals

Change the conditions and returned damage values, then restart the game.
Keep each possible target covered by an if, elif, or else branch.
"""


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

The file contains no pygame imports, class definitions, or engine internals.
Comments invite safe experiments such as swapping `LIGHT` for `HEAVY`, changing
a returned value, or changing which target kind enters the `elif` branch.

## New Unit Rules

| Unit | Cost | HP | Range | Attack interval | Move interval | Armor |
|---|---:|---:|---:|---:|---:|---|
| Machine Gun | 300 | 5 | 3 | 2 ticks | 1 tick | LIGHT |
| Cavalry | 200 | 6 | 1 | 1 tick | 1 tick | LIGHT |

Both classes keep `base_damage = 1` as safe metadata for the shared `Unit`
interface, but their actual attack damage always comes from the corresponding
student rule.

`MachineGun.damage_against(target)` passes `target.armor` to
`machine_gun_damage()`. Its default rule deals 4 damage to LIGHT armor and 1
damage to HEAVY armor.

`Cavalry.damage_against(target)` passes `target.kind` to `cavalry_damage()`.
Its default rule deals 5 damage to Artillery, 3 damage to Infantry, and 1
damage to every other unit kind.

The classes live beside the four existing subclasses in `domain.py` and are
registered under `machine_gun` and `cavalry`. Their short labels are `MG` and
`C`. They are added to every campaign's `allowed_units`, but no campaign uses
them as Red units or reinforcements.

## Architecture and Data Flow

The change keeps four responsibilities separate:

1. `student_rules.py` contains only student-editable conditional decisions.
2. `student_rules_validation.py` owns friendly validation and the
   `StudentRulesError` exception.
3. `domain.py` owns unit statistics and calls the student rules when damage is
   requested.
4. `game.py` owns keyboard mappings, cards, icons, and layout.

At application startup, `GameApp` validates Day 1 settings and then calls
`validate_student_rules()`. The validator evaluates Machine Gun with both
`LIGHT` and `HEAVY`, and evaluates Cavalry with all six supported target kinds:
`infantry`, `anti_tank`, `tank`, `artillery`, `machine_gun`, and `cavalry`.

During battle, the unit passes the target's armor or kind into the appropriate
student function. The returned value is checked again before becoming an
`AttackAction`, so pure-Python simulations receive the same friendly error even
when pygame is not running. No rule is permitted to inspect or mutate the
battle engine.

## Error Handling

A valid damage result is an exact `int` from `0` through `999`. Zero is allowed
so the student can intentionally make a unit unable to damage one category;
the existing maximum-tick rule still prevents an endless battle. Booleans,
floats, strings, negative numbers, values above 999, and `None` are rejected.

An uncovered branch produces a message in this form:

```text
CAVALRY_DAMAGE must return a whole-number damage from 0 to 999 for target_kind='tank'; got None.
```

Python syntax and indentation errors continue to point directly to the edited
line. The launchers already keep their terminal window open on failure, so the
student can read and repair the error before restarting.

## Game UI and Input

The selection panel changes from two rows of two cards to three compact rows of
two cards. Card order and keyboard order are:

1. Infantry
2. Anti-Tank
3. Tank
4. Artillery
5. Machine Gun
6. Cavalry

The setup instruction changes from `1–4 select` to `1–6 select`. Each compact
card retains unit name, cost, HP, and one rule line. The new cards use
`DMG BY ARMOR` and `DMG BY TYPE` instead of displaying a misleading single
base-damage number.

The Start, Restart, Campaigns, status, tick, and learning-note regions move
down or become slightly more compact without changing the 1280 by 760 window.
Rectangle helpers remain the single source of truth for drawing and click hit
testing.

Machine Gun receives a simple tripod-and-barrel geometric icon. Cavalry
receives a distinct chevron or horseshoe-inspired geometric icon. Both follow
the current abstract, non-graphic presentation. The separate four-unit image
asset design remains independent; illustrated assets for these two new units
are not required by this feature.

## Lesson Materials

Add the following artifacts using the same structure as Lesson 1:

- `lessons/lesson_02_conditionals.ipynb`: Korean-led, English-code student
  notebook.
- `lessons/lesson_02_conditionals_en.ipynb`: fully English student notebook.
- `lessons/lesson_02_curriculum_ko.md`: Korean 90-minute teacher guide.

`README.md` updates the controls to `1`–`6`, lists the two new units, and links
all Day 2 materials and the student rules file.

The notebook progression is:

1. Review variables and `True`/`False`.
2. Predict comparison results with `==`.
3. Run a small `if/else` armor example.
4. Add `elif` for three target kinds.
5. Read the real default functions from `student_rules.py`.
6. Predict, change one branch, restart, and observe the game.
7. Restore the exact default rules.

The core experiment changes only one condition or return value at a time. A
rule-preview cell calls both student functions with representative strings, so
the student can verify all branches before launching pygame.

## Testing and Verification

Automated domain tests cover:

- both new classes' fixed statistics and registry entries;
- Machine Gun default results for LIGHT and HEAVY armor;
- Cavalry default results for Artillery, Infantry, and an `else` target;
- validation of every supported armor and target-kind input;
- friendly rejection of `None`, strings, booleans, negative values, and values
  above 999;
- purchasing, placing, refunding, and restarting with the new units;
- availability of all six units in every campaign;
- unchanged Day 1 Tank-damage outcomes and existing Normal/Hard winning
  layouts; and
- unchanged click-order-independent event histories.

Presentation verification uses pygame's dummy video driver to render setup
screens containing six cards and both new battlefield icons. Rectangle checks
and visual inspection confirm that cards, buttons, status text, and the panel
footer do not overlap.

Notebook verification parses both files as JSON and confirms that their code
cells match while the surrounding instructional language differs. The final
verification run compiles `src`, executes the complete pytest suite, validates
both notebooks, checks the macOS launcher syntax, and saves a Day 2 screenshot.

## Compatibility and Non-Goals

The feature does not change campaign budgets, existing enemy deployments,
difficulty modifiers, target selection, movement, simultaneous damage, or
unit-ID generation. It does not add a new campaign, healing, repair, terrain,
animation, national factions, or online play.

It also does not teach general function design or OOP syntax during Day 2.
Those topics remain sequenced after conditionals so the new abstraction load
stays small.
