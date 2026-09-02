# Student Unit Class Design

**Date:** 2026-09-01

## Goal

Give the student one safe, real class file that changes a deployable unit in
Dawn Tactics. The class must visibly affect the game while the battle engine
and the existing six historical units remain stable.

## Chosen approach

Create `src/dawn_tactics/student_classes.py` with one student-editable class:
`StudentUnit`. It inherits the engine's protected `Unit` base class and is
registered as a seventh deployable unit with the fixed kind `student_unit`.

The student edits class-level game rules, not pygame or the battle loop:

- `display_name`
- `short_name`
- `cost`
- `max_hp`
- `base_damage`
- `attack_range`
- `attack_every`
- `move_every`
- `armor`
- `damage_against()`

The default class is a balanced, LIGHT-armored `Student Unit`. It uses ordinary
base damage so the student can begin by changing one value and later write a
small method that changes damage. There is only one new class; no additional
student subclasses, registries, or pygame code are introduced.

## Architecture and data flow

`domain.py` continues to own `Unit`, battle movement, targeting, damage
application, and the unit registry. After its stable built-in unit classes are
defined, it imports `StudentUnit` and adds it to `UNIT_REGISTRY` under the
fixed `student_unit` key. This import order avoids a circular dependency:
`student_classes.py` imports the already-defined `Unit` base class and does
not import the game UI.

The controller and pygame UI already read `UNIT_REGISTRY`, so the new unit
automatically gains a selection card, player deployment, enemy deployment,
combat, team colour, and existing fallback image rendering. It will use the
generic unit image fallback rather than requiring a new artwork asset.

`student_classes_validation.py` validates the student surface at game startup.
It checks that the class has the protected registration identity and that its
visible values are safe: short non-empty names, integer cost and combat values
within classroom-safe bounds, supported armor, and a whole-number damage result
in range. Validation errors explain the field and allowed range. The game calls
this validator beside the existing Lesson 01 settings and Lesson 02 rules
validators before opening a battle.

## Student file

The file begins with a Korean-led, English-code comment explaining that the
student edits only the marked class. `kind = "student_unit"` remains supplied
and marked as fixed, because game registration depends on it. The default
`damage_against(self, target)` returns `self.base_damage`; this is a small,
readable starting method and keeps ordinary attacks working.

The file is intentionally separate from `domain.py`: the student can freely
experiment with a meaningful class without accidentally changing all existing
units or the engine's `Unit` behavior.

## Tests

New focused tests will prove that:

1. `StudentUnit` is in `UNIT_REGISTRY` under `student_unit`.
2. The default class has the documented safe attributes and can take damage
   without changing another object.
3. `damage_against()` delegates to the student method and affects a real
   target in the same way built-in unit methods do.
4. The validator accepts defaults and rejects unsafe edited values with useful
   messages.
5. Game startup runs the student-class validator.
6. Existing domain, UI, lesson, and screenshot tests remain unchanged.

## Documentation boundary

README gains a Lesson 04 student class link and a short restart-and-observe
experiment. The existing Lesson 04 notebook keeps its from-scratch `Unit`
exercise; it does not reveal or duplicate the new game class solution. Lesson
05 can use `StudentUnit(Unit)` as the concrete inheritance bridge.

## Non-goals

- No edits to existing built-in unit balance.
- No student editing of `UNIT_REGISTRY`, terrain, controller logic, or pygame.
- No new image asset or external dependency.
- No automatic code rewriting or recovery of invalid Python syntax; Python's
  normal error is shown for syntax errors, while valid-but-unsafe values get
  the friendly validator message.
