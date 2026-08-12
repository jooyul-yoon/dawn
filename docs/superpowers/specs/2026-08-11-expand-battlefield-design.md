# Expanded Battlefield Design

## Goal

Expand the Dawn Tactics battlefield by one playable cell on every side. The
board grows from 12 columns by 8 rows to 14 columns by 10 rows while preserving
the current 64-pixel cell size, six-unit interface, combat rules, and translated
campaign balance.

## Board Geometry

- Change the default `Battle` size from 12 by 8 to 14 by 10.
- Keep `CELL_SIZE` at 64 pixels so unit art, HP bars, click targets, and movement
  remain the same physical size.
- Derive the rendered grid from the new board dimensions: 896 by 640 pixels.
- Keep the grid origin at `(40, 150)`.
- Move the command panel right by 128 pixels, preserving the existing 32-pixel
  gap between the grid and panel.
- Expand the window from 1280 by 760 to 1408 by 888. This preserves the current
  left, right, top, and bottom breathing room around the enlarged grid.
- Keep the command panel width and its internal card layout unchanged.

## Coordinate Migration

The old board is conceptually centered inside the new board. Stored campaign
enemy deployments therefore move by one row and one column:

```text
new_position = Position(old.row + 1, old.column + 1)
```

This applies to every normal and hard enemy deployment in `campaigns.py`.

Player deployment examples and deterministic test layouts also move by one row
and one column. The Blue deployment zone expands to the bottom four rows so the
translated formations remain legal and preserve their exact relative distance
from the translated enemy formations.

## Deployment Zones

- The red zone remains the top three rows: `0`, `1`, and `2`.
- The blue zone expands to the bottom four rows: `6`, `7`, `8`, and `9`.
- The new outer cells are fully playable during battle.
- The controller continues to derive the blue-zone boundary from the battle
  height rather than duplicating a fixed row number.
- Zone labels and colors continue to be derived from the active battle size.

Because stored red formations are shifted down by one row, units formerly on
row `2` may begin immediately below the red setup coloring. Red units are
campaign-controlled and are not validated by the player deployment rule, so
this is intentional: it preserves the old formation inside the centered map
instead of compressing it toward the new top edge.

## Combat and Learning Scope

- Do not change movement, range, damage, targeting, budgets, unit stats, or
  student-editable rules.
- Do not add terrain, scrolling, or zooming.
- Deterministic IDs remain derived from deployment coordinates. Translating both
  teams by the same offset and preserving row `6` as deployable keeps the
  existing campaign outcomes and click-order determinism reproducible.
- Lesson examples and built-in demo layouts must use legal positions on the new
  board.

## Testing and Visual Verification

Add or update tests that prove:

1. A default battle is exactly 14 by 10.
2. Positions on the new top, bottom, left, and right border cells are inside the
   battlefield, while positions beyond them are rejected.
3. The blue deployment zone accepts rows 6 through 9 and rejects row 5.
4. Every campaign deployment is inside the expanded board and matches the
   one-row, one-column migration.
5. Grid click conversion reaches the new bottom-right cell and rejects pixels
   outside the enlarged grid.
6. The rendered window is 1408 by 888, the command panel does not overlap the
   grid, and the six cards remain non-overlapping.
7. Campaign winning layouts and click-order determinism still pass with updated
   legal coordinates and freshly verified outcomes.
8. A headless screenshot shows the complete 14-by-10 grid, deployment-zone
   labels, unit images, HP bars, and command panel without clipping.

Run the complete test suite, compilation, `git diff --check`, and the dedicated
deployment-order regression before completion.

## Success Criteria

The player sees two additional columns and two additional rows, with one new
cell visibly surrounding each side of the old battlefield footprint. All cells
are clickable and usable during combat, setup remains limited to the bottom
four rows, campaign formations and verified outcomes remain reproducible, and
no interface element is clipped or overlapped.
