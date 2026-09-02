# Dawn Tactics

`Dawn Tactics` is a small deterministic strategy game for teaching Python OOP.
The player buys and deploys units, presses **Start Battle**, and watches both
teams follow the same automatic combat rules.

The demo contains:

- three budget-puzzle campaigns;
- selectable **Normal** and **Hard** modes;
- six Python subclasses: `Infantry`, `AntiTank`, `Tank`, `Artillery`,
  `MachineGun`, and `Cavalry`;
- purchase, deployment, full setup refund, restart, and next-mission flow;
- deterministic grid movement and simultaneous combat damage;
- abstract, non-graphic presentation with illustrated unit miniatures and pygame effects.

## Double-click launchers

- Windows: double-click `RUN_GAME_WINDOWS.bat`.
- macOS: double-click `RUN_GAME_MAC.command`.

On the first launch, the script creates a private Python environment and
installs the game. Internet access may be needed once. Later launches start the
game directly, and neither script requires manual environment activation.

If macOS reports that the command file is not executable, run this once in the
project folder:

```bash
chmod +x RUN_GAME_MAC.command
```

## macOS setup

```bash
/usr/local/bin/python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m dawn_tactics
```

## Windows setup

Install Python 3.12 and VS Code's Python extension, then open PowerShell in the
project folder:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m dawn_tactics
```

If PowerShell blocks activation, activation is optional. Run commands directly
with `.venv\Scripts\python.exe` instead.

## Difficulty

The game opens with **Hard** selected. Hard mode lowers each mission's budget
and adds a visible enemy reinforcement; it does not secretly increase unit
damage or HP. Choose **Normal** on the campaign screen for Lesson 01 so the
notebook's baseline battle results stay reproducible.

For a specific mode from the command line:

```bash
python -m dawn_tactics --difficulty normal
python -m dawn_tactics --difficulty hard
```

## Local 2 Player

Choose **LOCAL 2 PLAYER** from the menu for one-screen play. Blue goes first.
Each side receives $2,000 as a spending cap, and every successful placement
hands the turn to the other side; an invalid action spends nothing and keeps the
turn. Press `P` (or click **PASS**) to give up the current setup turn.

Right-click refunds one of the active team's units during setup without changing
the turn. Both Blue and Red need at least one unit before **Start Battle** (or
`Space`) can begin the automatic battle. Sea and building tiles block movement
and deployment, but do not block ranged fire. Press `R` to reset the local
match or `Esc` to return to the menu.

Save a deterministic local setup preview without opening a window:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m dawn_tactics --local-two-player --screenshot screenshots/local-two-player-setup.png
```

## Controls

- `1`–`6`: select a unit
- Left click: deploy for Blue in a campaign, or for the active team in Local
- Right click: refund a Blue campaign unit, or the active team's Local unit
- `Space`: start battle
- `R`: restart the current campaign or Local match
- `Esc`: return to the main menu

## Run tests

```bash
python -m pytest
```

The tests do not open a pygame window because all game rules live in the pure
Python domain model.

## Lesson 01: Variables

Install the notebook kernel and open the first lesson in VS Code:

```bash
python -m pip install -e ".[dev,lesson]"
```

- Korean/bilingual student notebook: `lessons/lesson_01_variables.ipynb`
- English student notebook: `lessons/lesson_01_variables_en.ipynb`
- Korean teacher guide: `lessons/lesson_01_curriculum_ko.md`
- Safe game variables: `src/dawn_tactics/student_settings.py`

Lesson 01 uses **Normal** mode, changes settings one at a time, restarts the
game, and compares a prediction with the visible result. Restore the defaults
printed at the end of the notebook after class.

## Lesson 02: Conditionals

Lesson 02 adds Machine Gun and Cavalry. Their damage decisions live in a small
student file so `if`, `elif`, and `else` visibly change real battles.

- [Korean/bilingual student notebook](lessons/lesson_02_conditionals.ipynb)
- [English student notebook](lessons/lesson_02_conditionals_en.ipynb)
- [Korean teacher guide](lessons/lesson_02_curriculum_ko.md)
- [Safe conditional rules](src/dawn_tactics/student_rules.py)

Use Normal Campaign 1 for the core experiment. Machine Gun costs $300 and
Cavalry costs $200, so both fit the original $500 budget. Restore the default
rules printed at the end of the notebook after class.

## Lesson 03: Functions

Lesson 03 is a notebook-only mission-planning lesson. Dawn defines and calls
small functions, supplies parameters and arguments, compares `print` with a
return value, uses a local variable, connects function outputs and inputs, and
writes `deployment_report()` from its `def` line.

- [Korean/bilingual student notebook](lessons/lesson_03_functions.ipynb)
- [English student notebook](lessons/lesson_03_functions_en.ipynb)
- [Korean teacher guide](lessons/lesson_03_curriculum_ko.md)

The core vocabulary is definition, function call, parameter, argument, return
value, and local variable. This lesson does not edit or rebalance the game.

## Lesson 04: Classes and Objects

Lesson 04 turns the function ideas into a small blueprint. Students make a
`MissionCard` class, create separate objects with independent state, read
`self` and `__init__`, then implement a compact `Unit` class with a
`take_damage()` method.

- [Korean/bilingual student notebook](lessons/lesson_04_classes.ipynb)
- [English student notebook](lessons/lesson_04_classes_en.ipynb)
- [Korean teacher guide](lessons/lesson_04_curriculum_ko.md)

The final task stays in the notebook and leaves its implementation to the
student. Lesson 05 will introduce inheritance after class, object, attribute,
method, and independent state are secure.

## Teaching boundary

In Lesson 01 students edit `student_settings.py`; in Lesson 02 they edit
`student_rules.py`. Lesson 03 stays in notebooks while students create
functions from scratch without changing the game. Later OOP lessons move into
`domain.py`, where the `Unit` base class and six subclasses expose state,
methods, inheritance, and overridden damage rules.

## Unit image assets

Battlefield and selection-card images live in
`src/dawn_tactics/assets/units/`. The same neutral PNG is reused for both teams;
pygame's Blue and Red team plates identify ownership. If an asset is missing or
invalid, the game falls back to its original geometric unit symbol.

## Save a preview image

```bash
python -m dawn_tactics --screenshot screenshots/demo.png --campaign 2 --difficulty hard --simulate-ticks 5
```
