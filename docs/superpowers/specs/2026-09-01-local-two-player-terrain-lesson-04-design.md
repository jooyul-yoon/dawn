# Local Two-Player, Terrain, and Lesson 04 Design

## Goal

Add a same-screen local two-player mode to Dawn Tactics. Blue and Red each
start with $2,000 and alternate placing exactly one unit after each successful
deployment. The new map introduces sea and building terrain while preserving
all existing campaign rules and verified campaign layouts.

Create a 90-minute Lesson 04 that teaches Python classes and objects after the
existing Variables -> Conditionals -> Functions sequence. The lesson gives Dawn
ownership of a complete simplified `Unit` class without teaching inheritance
yet.

The user's saved work in `lessons/lesson_03_functions.ipynb` is out of scope and
must not be normalized, reset, staged, or overwritten.

## Chosen Approach

Use a dedicated local-match mode and a pure-Python terrain model.

This keeps three concerns separate:

- campaigns continue to load fixed Red forces and use one Blue budget;
- local two-player setup owns two budgets and the deployment turn;
- `Battle` owns terrain collision and pathfinding but no pygame code.

Alternatives rejected:

1. Treating local play as a fourth campaign would leak the existing Blue-only
   controller assumptions into Red deployment and make two budgets awkward.
2. Rebuilding campaigns and local play around a new universal scenario system
   would provide a cleaner long-term abstraction, but it is too broad for this
   feature and risks changing verified campaign outcomes.

## Local Two-Player Rules

### Match setup

- The main menu has a distinct `LOCAL 2 PLAYER` entry below the three
  campaigns.
- Difficulty applies only to campaigns and has no effect on local play.
- The battlefield remains 14 columns by 12 rows.
- Red deploys in rows 0 through 4.
- Rows 5 and 6 remain neutral.
- Blue deploys in rows 7 through 11.
- Both teams may buy all six existing unit types.
- Blue takes the first deployment turn.
- Each team starts with exactly $2,000 available. The budget is a spending
  limit, not a requirement to spend every dollar.

### Turn behavior

- Selecting a unit card does not end the turn.
- A successful placement deducts that unit's cost from the active team's
  budget, then changes the active team.
- An invalid placement changes neither budget nor turn.
- The active player may right-click one of their own units to refund it. A
  refund does not change the active team.
- A player cannot refund the other team's unit.
- `PASS TURN` changes the active team without spending money.
- `START BATTLE` becomes valid after both teams have at least one unit.
- Starting the battle keeps the existing automatic deterministic combat loop.
- Restart restores the local map, both $2,000 budgets, an empty battlefield,
  and Blue's first turn.

### Status and error messages

Every setup action returns an `ActionResult`. Messages identify the active
team and explain the first correction the player can make. Required failures
include wrong deployment zone, neutral zone, occupied cell, terrain cell,
unknown unit, insufficient active-team budget, wrong-team refund, and trying
to start without both teams.

## Terrain Model and Rules

### Pure-Python model

Add a small `Terrain` class beside `Position` in the domain layer. A terrain
object stores:

- `kind`: `"sea"` or `"building"`;
- `position`: one battlefield `Position`;
- `blocks_movement`;
- `blocks_deployment`.

Both initial kinds block movement and deployment. This lesson deliberately
does not add cover, destructible buildings, boats, bridges as objects, terrain
damage modifiers, or line-of-sight rules.

`Battle` receives an optional terrain collection. It validates that terrain is
inside the map and does not contain duplicate positions. Unit deployment and
movement reject blocked positions. Breadth-first pathfinding routes around
terrain and remains deterministic. Campaign battles use an empty terrain
collection, so their combat histories and verified layouts remain unchanged.

Ranged attacks still use Manhattan distance and may fire across terrain. This
simple rule is shown in the local-mode legend so the visuals do not imply a
line-of-sight system that does not exist.

### Symmetric local map

The local map is 180-degree rotationally symmetric.

Sea occupies neutral rows 5 and 6 in every column except the four open
crossings at columns 2, 6, 7, and 11. This creates a two-cell-deep water line
with four passable crossings.

Buildings occupy:

- Red side: `(3, 4)` and `(3, 9)`;
- Blue side: `(8, 4)` and `(8, 9)`.

This leaves ample deployment space for the maximum force affordable with
$2,000 and gives both teams the same obstacle pattern.

### Rendering and assets

Add two square RGBA terrain tiles:

- `src/dawn_tactics/assets/terrain/sea.png`;
- `src/dawn_tactics/assets/terrain/building.png`.

They use a readable top-down early-20th-century tactical-map style and scale
cleanly into a 56-pixel cell. The grid draws terrain before units and grid
lines. If an image is missing or invalid, pygame draws a clear procedural
fallback rather than failing startup. Package data includes the terrain asset
directory.

Terrain remains visible beneath territory highlighting. Blocked cells receive
a small border/icon treatment, and the panel legend says:

```text
SEA / BUILDING: BLOCKS MOVE + DEPLOY
RANGED FIRE: NOT BLOCKED
```

## Controller Architecture

Add a match-mode value that distinguishes `CAMPAIGN` from
`LOCAL_TWO_PLAYER`. Preserve the existing campaign APIs as compatibility
entry points.

The controller gains local-match state and team-neutral operations:

- a budget for each team;
- the active deployment team;
- `load_local_two_player()`;
- `place_current_unit()`;
- `remove_current_unit()`;
- `pass_turn()`;
- `budget_for(team)` and `active_budget` queries.

`place_blue_unit()` and `remove_blue_unit()` retain their existing campaign
behavior and test contract. Campaign Red IDs stay unchanged. Local unit IDs are
derived from team and deployment position, so identical final layouts do not
depend on click order. The existing deterministic movement-reservation rule is
retained; this feature adds no randomness.

## UI Flow

### Menu

The three campaign cards remain unchanged. A fourth wide card opens local play
and states `$2,000 EACH • ALTERNATE ONE UNIT AT A TIME`.

### Local setup screen

- Header: `LOCAL 2 PLAYER`.
- Objective: `Build both forces, then start the automatic battle.`
- Territory labels: `RED DEPLOYMENT ZONE` and `BLUE DEPLOYMENT ZONE`.
- Panel header uses the active team's color and says `BLUE TURN` or `RED TURN`.
- Both remaining budgets stay visible at all times.
- Unit-card affordability is calculated from the active team's budget.
- The action row contains `START BATTLE` and `PASS TURN`.
- Restart and Menu remain available.
- Hover highlighting uses the active team's color and does not hide terrain.

After combat, the result overlay uses the existing Blue victory, Red victory,
or draw result. Local play has no Next Campaign button.

## Lesson 04: Classes and Objects

### Audience and style

- One 90-minute Korean-led lesson for a bilingual elementary learner.
- Code, identifiers, UI labels, and core vocabulary remain English.
- Every experiment follows `Predict -> Run -> Explain -> Change`.
- The teacher asks questions and uses hints instead of taking the keyboard.
- Combat stays abstract and non-graphic.

The saved Lesson 03 notebook shows that return, composition, and the final
function may not yet have been completed. Lesson 04 therefore begins with a
short function prerequisite check and supplies a recovery explanation without
turning the session back into a full Functions lesson.

### Learning outcomes

By the end of the lesson, Dawn can:

1. explain that a class is a blueprint and an object is one instance made from
   it;
2. create an object by calling a class;
3. explain that `__init__` sets up a new object;
4. trace `self` to the object receiving a method call;
5. read and change instance attributes with dot notation;
6. explain that different objects keep independent state;
7. call a method and observe the object's state change;
8. write a complete simplified `Unit` class from its `class` line and pass the
   supplied self-checks.

### Artifacts

Create:

- `lessons/lesson_04_classes.ipynb`;
- `lessons/lesson_04_classes_en.ipynb`;
- `lessons/lesson_04_curriculum_ko.md`;
- `tests/test_lesson_04_materials.py`.

Update `README.md` with links, run instructions, and the Lesson 04/Lesson 05
boundary. Korean and English notebooks have identical cell IDs, code cells,
tags, and technical metadata. Only Markdown explanations differ. Master
notebooks contain no saved execution counts or outputs.

### 90-minute path

1. **0-8 minutes:** identify definition, call, parameter, argument, and return
   in one prepared function.
2. **8-20 minutes:** class blueprint versus two physical object cards.
3. **20-34 minutes:** prepared `MissionCard`, `__init__`, `self`, and one
   attribute.
4. **34-46 minutes:** create two objects and prove that changing one attribute
   does not change the other.
5. **46-51 minutes:** movement break with one blueprint and two unit tokens.
6. **51-63 minutes:** add and call a method; connect method to Lesson 03's
   function idea.
7. **63-69 minutes:** prepared bridge to two real Dawn Tactics `Tank` objects;
   damage one and observe independent HP.
8. **69-84 minutes:** independent `Unit` class challenge.
9. **84-88 minutes:** run exact self-checks and explain state changes.
10. **88-90 minutes:** exit ticket and one-sentence inheritance preview.

### Final student-owned task

The `student-task` cell contains prompts only:

```python
# Write class Unit from its class line.
# Inputs after self: name, max_hp
# Store name, max_hp, and hp. hp starts equal to max_hp.
# take_damage(amount) subtracts damage and never lets hp go below 0.
```

The student writes the class line, `__init__`, three instance attributes, and
the `take_damage()` method. The teacher-only reference is:

```python
class Unit:
    def __init__(self, name, max_hp):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp

    def take_damage(self, amount):
        self.hp = self.hp - amount
        if self.hp < 0:
            self.hp = 0
```

The tagged self-check creates `Tank` and `Infantry` objects, confirms their
starting attributes, damages only the Tank, confirms the Infantry did not
change, applies excessive damage, and confirms HP stops at zero.

### Lesson boundary

Do not teach or require inheritance, subclasses, `super()`, overriding,
polymorphism, class attributes, `ClassVar`, registries, decorators,
`@property`, dataclasses, Enums, type hints, object identity, pygame, or battle
loop internals. Lesson 05 will connect the shared `Unit` design to specialized
unit subclasses.

## Testing and Verification

### Domain and controller

- local reset creates an empty 14x12 battle, two $2,000 budgets, Blue turn,
  and the exact symmetric terrain map;
- successful placement deducts only the active team's budget and changes turn;
- every failed placement preserves both budgets and the active turn;
- Red and Blue zone boundaries are symmetric;
- terrain rejects deployment and movement;
- deterministic pathfinding reaches an open crossing and never enters terrain;
- refunds affect only the owning team's budget and do not change turn;
- pass changes turn without changing either budget;
- battle start requires at least one living unit from each team;
- restart restores the full local setup;
- equivalent local layouts receive stable position-derived IDs.

### UI and assets

- local menu card does not overlap campaign cards or footer;
- active-team label, two budgets, Pass, and Start fit the panel;
- unit clicks route through the current team;
- local territory labels replace campaign labels;
- sea and building assets exist, load with alpha, and scale to a cell;
- procedural fallbacks render when assets are missing;
- a headless local-setup screenshot has visible units and terrain;
- local results offer no Next button;
- existing campaign menu, six cards, campaign screenshots, and geometry remain
  intact.

### Lesson materials

- both notebooks parse and share the exact cell/code/tag contract;
- completed examples execute in order;
- the real Tank bridge changes only one object's HP;
- the prompt-only task contains no solution fragments;
- exact self-check assertions and tags are present;
- master notebooks have no outputs or execution counts;
- prohibited inheritance and advanced syntax do not appear in notebook code;
- the teacher guide includes timing, hint ladder, error routine, reference
  solution, reset checklist, and explicit inheritance deferral;
- README links every Lesson 04 artifact.

### Final verification

Run the Lesson 04 material tests, domain/controller/UI/asset tests, the full
test suite from a clean feature worktree, compile all Python files, run
`git diff --check`, and render a local-mode screenshot with dummy SDL drivers.

The user's working copy of `lesson_03_functions.ipynb` intentionally differs
from the committed master and can make the bilingual parity regression fail in
the main checkout. Verification must therefore be performed against the clean
feature commit, while the final handoff separately reports that the student's
working notebook remains preserved and uncommitted.
