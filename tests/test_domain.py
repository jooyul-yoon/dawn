import pytest

from dawn_tactics import student_rules as rules
from dawn_tactics import student_settings as settings
from dawn_tactics.campaigns import CAMPAIGNS, VERIFIED_BLUE_LAYOUTS, Difficulty
from dawn_tactics.controller import GameController
from dawn_tactics.domain import (
    DEFAULT_BATTLE_HEIGHT,
    DEFAULT_BATTLE_WIDTH,
    TERRITORY_DEPTH,
    AntiTank,
    Artillery,
    Battle,
    BattleEvent,
    BattleState,
    Cavalry,
    EventKind,
    Infantry,
    MachineGun,
    Position,
    Tank,
    Team,
    UNIT_REGISTRY,
)
from dawn_tactics.settings_validation import (
    StudentSettingsError,
    validate_student_settings,
)


DEFAULT_BALANCE_IS_ACTIVE = (
    settings.FIRST_DEPLOYMENT_BUDGET == 500
    and settings.TANK_BREAKER_BUDGET == 1_000
    and settings.COMBINED_ARMS_BUDGET == 1_200
    and settings.TANK_COST == 400
    and settings.TANK_MAX_HP == 10
    and settings.TANK_DAMAGE == 3
    and settings.TANK_RANGE == 2
    and settings.ANTI_TANK_DAMAGE_VS_HEAVY == 5
)


def test_machine_gun_and_cavalry_stats_and_registry() -> None:
    assert UNIT_REGISTRY["machine_gun"] is MachineGun
    assert (
        MachineGun.display_name,
        MachineGun.short_name,
        MachineGun.cost,
        MachineGun.max_hp,
        MachineGun.base_damage,
        MachineGun.attack_range,
        MachineGun.attack_every,
        MachineGun.move_every,
        MachineGun.armor,
    ) == ("Machine Gun", "MG", 300, 5, 1, 3, 2, 1, "LIGHT")

    assert UNIT_REGISTRY["cavalry"] is Cavalry
    assert (
        Cavalry.display_name,
        Cavalry.short_name,
        Cavalry.cost,
        Cavalry.max_hp,
        Cavalry.base_damage,
        Cavalry.attack_range,
        Cavalry.attack_every,
        Cavalry.move_every,
        Cavalry.armor,
    ) == ("Cavalry", "C", 200, 6, 1, 1, 1, 1, "LIGHT")


def test_new_units_delegate_damage_to_student_rules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    machine_gun = MachineGun(1, Team.BLUE, Position(2, 2))
    cavalry = Cavalry(2, Team.BLUE, Position(2, 3))
    tank = Tank(3, Team.RED, Position(1, 2))
    artillery = Artillery(4, Team.RED, Position(1, 3))
    monkeypatch.setattr(rules, "machine_gun_damage", lambda armor: 7)
    monkeypatch.setattr(rules, "cavalry_damage", lambda kind: 8)

    assert machine_gun.damage_against(tank) == 7
    assert cavalry.damage_against(artillery) == 8


def test_anti_tank_specializes_against_heavy_armor() -> None:
    anti_tank = AntiTank(1, Team.BLUE, Position(1, 1))
    tank = Tank(2, Team.RED, Position(1, 2))
    infantry = Infantry(3, Team.RED, Position(2, 1))

    assert anti_tank.damage_against(tank) == settings.ANTI_TANK_DAMAGE_VS_HEAVY
    assert anti_tank.damage_against(infantry) == 1


def test_target_selection_uses_distance_then_hp_then_id() -> None:
    attacker = Infantry(10, Team.BLUE, Position(4, 4))
    farther = Infantry(1, Team.RED, Position(0, 4))
    closer_high_hp = Infantry(2, Team.RED, Position(4, 6))
    closer_low_hp_high_id = Infantry(4, Team.RED, Position(6, 4))
    closer_low_hp_low_id = Infantry(3, Team.RED, Position(4, 2))
    closer_low_hp_high_id.hp = 2
    closer_low_hp_low_id.hp = 2

    assert attacker.choose_target([farther, closer_high_hp]) is closer_high_hp
    assert (
        attacker.choose_target(
            [closer_high_hp, closer_low_hp_high_id, closer_low_hp_low_id]
        )
        is closer_low_hp_low_id
    )


def test_default_battle_is_fourteen_by_twelve() -> None:
    battle = Battle()

    assert DEFAULT_BATTLE_WIDTH == 14
    assert DEFAULT_BATTLE_HEIGHT == 12
    assert TERRITORY_DEPTH == 5
    assert (battle.width, battle.height) == (
        DEFAULT_BATTLE_WIDTH,
        DEFAULT_BATTLE_HEIGHT,
    )


def test_expanded_battle_accepts_all_four_corners() -> None:
    battle = Battle()
    positions = (
        Position(0, 0),
        Position(0, 13),
        Position(11, 0),
        Position(11, 13),
    )

    for unit_id, position in enumerate(positions, start=1):
        battle.add_unit(Infantry(unit_id, Team.BLUE, position))

    assert tuple(unit.position for unit in battle.units) == positions


@pytest.mark.parametrize(
    "position",
    (Position(-1, 0), Position(0, -1), Position(12, 0), Position(0, 14)),
)
def test_expanded_battle_rejects_positions_beyond_new_border(
    position: Position,
) -> None:
    with pytest.raises(ValueError, match="outside the battlefield"):
        Battle().add_unit(Infantry(1, Team.BLUE, position))


def test_blue_deployment_zone_is_bottom_five_rows() -> None:
    controller = GameController()
    controller.load_campaign(0)
    controller.remaining_budget = Infantry.cost * 6

    assert not controller.place_blue_unit("infantry", Position(6, 1)).ok
    for column, row in enumerate((7, 8, 9, 10, 11), start=1):
        assert controller.place_blue_unit("infantry", Position(row, column)).ok


def test_campaign_deployments_use_five_row_red_territory() -> None:
    expected = (
        (
            ("infantry", Position(3, 2)),
            ("infantry", Position(3, 7)),
            ("infantry", Position(3, 12)),
            ("anti_tank", Position(2, 7)),
        ),
        (
            ("tank", Position(3, 4)),
            ("tank", Position(3, 10)),
            ("infantry", Position(4, 7)),
            ("infantry", Position(4, 2)),
        ),
        (
            ("artillery", Position(1, 7)),
            ("infantry", Position(3, 2)),
            ("infantry", Position(3, 12)),
            ("anti_tank", Position(4, 4)),
            ("anti_tank", Position(4, 10)),
            ("tank", Position(4, 7)),
            ("artillery", Position(1, 11)),
        ),
    )
    actual = tuple(
        tuple(
            (item.unit_kind, item.position)
            for item in campaign.enemies + campaign.hard_reinforcements
        )
        for campaign in CAMPAIGNS
    )

    assert actual == expected


def test_budget_purchase_invalid_placement_and_full_refund() -> None:
    controller = GameController()
    controller.load_campaign(0)
    controller.remaining_budget = Tank.cost + Infantry.cost
    starting_budget = controller.remaining_budget

    invalid = controller.place_blue_unit("tank", Position(2, 2))
    assert not invalid.ok
    assert controller.remaining_budget == starting_budget

    assert controller.place_blue_unit("tank", Position(9, 6)).ok
    assert controller.remaining_budget == Infantry.cost
    assert controller.place_blue_unit("infantry", Position(9, 5)).ok
    assert controller.remaining_budget == 0

    too_expensive = controller.place_blue_unit("infantry", Position(9, 4))
    assert not too_expensive.ok
    assert controller.remaining_budget == 0

    refunded = controller.remove_blue_unit(Position(9, 6))
    assert refunded.ok
    assert controller.remaining_budget == Tank.cost


def test_damage_is_applied_simultaneously_and_can_draw() -> None:
    battle = Battle(width=4, height=4)
    blue = Infantry(1, Team.BLUE, Position(2, 1))
    red = Infantry(2, Team.RED, Position(1, 1))
    blue.hp = 1
    red.hp = 1
    battle.add_unit(blue)
    battle.add_unit(red)

    assert battle.start()
    events = battle.step()

    assert battle.state is BattleState.DRAW
    assert sum(event.kind is EventKind.ATTACK for event in events) == 2
    assert sum(event.kind is EventKind.DESTROY for event in events) == 2


def test_maximum_tick_limit_prevents_stalemates() -> None:
    battle = Battle(width=8, height=8, max_ticks=1)
    battle.add_unit(Infantry(1, Team.BLUE, Position(7, 0)))
    battle.add_unit(Infantry(2, Team.RED, Position(0, 7)))
    assert battle.start()

    battle.step()

    assert battle.tick == 1
    assert battle.state is BattleState.DRAW


def _run_repeatable_battle() -> tuple[BattleState, tuple[tuple[object, ...], ...]]:
    battle = Battle(width=8, height=6)
    battle.add_unit(Tank(1, Team.BLUE, Position(5, 2)))
    battle.add_unit(Infantry(2, Team.BLUE, Position(5, 3)))
    battle.add_unit(AntiTank(3, Team.RED, Position(0, 2)))
    battle.add_unit(Infantry(4, Team.RED, Position(0, 3)))
    assert battle.start()
    while battle.state is BattleState.RUNNING:
        battle.step()
    log = tuple(
        (
            event.kind,
            event.unit_id,
            event.target_id,
            event.from_position,
            event.to_position,
            event.amount,
            event.result,
        )
        for event in battle.history
    )
    return battle.state, log


def test_identical_battles_have_identical_results_and_event_logs() -> None:
    assert _run_repeatable_battle() == _run_repeatable_battle()


def _run_campaign_layout(
    campaign_index: int,
    difficulty: Difficulty,
    layout: tuple[tuple[str, Position], ...],
) -> tuple[BattleState, int, tuple[BattleEvent, ...]]:
    controller = GameController(difficulty)
    controller.load_campaign(campaign_index)
    for kind, position in layout:
        assert controller.place_blue_unit(kind, position).ok
    assert controller.start_battle().ok
    while controller.battle.state is BattleState.RUNNING:
        controller.step()
    return (
        controller.battle.state,
        controller.battle.tick,
        tuple(controller.battle.history),
    )


EXPECTED_VERIFIED_LAYOUTS = {
    Difficulty.NORMAL: (
        (
            ("infantry", Position(9, 4)),
            ("tank", Position(8, 8)),
        ),
        (
            ("anti_tank", Position(8, 4)),
            ("anti_tank", Position(8, 7)),
            ("anti_tank", Position(8, 10)),
            ("infantry", Position(10, 5)),
            ("infantry", Position(10, 9)),
        ),
        (
            ("tank", Position(10, 6)),
            ("anti_tank", Position(10, 4)),
            ("artillery", Position(10, 9)),
            ("infantry", Position(11, 5)),
            ("infantry", Position(11, 8)),
        ),
    ),
    Difficulty.HARD: (
        (
            ("infantry", Position(8, 6)),
            ("artillery", Position(9, 8)),
        ),
        (
            ("infantry", Position(8, 3)),
            ("infantry", Position(8, 7)),
            ("artillery", Position(11, 7)),
            ("anti_tank", Position(8, 10)),
            ("infantry", Position(10, 7)),
        ),
        (
            ("machine_gun", Position(11, 4)),
            ("tank", Position(11, 1)),
            ("infantry", Position(10, 1)),
            ("cavalry", Position(9, 1)),
        ),
    ),
}


def test_verified_blue_layout_data_matches_approved_positions() -> None:
    actual = {
        difficulty: tuple(
            tuple((item.unit_kind, item.position) for item in layout)
            for layout in layouts
        )
        for difficulty, layouts in VERIFIED_BLUE_LAYOUTS.items()
    }

    assert actual == EXPECTED_VERIFIED_LAYOUTS


@pytest.mark.parametrize(
    ("difficulty", "expected_ticks"),
    (
        (Difficulty.NORMAL, (9, 6, 15)),
        (Difficulty.HARD, (13, 14, 21)),
    ),
)
@pytest.mark.skipif(
    not DEFAULT_BALANCE_IS_ACTIVE,
    reason="Restore Lesson 01 defaults to verify the original campaign balance.",
)
def test_each_verified_layout_wins_and_ignores_click_order(
    difficulty: Difficulty,
    expected_ticks: tuple[int, int, int],
) -> None:
    for campaign_index, (layout, tick) in enumerate(
        zip(EXPECTED_VERIFIED_LAYOUTS[difficulty], expected_ticks, strict=True)
    ):
        forward = _run_campaign_layout(campaign_index, difficulty, layout)
        backward = _run_campaign_layout(
            campaign_index,
            difficulty,
            tuple(reversed(layout)),
        )

        assert forward == backward
        assert forward[:2] == (BattleState.BLUE_WIN, tick)


def test_restart_restores_campaign_budget_enemies_and_unit_ids() -> None:
    controller = GameController()
    controller.load_campaign(1)
    initial_enemy_signature = [
        (unit.unit_id, unit.kind, unit.position)
        for unit in controller.battle.units
    ]
    controller.place_blue_unit("anti_tank", Position(9, 5))

    controller.restart()

    assert controller.remaining_budget == settings.TANK_BREAKER_BUDGET
    assert [
        (unit.unit_id, unit.kind, unit.position)
        for unit in controller.battle.units
    ] == initial_enemy_signature
    assert all(unit.team is Team.RED for unit in controller.battle.units)


def test_student_settings_are_safe() -> None:
    validate_student_settings()


def test_zero_battle_speed_has_a_helpful_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "BATTLE_STEP_SECONDS", 0)

    with pytest.raises(StudentSettingsError, match="BATTLE_STEP_SECONDS"):
        validate_student_settings()


def test_text_used_for_tank_cost_has_a_helpful_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "TANK_COST", "200")

    with pytest.raises(StudentSettingsError, match="TANK_COST"):
        validate_student_settings()


def test_tank_class_uses_student_settings() -> None:
    tank = Tank(1, Team.BLUE, Position(1, 1))

    assert Tank.display_name == settings.TANK_NAME
    assert Tank.cost == settings.TANK_COST
    assert Tank.max_hp == settings.TANK_MAX_HP
    assert tank.hp == settings.TANK_MAX_HP
    assert Tank.base_damage == settings.TANK_DAMAGE
    assert Tank.attack_range == settings.TANK_RANGE


def test_campaigns_use_student_budget_settings() -> None:
    expected = (
        settings.FIRST_DEPLOYMENT_BUDGET,
        settings.TANK_BREAKER_BUDGET,
        settings.COMBINED_ARMS_BUDGET,
    )

    assert tuple(campaign.starting_budget for campaign in CAMPAIGNS) == expected
    for campaign, budget in zip(CAMPAIGNS, expected, strict=True):
        assert f"${budget:,}" in campaign.objective_for(Difficulty.NORMAL)


def test_hard_mode_has_less_budget_and_visible_reinforcements() -> None:
    for campaign in CAMPAIGNS:
        assert campaign.budget_for(Difficulty.HARD) < campaign.budget_for(
            Difficulty.NORMAL
        )
        assert len(campaign.enemies_for(Difficulty.HARD)) > len(
            campaign.enemies_for(Difficulty.NORMAL)
        )


def test_restart_preserves_hard_mode() -> None:
    controller = GameController(Difficulty.HARD)
    controller.load_campaign(1)
    hard_budget = CAMPAIGNS[1].budget_for(Difficulty.HARD)
    hard_enemy_count = len(CAMPAIGNS[1].enemies_for(Difficulty.HARD))

    controller.restart()

    assert controller.difficulty is Difficulty.HARD
    assert controller.remaining_budget == hard_budget
    assert len(controller.battle.units) == hard_enemy_count


@pytest.mark.parametrize(
    ("tank_damage", "expected_state", "expected_ticks"),
    (
        (3, BattleState.BLUE_WIN, 9),
        (1, BattleState.RED_WIN, 10),
        (6, BattleState.BLUE_WIN, 8),
    ),
)
@pytest.mark.skipif(
    not DEFAULT_BALANCE_IS_ACTIVE,
    reason="Restore Lesson 01 defaults to verify its baseline experiment.",
)
def test_lesson_one_normal_mode_damage_experiment_stays_reproducible(
    monkeypatch: pytest.MonkeyPatch,
    tank_damage: int,
    expected_state: BattleState,
    expected_ticks: int,
) -> None:
    monkeypatch.setattr(Tank, "base_damage", tank_damage)
    controller = GameController(Difficulty.NORMAL)
    controller.load_campaign(0)
    assert controller.place_blue_unit("infantry", Position(9, 4)).ok
    assert controller.place_blue_unit("tank", Position(8, 8)).ok
    assert controller.start_battle().ok

    while controller.battle.state is BattleState.RUNNING:
        controller.step()

    assert controller.battle.state is expected_state
    assert controller.battle.tick == expected_ticks


def test_all_campaigns_allow_six_player_unit_types() -> None:
    expected = (
        "infantry",
        "anti_tank",
        "tank",
        "artillery",
        "machine_gun",
        "cavalry",
    )
    assert all(campaign.allowed_units == expected for campaign in CAMPAIGNS)


def test_campaign_one_can_buy_and_refund_both_day_two_units() -> None:
    controller = GameController(Difficulty.NORMAL)
    controller.load_campaign(0)
    assert controller.place_blue_unit("machine_gun", Position(9, 5)).ok
    assert controller.remaining_budget == 200
    assert controller.place_blue_unit("cavalry", Position(9, 7)).ok
    assert controller.remaining_budget == 0
    assert controller.remove_blue_unit(Position(9, 5)).ok
    assert controller.remaining_budget == 300
