# Lesson 02 — Conditionals: 유닛이 상황을 판단하게 만들기

## 수업 개요

- 시간: 90분
- 설명 언어: 한국어
- 코드·UI·핵심 용어: 영어
- 학생 편집 파일: `src/dawn_tactics/student_rules.py`
- 중심 문장: A condition is a question that becomes `True` or `False`.

Day 2는 `if`, `elif`, `else`에 집중한다. `def`와 `return`은 준비된 규칙
상자의 입구와 출구로만 설명하고 function 수업은 Day 3로 미룬다.

## 학습 목표

1. 비교식 결과를 `True` 또는 `False`로 예측한다.
2. 주어진 입력에서 실행될 branch를 가리킨다.
3. indentation이 branch 범위를 나타낸다고 설명한다.
4. `if/else`와 `if/elif/else`를 구분한다.
5. 한 조건 또는 return value만 바꾸고 게임 결과와 연결한다.
6. 실험 뒤 기본 규칙을 Restore한다.

## 수업 전 준비

1. 게임과 두 notebook을 실행한다.
2. `student_rules.py`가 기본값인지 확인한다.
3. Normal Campaign 1에서 Machine Gun과 Cavalry를 함께 구매한다.
4. preview 결과가 `4, 1, 5, 3, 1`인지 확인한다.
5. `python -m pytest`가 통과하는지 확인한다.

## 90분 진행안

### 0–10분 — Day 1 variable 복습

`target_armor`, `target_kind`, `damage`에서 name과 value를 찾는다.

### 10–25분 — 비교식은 yes/no 질문

`target_armor == "LIGHT"`의 결과를 실행 전에 예상한다. `=`는 저장,
`==`는 질문이라는 차이를 확인한다.

### 25–40분 — if와 else

LIGHT와 HEAVY 카드를 Machine Gun의 두 갈래 규칙에 넣고 실행 branch를
학생이 손으로 가리킨 뒤 코드를 실행한다.

### 40–52분 — elif로 세 번째 선택

Artillery, Infantry, Tank 카드를 Cavalry 규칙에 차례로 넣는다. Python이
위에서 아래로 확인하고 첫 번째 참인 branch 뒤에는 멈춤을 관찰한다.

### 52–60분 — 실제 규칙 읽기

`student_rules.py`를 열고 function 구조는 제공된 것이라고 설명한다.
파일을 저장한 뒤 notebook의 preview cell을 다시 실행하면 `importlib.reload`가
최신 rule을 읽어온다는 점을 확인한다.

### 60–75분 — 통제된 게임 실험

Normal Campaign 1에서 두 유닛 위치를 고정한다. 기본 전투를 기록한 뒤
Machine Gun의 `LIGHT`를 `HEAVY`로 한 줄만 바꾸고 같은 배치를 비교한다.

### 75–83분 — 학생 선택 실험

- Cavalry의 Infantry damage를 3에서 1로 변경
- Cavalry의 `elif` target을 Infantry에서 Anti-Tank로 변경
- Machine Gun의 LIGHT damage를 4에서 0으로 변경

### 83–88분 — Exit ticket

`if`가 묻는 질문, `else`가 실행되는 때, branch order가 중요한 이유,
바꾼 규칙과 관찰 결과를 답한다.

### 88–90분 — 기본값 복구

두 함수를 기본값과 대조하고 preview `4, 1, 5, 3, 1`을 확인한다.

## 문제 해결표

| 증상 | 먼저 확인할 것 |
|---|---|
| `SyntaxError` | 조건 끝의 `:` 또는 따옴표 |
| `IndentationError` | branch 안의 네 칸 들여쓰기 |
| `StudentRulesError`와 `None` | 모든 입력을 처리하는 `else` |
| 게임 결과가 그대로 | 저장 후 게임을 완전히 재시작했는가? |
| 원인을 설명하기 어려움 | 한 번에 두 줄 이상 바꾸지 않았는가? |

## 기본 규칙

```python
def machine_gun_damage(target_armor):
    if target_armor == "LIGHT":
        return 4
    else:
        return 1


def cavalry_damage(target_kind):
    if target_kind == "artillery":
        return 5
    elif target_kind == "infantry":
        return 3
    else:
        return 1
```

## 다음 수업 연결

Day 3에서는 오늘 사용한 규칙 상자를 통해 `function`, parameter,
argument, return을 정식으로 배운다.
