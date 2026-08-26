# Lesson 03 Functions Design

## Goal

Create a 90-minute notebook-only Lesson 03 that lets Dawn learn Python
functions through Dawn Tactics planning problems. The lesson follows the
existing sequence:

```text
Lesson 01: Variables -> Lesson 02: Conditionals -> Lesson 03: Functions
```

Dawn will distinguish a function definition from a call, use parameters and
arguments, return reusable values, recognize local scope, compose two small
functions, and finish by writing one complete function from `def` onward.

The lesson does not change the game executable, combat rules, campaigns, unit
stats, or student-editable Lesson 01 and Lesson 02 files.

## Audience and Teaching Style

- Python beginner and elementary-age bilingual learner.
- Teacher explanations are Korean-led.
- Code, identifiers, UI terms, and core vocabulary remain English.
- History and tactics provide motivation without graphic combat descriptions.
- The student types and owns the final function; the teacher guides with
  questions and does not take over the keyboard.
- Every experiment follows `Predict -> Run -> Explain -> Change`.

## Artifacts

Create:

- `lessons/lesson_03_functions.ipynb`: Korean-led bilingual student notebook.
- `lessons/lesson_03_functions_en.ipynb`: English student notebook.
- `lessons/lesson_03_curriculum_ko.md`: Korean teacher guide for one 90-minute
  session.
- `tests/test_lesson_03_materials.py`: structural and executable-example tests.

Modify:

- `README.md`: add Lesson 03 links, purpose, and execution instructions.

The Korean and English notebooks use identical code cells and cell IDs. Only
their Markdown explanations differ. This preserves a single technical lesson
while allowing the learner to switch explanation language.

## Learning Outcomes

By the end of the lesson, Dawn can:

1. point to a function definition and a function call;
2. explain that a parameter is a name in the definition and an argument is a
   value supplied by a call;
3. use `return` to make a result available to later code;
4. demonstrate that `print()` displays a value while `return` hands a value
   back to the caller;
5. identify a local variable as a name that belongs to one function call;
6. pass one function's return value into another function;
7. return a Boolean from a function that reuses the Lesson 02 comparison idea;
8. write `deployment_report()` from its `def` line through its return statement
   and make every provided self-check pass.

## Concept Boundaries

Teach only:

- `def`;
- function name;
- function body and indentation;
- function call;
- parameter;
- argument;
- `return` and return value;
- local variable;
- using one function's result as another function's input;
- a Boolean-returning function as a bridge from Lesson 02.

Do not teach or require:

- `*args` or `**kwargs`;
- keyword-only or positional-only parameters;
- default parameters;
- recursion;
- lambda expressions;
- decorators;
- generators;
- type hints;
- classes, methods, inheritance, or `self`;
- lists, loops, dictionaries, imports, or game source editing.

Those exclusions keep the lesson focused on the function input/output model.

## Notebook Learning Path

The notebooks use a Mission Ladder. Each rung adds one concept and retains the
same Dawn Tactics planning context.

### 1. Call a Prepared Function

Provide and call:

```python
def announce_mission():
    print("Mission ready!")


announce_mission()
```

The learner labels the definition, body, and call before changing the message.
This rung introduces no parameter or return value.

### 2. Write a Parameter-Free Function

Dawn writes this from a short scaffold:

```python
def show_objective():
    print("Keep the deployment inside budget.")
```

The notebook asks the learner to predict what happens if the call is removed.

### 3. Add a Parameter and Supply Arguments

Use:

```python
def unit_report(unit_name):
    print("Selected unit:", unit_name)


unit_report("Tank")
unit_report("Cavalry")
```

The learner identifies `unit_name` as the parameter and the two strings as
arguments, then adds a third call without copying the function body.

### 4. Return a Calculated Value

Use:

```python
def total_cost(unit_cost, count):
    return unit_cost * count


cost = total_cost(100, 3)
assert cost == 300
```

Contrast it with a provided display-only function:

```python
def print_total(unit_cost, count):
    print(unit_cost * count)
```

The explanation is explicit: `print()` shows something to a person; `return`
gives a value back to the calling code. The lesson does not imply that one is
always preferable.

### 5. Use a Local Variable

Use:

```python
def remaining_budget(budget, cost):
    remaining = budget - cost
    return remaining


assert remaining_budget(500, 300) == 200
```

After the successful call, a provided `try/except NameError` safety wrapper
attempts to read `remaining` outside the function and prints the error name.
The learner is told that the wrapper is a safety net supplied by the notebook;
exception syntax is not a Lesson 03 objective.

### 6. Connect Function Outputs and Inputs

Use the previously defined functions without duplicating their calculations:

```python
cost = total_cost(250, 3)
money_left = remaining_budget(1000, cost)
assert cost == 750
assert money_left == 250
```

The notebook includes an input/output trace table that Dawn completes before
running the cell.

### 7. Return a Boolean

Review the previous lesson through:

```python
def can_deploy(budget, cost):
    return budget >= cost


assert can_deploy(500, 400) is True
assert can_deploy(300, 400) is False
```

This is a function lesson, not another branching lesson. It reuses a Boolean
comparison but does not add an `if` statement because the comparison already
produces the value the function should return.

### 8. Final Independent Challenge

The student notebook supplies this signature and docstring but no completed
body:

```python
def deployment_report(unit_name, unit_cost, count, budget):
    """Return one deployment cost and budget report."""
    # Write the function body here.
    pass
```

The required behavior is:

```python
deployment_report("Infantry", 100, 3, 500)
# "3 Infantry units: cost $300, remaining $200"
```

The student must call `total_cost()` and `remaining_budget()` inside the new
function, store their results in local variables, and return this exact f-string
shape:

```text
{count} {unit_name} units: cost ${cost}, remaining ${remaining}
```

The self-check cell is tagged `student-self-check` and contains:

```python
assert deployment_report("Infantry", 100, 3, 500) == (
    "3 Infantry units: cost $300, remaining $200"
)
assert deployment_report("Cavalry", 200, 2, 500) == (
    "2 Cavalry units: cost $400, remaining $100"
)
print("Mission complete: your function passed every check!")
```

The incomplete function cell is tagged `student-task`. It intentionally fails
the following self-check until the learner implements it. Automated lesson
tests execute every completed example before this cell, then inspect rather
than execute the student task and self-check cells.

The teacher guide contains the exact reference solution:

```python
def deployment_report(unit_name, unit_cost, count, budget):
    cost = total_cost(unit_cost, count)
    remaining = remaining_budget(budget, cost)
    return (
        f"{count} {unit_name} units: "
        f"cost ${cost}, remaining ${remaining}"
    )
```

The complete solution must not appear in either student notebook.

## Notebook Structure

Both notebooks use the following stable cell IDs:

```text
title
mission-brief
learning-goals
function-map
call-predict
call-example
definition-challenge
definition-check
parameter-map
parameter-example
argument-challenge
return-predict
return-example
print-versus-return
local-variable-map
local-variable-example
local-scope-safety-net
compose-trace
compose-example
boolean-bridge
final-brief
student-task
student-self-check
exit-ticket
teacher-next-step
```

Code cells have no saved execution count or output. Notebook metadata uses the
project Python kernel convention and `nbformat` 4.

## Error Learning

The lesson covers four common symptoms without expanding into exception
handling as a topic:

| Symptom | Student's first check |
|---|---|
| `NameError` | Was the function defined before the call? Is the name local? |
| `TypeError` | Does the call supply one argument for every parameter? |
| `IndentationError` | Is every function-body line indented four spaces? |
| `AssertionError` | What value was returned, and what value did the check expect? |

The teacher routine is:

```text
Read -> Find the function name -> Count arguments -> Check indentation -> Run again
```

Errors are treated as evidence. The teacher asks Dawn to point to the function
name and inputs before showing a correction.

## Teacher Guide Timing

The Korean teacher guide uses this 90-minute structure:

- 0–10: review variables and the Lesson 02 “rule box” metaphor;
- 10–22: definition, body, and call;
- 22–37: parameter and argument;
- 37–52: `return` versus `print`;
- 52–62: local variable and the safe `NameError` observation;
- 62–72: composing `total_cost()` and `remaining_budget()`;
- 72–84: independent `deployment_report()` challenge;
- 84–88: explain the finished function using input/process/output;
- 88–90: exit ticket and preview of classes/methods.

The guide includes prompts, expected responses, hints in three levels, the
reference solution, the error table, extension questions for early finishers,
and a reset checklist. Extensions alter arguments or report wording; they do
not introduce excluded function features.

## Testing

Create `tests/test_lesson_03_materials.py` to prove:

1. both notebooks parse as `nbformat == 4` and the teacher guide exists;
2. Korean and English notebooks contain the exact stable cell-ID sequence;
3. both notebooks have identical code-cell sources and metadata tags;
4. the Korean notebook is Korean-led by a minimum Hangul-character threshold;
5. required terms and function names appear across the materials;
6. examples before `student-task` execute sequentially in an isolated namespace;
7. `total_cost`, `remaining_budget`, and `can_deploy` return the documented
   values after example execution;
8. `student-task` contains the signature, docstring, comment, and `pass`, but
   not the reference solution's two function calls or f-string;
9. `student-self-check` contains both exact assertions and its required tag;
10. the teacher guide contains the exact reference solution and 90-minute
    progression;
11. README links all three Lesson 03 artifacts;
12. the full existing game and lesson suite still passes.

Tests do not execute the deliberately incomplete student task or its self-check.
They do not require Jupyter to be running.

## README Changes

Add a `Lesson 03: Functions` section after Lesson 02. It states that this is a
notebook-only lesson, links the Korean notebook, English notebook, and Korean
teacher guide, and lists the core vocabulary: definition, call, parameter,
argument, return value, and local variable.

Update the teaching boundary to say:

- Lesson 01 edits `student_settings.py`;
- Lesson 02 edits `student_rules.py`;
- Lesson 03 stays in notebooks while the learner creates functions from
  scratch;
- later lessons move into `domain.py` for methods, classes, and inheritance.

## Scope Boundaries

Do not modify:

- `src/dawn_tactics/` production code;
- `student_settings.py`, `student_rules.py`, or their validators;
- campaigns, budgets, unit stats, unit images, or gameplay;
- Lesson 01 or Lesson 02 notebooks and teacher guides;
- launch scripts or dependencies.

Do not restore or apply the unrelated preserved stash created during the
battlefield work.

## Success Criteria

The work is complete when the bilingual notebooks and Korean teacher guide form
one coherent 90-minute function lesson, all completed notebook examples execute
in order, Dawn must genuinely write the final function body, the self-checks
give immediate feedback, the reference answer appears only in the teacher
guide, README exposes the materials, production game code is unchanged, and the
entire test suite passes.
