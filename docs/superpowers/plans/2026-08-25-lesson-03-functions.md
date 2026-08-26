# Lesson 03 Functions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bilingual notebook-only Lesson 03 materials that teach function definitions, calls, parameters, arguments, return values, local variables, composition, and a final student-authored `deployment_report()` function.

**Architecture:** Two Jupyter notebooks share identical code cells and stable cell IDs while using Korean-led and English Markdown explanations. A Korean teacher guide owns timing, hints, error coaching, and the reference solution; a dedicated pytest module parses notebooks, executes every completed example before the final student task, prevents solution leakage, and verifies README routing. Production game code remains untouched.

**Tech Stack:** Python 3.12, Jupyter Notebook JSON (`nbformat` 4), Markdown, pytest

---

## File Map

- Create `lessons/lesson_03_functions.ipynb`: Korean-led student notebook.
- Create `lessons/lesson_03_functions_en.ipynb`: English student notebook with identical code cells.
- Create `lessons/lesson_03_curriculum_ko.md`: 90-minute Korean teacher guide and reference solution.
- Create `tests/test_lesson_03_materials.py`: artifact, notebook, execution, ownership, guide, and README tests.
- Modify `README.md`: link Lesson 03 and update the teaching boundary.
- Inspect but do not modify `src/dawn_tactics/`, Lesson 01/02 artifacts, launchers, dependencies, or `stash@{0}`.

## Canonical Notebook Contract

Both notebooks use this exact cell-ID order:

```python
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
```

Use these exact code-cell sources in both notebooks:

```python
CODE_BY_ID = {
    "call-example": '''def announce_mission():
    print("Mission ready!")


announce_mission()
''',
    "definition-check": '''# Type show_objective() from its def line, then call it.
# It should print: Keep the deployment inside budget.
''',
    "parameter-example": '''def unit_report(unit_name):
    print("Selected unit:", unit_name)


unit_report("Tank")
unit_report("Cavalry")
''',
    "argument-challenge": '''# Add one more unit_report() call with "Artillery" as the argument.
''',
    "return-example": '''def total_cost(unit_cost, count):
    return unit_cost * count


cost = total_cost(100, 3)
assert cost == 300
print("Total cost:", cost)
''',
    "print-versus-return": '''def print_total(unit_cost, count):
    print(unit_cost * count)


displayed = print_total(100, 3)
returned = total_cost(100, 3)
assert displayed is None
assert returned == 300
print("print_total returned:", displayed)
print("total_cost returned:", returned)
''',
    "local-variable-example": '''def remaining_budget(budget, cost):
    remaining = budget - cost
    return remaining


assert remaining_budget(500, 300) == 200
''',
    "local-scope-safety-net": '''try:
    print(remaining)
except NameError as error:
    print("Safety net caught:", type(error).__name__)
else:
    raise AssertionError("remaining should stay local to the function")
''',
    "compose-example": '''cost = total_cost(250, 3)
money_left = remaining_budget(1000, cost)
assert cost == 750
assert money_left == 250
print("Cost:", cost, "Remaining:", money_left)
''',
    "boolean-bridge": '''def can_deploy(budget, cost):
    return budget >= cost


assert can_deploy(500, 400) is True
assert can_deploy(300, 400) is False
''',
    "student-task": '''# Write deployment_report() from its def line.
# Parameters: unit_name, unit_cost, count, budget
# Return the exact deployment report described above.
''',
    "student-self-check": '''assert deployment_report("Infantry", 100, 3, 500) == (
    "3 Infantry units: cost $300, remaining $200"
)
assert deployment_report("Cavalry", 200, 2, 500) == (
    "2 Cavalry units: cost $400, remaining $100"
)
print("Mission complete: your function passed every check!")
''',
}
```

Only `student-task` has metadata `{"tags": ["student-task"]}` and only
`student-self-check` has metadata `{"tags": ["student-self-check"]}`. Other
cells use `{}` metadata. All code cells use `execution_count: null` and
`outputs: []`.

Notebook top-level metadata is:

```json
{
  "kernelspec": {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3"
  },
  "language_info": {"name": "python", "version": "3.12"}
}
```

### Task 1: Add notebook contract tests first

**Files:**
- Create: `tests/test_lesson_03_materials.py`

- [ ] **Step 1: Create parsing helpers and failing artifact tests**

Create the test module with these imports, paths, helpers, and cell contract:

```python
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
```

- [ ] **Step 2: Add executable-example and student-ownership tests**

Append:

```python
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
```

- [ ] **Step 3: Add language, guide, and README routing tests**

Append:

```python
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
```

- [ ] **Step 4: Run notebook tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_lesson_03_materials.py -q
```

Expected: failures begin with `FileNotFoundError` for
`lessons/lesson_03_functions.ipynb`; no Lesson 03 artifact exists yet.

### Task 2: Create the two student notebooks

**Files:**
- Create: `lessons/lesson_03_functions.ipynb`
- Create: `lessons/lesson_03_functions_en.ipynb`
- Test: `tests/test_lesson_03_materials.py`

- [ ] **Step 1: Create the Korean-led notebook JSON**

Use `nbformat: 4`, `nbformat_minor: 5`, the canonical metadata, IDs, code, and
tags above. Use these exact Markdown headings and required content:

| Cell ID | Korean-led Markdown content |
|---|---|
| `title` | `# Lesson 03 — Functions: 작전을 재사용 가능한 명령으로 만들기` |
| `mission-brief` | Dawn is the mission planner; function is a reusable mission card; follow `Predict → Run → Explain → Change`. |
| `learning-goals` | List definition/call, parameter/argument, print/return, local variable, composition, and writing `deployment_report()` from `def`. |
| `function-map` | Label `def announce_mission():`, indented body, and `announce_mission()` call; define **definition** and **function call** in Korean. |
| `call-predict` | Ask what prints, how often, and what happens if the call is removed. |
| `definition-challenge` | Tell Dawn to type `show_objective()` from its `def` line and print `Keep the deployment inside budget.` |
| `parameter-map` | Define parameter as the input name and argument as the supplied value; point to `unit_name` and `"Tank"`. |
| `return-predict` | Predict `total_cost(100, 3)` before running and introduce **return value**. |
| `local-variable-map` | Define `remaining` as a **local variable** and explain that it exists only inside the function call. |
| `compose-trace` | Provide an empty input/process/output table for `total_cost(250, 3)` then `remaining_budget(1000, cost)`. |
| `final-brief` | Require exact signature, use of both earlier functions, two local variables, and exact return shape; explicitly say no answer is prefilled. |
| `exit-ticket` | Ask five questions covering definition vs call, parameter vs argument, print vs return, local scope, and tracing the final function. |
| `teacher-next-step` | Preview methods: a method is a function belonging to an object; do not teach `self` yet. |

The Korean prose must include at least 350 Hangul characters overall. Keep the
English vocabulary exactly as spelled in the contract tests.

- [ ] **Step 2: Create the English notebook JSON**

Copy the Korean notebook's structure, top-level metadata, every code cell,
code-cell metadata, and IDs exactly. Translate only Markdown cells using these
headings and messages:

| Cell ID | English Markdown content |
|---|---|
| `title` | `# Lesson 03 — Functions: Turn a plan into a reusable command` |
| `mission-brief` | Dawn is the mission planner; use `Predict → Run → Explain → Change`. |
| `learning-goals` | The same six outcomes as the Korean notebook. |
| `function-map` | Define **definition**, indented body, and **function call**. |
| `call-predict` | The same three prediction questions. |
| `definition-challenge` | Type `show_objective()` from its `def` line and call it. |
| `parameter-map` | Define **parameter** and **argument** using `unit_name` and `"Tank"`. |
| `return-predict` | Predict `total_cost(100, 3)` and define **return value**. |
| `local-variable-map` | Define **local variable** with `remaining`. |
| `compose-trace` | The identical blank input/process/output trace. |
| `final-brief` | The identical signature, function-use, local-variable, and output requirements without the answer. |
| `exit-ticket` | The same five questions in English. |
| `teacher-next-step` | Preview a method as a function belonging to an object. |

- [ ] **Step 3: Run notebook-focused tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_lesson_03_materials.py::test_lesson_three_notebooks_exist_and_parse \
  tests/test_lesson_03_materials.py::test_lesson_three_notebooks_share_cell_contract_and_code \
  tests/test_lesson_03_materials.py::test_completed_examples_execute_and_return_documented_values \
  tests/test_lesson_03_materials.py::test_final_task_requires_student_to_write_from_def \
  tests/test_lesson_03_materials.py::test_final_self_check_has_exact_examples_and_tag \
  tests/test_lesson_03_materials.py::test_korean_lesson_three_notebook_is_korean_led -q
```

Expected: 6 passed. Output printed by executed examples is captured by pytest.

- [ ] **Step 4: Commit the student notebooks and their passing contract tests**

Run:

```bash
git add lessons/lesson_03_functions.ipynb lessons/lesson_03_functions_en.ipynb tests/test_lesson_03_materials.py
git diff --cached --check
git commit -m "Add Lesson 03 functions notebooks"
```

### Task 3: Create the Korean 90-minute teacher guide

**Files:**
- Create: `lessons/lesson_03_curriculum_ko.md`
- Test: `tests/test_lesson_03_materials.py`

- [ ] **Step 1: Verify the guide tests are RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_lesson_03_materials.py::test_lesson_three_materials_cover_required_function_vocabulary \
  tests/test_lesson_03_materials.py::test_teacher_guide_has_timing_error_coaching_and_reference_solution -q
```

Expected: both fail because `lessons/lesson_03_curriculum_ko.md` is absent.

- [ ] **Step 2: Write the guide with exact sections and examples**

Create a Korean-led guide beginning:

```markdown
# Lesson 03 — Functions: 입력을 받아 결과를 돌려주는 작전 상자

## 수업 개요

- 대상: Lesson 01 Variables와 Lesson 02 Conditionals를 마친 학생
- 시간: 90분
- 설명 언어: 한국어
- 코드·핵심 용어: 영어
- 학생 편집 위치: `lessons/lesson_03_functions.ipynb`
- 게임 코드 변경: 없음
- 중심 문장: A function takes input, does one job, and returns a result.
```

Include the eight learning outcomes from the design, setup instructions for the
project `.venv` kernel, and the exact timing sections:

```markdown
### 0–10분 — Variable과 rule box 복습
### 10–22분 — Definition, body, call
### 22–37분 — Parameter와 argument
### 37–52분 — print와 return
### 52–62분 — Local variable과 scope
### 62–72분 — Function 두 개 연결하기
### 72–84분 — deployment_report 독립 과제
### 84–88분 — Input → Process → Output 설명하기
### 88–90분 — Exit ticket과 method 예고
```

For each timing section include one teacher prompt, one expected student action,
and one check-for-understanding question. Include this exact hint ladder:

```markdown
## 독립 과제 Hint ladder

1. Hint 1 — 네 parameter 이름과 필요한 return 문장을 다시 읽는다.
2. Hint 2 — 먼저 `cost = total_cost(unit_cost, count)`를 작성한다.
3. Hint 3 — `remaining = remaining_budget(budget, cost)` 다음 두 f-string을 이어 return한다.
```

Include this exact error routine and table:

```markdown
> Read → Find the function name → Count arguments → Check indentation → Run again

| 오류 | 먼저 확인할 것 |
|---|---|
| `NameError` | definition이 call보다 먼저 있는가? local name을 밖에서 썼는가? |
| `TypeError` | parameter 수와 argument 수가 같은가? |
| `IndentationError` | function body가 네 칸 들여쓰기 되었는가? |
| `AssertionError` | 실제 return value와 expected value가 무엇인가? |
```

Include the exact reference answer only in the guide:

```python
def deployment_report(unit_name, unit_cost, count, budget):
    cost = total_cost(unit_cost, count)
    remaining = remaining_budget(budget, cost)
    return (
        f"{count} {unit_name} units: "
        f"cost ${cost}, remaining ${remaining}"
    )
```

End with a reset checklist confirming the student task is saved in the
student's notebook copy, the repository master notebooks retain prompt-only
cells, and no game file was edited. Early-finisher extensions may change
arguments or report wording only.

- [ ] **Step 3: Run all Lesson 03 tests that no longer depend on README**

Run:

```bash
.venv/bin/python -m pytest tests/test_lesson_03_materials.py -q \
  -k "not readme"
```

Expected: every selected Lesson 03 test passes.

- [ ] **Step 4: Commit the teacher guide**

Run:

```bash
git add lessons/lesson_03_curriculum_ko.md
git diff --cached --check
git commit -m "Add Lesson 03 functions teacher guide"
```

### Task 4: Route Lesson 03 from README

**Files:**
- Modify: `README.md:95-130`
- Test: `tests/test_lesson_03_materials.py`

- [ ] **Step 1: Verify the README test is RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_lesson_03_materials.py::test_readme_links_lesson_three_materials_and_boundary -q
```

Expected: failure because README has no `Lesson 03: Functions` heading or links.

- [ ] **Step 2: Add the Lesson 03 section after Lesson 02**

Insert:

```markdown
## Lesson 03: Functions

Lesson 03 is a notebook-only mission-planning lesson. Dawn defines and calls
small functions, supplies parameters and arguments, compares `print` with a
return value, uses a local variable, connects function outputs and inputs, and
writes `deployment_report()` from its `def` line.

- [Korean/bilingual student notebook](lessons/lesson_03_functions.ipynb)
- [English student notebook](lessons/lesson_03_functions_en.ipynb)
- [Korean teacher guide](lessons/lesson_03_curriculum_ko.md)

The core vocabulary is definition, function call, parameter, argument, return
value, and local variable. This lesson does not edit or rebalance the game.
```

Replace the Teaching Boundary paragraph with:

```markdown
In Lesson 01 students edit `student_settings.py`; in Lesson 02 they edit
`student_rules.py`. Lesson 03 stays in notebooks while students create
functions from scratch without changing the game. Later OOP lessons move into
`domain.py`, where the `Unit` base class and six subclasses expose state,
methods, inheritance, and overridden damage rules.
```

- [ ] **Step 3: Verify the README test is GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_lesson_03_materials.py::test_readme_links_lesson_three_materials_and_boundary -q
```

Expected: 1 passed.

- [ ] **Step 4: Commit README routing**

Run:

```bash
git add README.md
git diff --cached --check
git commit -m "Document Lesson 03 functions materials"
```

### Task 5: Verify lesson execution, scope, and full regression

**Files:**
- Verify: all Lesson 03 artifacts, tests, and repository source

- [ ] **Step 1: Validate both notebook JSON files and code equality directly**

Run:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path

paths = (
    Path("lessons/lesson_03_functions.ipynb"),
    Path("lessons/lesson_03_functions_en.ipynb"),
)
notebooks = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
assert all(notebook["nbformat"] == 4 for notebook in notebooks)
code = [
    [(cell["id"], cell["source"], cell["metadata"])
     for cell in notebook["cells"] if cell["cell_type"] == "code"]
    for notebook in notebooks
]
assert code[0] == code[1]
print(len(notebooks[0]["cells"]), "cells; bilingual code matches")
PY
```

Expected: `25 cells; bilingual code matches`.

- [ ] **Step 2: Run Lesson 03 tests and the complete suite**

Run:

```bash
.venv/bin/python -m pytest tests/test_lesson_03_materials.py -q
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
```

Expected: Lesson 03 tests pass, the complete suite passes, and compilation
exits 0.

- [ ] **Step 3: Audit that production and earlier lessons did not change**

Run:

```bash
git diff 021220b..HEAD -- \
  src/dawn_tactics \
  lessons/lesson_01_curriculum_ko.md \
  lessons/lesson_01_variables.ipynb \
  lessons/lesson_01_variables_en.ipynb \
  lessons/lesson_02_curriculum_ko.md \
  lessons/lesson_02_conditionals.ipynb \
  lessons/lesson_02_conditionals_en.ipynb \
  pyproject.toml \
  RUN_GAME_MAC.command \
  RUN_GAME_WINDOWS.bat
git status -sb
git stash list --max-count=1
```

Expected: the scoped diff command has no output; the worktree is clean; the
unrelated preserved battlefield-document stash remains present and unapplied.

- [ ] **Step 4: Final content review**

Open both notebooks in Jupyter or VS Code and verify:

- Markdown renders cleanly with no raw JSON artifacts;
- Korean is the leading explanation language in the Korean notebook;
- both notebooks have identical runnable code cells;
- the final student task contains only three prompt comments;
- the final self-check follows immediately after the task;
- the guide's answer does not appear in either student notebook;
- all cell outputs and execution counts are empty in committed notebooks.

If rendering reveals a content problem, change only the affected Markdown or
cell source, add a focused assertion to `tests/test_lesson_03_materials.py`,
rerun that assertion and the full Lesson 03 test module, then commit the fix.

- [ ] **Step 5: Final verification immediately before completion**

Run:

```bash
git diff --check
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
git log --oneline -6
git status -sb
```

Expected: all checks exit 0, all tests pass, implementation commits are visible,
and the branch is clean.
