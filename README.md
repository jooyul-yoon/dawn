# Dawn Tactics

`Dawn Tactics` is a small deterministic strategy game for teaching Python OOP.
The player buys and deploys units, presses **Start Battle**, and watches both
teams follow the same automatic combat rules.

The demo contains:

- three budget-puzzle campaigns;
- selectable **Normal** and **Hard** modes;
- four Python subclasses: `Infantry`, `AntiTank`, `Tank`, and `Artillery`;
- purchase, deployment, full setup refund, restart, and next-mission flow;
- deterministic grid movement and simultaneous combat damage;
- abstract, non-graphic presentation made entirely with pygame shapes.

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

## Controls

- `1`–`4`: select a unit
- Left click: place the selected unit in the blue deployment zone
- Right click: remove a blue unit and receive a full refund during setup
- `Space`: start battle
- `R`: restart the current campaign
- `Esc`: return to campaign selection

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

## Teaching boundary

In Lesson 01 students edit `src/dawn_tactics/student_settings.py`. In later OOP
lessons they move into `src/dawn_tactics/domain.py`, where the `Unit` base class
and four subclasses expose state, methods, inheritance, and an overridden
anti-tank damage rule. Rendering and input live separately in `game.py`, so a
rule change can be tested without knowing pygame first.

## Save a preview image

```bash
python -m dawn_tactics --screenshot screenshots/demo.png --campaign 2 --difficulty hard --simulate-ticks 5
```
