# Lesson 04 — Class와 Object: 교사용 90분 수업안

## 수업의 한 문장 목표

학생이 `class`를 설계도, `object`를 그 설계도로 만든 한 유닛으로 설명하고,
`self`를 사용하여 두 유닛이 독립적인 체력을 갖는 `Unit`을 직접 작성한다.

## 준비물과 수업 원칙

- 학생용: `lesson_04_classes.ipynb` 또는 영어판 `lesson_04_classes_en.ipynb`
- 교사용: 이 문서와 실행 가능한 Dawn Tactics 설치 환경
- 오늘의 코드 언어는 영어, 설명과 대화는 한국어로 진행한다.
- 학생의 코드를 교사가 대신 완성하지 않는다. 예측, 실행, 설명, 수정의 순서로
  한 단계씩 힌트를 준다.
- 오늘은 class와 object까지만 다룬다. inheritance, subclass, `super()`,
  overriding은 다음 Lesson 05의 주제다.

## 핵심 낱말

| 낱말 | 학생에게 할 설명 |
| --- | --- |
| class | 같은 규칙을 찍어 내는 blueprint(설계도) |
| object | 설계도로 만든 실제 한 물건 또는 한 유닛 |
| attribute | object 안에 기억해 둔 값. 예: `hp` |
| method | object가 할 수 있는 일. 예: `take_damage()` |
| `__init__` | object가 만들어질 때 처음 값을 넣는 method |
| `self` | 지금 이 method call을 받은 바로 그 object |
| dot notation | `tank.hp`, `tank.take_damage(3)`처럼 점으로 접근하는 표기 |

## 시간별 진행

### 0–8분 — Function prerequisite pulse

Lesson 03의 `mission_label()`을 실행한다. “function은 입력을 받아 일을 하고
결과를 돌려준다”를 학생 말로 확인한다. 이어서 “유닛 하나가 이름, 최대 체력,
현재 체력을 모두 기억하고 피해도 받으려면 function만 여러 개 두는 것보다 어떤
묶음이 편할까?”라고 질문한다. 오늘 class는 function을 버리는 새 문법이 아니라,
데이터와 function을 한 설계도로 묶는 방법임을 강조한다.

### 8–20분 — Blueprint와 object

쿠키 틀과 쿠키, 또는 같은 모양의 병사 토큰을 사용해 class와 object를 구별한다.
칠판에 `MissionCard`를 설계도, `first_card`를 첫 물건으로 적는다. “설계도를
바꾸지 않고 서로 다른 임무 카드 두 장을 만들 수 있는가?”를 먼저 묻는다.
학생이 `class`와 `object`를 바꾸어 말하면, “설계도는 몇 개를 만들 수 있지?”
라고 되물어 구별하게 한다.

### 20–34분 — class, __init__, self

`MissionCard` class를 천천히 읽는다. 들여쓰기는 class 안에 속한다는 표시이며,
class 줄의 콜론은 꼭 필요하다고 표시한다. `__init__`는 새 object를 만들 때
자동으로 실행된다. `objective`는 들어오는 값이고 `self.objective`는 그 object
속 attribute다. `self`를 “나 자신”이라고만 외우게 하지 말고, `first_card`가
`brief()`를 부르면 `self`가 `first_card`라고 실제 이름으로 바꾸어 말하게 한다.

### 34–46분 — 두 object와 independent state

둘째 카드를 만든 뒤 첫째 카드의 attribute만 바꾼다. 실행 전 둘째 카드가 바뀔지
손으로 투표한다. 실행 뒤 각 object가 자기 attribute를 따로 저장한다는 것을
확인한다. “같은 class라서 규칙은 같지만, object가 달라서 state는 독립적이다”를
학생이 완성 문장으로 말하게 한다. `first_card.objective`의 점이 어느 object를
고르는지 색으로 표시하면 도움이 된다.

### 46–51분 — Movement break

학생은 각각 Tank 또는 Infantry object가 된다. 교사가 “왼쪽 Tank hp에서 3을
빼라”고 말하면 해당 학생만 숫자 카드를 바꾼다. 다른 학생의 숫자가 그대로인
것을 보고 independent state를 몸으로 확인한다. 짧게 끝내고 다시 노트북으로
돌아온다.

### 51–63분 — Method가 state를 사용하기

`brief()`는 class 안의 function, 즉 method임을 소개한다. `first_card.brief()`의
dot notation을 읽고, method 안에서 `self.objective`가 첫 카드 값을 가져오는
이유를 확인한다. 학생에게 `second_card.brief()`를 예측하게 하되, 코드를 바꾸기
전에 기대 문장을 먼저 적게 한다. method는 object가 가진 attribute를 읽거나
바꾸는 행동이라는 연결을 남긴다.

### 63–69분 — 실제 Dawn Tactics Tank object

`left_tank`와 `right_tank` 코드를 실행한다. ID와 좌표는 지금 외울 필요 없다고
말하고, `Tank(...)`가 새 object를 만드는 부분과 `left_tank.take_damage(3)`가
왼쪽 object만 바꾸는 부분에 집중한다. assert가 두 Tank의 HP를 비교해 주는 것을
읽는다. 게임 안의 많은 유닛도 이런 방식으로 각자의 상태를 가진다는 연결만
보여 준다.

### 69–84분 — Unit class 독립 과제

학생에게 빈 `student-task` 칸을 보이게 하고, 먼저 종이에 object가 기억해야 할
세 값(`name`, `max_hp`, `hp`)을 쓰게 한다. 그 뒤 class 줄, `__init__`, 세
attribute, `take_damage` 순으로 스스로 작성하게 한다. 처음부터 완성 코드를
보여 주지 않는다. 에러가 나면 아래 error routine을 그대로 가리키며 학생이
검사할 항목 하나를 고르게 한다.

**Hint 1 — Circle the two inputs after self and list the three attributes every object must remember.**

**Hint 2 — hp begins with the same value as max_hp; write all three self assignments before the method.**

**Hint 3 — subtract amount from self.hp, then use the previous if lesson to replace a negative value with 0.**

### 84–88분 — Self-check와 설명

학생이 self-check를 실행한다. `tank`가 피해를 받은 뒤에도 `infantry.hp`가 5인
assert를 손가락으로 찾게 한다. 통과한 학생에게는 결과를 자랑하기보다 “어느
줄이 두 object를 만들었고, 어느 `self`가 Tank를 가리켰나?”를 말로 설명하게
한다. 통과하지 않으면 가장 첫 에러만 읽고 error routine으로 돌아간다.

### 88–90분 — Exit ticket과 inheritance 예고

class/object 차이, `self`, 독립 상태를 각각 한 문장으로 적게 한다. 다음 Lesson
05에서는 공통 `Unit` 규칙을 Tank와 Infantry가 함께 쓰는 inheritance를 배운다고
예고한다. 아직 `super()`나 subclass 코드는 오늘 추가하지 않는다.

## Error routine

학생이 오류를 만나면 교사가 정답을 말하기 전에 이 순서를 같이 읽는다.

Read → Find the class/object name → Check colon and indentation → Count arguments after self → Check every self. prefix → Run again

- **Read:** 빨간 글 전체에서 첫 줄과 마지막 핵심 단어를 읽는다.
- **Find:** 오류에 나온 class/object 이름이 실제 만든 이름과 같은지 찾는다.
- **Colon and indentation:** `class`, `def`, `if` 뒤 콜론과 class 안쪽 네 칸
  들여쓰기를 확인한다.
- **Arguments:** `self` 뒤에 `name, max_hp` 또는 `amount`가 맞게 있는지 센다.
- **Every self. prefix:** object 안에 저장할 값은 `self.`로 시작하는지 본다.
- **Run again:** 한 가지만 고친 뒤 처음부터 다시 실행한다.

## 교사용 reference solution

학생이 충분히 시도한 뒤에만, 또는 수업 뒤 복습용으로 사용한다. 학생 노트북에는
이 답을 넣지 않는다.

```python
class Unit:
    def __init__(self, name, max_hp):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp

    def take_damage(self, amount):
        self.hp = self.hp - amount
        if self.hp < 0:
            self.hp = 0
```

## Reset checklist

- 학생용 master notebook의 code cell은 실행 결과 없이 배포한다.
- `student-task`에는 힌트만 있고 reference solution이 없는지 확인한다.
- `student-self-check`가 Tank와 Infantry의 독립 상태, 0 아래로 내려가지 않는 HP를
  모두 확인하는지 실행한다.
- `MissionCard`와 실제 `Tank` 예제가 오류 없이 실행되는지 확인한다.
- 다음 Lesson 05 전에는 오늘 만든 독립 `Unit`을 상속 구조로 확장하지 않는다.
