from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KOREAN_NOTEBOOK = ROOT / "lessons" / "lesson_02_conditionals.ipynb"
ENGLISH_NOTEBOOK = ROOT / "lessons" / "lesson_02_conditionals_en.ipynb"
TEACHER_GUIDE = ROOT / "lessons" / "lesson_02_curriculum_ko.md"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _code_sources(notebook: dict[str, object]) -> list[list[str]]:
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return [cell["source"] for cell in cells if cell["cell_type"] == "code"]


def test_day_two_lesson_artifacts_exist_and_parse() -> None:
    assert _load(KOREAN_NOTEBOOK)["nbformat"] == 4
    assert _load(ENGLISH_NOTEBOOK)["nbformat"] == 4
    assert TEACHER_GUIDE.read_text(encoding="utf-8").startswith(
        "# Lesson 02 — Conditionals"
    )


def test_day_two_notebooks_share_identical_code_cells() -> None:
    assert _code_sources(_load(KOREAN_NOTEBOOK)) == _code_sources(
        _load(ENGLISH_NOTEBOOK)
    )


def test_day_two_materials_cover_rules_and_reset() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (KOREAN_NOTEBOOK, ENGLISH_NOTEBOOK, TEACHER_GUIDE)
    )
    for required in (
        "student_rules.py",
        "machine_gun_damage",
        "cavalry_damage",
        "if",
        "elif",
        "else",
        "Predict",
        "Restore",
    ):
        assert required in combined
