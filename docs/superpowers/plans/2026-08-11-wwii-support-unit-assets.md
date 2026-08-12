# WWII Support Unit Assets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate historically appropriate early-WWII Machine Gun and Cavalry miniatures and add them to Dawn Tactics' existing six-unit image pipeline.

**Architecture:** Create two neutral, transparent PNGs that match the current four-asset tabletop miniature set. Extend the presentation-layer asset registry only; the existing startup loader, two-size caches, team plates, card renderer, shape fallback, and setuptools PNG glob will handle both units without domain or combat changes.

**Tech Stack:** Python 3.12, pygame-ce 2.5.7, pytest, setuptools package data, built-in ImageGen, Pillow-based chroma-key removal

---

## File Map

- Create `src/dawn_tactics/assets/units/machine_gun.png`: transparent early-WWII heavy machine gun miniature.
- Create `src/dawn_tactics/assets/units/cavalry.png`: transparent mounted reconnaissance miniature.
- Modify `src/dawn_tactics/game.py:35-41`: register the two filenames.
- Modify `tests/test_game_assets.py:8-57`: require six registered, loadable alpha assets.
- Create for inspection only `screenshots/wwii-support-units-final.png`: setup screen containing both new battlefield images and all six cards.

### Task 1: Generate and validate the two transparent assets

**Files:**
- Create: `src/dawn_tactics/assets/units/machine_gun.png`
- Create: `src/dawn_tactics/assets/units/cavalry.png`

- [ ] **Step 1: Create project-local source directories**

Run:

```bash
mkdir -p tmp/imagegen/wwii-support-sources src/dawn_tactics/assets/units
```

Expected: both directories exist; no tracked source file is modified.

- [ ] **Step 2: Generate the Machine Gun chroma source with built-in ImageGen**

Use one built-in ImageGen call with this exact prompt:

Immediately before the call, run:

```bash
touch tmp/imagegen/wwii-support-sources/machine-gun-generation-start
```

```text
Use case: stylized-concept
Asset type: square game-unit sprite for a 64-pixel tactical grid
Primary request: one generic early-Second-World-War heavy machine gun mounted on a low sturdy tripod, with a long barrel jacket and one small closed ammunition box beside the tripod, no crew
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background for background removal
Style/medium: polished hand-painted tabletop strategy miniature, softly modeled 3D illustration, crisp silhouette matching the existing Dawn Tactics unit set
Composition/framing: centered complete weapon in an elevated three-quarter view, low horizontal silhouette, barrel pointing toward the upper right, tripod and ammunition box fully visible, generous even padding, no cropped parts
Lighting/mood: soft neutral studio lighting, calm educational strategy-game mood
Color palette: warm ivory, charcoal, muted steel, restrained tan accents; do not use green on the subject
Materials/textures: painted resin miniature with restrained mechanical detail that stays readable at 48 pixels
Historical constraints: broadly plausible for the early Second World War but not an identifiable national model; no crew; no national identity
Background constraints: one uniform #00ff00 color with no shadows, gradients, texture, reflections, floor plane, or lighting variation; no cast shadow; no contact shadow
Avoid: flags, insignia, unit markings, logos, words, numbers, exposed ammunition belt, firing, muzzle flash, smoke, explosion, blood, injury, people, scenery, watermark
```

After the call, identify the one newly generated file and copy it into the
project-local source directory:

```bash
machine_gun_generated_path=$(find /Users/mygenbio/.codex/generated_images -type f -name 'exec-*.png' -newer tmp/imagegen/wwii-support-sources/machine-gun-generation-start -print)
test -n "$machine_gun_generated_path"
test "$(printf '%s\n' "$machine_gun_generated_path" | wc -l | tr -d ' ')" -eq 1
cp "$machine_gun_generated_path" tmp/imagegen/wwii-support-sources/machine_gun-chroma.png
```

Expected: a square PNG containing one low tripod-mounted heavy machine gun on uniform green.

- [ ] **Step 3: Generate the Cavalry chroma source with built-in ImageGen**

Use one built-in ImageGen call with this exact prompt:

Immediately before the call, run:

```bash
touch tmp/imagegen/wwii-support-sources/cavalry-generation-start
```

```text
Use case: stylized-concept
Asset type: square game-unit sprite for a 64-pixel tactical grid
Primary request: one generic early-Second-World-War mounted reconnaissance soldier riding one calm horse at a gentle trot, with a short carbine safely slung across the rider's back
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background for background removal
Style/medium: polished hand-painted tabletop strategy miniature, softly modeled 3D illustration, crisp silhouette matching the existing Dawn Tactics unit set
Composition/framing: centered complete horse and rider in an elevated three-quarter side view, facing upper right, all four legs and the full rider visible, generous even padding, no cropped parts
Lighting/mood: soft neutral studio lighting, calm educational strategy-game mood
Color palette: warm ivory and tan uniform, charcoal steel helmet and tack, medium warm-brown horse, muted steel accents; do not use green on the subject
Materials/textures: painted resin miniature with restrained horse, uniform, and saddle detail that stays readable at 48 pixels
Historical constraints: broadly plausible for early-Second-World-War reconnaissance but not an identifiable national uniform; plain steel helmet; calm non-combat pose
Background constraints: one uniform #00ff00 color with no shadows, gradients, texture, reflections, floor plane, or lighting variation; no cast shadow; no contact shadow
Avoid: flags, insignia, unit markings, logos, words, numbers, raised saber, raised firearm, charge pose, firing, smoke, explosion, blood, injury, distressed horse, extra people, extra animals, scenery, watermark
```

After the call, identify the one newly generated file and copy it into the
project-local source directory:

```bash
cavalry_generated_path=$(find /Users/mygenbio/.codex/generated_images -type f -name 'exec-*.png' -newer tmp/imagegen/wwii-support-sources/cavalry-generation-start -print)
test -n "$cavalry_generated_path"
test "$(printf '%s\n' "$cavalry_generated_path" | wc -l | tr -d ' ')" -eq 1
cp "$cavalry_generated_path" tmp/imagegen/wwii-support-sources/cavalry-chroma.png
```

Expected: a square PNG containing one complete mounted scout on uniform green.

- [ ] **Step 4: Remove both chroma backgrounds**

Run with the system Python whose Pillow installation is already verified:

```bash
/usr/local/bin/python3.12 /Users/mygenbio/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --input tmp/imagegen/wwii-support-sources/machine_gun-chroma.png --out src/dawn_tactics/assets/units/machine_gun.png --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill
/usr/local/bin/python3.12 /Users/mygenbio/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --input tmp/imagegen/wwii-support-sources/cavalry-chroma.png --out src/dawn_tactics/assets/units/cavalry.png --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill
```

Expected: two RGBA PNG files are written under `src/dawn_tactics/assets/units/`.

- [ ] **Step 5: Validate alpha, corners, and subject coverage**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python - <<'PY'
from pathlib import Path
import pygame

pygame.init()
for name in ("machine_gun", "cavalry"):
    path = Path("src/dawn_tactics/assets/units") / f"{name}.png"
    image = pygame.image.load(path)
    assert image.get_masks()[3] != 0, f"{path} has no alpha channel"
    corners = (
        (0, 0),
        (image.get_width() - 1, 0),
        (0, image.get_height() - 1),
        (image.get_width() - 1, image.get_height() - 1),
    )
    assert all(image.get_at(point).a == 0 for point in corners), (
        f"{path} corners are opaque"
    )
    mask = pygame.mask.from_surface(image, 16)
    coverage = mask.count() / (image.get_width() * image.get_height())
    assert 0.08 <= coverage <= 0.72, (
        f"{path} coverage {coverage:.1%} is implausible"
    )
    print(path.name, image.get_size(), f"coverage={coverage:.1%}")
pygame.quit()
PY
```

Expected: both filenames print with plausible coverage and no assertion failure.

- [ ] **Step 6: Inspect both final PNGs at original resolution**

Open `machine_gun.png` and `cavalry.png` with the local image viewer. Confirm clean alpha edges, complete silhouettes, matching ivory/charcoal miniature finish, no national markings or forbidden content, and strong distinction from Anti-Tank and Infantry. If only a thin green fringe remains, rerun the affected helper command with `--edge-contract 1`. If content is wrong, regenerate only the affected image using one targeted prompt correction.

- [ ] **Step 7: Commit the validated PNGs**

```bash
git add src/dawn_tactics/assets/units/machine_gun.png src/dawn_tactics/assets/units/cavalry.png
git commit -m "Add WWII support unit image assets"
```

### Task 2: Register all six assets with TDD

**Files:**
- Modify: `tests/test_game_assets.py:8-57`
- Modify: `src/dawn_tactics/game.py:35-41`

- [ ] **Step 1: Write the failing six-asset registry test**

Add `UNIT_KINDS` to the import from `dawn_tactics.game` and replace `test_unit_asset_registry_matches_every_unit_kind` with:

```python
def test_unit_asset_registry_matches_every_unit_kind() -> None:
    assert UNIT_ASSET_FILES == {
        "infantry": "infantry.png",
        "anti_tank": "anti_tank.png",
        "tank": "tank.png",
        "artillery": "artillery.png",
        "machine_gun": "machine_gun.png",
        "cavalry": "cavalry.png",
    }
    assert tuple(UNIT_ASSET_FILES) == UNIT_KINDS
    assert all(
        (UNIT_ASSET_DIR / filename).is_file()
        for filename in UNIT_ASSET_FILES.values()
    )
```

The existing parametrized `test_load_unit_images_scales_every_asset` remains unchanged and will automatically require all registered files at 48 by 48 and 44 by 44.

- [ ] **Step 2: Run the registry and loader tests to verify RED**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py::test_unit_asset_registry_matches_every_unit_kind tests/test_game_assets.py::test_load_unit_images_scales_every_asset -q
```

Expected: the registry test fails because `UNIT_ASSET_FILES` contains only four entries.

- [ ] **Step 3: Add the minimal registry entries**

Change `UNIT_ASSET_FILES` in `src/dawn_tactics/game.py` to:

```python
UNIT_ASSET_FILES = {
    "infantry": "infantry.png",
    "anti_tank": "anti_tank.png",
    "tank": "tank.png",
    "artillery": "artillery.png",
    "machine_gun": "machine_gun.png",
    "cavalry": "cavalry.png",
}
```

No renderer or domain changes are needed.

- [ ] **Step 4: Run focused and complete tests to verify GREEN**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py::test_unit_asset_registry_matches_every_unit_kind tests/test_game_assets.py::test_load_unit_images_scales_every_asset -q
.venv/bin/python -m pytest -q
```

Expected: 3 focused test cases pass because the loader test is parametrized twice, then all 59 current tests pass.

- [ ] **Step 5: Commit registry and test changes**

```bash
git add src/dawn_tactics/game.py tests/test_game_assets.py
git commit -m "Load Machine Gun and Cavalry images"
```

### Task 3: Verify packaging and the six-unit rendered interface

**Files:**
- Create for inspection only: `screenshots/wwii-support-units-final.png`

- [ ] **Step 1: Build a wheel and verify exactly six packaged PNGs**

Run:

```bash
mkdir -p dist
.venv/bin/python -m pip wheel . --no-deps --wheel-dir dist
.venv/bin/python - <<'PY'
from pathlib import Path
from zipfile import ZipFile

wheel = next(Path("dist").glob("dawn_tactics-*.whl"))
with ZipFile(wheel) as archive:
    packaged = {name for name in archive.namelist() if "/assets/units/" in name}
expected = {
    f"dawn_tactics/assets/units/{name}.png"
    for name in (
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    )
}
assert packaged == expected, (packaged, expected)
print("Packaged unit assets:", *sorted(packaged), sep="\n")
PY
```

Expected: the wheel builds and prints exactly six unit PNG paths.

- [ ] **Step 2: Render a setup screen containing both new units**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python - <<'PY'
from pathlib import Path
import pygame

from dawn_tactics.campaigns import Difficulty
from dawn_tactics.domain import Position
from dawn_tactics.game import GameApp

output = Path("screenshots/wwii-support-units-final.png")
output.parent.mkdir(parents=True, exist_ok=True)

app = GameApp(Difficulty.NORMAL)
app._load_campaign(2)
assert app.controller.place_blue_unit("machine_gun", Position(7, 4)).ok
assert app.controller.place_blue_unit("cavalry", Position(7, 6)).ok
app.status = "Machine Gun and Cavalry image check."
app.draw()
pygame.image.save(app.screen, output)
pygame.quit()
print(output)
PY
file screenshots/wwii-support-units-final.png
```

Expected: a 1280 by 760 PNG shows Blue Machine Gun and Cavalry images on the grid and all six illustrated card images.

- [ ] **Step 3: Inspect the final screenshot at original resolution**

Confirm:

- Machine Gun is a low tripod weapon and is not confused with Anti-Tank.
- Cavalry reads as one calm horse and mounted scout, not Infantry.
- both new battlefield units sit inside their 64-pixel cells;
- Blue team plates and HP bars remain visible;
- all six card names, costs, HP, and rule text remain readable; and
- no image overlaps adjacent card text or another card.

If visual inspection requires an asset correction, regenerate only that asset, rerun chroma removal and alpha validation, then repeat the full test and screenshot steps before committing the corrected PNG.

- [ ] **Step 4: Commit any verification-driven asset correction**

If no correction was required, skip this commit. If a correction was required:

```bash
git add src/dawn_tactics/assets/units/machine_gun.png src/dawn_tactics/assets/units/cavalry.png
git commit -m "Refine WWII support unit images"
```

### Task 4: Final regression audit and cleanup

**Files:**
- No tracked file changes expected.

- [ ] **Step 1: Run static, complete, and deterministic verification**

Run:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest tests/test_domain.py::test_deployment_click_order_does_not_change_the_battle -q
git diff --check
```

Expected: compilation succeeds, all 59 tests pass, the deterministic battle regression passes, and `git diff --check` prints nothing.

- [ ] **Step 2: Prove domain and lesson rules were not changed**

```bash
base_sha=$(git merge-base HEAD main)
git diff --exit-code "$base_sha"..HEAD -- src/dawn_tactics/domain.py src/dawn_tactics/student_rules.py src/dawn_tactics/student_rules_validation.py src/dawn_tactics/campaigns.py
```

Expected: no output and exit code 0.

- [ ] **Step 3: Remove generated chroma sources**

After the transparent PNGs are committed and verified, remove only the two generated intermediate sources:

```bash
rm tmp/imagegen/wwii-support-sources/machine_gun-chroma.png
rm tmp/imagegen/wwii-support-sources/cavalry-chroma.png
rm tmp/imagegen/wwii-support-sources/machine-gun-generation-start
rm tmp/imagegen/wwii-support-sources/cavalry-generation-start
rmdir tmp/imagegen/wwii-support-sources tmp/imagegen tmp
```

Expected: the project-local temporary directory is removed. The original built-in ImageGen files remain under the Codex generated-images directory.

- [ ] **Step 4: Check final repository state**

Run:

```bash
git status --short
git log -5 --oneline --decorate
```

Expected: the feature branch has no tracked or untracked changes; its commits contain exactly the two new PNGs, the six-entry registry, and the registry test update.
