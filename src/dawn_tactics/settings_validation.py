from __future__ import annotations

from . import student_settings as settings


class StudentSettingsError(ValueError):
    """Raised when a lesson setting cannot be used safely by the game."""


def validate_student_settings() -> None:
    _require_text("GAME_TITLE", settings.GAME_TITLE, maximum_length=30)
    _require_text("TANK_NAME", settings.TANK_NAME, maximum_length=14)

    for name, value in (
        ("FIRST_DEPLOYMENT_BUDGET", settings.FIRST_DEPLOYMENT_BUDGET),
        ("TANK_BREAKER_BUDGET", settings.TANK_BREAKER_BUDGET),
        ("COMBINED_ARMS_BUDGET", settings.COMBINED_ARMS_BUDGET),
    ):
        _require_integer(name, value, minimum=0, maximum=100_000)

    _require_integer("TANK_COST", settings.TANK_COST, minimum=1, maximum=100_000)
    _require_integer("TANK_MAX_HP", settings.TANK_MAX_HP, minimum=1, maximum=999)
    _require_integer("TANK_DAMAGE", settings.TANK_DAMAGE, minimum=1, maximum=999)
    _require_integer("TANK_RANGE", settings.TANK_RANGE, minimum=1, maximum=12)
    _require_integer(
        "ANTI_TANK_DAMAGE_VS_HEAVY",
        settings.ANTI_TANK_DAMAGE_VS_HEAVY,
        minimum=1,
        maximum=999,
    )

    speed = settings.BATTLE_STEP_SECONDS
    if type(speed) not in {int, float} or not 0.05 <= speed <= 2.0:
        raise StudentSettingsError(
            "BATTLE_STEP_SECONDS must be a number from 0.05 to 2.0."
        )
    if type(settings.SHOW_HISTORY_NOTE) is not bool:
        raise StudentSettingsError(
            "SHOW_HISTORY_NOTE must be exactly True or False."
        )


def _require_text(name: str, value: object, maximum_length: int) -> None:
    if type(value) is not str or not value.strip() or len(value) > maximum_length:
        raise StudentSettingsError(
            f"{name} must be text from 1 to {maximum_length} characters."
        )


def _require_integer(
    name: str,
    value: object,
    *,
    minimum: int,
    maximum: int,
) -> None:
    if type(value) is not int or not minimum <= value <= maximum:
        raise StudentSettingsError(
            f"{name} must be a whole number from {minimum} to {maximum}."
        )
