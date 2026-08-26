# Lesson 03 — Functions: 입력을 받아 결과를 돌려주는 작전 상자

## 수업 개요

- 대상: Lesson 01 Variables와 Lesson 02 Conditionals를 마친 학생
- 시간: 90분
- 설명 언어: 한국어
- 코드·핵심 용어: 영어
- 학생 편집 위치: `lessons/lesson_03_functions.ipynb`
- 영어 참고 노트북: `lessons/lesson_03_functions_en.ipynb`
- 게임 코드 변경: 없음
- 중심 문장: A function takes input, does one job, and returns a result.

이번 수업은 게임 코드를 편집하지 않는 notebook-only 수업이다. 새벽이는
Dawn Tactics의 예산과 배치 문제를 사용하지만, 실제 캠페인 규칙이나 유닛
수치를 변경하지 않는다. 목표는 function을 외워 쓰는 것이 아니라 input이
들어와 한 가지 process를 거쳐 output이 나오는 흐름을 말과 코드로 연결하는
것이다.

## 학습 목표와 성공 기준

수업이 끝날 때 학생이 다음을 할 수 있으면 성공이다.

1. function definition과 function call을 가리켜 구분한다.
2. parameter는 definition의 input name, argument는 call에 넣는 실제 value라고
   설명한다.
3. `return`이 만든 return value를 variable에 저장한다.
4. `print()`는 사람에게 보여 주고 `return`은 calling code에 값을 준다는
   차이를 실행 결과로 설명한다.
5. local variable이 function body 안에 속한다는 점을 확인한다.
6. `total_cost()`의 output을 `remaining_budget()`의 input으로 연결한다.
7. `can_deploy()`가 `True` 또는 `False`를 return하는 이유를 설명한다.
8. `deployment_report()`를 `def`부터 직접 작성하고 두 self-check를 통과한다.

`*args`, default parameter, recursion, lambda, type hint, class, method 문법은
다루지 않는다. 마지막 2분에 method가 “object에 속한 function”이라는 다음
수업 예고만 한다.

## 수업 전 준비

1. 프로젝트 폴더에서 `.venv`가 준비되어 있는지 확인한다.
2. VS Code에 Python과 Jupyter 확장을 설치한다.
3. 한국어 노트북을 열고 kernel로 프로젝트의 `.venv` Python을 선택한다.
4. 원본 노트북 대신 학생 이름을 붙인 복사본에서 작업한다.
5. `student-task` 셀에 정답 코드가 미리 들어 있지 않은지 확인한다.
6. 다음 명령으로 기존 테스트가 통과하는지 확인한다.

```bash
python -m pytest
```

코드 셀은 위에서 아래로 실행한다. 이전 cell을 실행하지 않아 function name이
없어지는 일을 줄이기 위해 수업 시작 전 kernel을 restart하고 첫 cell부터
순서대로 실행한다.

## 수업 공통 루틴

각 code cell에서 다음 네 단계를 지킨다.

> Predict → Run → Explain → Change

- Predict: 실행 전에 output이나 return value를 말한다.
- Run: 한 번 실행하고 출력 또는 오류를 끝까지 읽는다.
- Explain: input, process, output을 손가락으로 가리키며 설명한다.
- Change: argument나 한 줄만 바꾸고 다시 예측한다.

교사는 학생이 타이핑할 시간을 기다린다. 문법 오류가 생겨도 키보드를 대신
잡지 않고 function name, argument 수, indentation을 차례로 질문한다.

## 90분 진행안

### 0–10분 — Variable과 rule box 복습

Lesson 01의 variable과 Lesson 02의 rule box를 짧게 연결한다. 종이에
`budget = 500`, `cost = 300`을 적고 “이 계산을 세 번 해야 한다면 매번 다시
쓸까, 이름 붙은 작전 카드로 만들까?”라고 묻는다.

- 교사 prompt: “Function이 받는 것과 돌려주는 것을 상자 그림으로 그리면?”
- 예상 학생 행동: 왼쪽에 input, 가운데 process, 오른쪽에 output을 그린다.
- 확인 질문: “Variable 하나와 function 하나는 어떤 점이 다른가?”

정답 용어를 먼저 요구하지 않는다. “값을 기억하는 이름”과 “일을 기억하는
이름”의 차이를 학생 문장으로 듣는다.

### 10–22분 — Definition, body, call

`announce_mission()` 예제를 읽는다. Definition을 실행하면 Python이 function을
기억하고, call이 있을 때 body가 실행된다는 순서를 몸동작으로 표현한다.

- 교사 prompt: “어느 줄이 작전 카드를 만들고, 어느 줄이 카드를 사용하지?”
- 예상 학생 행동: `def` 줄, 들여쓴 body, 마지막 function call을 가리킨다.
- 확인 질문: “Call을 두 번 쓰면 output은 몇 번 나올까?”

이후 `definition-check` 셀에서 새벽이가 다음 function을 `def`부터 입력한다.

```python
def show_objective():
    print("Keep the deployment inside budget.")


show_objective()
```

교사는 `def`를 입력해 주지 않는다. 학생이 네 칸 들여쓰기를 직접 만든다.

### 22–37분 — Parameter와 argument

`unit_report(unit_name)`에서 `unit_name`에 parameter 이름표를 붙이고,
`"Tank"`와 `"Cavalry"`에 argument value 카드를 놓는다.

- 교사 prompt: “같은 body가 Tank와 Cavalry를 모두 말할 수 있는 이유는?”
- 예상 학생 행동: argument가 parameter 자리에 들어간다고 설명한다.
- 확인 질문: “`unit_report("Artillery")`에서 parameter와 argument는 각각?”

학생은 `argument-challenge` 셀에 Artillery call을 추가한다. Function body를
복사하려 하면 argument만 바꾸어 재사용하는 것이 이번 단계의 목적임을
상기시킨다.

### 37–52분 — print와 return

`total_cost(100, 3)`의 결과를 종이로 먼저 계산한 뒤 셀을 실행한다. 이어서
`print_total()`과 `total_cost()`의 결과를 비교한다.

- 교사 prompt: “화면에 300이 보이는 것과 variable에 300을 저장할 수 있는
  것은 같은 일일까?”
- 예상 학생 행동: `displayed is None`, `returned == 300` 결과를 비교한다.
- 확인 질문: “다음 계산에 사용하려면 어떤 function의 결과가 필요한가?”

수업 표현은 다음과 같이 고정한다.

> `print()` shows a value to a person. `return` gives a value back to the caller.

`print`가 나쁘거나 `return`이 항상 더 좋다고 설명하지 않는다. 두 도구의
목적이 다르다는 점만 확인한다.

### 52–62분 — Local variable과 scope

`remaining_budget()` 안의 `remaining`을 function 내부 메모라고 설명한다.
Function call이 끝난 뒤 바깥에서 같은 local name을 읽으면 제공된 safety net이
`NameError`를 보여준다.

- 교사 prompt: “`remaining`은 누구의 메모인가?”
- 예상 학생 행동: `remaining_budget()` 안에서 만들어진 local variable이라고
  답한다.
- 확인 질문: “Return하지 않았다면 calling code가 계산 결과를 받을 수 있을까?”

`try/except`는 교사가 제공한 안전장치다. Exception handling 문법을 설명하는
새 수업으로 확장하지 않는다.

### 62–72분 — Function 두 개 연결하기

학생은 `compose-trace` 표의 빈칸을 먼저 채운다.

1. `total_cost(250, 3)` → 750
2. `remaining_budget(1000, 750)` → 250

- 교사 prompt: “첫 function의 output이 두 번째 function에서 무엇이 되지?”
- 예상 학생 행동: return value 750이 다음 call의 argument `cost`가 된다고
  설명한다.
- 확인 질문: “곱셈과 뺄셈을 다시 쓰지 않아도 되는 이유는?”

`can_deploy()`는 Lesson 02와 연결한다. `budget >= cost` 비교식 자체가 Boolean을
만들기 때문에 별도의 `if` 없이 그 값을 return할 수 있음을 확인한다.

### 72–84분 — deployment_report 독립 과제

학생은 final brief를 읽고 input 네 개, process 두 개, output 한 개를 종이에
그린다. 이후 prompt-only cell에서 `def deployment_report(...)`부터 직접 쓴다.

- 교사 prompt: “첫 줄을 쓰기 전에 parameter 네 개를 순서대로 말해 볼까?”
- 예상 학생 행동: signature, 두 local variable, 두 function call, return을
  스스로 작성한다.
- 확인 질문: “Self-check가 print 화면이 아니라 return value를 검사하는 이유는?”

교사는 바로 정답을 보여 주지 않고 아래 Hint ladder를 순서대로 사용한다.

## 독립 과제 Hint ladder

1. Hint 1 — 네 parameter 이름과 필요한 return 문장을 다시 읽는다.
2. Hint 2 — 먼저 `cost = total_cost(unit_cost, count)`를 작성한다.
3. Hint 3 — `remaining = remaining_budget(budget, cost)` 다음 두 f-string을 이어 return한다.

두 assert가 모두 통과하면 argument 하나만 바꾸어 새 보고서를 만들어 본다.

### 84–88분 — Input → Process → Output 설명하기

완성한 code를 숨기지 않고 한 줄씩 설명하게 한다.

- 교사 prompt: “이 function의 input, process, output을 네 코드에서 가리켜 줘.”
- 예상 학생 행동: parameter 네 개, 두 call, return string을 가리킨다.
- 확인 질문: “`count`가 3에서 4로 바뀌면 어느 줄을 고치지 않아도 되는가?”

학생의 표현이 정확한 전문 용어가 아니어도 데이터 흐름을 설명하면 이해로
본다. 이후 parameter/argument 용어로 문장을 한 번만 다듬는다.

### 88–90분 — Exit ticket과 method 예고

노트북의 다섯 질문 중 두 개는 말로, 세 개는 짧게 적는다. 다음 수업은
method가 object에 속한 function이라는 연결만 예고한다. `self`나 class 문법은
설명하지 않는다.

- 교사 prompt: “오늘 만든 function이 실제 Unit object에 속하면 무엇이라고
  부를까?”
- 예상 학생 행동: method라는 다음 용어를 듣고 function과 연결한다.
- 확인 질문: “오늘 가장 중요한 input → output 예시는 무엇이었나?”

## 오류를 다루는 순서

> Read → Find the function name → Count arguments → Check indentation → Run again

| 오류 | 먼저 확인할 것 |
|---|---|
| `NameError` | definition이 call보다 먼저 있는가? local name을 밖에서 썼는가? |
| `TypeError` | parameter 수와 argument 수가 같은가? |
| `IndentationError` | function body가 네 칸 들여쓰기 되었는가? |
| `AssertionError` | 실제 return value와 expected value가 무엇인가? |

오류 문장을 가리지 않는다. 학생이 error type과 function name을 먼저 찾은 뒤
한 번에 한 줄만 바꾸게 한다.

## 교사용 reference solution

이 답은 교사용 수업안에만 둔다. 학생 노트북에 미리 붙여 넣지 않는다.

```python
def deployment_report(unit_name, unit_cost, count, budget):
    cost = total_cost(unit_cost, count)
    remaining = remaining_budget(budget, cost)
    return (
        f"{count} {unit_name} units: "
        f"cost ${cost}, remaining ${remaining}"
    )
```

Expected return values:

```text
3 Infantry units: cost $300, remaining $200
2 Cavalry units: cost $400, remaining $100
```

## 빠른 학생을 위한 extension

아래 중 하나만 선택한다.

- Infantry count argument를 4로 바꾸고 output을 먼저 예측한다.
- unit name을 `Machine Gun`으로 바꾸고 띄어쓰기가 string에 유지되는지 본다.
- 보고 문장의 `remaining`을 `money left`로 바꾸되 계산 function은 그대로 둔다.

Default parameter, list, loop, recursion, lambda는 추가하지 않는다.

## Exit ticket 평가 기준

- Definition과 call을 “만들기/사용하기”로 구분하면 충족한다.
- Parameter와 argument를 name/value로 연결하면 충족한다.
- `print`와 `return`의 받는 대상을 구분하면 충족한다.
- Local variable이 function 내부에 속한다고 말하면 충족한다.
- Final function의 두 intermediate value 흐름을 설명하면 충족한다.

## 수업 후 reset checklist

1. 학생이 완성한 답은 학생 이름이 붙은 notebook copy에 저장한다.
2. repository의 master student notebooks는 prompt-only `student-task`를 유지한다.
3. 학생 notebook의 kernel을 종료한다.
4. `src/dawn_tactics/` 아래 게임 파일을 수정하지 않았는지 확인한다.
5. Lesson 01과 Lesson 02 자료가 변경되지 않았는지 확인한다.
6. 다음 명령으로 전체 테스트를 실행한다.

```bash
python -m pytest
```
