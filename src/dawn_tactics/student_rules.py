"""Lesson 02 — Conditionals

Change the conditions and returned damage values, then restart the game.
Keep each possible target covered by an if, elif, or else branch.
"""


def machine_gun_damage(target_armor):
    """Choose Machine Gun damage from the target's armor."""
    if target_armor == "LIGHT":
        return 4
    else:
        return 1


def cavalry_damage(target_kind):
    """Choose Cavalry damage from the target's unit kind."""
    if target_kind == "artillery":
        return 5
    elif target_kind == "infantry":
        return 3
    else:
        return 1
