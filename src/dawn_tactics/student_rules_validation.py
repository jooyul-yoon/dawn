from __future__ import annotations

from . import student_rules as rules


SUPPORTED_TARGET_ARMORS = ("LIGHT", "HEAVY")
SUPPORTED_TARGET_KINDS = (
    "infantry",
    "anti_tank",
    "tank",
    "artillery",
    "machine_gun",
    "cavalry",
)


class StudentRulesError(ValueError):
    """Raised when a Day 2 conditional rule returns unsafe damage."""


def _checked_damage(
    rule_name: str,
    input_name: str,
    input_value: str,
    result: object,
) -> int:
    if type(result) is not int or not 0 <= result <= 999:
        raise StudentRulesError(
            f"{rule_name} must return a whole-number damage from 0 to 999 "
            f"for {input_name}={input_value!r}; got {result!r}."
        )
    return result


def machine_gun_damage_for(target_armor: str) -> int:
    return _checked_damage(
        "MACHINE_GUN_DAMAGE",
        "target_armor",
        target_armor,
        rules.machine_gun_damage(target_armor),
    )


def cavalry_damage_for(target_kind: str) -> int:
    return _checked_damage(
        "CAVALRY_DAMAGE",
        "target_kind",
        target_kind,
        rules.cavalry_damage(target_kind),
    )


def validate_student_rules() -> None:
    for armor in SUPPORTED_TARGET_ARMORS:
        machine_gun_damage_for(armor)
    for kind in SUPPORTED_TARGET_KINDS:
        cavalry_damage_for(kind)
