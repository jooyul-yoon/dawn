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


def _cell_source(notebook: dict[str, object], cell_id: str) -> str:
    cells = notebook["cells"]
    assert isinstance(cells, list)
    cell = next(cell for cell in cells if cell["id"] == cell_id)
    return "".join(cell["source"])


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


def test_preview_cell_reloads_rules_after_student_edits() -> None:
    preview = _cell_source(_load(KOREAN_NOTEBOOK), "preview-rules")
    assert "import importlib" in preview
    assert "rules = importlib.reload(rules)" in preview
    assert "validate_student_rules()" in preview


def test_campaign_one_experiments_use_targets_present_in_campaign_one() -> None:
    korean = KOREAN_NOTEBOOK.read_text(encoding="utf-8")
    english = ENGLISH_NOTEBOOK.read_text(encoding="utf-8")
    guide = TEACHER_GUIDE.read_text(encoding="utf-8")
    assert "Cavalry의 Infantry damage를 `3`에서 `1`" in korean
    assert "Cavalry's Infantry damage from `3` to `1`" in english
    assert "Cavalry의 Infantry damage를 3에서 1" in guide
    assert "Machine Gun의 LIGHT damage를 4에서 0" in guide
    assert "Cavalry의 Artillery damage를 5에서 1" not in guide
    assert "Machine Gun의 HEAVY damage를 1에서 0" not in guide


def test_korean_notebook_is_korean_led() -> None:
    text = KOREAN_NOTEBOOK.read_text(encoding="utf-8")
    hangul_count = sum("가" <= character <= "힣" for character in text)
    assert hangul_count >= 250


def test_readme_links_day_two_student_materials() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "`1`–`6`" in readme
    assert "Machine Gun" in readme
    assert "Cavalry" in readme
    assert "lessons/lesson_02_conditionals.ipynb" in readme
    assert "lessons/lesson_02_conditionals_en.ipynb" in readme
    assert "lessons/lesson_02_curriculum_ko.md" in readme
    assert "src/dawn_tactics/student_rules.py" in readme
    assert "](lessons/lesson_02_conditionals.ipynb)" in readme
    assert "](lessons/lesson_02_conditionals_en.ipynb)" in readme
    assert "](lessons/lesson_02_curriculum_ko.md)" in readme
    assert "](src/dawn_tactics/student_rules.py)" in readme
