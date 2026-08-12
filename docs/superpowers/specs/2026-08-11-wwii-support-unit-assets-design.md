# WWII Support Unit Assets Design

## Goal

Add illustrated `MachineGun` and `Cavalry` assets to the existing Dawn Tactics
miniature set and render them on the battlefield and in the six unit-selection
cards. The images should communicate an early Second World War setting without
assigning the game to a specific country, army, or historical battle.

## Historical and Visual Direction

Use the equipment-centered approach that best matches the existing Infantry,
Anti-Tank, Tank, and Artillery images while remaining readable at 48 pixels.
Both new images use the set's polished hand-painted tabletop-miniature finish,
elevated three-quarter view, warm ivory, charcoal, muted steel, and restrained
tan accents.

`MachineGun` depicts one generic early-Second-World-War heavy machine gun on a
low tripod. A long barrel jacket and a small closed ammunition box make its role
clear, but there is no crew, exposed ammunition belt, firing effect, or national
model detail. Its low horizontal silhouette must remain distinct from the
long-barreled Anti-Tank gun.

`Cavalry` depicts one mounted reconnaissance rider at a calm trot. The rider
wears a plain steel helmet and neutral tan uniform with a carbine safely slung
across the back. The rider carries no raised saber or flag, and the horse shows
no distress. The combined horse-and-rider silhouette should fill the frame
without resembling Infantry when reduced to game size.

Neither image may contain national insignia, flags, unit markings, readable
text, logos, blood, injuries, firing, explosions, aggressive gestures, scenery,
or a watermark. Exact historical equipment models are intentionally avoided so
the game remains a broadly educational, non-gory strategy setting.

## Asset Layout

Add two transparent PNG files beside the existing four assets:

```text
src/dawn_tactics/assets/units/
├── anti_tank.png
├── artillery.png
├── cavalry.png
├── infantry.png
├── machine_gun.png
└── tank.png
```

Each subject is generated centered on a perfectly flat chroma-key background,
then processed locally to produce an RGBA PNG with transparent corners and
clean antialiased edges. The two final files should have generous padding and
visually match the apparent scale and lighting of the existing set.

## Rendering Architecture

Extend `UNIT_ASSET_FILES` in `game.py` with `machine_gun.png` and `cavalry.png`.
No new loader, renderer, or runtime branch is needed: `GameApp` already loads
every registered image once at startup, caches 48-pixel battlefield and
44-pixel card surfaces, draws team-colored plates, and falls back to pygame
shapes if a file is missing or invalid.

The asset registry remains in the pygame presentation layer. `domain.py`,
`student_rules.py`, validation, movement, damage, unit costs, and campaign
behavior remain unchanged.

## Data Flow and Failure Handling

At startup, the two new filenames participate in the existing package-relative
load loop. Successful loads populate both image caches. A missing or invalid
new file is omitted from the cache, so the existing `MG` or `C` geometric
symbol renders instead while all other units continue normally.

The existing setuptools glob already packages every PNG under
`assets/units/`, so adding the files requires no new packaging mechanism. A
wheel inspection will still verify that all six expected files are included.

## Testing and Verification

Update the asset registry test so its expected mapping contains all six
`UNIT_KINDS`. The existing parametrized loader test must then prove that all six
assets load as alpha-aware surfaces at both battlefield and card sizes.

Final verification will:

- validate both new images' alpha channels, transparent corners, and subject
  coverage;
- run the full Python test suite without changing existing expected outcomes;
- build a wheel and confirm exactly six unit PNG paths are packaged;
- render a setup screen with Blue Machine Gun and Cavalry units deployed; and
- visually confirm the two new images are distinct, team plates and HP remain
  legible, all six card labels and rules fit, and no image crosses a cell or
  overlaps adjacent card text.

## Out of Scope

This work does not change unit balance, conditional lesson rules, campaign
forces, history-note copy, input controls, layout dimensions, existing four
images, animations, sounds, factions, or national identities.
