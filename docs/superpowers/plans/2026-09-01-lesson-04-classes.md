# Lesson 04 Classes and Objects Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Create a complete 90-minute bilingual Lesson 04 in which Dawn learns class, object, __init__, self, attributes, methods, and independent object state by authoring a simplified Unit class.

**Architecture:** Keep the lesson notebook-first and pygame-independent. Korean and English notebooks share one exact technical contract; a Korean teacher guide owns the reference answer, coaching sequence, and recovery path, while automated tests execute prepared examples and protect the prompt-only student task.

**Tech Stack:** Jupyter nbformat 4 JSON, Python 3.12, Dawn Tactics pure-Python domain model, pytest.

---

## File Structure

- Create lessons/lesson_04_classes.ipynb: Korean-led student notebook.
- Create lessons/lesson_04_classes_en.ipynb: English student notebook with identical code and metadata.
- Create lessons/lesson_04_curriculum_ko.md: 90-minute Korean teacher guide and reference solution.
- Create tests/test_lesson_04_materials.py: notebook contract, example execution, pedagogy, and README tests.
- Modify README.md: Lesson 04 links, execution instructions, and inheritance boundary.

The user's uncommitted lessons/lesson_03_functions.ipynb is student work. Never edit, normalize, stage, or restore it.

### Task 1: Lock the Lesson 04 notebook contract with failing tests

**Files:**
- Create: tests/test_lesson_04_materials.py

- [ ] **Step 1: Create parsing helpers and the exact cell contract**

Create tests/test_lesson_04_materials.py:

~~~python
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
~~~

- [ ] **Step 2: Add prepared-example execution tests**

Append:

~~~python
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


def test_prepared_examples_execute_and_keep_object_state_independent() -> None:
    namespace = _execute_prepared_examples(_load(ENGLISH_NOTEBOOK))

    first = namespace["first_card"]
    second = namespace["second_card"]
    assert first.objective == "Hold the bridge"
    assert second.objective == "Protect the town"
    assert first.brief() == "Objective: Hold the bridge"

    left_tank = namespace["left_tank"]
    right_tank = namespace["right_tank"]
    assert left_tank.hp == left_tank.max_hp - 3
    assert right_tank.hp == right_tank.max_hp
~~~

- [ ] **Step 3: Add task ownership, vocabulary, and boundary tests**

Append:

~~~python
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
        "class Unit",
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
~~~

- [ ] **Step 4: Add teacher-guide and README contract tests**

Append:

~~~python
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
~~~

- [ ] **Step 5: Run the new material tests and observe RED**

Run:

~~~bash
.venv/bin/python -m pytest tests/test_lesson_04_materials.py -q
~~~

Expected: failures because the two notebooks and teacher guide do not exist and README has no Lesson 04 section.

- [ ] **Step 6: Commit the red contract**

~~~bash
git add tests/test_lesson_04_materials.py
git commit -m "Test Lesson 04 classes materials"
~~~

### Task 2: Build the paired student notebooks

**Files:**
- Create: lessons/lesson_04_classes.ipynb
- Create: lessons/lesson_04_classes_en.ipynb

- [ ] **Step 1: Create the English notebook with the exact 20 cells**

Use nbformat 4, nbformat_minor 5, Python 3 kernelspec, null execution counts, and empty outputs. Use EXPECTED_CELL_IDS in exact order.

The six prepared code cells must be exactly:

function-prerequisite:

~~~python
def mission_label(objective):
    return "Mission: " + objective


label = mission_label("Hold the bridge")
assert label == "Mission: Hold the bridge"
print(label)
~~~

first-class:

~~~python
class MissionCard:
    def __init__(self, objective):
        self.objective = objective

    def brief(self):
        return "Objective: " + self.objective
~~~

first-object:

~~~python
first_card = MissionCard("Hold the bridge")
assert first_card.objective == "Hold the bridge"
print(first_card.objective)
~~~

two-objects:

~~~python
second_card = MissionCard("Protect the town")
original_second_objective = second_card.objective
first_card.objective = "Hold the bridge"

assert first_card.objective == "Hold the bridge"
assert second_card.objective == original_second_objective
print(first_card.objective)
print(second_card.objective)
~~~

method-example:

~~~python
briefing = first_card.brief()
assert briefing == "Objective: Hold the bridge"
print(briefing)
~~~

real-game-bridge:

~~~python
from dawn_tactics import Position, Tank, Team


left_tank = Tank(101, Team.BLUE, Position(9, 4))
right_tank = Tank(102, Team.BLUE, Position(9, 6))

left_tank.take_damage(3)

assert left_tank.hp == left_tank.max_hp - 3
assert right_tank.hp == right_tank.max_hp
print("Left Tank:", left_tank.hp, "Right Tank:", right_tank.hp)
~~~

The student-task cell is exactly the four prompt lines in Task 1 and tagged student-task.

The student-self-check cell is:

~~~python
tank = Unit("Tank", 10)
infantry = Unit("Infantry", 5)

assert tank.name == "Tank"
assert tank.max_hp == 10
assert tank.hp == 10
assert infantry.hp == 5

tank.take_damage(3)
assert tank.hp == 7
assert infantry.hp == 5

tank.take_damage(99)
assert tank.hp == 0
print("Mission complete: two objects kept their own state!")
~~~

Tag it student-self-check.

English Markdown must explicitly label:

- class as blueprint;
- object as one thing made from the blueprint;
- __init__ as setup method;
- self as the receiving object;
- attribute as object state reached by dot notation;
- method as a function belonging to an object;
- independent state as the reason changing one card or tank does not change the other;
- final challenge inputs, required behavior, and success criteria;
- inheritance as a one-sentence next lesson preview only.

- [ ] **Step 2: Create the Korean-led notebook from the same contract**

Copy the exact cell IDs, code cells, tags, code metadata, kernelspec, and language metadata from the English notebook. Translate and expand only Markdown.

Use Korean explanations with English core vocabulary. Include these fixed teaching sentences:

~~~text
A class is a blueprint. An object is one thing made from that blueprint.
self는 지금 이 method call을 받은 object를 가리킨다.
각 object는 자기만의 state를 가진다.
~~~

The Korean Markdown must describe Predict -> Run -> Explain -> Change and must exceed the 450-Hangul-character test without filler.

- [ ] **Step 3: Validate notebook JSON and exact code parity**

Run:

~~~bash
.venv/bin/python -m json.tool lessons/lesson_04_classes.ipynb >/dev/null
.venv/bin/python -m json.tool lessons/lesson_04_classes_en.ipynb >/dev/null
.venv/bin/python -m pytest tests/test_lesson_04_materials.py -q
~~~

Expected: notebook parsing, parity, execution, vocabulary, ownership, and saved-state tests pass; teacher-guide and README tests still fail.

- [ ] **Step 4: Commit the paired notebooks**

~~~bash
git add lessons/lesson_04_classes.ipynb lessons/lesson_04_classes_en.ipynb
git commit -m "Add Lesson 04 classes notebooks"
~~~

### Task 3: Write the 90-minute Korean teacher guide

**Files:**
- Create: lessons/lesson_04_curriculum_ko.md

- [ ] **Step 1: Write overview, outcomes, prerequisites, and setup**

The guide begins with:

~~~markdown
# Lesson 04 — Classes and Objects: 하나의 설계도로 서로 다른 유닛 만들기

## 수업 개요

- 대상: Lesson 01–03을 진행한 학생
- 시간: 90분
- 설명 언어: 한국어
- 코드·핵심 용어: English
- 학생 편집 위치: lessons/lesson_04_classes.ipynb의 student-task cell
- 중심 문장: A class is a blueprint. An object is one thing made from that blueprint.
~~~

List the eight learning outcomes from the design. State that Lesson 03 saved work may stop before return/composition, so the first eight minutes are a prerequisite pulse. If the student cannot explain return, use the prepared recovery sentence and continue:

~~~text
A function can return a value. A method is a function that belongs to an object.
~~~

Preparation includes selecting the project .venv kernel, working in a student-named notebook copy, checking the final task has no answer, and keeping the repository master notebook unchanged.

- [ ] **Step 2: Write every timed teaching block**

Create all ten exact headings:

- 0–8분 — Function prerequisite pulse
- 8–20분 — Blueprint와 object
- 20–34분 — class, __init__, self
- 34–46분 — 두 object와 independent state
- 46–51분 — Movement break
- 51–63분 — Method가 state를 사용하기
- 63–69분 — 실제 Dawn Tactics Tank object
- 69–84분 — Unit class 독립 과제
- 84–88분 — Self-check와 설명
- 88–90분 — Exit ticket과 inheritance 예고

For each block include:

- teacher prompt;
- expected student action;
- one check-for-understanding question;
- what not to explain yet.

In the real-game bridge, explain only that two Tank objects were made from an existing game class and one inherited a take_damage method internally; do not open or teach inheritance syntax.

- [ ] **Step 3: Add coaching, hint ladder, solution, and reset**

Include the exact error routine as one line:

~~~text
Read → Find the class/object name → Check colon and indentation → Count arguments after self → Check every self. prefix → Run again
~~~

Add an error table for NameError, TypeError, AttributeError, IndentationError, and AssertionError.

Use this exact three-level hint ladder:

1. Hint 1 — Circle the two inputs after self and list the three attributes every object must remember.
2. Hint 2 — hp begins with the same value as max_hp; write all three self assignments before the method.
3. Hint 3 — subtract amount from self.hp, then use the previous if lesson to replace a negative value with 0.

Put this reference solution only in the guide:

~~~python
class Unit:
    def __init__(self, name, max_hp):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp

    def take_damage(self, amount):
        self.hp = self.hp - amount
        if self.hp < 0:
            self.hp = 0
~~~

Include a reset checklist that preserves the student's named copy, restores no repository files, confirms master task cells remain prompt-only, closes the kernel, and runs the Lesson 04 plus full tests from a clean checkout.

Explicitly defer inheritance, subclass syntax, super(), overriding, polymorphism, ClassVar, decorators, dataclasses, Enums, type hints, registries, and pygame.

- [ ] **Step 4: Run teacher-guide tests**

Run:

~~~bash
.venv/bin/python -m pytest tests/test_lesson_04_materials.py -q
~~~

Expected: every Lesson 04 test except the README link test passes.

- [ ] **Step 5: Commit the teacher guide**

~~~bash
git add lessons/lesson_04_curriculum_ko.md
git commit -m "Add Lesson 04 classes teacher guide"
~~~

### Task 4: README integration and full lesson verification

**Files:**
- Modify: README.md

- [ ] **Step 1: Add the Lesson 04 section**

After Lesson 03, add:

~~~markdown
## Lesson 04 — Classes and Objects

- Korean-led notebook: lessons/lesson_04_classes.ipynb
- English notebook: lessons/lesson_04_classes_en.ipynb
- Korean 90-minute teacher guide: lessons/lesson_04_curriculum_ko.md

Lesson 04 connects functions to methods and teaches class, object, __init__,
self, instance attributes, and independent object state. Dawn writes a complete
simplified Unit class from its class line and implements take_damage().

Run the notebook with the project .venv kernel. Work in a student-named copy so
the repository notebook keeps its prompt-only final task.

Lesson 05 will introduce inheritance and connect a shared Unit design to
specialized unit subclasses. Lesson 04 does not require subclass or super()
syntax.
~~~

Use clickable Markdown paths matching the README's existing link style rather than leaving bare paths if the surrounding sections use links.

- [ ] **Step 2: Run focused Lesson 04 verification**

~~~bash
.venv/bin/python -m pytest tests/test_lesson_04_materials.py -q
~~~

Expected: all Lesson 04 material tests pass.

- [ ] **Step 3: Inspect notebook state directly**

Run a read-only script or jq query that reports for both notebooks:

- 20 cells;
- exact EXPECTED_CELL_IDS;
- null execution_count for every code cell;
- empty outputs for every code cell;
- identical code signatures;
- student-task and student-self-check tags;
- no class Unit solution in either task cell.

Expected: every reported condition is true.

- [ ] **Step 4: Run complete clean-worktree verification**

~~~bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
git diff --check
~~~

Expected: full suite passes in the clean feature worktree, compileall emits no errors, and git diff --check emits no output.

Do not use the user's main working checkout for the full-suite claim because its saved Lesson 03 answers intentionally break the committed Korean/English code-parity contract.

- [ ] **Step 5: Commit README integration**

~~~bash
git add README.md
git commit -m "Document Lesson 04 classes materials"
~~~
