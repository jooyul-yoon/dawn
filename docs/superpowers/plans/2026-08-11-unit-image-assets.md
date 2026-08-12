# Unit Image Assets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create four distinct transparent unit images and use them in the Dawn Tactics battlefield and unit-selection cards without changing deterministic combat behavior.

**Architecture:** Generate one neutral board-game miniature PNG per unit and reuse it for both teams. The pygame presentation layer loads and scales the four package-relative files once during `GameApp` initialization, draws Blue or Red team plates behind battlefield images, and falls back to the existing geometric renderer when an asset cannot load. Domain and controller code remain unchanged.

**Tech Stack:** Python 3.12, pygame-ce 2.5.7, pytest, setuptools package data, built-in ImageGen, local chroma-key removal helper

---

## File Map

- Create `src/dawn_tactics/assets/units/infantry.png`: transparent infantry miniature.
- Create `src/dawn_tactics/assets/units/anti_tank.png`: transparent anti-tank gun miniature.
- Create `src/dawn_tactics/assets/units/tank.png`: transparent tracked tank miniature.
- Create `src/dawn_tactics/assets/units/artillery.png`: transparent field howitzer miniature.
- Create `tests/test_game_assets.py`: asset loading, image sizing, battlefield rendering, and fallback tests.
- Modify `src/dawn_tactics/game.py`: registry, cached loader, battlefield renderer, and card renderer.
- Modify `pyproject.toml`: include the PNG files in built distributions.
- Modify `README.md`: describe image-backed presentation and the asset location.

### Task 1: Generate and validate the four transparent unit assets

**Files:**
- Create: `src/dawn_tactics/assets/units/infantry.png`
- Create: `src/dawn_tactics/assets/units/anti_tank.png`
- Create: `src/dawn_tactics/assets/units/tank.png`
- Create: `src/dawn_tactics/assets/units/artillery.png`

- [ ] **Step 1: Create source and final asset directories**

Run:

```bash
mkdir -p tmp/imagegen/unit-assets-sources src/dawn_tactics/assets/units
```

Expected: both directories exist and contain no newly generated files yet.

- [ ] **Step 2: Generate the infantry source with built-in ImageGen**

Use one built-in ImageGen call with this exact prompt:

```text
Use case: stylized-concept
Asset type: square game-unit sprite for a 64-pixel tactical grid
Primary request: a single generic twentieth-century infantry board-game miniature, standing in a steady non-combat pose, holding a simple rifle safely downward
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background for background removal
Style/medium: polished hand-painted tabletop strategy miniature, softly modeled 3D illustration, crisp silhouette
Composition/framing: centered full figure, consistent elevated three-quarter view, generous even padding, entire miniature visible, no cropped parts
Lighting/mood: soft neutral studio lighting, calm educational strategy-game mood
Color palette: warm ivory, charcoal, muted steel, small tan accents; do not use green on the subject
Materials/textures: painted resin miniature with restrained detail that stays readable at 48 pixels
Constraints: one subject only; perfectly uniform #00ff00 background with no shadows, gradients, texture, reflections, floor plane, or lighting variation; no cast shadow; no contact shadow; no national identity
Avoid: flags, insignia, logos, words, numbers, blood, injury, muzzle flash, explosion, aggressive action, extra figures, scenery, watermark
```

Copy the generated file path reported by the tool to `tmp/imagegen/unit-assets-sources/infantry-chroma.png`.

Expected: one centered infantry miniature on flat green.

- [ ] **Step 3: Generate the anti-tank source with built-in ImageGen**

Use one built-in ImageGen call with this exact prompt:

```text
Use case: stylized-concept
Asset type: square game-unit sprite for a 64-pixel tactical grid
Primary request: a single generic twentieth-century low-profile wheeled anti-tank gun board-game miniature with a long horizontal barrel, no crew
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background for background removal
Style/medium: polished hand-painted tabletop strategy miniature, softly modeled 3D illustration, crisp silhouette matching a unit set
Composition/framing: centered complete gun, consistent elevated three-quarter view, long barrel fully inside frame, generous even padding, no cropped parts
Lighting/mood: soft neutral studio lighting, calm educational strategy-game mood
Color palette: warm ivory, charcoal, muted steel, small tan accents; do not use green on the subject
Materials/textures: painted resin miniature with restrained detail that stays readable at 48 pixels
Constraints: one subject only; perfectly uniform #00ff00 background with no shadows, gradients, texture, reflections, floor plane, or lighting variation; no cast shadow; no contact shadow; no national identity
Avoid: flags, insignia, logos, words, numbers, blood, injury, muzzle flash, explosion, ammunition, people, scenery, watermark
```

Copy the generated file path reported by the tool to `tmp/imagegen/unit-assets-sources/anti_tank-chroma.png`.

Expected: a low, long silhouette clearly different from artillery.

- [ ] **Step 4: Generate the tank source with built-in ImageGen**

Use one built-in ImageGen call with this exact prompt:

```text
Use case: stylized-concept
Asset type: square game-unit sprite for a 64-pixel tactical grid
Primary request: a single generic compact twentieth-century tracked tank board-game miniature with a short turret and clearly visible tracks
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background for background removal
Style/medium: polished hand-painted tabletop strategy miniature, softly modeled 3D illustration, crisp silhouette matching a unit set
Composition/framing: centered complete vehicle, consistent elevated three-quarter view, turret pointing upper-right, generous even padding, no cropped parts
Lighting/mood: soft neutral studio lighting, calm educational strategy-game mood
Color palette: warm ivory, charcoal, muted steel, small tan accents; do not use green on the subject
Materials/textures: painted resin miniature with restrained detail that stays readable at 48 pixels
Constraints: one subject only; perfectly uniform #00ff00 background with no shadows, gradients, texture, reflections, floor plane, or lighting variation; no cast shadow; no contact shadow; no national identity
Avoid: flags, insignia, logos, words, numbers, blood, injury, muzzle flash, explosion, people, scenery, watermark
```

Copy the generated file path reported by the tool to `tmp/imagegen/unit-assets-sources/tank-chroma.png`.

Expected: tracks and turret remain readable at thumbnail scale.

- [ ] **Step 5: Generate the artillery source with built-in ImageGen**

Use one built-in ImageGen call with this exact prompt:

```text
Use case: stylized-concept
Asset type: square game-unit sprite for a 64-pixel tactical grid
Primary request: a single generic twentieth-century field howitzer board-game miniature with two large wheels and a barrel raised distinctly upward, no crew
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background for background removal
Style/medium: polished hand-painted tabletop strategy miniature, softly modeled 3D illustration, crisp silhouette matching a unit set
Composition/framing: centered complete howitzer, consistent elevated three-quarter view, raised barrel fully inside frame, generous even padding, no cropped parts
Lighting/mood: soft neutral studio lighting, calm educational strategy-game mood
Color palette: warm ivory, charcoal, muted steel, small tan accents; do not use green on the subject
Materials/textures: painted resin miniature with restrained detail that stays readable at 48 pixels
Constraints: one subject only; perfectly uniform #00ff00 background with no shadows, gradients, texture, reflections, floor plane, or lighting variation; no cast shadow; no contact shadow; no national identity
Avoid: flags, insignia, logos, words, numbers, blood, injury, muzzle flash, explosion, ammunition, people, scenery, watermark
```

Copy the generated file path reported by the tool to `tmp/imagegen/unit-assets-sources/artillery-chroma.png`.

Expected: raised barrel and large wheels distinguish it from the anti-tank gun.

- [ ] **Step 6: Remove the chroma key from all four sources**

Run:

```bash
.venv/bin/python /Users/mygenbio/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --input tmp/imagegen/unit-assets-sources/infantry-chroma.png --out src/dawn_tactics/assets/units/infantry.png --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill
.venv/bin/python /Users/mygenbio/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --input tmp/imagegen/unit-assets-sources/anti_tank-chroma.png --out src/dawn_tactics/assets/units/anti_tank.png --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill
.venv/bin/python /Users/mygenbio/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --input tmp/imagegen/unit-assets-sources/tank-chroma.png --out src/dawn_tactics/assets/units/tank.png --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill
.venv/bin/python /Users/mygenbio/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --input tmp/imagegen/unit-assets-sources/artillery-chroma.png --out src/dawn_tactics/assets/units/artillery.png --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill
```

Expected: four RGBA PNG files under `src/dawn_tactics/assets/units/`.

- [ ] **Step 7: Validate alpha, transparent corners, and subject coverage**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python - <<'PY'
from pathlib import Path
import pygame

pygame.init()
for path in sorted(Path("src/dawn_tactics/assets/units").glob("*.png")):
    image = pygame.image.load(path)
    assert image.get_masks()[3] != 0, f"{path} has no alpha channel"
    corners = (
        (0, 0),
        (image.get_width() - 1, 0),
        (0, image.get_height() - 1),
        (image.get_width() - 1, image.get_height() - 1),
    )
    assert all(image.get_at(point).a == 0 for point in corners), f"{path} corners are opaque"
    mask = pygame.mask.from_surface(image, 16)
    coverage = mask.count() / (image.get_width() * image.get_height())
    assert 0.08 <= coverage <= 0.72, f"{path} coverage {coverage:.1%} is implausible"
    print(path.name, image.get_size(), f"coverage={coverage:.1%}")
pygame.quit()
PY
```

Expected: four filenames print with plausible coverage and no assertion failure.

- [ ] **Step 8: Inspect all four final PNG files visually**

Open each final PNG at original resolution. Confirm the subjects are complete, coherent, clean-edged, free of forbidden details, and distinct at 48 pixels. If there is only a thin green fringe, rerun the affected image with `--edge-contract 1`. If subject or style is wrong, regenerate only that unit with one targeted prompt change.

- [ ] **Step 9: Commit the validated assets**

```bash
git add src/dawn_tactics/assets/units/*.png
git commit -m "Add illustrated unit image assets"
```

### Task 2: Add a tested asset registry and cached loader

**Files:**
- Create: `tests/test_game_assets.py`
- Modify: `src/dawn_tactics/game.py:24-71`

- [ ] **Step 1: Write failing registry and loader tests**

Create `tests/test_game_assets.py` with:

```python
from pathlib import Path

import pygame
import pytest

from dawn_tactics.game import (
    BATTLE_UNIT_IMAGE_SIZE,
    CARD_UNIT_IMAGE_SIZE,
    UNIT_ASSET_DIR,
    UNIT_ASSET_FILES,
    _load_unit_images,
)


@pytest.fixture
def pygame_display() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def test_unit_asset_registry_matches_every_unit_kind() -> None:
    assert UNIT_ASSET_FILES == {
        "infantry": "infantry.png",
        "anti_tank": "anti_tank.png",
        "tank": "tank.png",
        "artillery": "artillery.png",
    }
    assert all(
        (UNIT_ASSET_DIR / filename).is_file()
        for filename in UNIT_ASSET_FILES.values()
    )


@pytest.mark.parametrize("size", [BATTLE_UNIT_IMAGE_SIZE, CARD_UNIT_IMAGE_SIZE])
def test_load_unit_images_scales_every_asset(
    pygame_display: None,
    size: tuple[int, int],
) -> None:
    images = _load_unit_images(size)

    assert set(images) == set(UNIT_ASSET_FILES)
    assert all(image.get_size() == size for image in images.values())
    assert all(image.get_flags() & pygame.SRCALPHA for image in images.values())


def test_load_unit_images_skips_missing_and_invalid_files(
    pygame_display: None,
    tmp_path: Path,
) -> None:
    valid = pygame.Surface((12, 12), pygame.SRCALPHA)
    valid.fill((240, 220, 180, 255))
    pygame.image.save(valid, tmp_path / "tank.png")
    (tmp_path / "infantry.png").write_text("not a png", encoding="utf-8")

    images = _load_unit_images((8, 8), tmp_path)

    assert set(images) == {"tank"}
    assert images["tank"].get_size() == (8, 8)
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py -q
```

Expected: collection fails because the constants and `_load_unit_images` do not exist.

- [ ] **Step 3: Add the minimal registry, loader, and caches**

Add below the layout constants in `src/dawn_tactics/game.py`:

```python
UNIT_ASSET_DIR = Path(__file__).resolve().parent / "assets" / "units"
UNIT_ASSET_FILES = {
    "infantry": "infantry.png",
    "anti_tank": "anti_tank.png",
    "tank": "tank.png",
    "artillery": "artillery.png",
}
BATTLE_UNIT_IMAGE_SIZE = (48, 48)
CARD_UNIT_IMAGE_SIZE = (44, 44)


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
```

After `self.screen` is created in `GameApp.__init__`, add:

```python
self.unit_images = _load_unit_images(BATTLE_UNIT_IMAGE_SIZE)
self.unit_card_images = _load_unit_images(CARD_UNIT_IMAGE_SIZE)
```

- [ ] **Step 4: Run focused and full tests to verify GREEN**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py -q
.venv/bin/python -m pytest -q
```

Expected: 4 focused tests pass, then 28 total tests pass.

- [ ] **Step 5: Commit loader and tests**

```bash
git add tests/test_game_assets.py src/dawn_tactics/game.py
git commit -m "Load and cache unit image assets"
```

### Task 3: Render battlefield images with team identity and fallback

**Files:**
- Modify: `tests/test_game_assets.py`
- Modify: `src/dawn_tactics/game.py:360-416`

- [ ] **Step 1: Write failing battlefield renderer tests**

Add the following imports and tests to `tests/test_game_assets.py`:

```python
from dawn_tactics.campaigns import Difficulty
from dawn_tactics.domain import Infantry, Position, Team
from dawn_tactics.game import BACKGROUND, BLUE, GameApp


@pytest.fixture
def app() -> GameApp:
    game = GameApp(Difficulty.NORMAL)
    yield game
    pygame.quit()


def test_draw_unit_visual_blits_cached_image_over_team_plate(app: GameApp) -> None:
    marker = (17, 219, 83, 255)
    image = pygame.Surface(BATTLE_UNIT_IMAGE_SIZE, pygame.SRCALPHA)
    image.fill(marker)
    app.unit_images = {"infantry": image}
    unit = Infantry(1, Team.BLUE, Position(7, 2))
    center = (160, 200)
    app.screen.fill(BACKGROUND)

    used_image = app._draw_unit_visual(unit, center, BLUE)

    assert used_image
    assert app.screen.get_at(center) == marker
    assert app.screen.get_at((center[0] + 24, center[1])).b > 150


def test_draw_unit_visual_uses_shape_fallback_when_asset_is_missing(
    app: GameApp,
) -> None:
    app.unit_images = {}
    unit = Infantry(1, Team.BLUE, Position(7, 2))
    center = (160, 200)
    app.screen.fill(BACKGROUND)

    used_image = app._draw_unit_visual(unit, center, BLUE)

    assert not used_image
    assert app.screen.get_at(center) != BACKGROUND
```

- [ ] **Step 2: Run the new tests and verify RED**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py::test_draw_unit_visual_blits_cached_image_over_team_plate tests/test_game_assets.py::test_draw_unit_visual_uses_shape_fallback_when_asset_is_missing -q
```

Expected: both fail because `GameApp` has no `_draw_unit_visual` method.

- [ ] **Step 3: Add the minimal battlefield visual method**

Add before `_draw_unit_shape`:

```python
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
```

Replace the old shadow and shape calls in `_draw_units` with:

```python
self._draw_unit_visual(unit, center, color)
```

Keep HP bar and numeric HP rendering unchanged.

- [ ] **Step 4: Run focused and full UI tests to verify GREEN**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py::test_draw_unit_visual_blits_cached_image_over_team_plate tests/test_game_assets.py::test_draw_unit_visual_uses_shape_fallback_when_asset_is_missing -q
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py -q
```

Expected: 2 focused tests pass, then all 6 UI asset tests pass.

- [ ] **Step 5: Commit battlefield rendering**

```bash
git add tests/test_game_assets.py src/dawn_tactics/game.py
git commit -m "Render illustrated units on the battlefield"
```

### Task 4: Render unit images in selection cards

**Files:**
- Modify: `tests/test_game_assets.py`
- Modify: `src/dawn_tactics/game.py:477-514`

- [ ] **Step 1: Write failing card image and fallback tests**

Append:

```python
def test_draw_unit_card_visual_blits_cached_image(app: GameApp) -> None:
    marker = (214, 137, 29, 255)
    image = pygame.Surface(CARD_UNIT_IMAGE_SIZE, pygame.SRCALPHA)
    image.fill(marker)
    app.unit_card_images = {"tank": image}
    card = pygame.Rect(100, 100, 174, 92)
    app.screen.fill(BACKGROUND)

    used_image = app._draw_unit_card_visual("tank", card)

    assert used_image
    assert app.screen.get_at((card.x + 27, card.centery)) == marker


def test_draw_unit_card_visual_uses_shape_fallback(app: GameApp) -> None:
    app.unit_card_images = {}
    card = pygame.Rect(100, 100, 174, 92)
    app.screen.fill(BACKGROUND)

    used_image = app._draw_unit_card_visual("tank", card)

    assert not used_image
    assert app.screen.get_at((card.x + 27, card.centery)) != BACKGROUND
```

- [ ] **Step 2: Run the new tests and verify RED**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py::test_draw_unit_card_visual_blits_cached_image tests/test_game_assets.py::test_draw_unit_card_visual_uses_shape_fallback -q
```

Expected: both fail because `GameApp` has no `_draw_unit_card_visual` method.

- [ ] **Step 3: Add the minimal card visual method and text inset**

Add before `_draw_side_panel`:

```python
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
```

Inside the card loop add:

```python
self._draw_unit_card_visual(kind, rect)
text_x = rect.x + 56
```

Change each of the three card text x positions from `rect.x + 12` to `text_x`. Preserve vertical positions, fonts, values, and colors.

- [ ] **Step 4: Run focused, UI, and full tests to verify GREEN**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py::test_draw_unit_card_visual_blits_cached_image tests/test_game_assets.py::test_draw_unit_card_visual_uses_shape_fallback -q
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest tests/test_game_assets.py -q
.venv/bin/python -m pytest -q
```

Expected: 2 focused tests, 8 UI asset tests, and 32 total tests pass.

- [ ] **Step 5: Commit card rendering**

```bash
git add tests/test_game_assets.py src/dawn_tactics/game.py
git commit -m "Show unit images in selection cards"
```

### Task 5: Package and document the assets

**Files:**
- Modify: `pyproject.toml:26-29`
- Modify: `README.md:9-16`
- Modify: `README.md:85-114`

- [ ] **Step 1: Add explicit setuptools package data**

Add below `[tool.setuptools.packages.find]`:

```toml
[tool.setuptools.package-data]
dawn_tactics = ["assets/units/*.png"]
```

- [ ] **Step 2: Update presentation and customization documentation**

Change the README presentation bullet to:

```markdown
- abstract, non-graphic presentation with illustrated unit miniatures and pygame effects.
```

Add after the Teaching boundary section:

```markdown
## Unit image assets

Battlefield and selection-card images live in
`src/dawn_tactics/assets/units/`. The same neutral PNG is reused for both teams;
pygame's Blue and Red team plates identify ownership. If an asset is missing or
invalid, the game falls back to its original geometric unit symbol.
```

- [ ] **Step 3: Build a wheel and verify the four packaged files**

Run:

```bash
.venv/bin/python -m pip wheel . --no-deps --wheel-dir dist
.venv/bin/python - <<'PY'
from pathlib import Path
from zipfile import ZipFile

wheel = next(Path("dist").glob("dawn_tactics-*.whl"))
with ZipFile(wheel) as archive:
    packaged = {name for name in archive.namelist() if "/assets/units/" in name}
expected = {
    f"dawn_tactics/assets/units/{name}.png"
    for name in ("infantry", "anti_tank", "tank", "artillery")
}
assert packaged == expected, (packaged, expected)
print("Packaged unit assets:", *sorted(packaged), sep="\n")
PY
```

Expected: the wheel builds and prints exactly four package-relative PNG paths.

- [ ] **Step 4: Commit packaging and documentation**

```bash
git add pyproject.toml README.md
git commit -m "Package and document unit image assets"
```

### Task 6: Verify deterministic gameplay and rendered output

**Files:**
- Create for inspection only: `screenshots/unit-assets-final.png`

- [ ] **Step 1: Run static and automated verification**

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest -q
git diff --check
```

Expected: compilation succeeds, 32 tests pass, and `git diff --check` prints nothing.

- [ ] **Step 2: Confirm deterministic campaign behavior remains unchanged**

```bash
.venv/bin/python -m pytest tests/test_domain.py::test_deployment_click_order_does_not_change_the_battle -q
```

Expected: 1 test passes and retains the Hard Campaign 3 Blue victory at tick 19.

- [ ] **Step 3: Render the all-unit screenshot**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m dawn_tactics --screenshot screenshots/unit-assets-final.png --campaign 2 --difficulty hard --simulate-ticks 5
```

Expected: a 1280 by 760 screenshot containing all four unit types in the battle and all four selection cards.

- [ ] **Step 4: Inspect the screenshot at original resolution**

Confirm every unit is distinct, Blue and Red team plates are clear, HP remains readable, attack lines remain visible, card text is not clipped, no sprite crosses a grid-cell boundary, and no card image overlaps text.

- [ ] **Step 5: Check repository state**

```bash
git status --short
git log -6 --oneline --decorate
```

Expected: source, tests, package configuration, documentation, and final assets are committed. Any correction triggered by visual inspection must be rechecked with its focused test, the full suite, and a fresh screenshot before its correction commit.
