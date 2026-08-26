from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KOREAN_NOTEBOOK = ROOT / "lessons" / "lesson_03_functions.ipynb"
ENGLISH_NOTEBOOK = ROOT / "lessons" / "lesson_03_functions_en.ipynb"
TEACHER_GUIDE = ROOT / "lessons" / "lesson_03_curriculum_ko.md"

EXPECTED_CELL_IDS = (
    "title",
    "mission-brief",
    "learning-goals",
    "function-map",
    "call-predict",
    "call-example",
    "definition-challenge",
    "definition-check",
    "parameter-map",
    "parameter-example",
    "argument-challenge",
    "return-predict",
    "return-example",
    "print-versus-return",
    "local-variable-map",
    "local-variable-example",
    "local-scope-safety-net",
    "compose-trace",
    "compose-example",
    "boolean-bridge",
    "final-brief",
    "student-task",
    "student-self-check",
    "exit-ticket",
    "teacher-next-step",
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _cells(notebook: dict[str, object]) -> list[dict[str, object]]:
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return cells


def _cell_source(notebook: dict[str, object], cell_id: str) -> str:
    cell = next(cell for cell in _cells(notebook) if cell["id"] == cell_id)
    return "".join(cell["source"])


def _code_signature(notebook: dict[str, object]) -> list[tuple[object, ...]]:
    return [
        (cell["id"], cell["source"], cell["metadata"])
        for cell in _cells(notebook)
        if cell["cell_type"] == "code"
    ]


def _execute_completed_examples(notebook: dict[str, object]) -> dict[str, object]:
    namespace: dict[str, object] = {}
    for cell in _cells(notebook):
        if cell["id"] == "student-task":
            break
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            exec(compile(source, f"<lesson-03:{cell['id']}>", "exec"), namespace)
    return namespace


def test_lesson_three_notebooks_exist_and_parse() -> None:
    assert _load(KOREAN_NOTEBOOK)["nbformat"] == 4
    assert _load(ENGLISH_NOTEBOOK)["nbformat"] == 4


def test_lesson_three_notebooks_share_cell_contract_and_code() -> None:
    korean = _load(KOREAN_NOTEBOOK)
    english = _load(ENGLISH_NOTEBOOK)
    assert tuple(cell["id"] for cell in _cells(korean)) == EXPECTED_CELL_IDS
    assert tuple(cell["id"] for cell in _cells(english)) == EXPECTED_CELL_IDS
    assert _code_signature(korean) == _code_signature(english)


def test_completed_examples_execute_and_return_documented_values() -> None:
    namespace = _execute_completed_examples(_load(KOREAN_NOTEBOOK))
    assert namespace["total_cost"](250, 3) == 750
    assert namespace["remaining_budget"](1000, 750) == 250
    assert namespace["can_deploy"](500, 400) is True
    assert namespace["can_deploy"](300, 400) is False


def test_final_task_requires_student_to_write_from_def() -> None:
    notebook = _load(KOREAN_NOTEBOOK)
    task = _cell_source(notebook, "student-task")
    task_cell = next(
        cell for cell in _cells(notebook) if cell["id"] == "student-task"
    )
    assert task == (
        "# Write deployment_report() from its def line.\n"
        "# Parameters: unit_name, unit_cost, count, budget\n"
        "# Return the exact deployment report described above.\n"
    )
    assert task_cell["metadata"] == {"tags": ["student-task"]}
    assert "def deployment_report" not in task
    assert "total_cost(unit_cost, count)" not in task
    assert "remaining_budget(budget, cost)" not in task
    assert "pass" not in task


def test_final_self_check_has_exact_examples_and_tag() -> None:
    notebook = _load(KOREAN_NOTEBOOK)
    check = _cell_source(notebook, "student-self-check")
    check_cell = next(
        cell for cell in _cells(notebook) if cell["id"] == "student-self-check"
    )
    assert check_cell["metadata"] == {"tags": ["student-self-check"]}
    assert 'deployment_report("Infantry", 100, 3, 500)' in check
    assert '"3 Infantry units: cost $300, remaining $200"' in check
    assert 'deployment_report("Cavalry", 200, 2, 500)' in check
    assert '"2 Cavalry units: cost $400, remaining $100"' in check


def test_lesson_three_materials_cover_required_function_vocabulary() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (KOREAN_NOTEBOOK, ENGLISH_NOTEBOOK, TEACHER_GUIDE)
    )
    for required in (
        "definition",
        "function call",
        "parameter",
        "argument",
        "return value",
        "local variable",
        "total_cost",
        "remaining_budget",
        "can_deploy",
        "deployment_report",
        "Predict",
    ):
        assert required in combined


def test_korean_lesson_three_notebook_is_korean_led() -> None:
    text = KOREAN_NOTEBOOK.read_text(encoding="utf-8")
    hangul_count = sum("가" <= character <= "힣" for character in text)
    assert hangul_count >= 350


def test_teacher_guide_has_timing_error_coaching_and_reference_solution() -> None:
    guide = TEACHER_GUIDE.read_text(encoding="utf-8")
    assert guide.startswith("# Lesson 03 — Functions")
    for time_range in (
        "0–10분",
        "10–22분",
        "22–37분",
        "37–52분",
        "52–62분",
        "62–72분",
        "72–84분",
        "84–88분",
        "88–90분",
    ):
        assert time_range in guide
    assert "Read → Find the function name → Count arguments" in guide
    assert "def deployment_report(unit_name, unit_cost, count, budget):" in guide
    assert "cost = total_cost(unit_cost, count)" in guide
    assert "remaining = remaining_budget(budget, cost)" in guide


def test_readme_links_lesson_three_materials_and_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for path in (
        "lessons/lesson_03_functions.ipynb",
        "lessons/lesson_03_functions_en.ipynb",
        "lessons/lesson_03_curriculum_ko.md",
    ):
        assert f"]({path})" in readme
    assert "Lesson 03: Functions" in readme
    assert "notebook-only" in readme
    assert "Lesson 03 stays in notebooks" in readme
