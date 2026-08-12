import pytest

from dawn_tactics import student_rules as rules
from dawn_tactics.student_rules_validation import (
    StudentRulesError,
    cavalry_damage_for,
    machine_gun_damage_for,
    validate_student_rules,
)


def test_default_student_rules_cover_if_elif_and_else_branches() -> None:
    assert rules.machine_gun_damage("LIGHT") == 4
    assert rules.machine_gun_damage("HEAVY") == 1
    assert rules.cavalry_damage("artillery") == 5
    assert rules.cavalry_damage("infantry") == 3
    assert rules.cavalry_damage("tank") == 1


def test_default_student_rules_are_safe() -> None:
    validate_student_rules()


def test_startup_validation_evaluates_every_supported_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_armors: list[str] = []
    seen_kinds: list[str] = []
    monkeypatch.setattr(
        rules,
        "machine_gun_damage",
        lambda armor: seen_armors.append(armor) or 1,
    )
    monkeypatch.setattr(
        rules,
        "cavalry_damage",
        lambda kind: seen_kinds.append(kind) or 1,
    )

    validate_student_rules()

    assert seen_armors == ["LIGHT", "HEAVY"]
    assert seen_kinds == [
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    ]


@pytest.mark.parametrize("bad_result", (None, "4", True, -1, 1_000))
def test_machine_gun_rule_rejects_invalid_damage(
    monkeypatch: pytest.MonkeyPatch,
    bad_result: object,
) -> None:
    monkeypatch.setattr(
        rules,
        "machine_gun_damage",
        lambda target_armor: bad_result,
    )
    with pytest.raises(
        StudentRulesError,
        match=r"MACHINE_GUN_DAMAGE.*target_armor='LIGHT'",
    ):
        machine_gun_damage_for("LIGHT")


def test_missing_cavalry_else_has_a_helpful_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def incomplete_rule(target_kind):
        if target_kind == "artillery":
            return 5

    monkeypatch.setattr(rules, "cavalry_damage", incomplete_rule)
    with pytest.raises(
        StudentRulesError,
        match=r"CAVALRY_DAMAGE.*target_kind='tank'.*None",
    ):
        cavalry_damage_for("tank")


def test_zero_damage_is_a_valid_student_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rules, "cavalry_damage", lambda target_kind: 0)
    assert cavalry_damage_for("tank") == 0
