from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KOREAN_NOTEBOOK = ROOT / "lessons" / "lesson_04_classes.ipynb"
ENGLISH_NOTEBOOK = ROOT / "lessons" / "lesson_04_classes_en.ipynb"
TEACHER_GUIDE = ROOT / "lessons" / "lesson_04_curriculum_ko.md"
README = ROOT / "README.md"

EXPECTED_CELL_IDS = (
    "title",
    "mission-brief",
    "learning-goals",
    "function-prerequisite",
    "blueprint-map",
    "first-class",
    "first-object-predict",
    "first-object",
    "self-init-map",
    "two-objects-predict",
    "two-objects",
    "method-map",
    "method-example",
    "real-game-bridge",
    "final-brief",
    "student-task",
    "student-self-check",
    "student-explain",
    "exit-ticket",
    "teacher-next-step",
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _cells(notebook: dict[str, object]) -> list[dict[str, object]]:
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return cells


def _source(cell: dict[str, object]) -> str:
    return "".join(cell["source"])


def _cell(notebook: dict[str, object], cell_id: str) -> dict[str, object]:
    return next(cell for cell in _cells(notebook) if cell["id"] == cell_id)


def _code_signature(
    notebook: dict[str, object],
) -> list[tuple[object, object, object]]:
    return [
        (cell["id"], cell["metadata"], cell["source"])
        for cell in _cells(notebook)
        if cell["cell_type"] == "code"
    ]


def _execute_prepared_examples(
    notebook: dict[str, object],
) -> dict[str, object]:
    namespace: dict[str, object] = {}
    for cell in _cells(notebook):
        if cell["id"] == "student-task":
            break
        if cell["cell_type"] == "code":
            exec(compile(_source(cell), f"<{cell['id']}>", "exec"), namespace)
    return namespace


def test_lesson_four_notebooks_exist_parse_and_share_contract() -> None:
    korean = _load(KOREAN_NOTEBOOK)
    english = _load(ENGLISH_NOTEBOOK)

    assert korean["nbformat"] == english["nbformat"] == 4
    assert tuple(cell["id"] for cell in _cells(korean)) == EXPECTED_CELL_IDS
    assert tuple(cell["id"] for cell in _cells(english)) == EXPECTED_CELL_IDS
    assert _code_signature(korean) == _code_signature(english)


def test_master_notebooks_have_no_saved_execution_state() -> None:
    for path in (KOREAN_NOTEBOOK, ENGLISH_NOTEBOOK):
        for cell in _cells(_load(path)):
            if cell["cell_type"] != "code":
                continue
            assert cell["execution_count"] is None
            assert cell["outputs"] == []


def test_prepared_examples_execute_and_keep_object_state_independent() -> None:
    namespace = _execute_prepared_examples(_load(ENGLISH_NOTEBOOK))

    assert namespace["label"] == "Mission: Hold the bridge"
    first = namespace["first_card"]
    second = namespace["second_card"]
    assert first.objective == "Hold the bridge"
    assert second.objective == "Protect the town"
    assert first.brief() == "Objective: Hold the bridge"

    left_tank = namespace["left_tank"]
    right_tank = namespace["right_tank"]
    assert left_tank.hp == left_tank.max_hp - 3
    assert right_tank.hp == right_tank.max_hp


def test_final_task_is_prompt_only_and_self_check_is_exact() -> None:
    notebook = _load(ENGLISH_NOTEBOOK)
    task = _cell(notebook, "student-task")
    check = _cell(notebook, "student-self-check")
    task_source = _source(task)
    check_source = _source(check)

    assert task["metadata"]["tags"] == ["student-task"]
    assert task_source == (
        "# Write class Unit from its class line.\n"
        "# Inputs after self: name, max_hp\n"
        "# Store name, max_hp, and hp. hp starts equal to max_hp.\n"
        "# take_damage(amount) subtracts damage and never lets hp go below 0.\n"
    )
    for solution_fragment in (
        "class Unit:",
        "def __init__",
        "def take_damage",
        "self.hp",
        "pass",
    ):
        assert solution_fragment not in task_source

    assert check["metadata"]["tags"] == ["student-self-check"]
    for expected in (
        'tank = Unit("Tank", 10)',
        'infantry = Unit("Infantry", 5)',
        "assert tank.name == \"Tank\"",
        "assert tank.max_hp == 10",
        "assert tank.hp == 7",
        "assert infantry.hp == 5",
        "tank.take_damage(99)",
        "assert tank.hp == 0",
    ):
        assert expected in check_source


def test_lesson_covers_class_vocabulary_without_inheritance_code() -> None:
    notebook = _load(ENGLISH_NOTEBOOK)
    all_text = "\n".join(_source(cell) for cell in _cells(notebook))
    code = "\n".join(
        _source(cell)
        for cell in _cells(notebook)
        if cell["cell_type"] == "code"
    )

    for phrase in (
        "class",
        "object",
        "blueprint",
        "__init__",
        "self",
        "attribute",
        "method",
        "dot notation",
        "independent state",
    ):
        assert phrase.lower() in all_text.lower()

    for prohibited in (
        "class Tank(Unit)",
        "super(",
        "ClassVar",
        "@property",
        "@dataclass",
        "UNIT_REGISTRY",
        "import pygame",
    ):
        assert prohibited not in code


def test_korean_notebook_is_korean_led() -> None:
    notebook = _load(KOREAN_NOTEBOOK)
    markdown = "\n".join(
        _source(cell)
        for cell in _cells(notebook)
        if cell["cell_type"] == "markdown"
    )
    hangul_count = sum("가" <= character <= "힣" for character in markdown)
    assert hangul_count >= 450


def test_teacher_guide_has_timing_coaching_solution_and_boundary() -> None:
    guide = TEACHER_GUIDE.read_text(encoding="utf-8")

    for timing in (
        "0–8분",
        "8–20분",
        "20–34분",
        "34–46분",
        "46–51분",
        "51–63분",
        "63–69분",
        "69–84분",
        "84–88분",
        "88–90분",
    ):
        assert timing in guide

    assert (
        "Read → Find the class/object name → Check colon and indentation "
        "→ Count arguments after self → Check every self. prefix → Run again"
    ) in guide
    assert "Hint 1" in guide
    assert "Hint 2" in guide
    assert "Hint 3" in guide
    assert "class Unit:" in guide
    assert "def __init__(self, name, max_hp):" in guide
    assert "def take_damage(self, amount):" in guide
    assert "inheritance" in guide.lower()
    assert "super()" in guide
    assert "reset checklist" in guide.lower()


def test_readme_links_lesson_four_and_defers_inheritance() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "lessons/lesson_04_classes.ipynb" in readme
    assert "lessons/lesson_04_classes_en.ipynb" in readme
    assert "lessons/lesson_04_curriculum_ko.md" in readme
    assert "Lesson 04" in readme
    assert "Lesson 05" in readme
    assert "inheritance" in readme.lower()
