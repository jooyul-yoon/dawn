# Five-Row Territories Design

## Goal

Expand Dawn Tactics to a 14-column by 12-row battlefield composed of two equal
team territories and a central neutral strip:

```text
Red territory     rows 0-4    5 x 14
Neutral territory rows 5-6    2 x 14
Blue territory    rows 7-11   5 x 14
```

The change increases tactical deployment space without changing unit stats,
budgets, combat rules, or student-editable lesson rules.

## Screen and Cell Geometry

- The authoritative default `Battle` size becomes 14 columns by 12 rows.
- `CELL_SIZE` becomes 56 pixels. The grid is therefore 784 by 672 pixels.
- Keep the grid origin at `(40, 150)`.
- Place the command panel at x=856, preserving a 32-pixel gap after the grid.
- Use a 1280 by 888 window. The grid ends at y=822, leaving 66 pixels below it.
- Keep the command panel width at 400 pixels and extend its background to align
  with the grid bottom. Existing cards, buttons, and text keep their internal
  sizes and positions.
- Keep 48-pixel battlefield images and 44-pixel card images. The team plate
  remains a 24-pixel-radius circle, which leaves four pixels of cell padding.
- Reduce the battlefield HP bar to 42 by 5 pixels and position it one pixel
  inside the top of its 56-pixel cell. HP text remains inside the lower edge.

This fixed layout is preferred to responsive scaling because it stays simple
for the educational codebase and fits the complete 14-by-12 map without the
1016-pixel-tall window required by 64-pixel cells.

## Territory Rules

- Red territory coloring and the `ENEMY ZONE` label cover rows 0 through 4.
- Rows 5 and 6 use the neutral battlefield color.
- Blue territory coloring and `YOUR DEPLOYMENT ZONE` label cover rows 7 through
  11.
- Player setup accepts deployment in rows 7 through 11 and rejects row 6.
- Every cell, including the outermost row and column, remains usable for
  movement and combat after setup.
- Territory depth is derived from a shared constant rather than separate magic
  numbers in controller and renderer code.

## Enemy Deployment

Campaign unit composition, budgets, difficulty penalties, and reinforcements
remain unchanged. Only positions change.

### Campaign 1: First Deployment

Normal enemies form a broad infantry line in the Red territory:

```text
Infantry    (3, 2), (3, 7), (3, 12)
```

Hard adds one Anti-Tank unit behind the center:

```text
Anti-Tank   (2, 7)
```

### Campaign 2: Tank Breaker

The tanks hold the left and right approach while infantry screens the center:

```text
Tank        (3, 4), (3, 10)
Infantry    (4, 7)
```

Hard adds one Infantry unit on the left flank:

```text
Infantry    (4, 2)
```

### Campaign 3: Combined Arms

Artillery occupies the rear, infantry protects the flanks, Anti-Tank units
cover the approaches, and the tank anchors the center:

```text
Artillery   (1, 7)
Infantry    (3, 2), (3, 12)
Anti-Tank   (4, 4), (4, 10)
Tank        (4, 7)
```

Hard adds a second rear Artillery unit:

```text
Artillery   (1, 11)
```

These arrangements are nation-neutral and tactical rather than decorative.
They use the full 14-column width without placing units on territory labels.

## Player and Demo Layouts

- Existing built-in player layouts are not mechanically translated. Each Normal
  and Hard campaign receives a newly verified legal layout within rows 7-11.
- A verified layout must respect that campaign's budget and allowed unit list.
- Each Normal and Hard campaign must retain at least one automated Blue-winning
  layout before `max_ticks`.
- `prepare_demo_layout()` uses the same verified layouts as the tests.
- Blue unit IDs remain derived from coordinates. Forward and reverse deployment
  order must produce identical event history, result, and tick count.
- Changing enemy positions may change the verified tick counts. Tests record
  newly observed deterministic values; production combat behavior is not tuned
  merely to preserve old counts.

## Scope Boundaries

Do not change:

- unit costs, HP, damage, range, armor, attack cadence, or movement cadence;
- campaign budgets, difficulty penalties, enemy composition, or allowed units;
- targeting, pathfinding, simultaneous damage, or victory rules;
- student settings, student rules, or their validation;
- unit image assets or card layout; or
- terrain, scrolling, zooming, networking, or new game modes.

## Testing and Visual Verification

Tests must prove:

1. The default battle is exactly 14 by 12.
2. All four new corner cells are valid and coordinates outside row 11 or column
   13 are rejected.
3. Red rows are 0-4, neutral rows are 5-6, and Blue rows are 7-11.
4. Player deployment accepts rows 7-11 and rejects row 6.
5. Every campaign's Normal and Hard enemy signatures exactly match this design.
6. Mouse conversion reaches bottom-right `Position(11, 13)` and rejects pixels
   beyond the grid.
7. Window, grid, panel, cards, buttons, unit plates, HP bars, and labels do not
   overlap or clip.
8. All six Normal/Hard campaign variants have a verified Blue-winning layout.
9. Forward/reverse deployment order remains deterministic.
10. The complete existing test suite and compilation pass.

Create a headless 1280-by-888 screenshot containing Machine Gun and Cavalry in
the Blue territory and inspect it at original resolution. It must visibly show
five Red rows, two neutral rows, five Blue rows, fourteen columns, readable
labels/cards/text, a 32-pixel panel gap, and uncropped outer borders.

## Success Criteria

The player sees a complete 14-by-12 board with equal 5-by-14 Red and Blue
territories separated by a 2-by-14 neutral strip. Enemy formations use the new
space intentionally, Blue can deploy anywhere in its five rows, every campaign
remains winnable and deterministic, and the full interface fits without
clipping.
