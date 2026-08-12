# Unit Image Assets Design

## Goal

Replace the abstract unit shapes in Dawn Tactics with readable illustrated
assets for `Infantry`, `AntiTank`, `Tank`, and `Artillery`. Reuse the same four
images for both teams, preserve the game's non-graphic educational tone, and
keep combat rules independent from pygame.

## Visual Direction

Use a stylized twentieth-century board-game miniature look with a neutral warm
ivory, charcoal, and muted steel palette. The images should feel historical
without representing a specific country or conflict. They must contain no
flags, insignia, words, blood, injuries, muzzle flashes, explosions, or
watermarks.

Each unit needs a distinct silhouette that remains identifiable at 48 pixels:

- `Infantry`: one helmeted infantry miniature in a steady standing pose.
- `AntiTank`: a low-profile wheeled anti-tank gun with a long horizontal barrel.
- `Tank`: a compact tracked tank viewed from a consistent elevated three-quarter angle.
- `Artillery`: a field howitzer with a raised barrel and visibly larger wheels.

Generate every subject centered with generous padding on a perfectly flat
chroma-key background. Remove the chroma key locally and save a transparent PNG
for each unit. All four outputs should share the same lighting, viewing angle,
apparent scale, palette, and edge treatment.

## Asset Layout

Store the final project assets at:

```text
src/dawn_tactics/assets/units/
├── infantry.png
├── anti_tank.png
├── tank.png
└── artillery.png
```

The PNG files are the source assets used at runtime. Runtime code scales them
once during application initialization and caches separate battlefield and card
surfaces. The game does not load or transform image files inside the frame loop.
`pyproject.toml` will explicitly include the PNG directory as package data so
editable installs, built distributions, and the double-click launchers all see
the same assets.

## Rendering Architecture

Image ownership remains entirely inside the pygame presentation layer.
`domain.py`, the unit subclasses, the controller, and deterministic combat rules
remain unchanged.

`game.py` will define a UI-only mapping from unit kind to asset filename and a
small loader that returns cached pygame surfaces. A failed or missing image is
represented by `None`; rendering then calls the existing shape renderer. This
keeps the game playable from incomplete source checkouts and makes individual
asset replacement safe for future lessons.

Battlefield rendering will use this order:

1. Draw a subtle dark drop shadow.
2. Draw a Blue or Red circular team plate and high-contrast outline.
3. Blit the neutral unit image centered on the plate at approximately 48 pixels.
4. Draw the existing HP bar above the unit and numeric HP below it.

The team plate, not an image tint, communicates team identity. This prevents
recoloring from obscuring the miniature's details and lets both teams reuse an
identical asset.

Unit selection cards will show the same image at approximately 44 pixels on the
left. Name, cost, HP, damage, and range text will shift to the right so the
existing gameplay information stays visible. Selected and affordability states
continue to use the current border and text colors.

## Data Flow and Failure Handling

At startup, `GameApp` resolves each path relative to the installed
`dawn_tactics` package, loads it with `pygame.image.load`, converts it to an
alpha-aware surface, scales it, and stores it by unit kind. Draw methods request
only an already-cached surface.

If a file is absent, unreadable, or not a valid image, the loader records no
surface for that kind. The affected unit and card use the existing pygame shape
and short-name fallback while all other assets continue to render. Asset errors
must never change unit placement, IDs, battle timing, targeting, or results.

## Testing and Verification

Automated checks will cover the UI asset registry, expected files, successful
loading in a dummy SDL display, scaled surface sizes, and the fallback behavior
for an unavailable image. Existing domain and controller tests must continue to
pass unchanged.

Final visual verification will render a deterministic headless screenshot of a
battle containing all four unit types. The screenshot must prove that:

- every unit has a distinct image;
- Blue and Red units remain immediately distinguishable;
- HP values and attack effects remain legible;
- all four selection cards retain their rule text;
- no image crosses its 64-pixel grid cell or overlaps adjacent UI; and
- the application works without changing deterministic battle outcomes.

## Out of Scope

Animations, team-specific image sets, national factions, sound effects, combat
rule changes, new unit types, and modifications to the curriculum notebooks are
not part of this work.
