# Lesson 01 — Variables: 게임의 규칙에 이름 붙이기

## 수업 개요

- 대상: Python 경험은 없지만 한국어·영어 소통이 원활한 학생
- 시간: 90분
- 설명 언어: 한국어
- 코드·게임 UI·핵심 용어: 영어
- 학생 결과물: 실행한 노트북, 게임 변수 실험 기록, exit ticket
- 편집 파일: `src/dawn_tactics/student_settings.py`
- 한국어 중심 실습 노트북: `lessons/lesson_01_variables.ipynb`
- 영어 실습 노트북: `lessons/lesson_01_variables_en.ipynb`

이번 수업의 중심 문장은 다음과 같다.

> A variable is a name for a value. 값을 바꾸기 전에 결과를 예측하고, 한 번에 하나만 바꾼다.

`TANK_COST` 같은 값은 나중에 배울 class attribute와 연결되어 있지만, 첫
수업에서는 이를 “게임이 시작할 때 읽는 설정 variable”로만 설명한다. OOP
용어를 미리 많이 소개하지 않는다.

## 학습 목표와 성공 기준

수업 종료 시 학생이 다음을 할 수 있으면 성공이다.

1. variable, name, value를 자신의 예로 설명한다.
2. `str`, `int`, `float`, `bool`을 실제 값과 연결한다.
3. `TANK_COST = 400`에서 왼쪽은 name, 오른쪽은 value라고 구분한다.
4. 값을 바꾸기 전에 게임에서 생길 변화를 말한다.
5. 한 번에 변수 하나만 바꾸고 관찰 결과를 원인과 연결한다.
6. 설정 파일을 저장한 뒤 게임을 재시작해야 하는 이유를 대략 설명한다.

문법을 외우는 것보다 “예측 → 변경 → 관찰 → 설명 → 원상복구” 습관을
만드는 것이 우선이다.

## 수업 전 준비

### 선생님 컴퓨터와 학생 Windows 컴퓨터

두 컴퓨터 모두 프로젝트 폴더에서 다음 환경을 준비한다.

```bash
python -m pip install -e ".[dev,lesson]"
```

Windows PowerShell에서 가상환경을 활성화하지 못하면 다음처럼 직접 실행한다.

```powershell
.venv\Scripts\python.exe -m pip install -e ".[dev,lesson]"
.venv\Scripts\python.exe -m dawn_tactics
```

VS Code에 Python과 Jupyter 확장을 설치하고, 노트북 kernel로 프로젝트의
`.venv` Python을 선택한다.

### 5분 사전 점검

1. `python -m dawn_tactics`로 게임이 실행되는지 확인한다.
2. 캠페인 화면에서 **NORMAL**을 선택한다. 게임의 기본 선택은 HARD이다.
3. Campaign 1 `First Deployment`를 연다.
4. Infantry 한 개와 Tank 한 개를 배치할 수 있는지 확인한다.
5. `student_settings.py`의 값이 모두 기본값인지 확인한다.
6. 수업 시작 전에 게임은 종료해 둔다.

HARD는 예산이 더 적고 적 증원 유닛이 추가되는 도전 모드다. 유닛의 숨은
공격력이나 HP가 달라지는 것은 아니지만, 아래의 고정 baseline 결과는
NORMAL을 기준으로 기록했으므로 첫 변수 수업 동안에는 NORMAL을 유지한다.

학생이 잘못된 값을 입력해도 게임은 안전 범위를 검사하여
`StudentSettingsError`와 변수 이름을 보여준다. 오류가 생기면 바로 정답을
고쳐주기보다 오류 문장에서 문제의 variable을 먼저 찾게 한다.

## 90분 진행안

### 0–10분 — 역사 게임 디자이너로 초대하기

게임을 먼저 2분 정도 보여주되 코드는 열지 않는다.

질문:

- “탱크 가격은 게임이 어떻게 기억하고 있을까?”
- “똑같은 탱크인데 HP가 10에서 20이 되면 무엇이 달라질까?”
- “가격만 바꿨는데 공격력도 달라질까?”

종이나 포스트잇에 `budget → 500`, `tank cost → 400`, `tank HP → 10`을
적어 이름표처럼 놓는다. 값 카드만 교체하면서 “name은 유지되고 value가
바뀐다”는 모습을 보여준다.

이 단계에서 학생의 사전 경험을 자연스럽게 확인한다.

- Python이나 다른 코딩 언어를 본 적이 있는가?
- `=`를 보면 어떤 뜻이 떠오르는가?
- 숫자와 따옴표가 있는 숫자가 다르다고 생각하는가?

### 10–25분 — 첫 variable과 assignment

노트북의 1번 부분을 함께 실행한다.

```python
budget = 1000
print("Current budget:", budget)
```

교사 표현:

- “`budget`이라는 이름에 1000을 저장한다.”
- “`=`를 오늘은 ‘gets’ 또는 ‘저장한다’라고 읽어보자.”
- “실행 버튼을 누르기 전에 결과를 먼저 말해보자.”

학생이 `1000`을 `1500`으로 직접 바꾸고 재실행한다. 타이핑은 학생이 하고,
선생님은 키보드를 대신 잡지 않고 어느 부분을 확인할지 질문한다.

확인 질문:

- name은 무엇인가?
- value는 무엇인가?
- 같은 name에 새 value를 저장하면 어떤 출력이 나오는가?
- variable의 이름을 `money`로 바꾸면 숫자도 자동으로 바뀌는가?

### 25–38분 — 네 가지 value type

노트북의 `str`, `int`, `float`, `bool` 셀을 실행한다.

| Type | 수업 표현 | 게임 예시 |
|---|---|---|
| `str` | 따옴표로 감싼 text | `"Tank"` |
| `int` | whole number | `400`, `10` |
| `float` | decimal을 가질 수 있는 number | `0.42` seconds |
| `bool` | yes/no switch | `True`, `False` |

따옴표가 있는 `"400"`과 숫자 `400`을 비교한다. type 이름을 모두 암기하게
하기보다 “Python이 어떤 종류의 값으로 보는가?”를 묻는다.

### 38–45분 — Budget 계산과 값 업데이트

노트북의 budget 셀을 실행하기 전에 답을 예상한다.

```python
starting_budget = 1000
tank_cost = 400
```

예상 답:

- 살 수 있는 Tank: 2
- 남는 돈: 200

이후 HP 업데이트 셀을 실행한다. `tank_hp = tank_hp - damage`에서는 오른쪽
계산이 먼저 이루어지고 그 결과가 다시 왼쪽 name에 저장된다고 설명한다.

`=`와 `==`의 차이는 한 문장과 한 번의 실행으로만 소개한다. 조건문은 다음
수업 이후에 다룬다.

### 45–50분 — 움직임 휴식과 실험 규칙 정하기

자리에서 일어나 “Predict → Change → Observe → Explain → Reset”을 몸동작과
함께 한 번 반복한다.

수업의 세 가지 안전 규칙을 학생이 다시 말하게 한다.

1. 오른쪽 value만 바꾼다.
2. 한 번에 variable 하나만 바꾼다.
3. 실험 뒤 default로 되돌린다.

### 50–60분 — Baseline 게임 기록

`student_settings.py`를 열고 먼저 읽기만 한다. **NORMAL**인지 다시 확인한
뒤 Campaign 1에서 다음 고정 배치를 사용한다.

- Infantry: 맨 아래 행, 왼쪽에서 5번째 칸
- Tank: 맨 아래 행, 왼쪽에서 7번째 칸

기본값 `TANK_DAMAGE = 3`으로 실행하면 현재 deterministic rules에서
`BLUE VICTORY`, 9 ticks가 나온다. 결과와 살아남은 Tank HP를 기록한다.

여기서 baseline은 “비교하기 위한 원래 결과”라고 설명한다.

### 60–72분 — 통제 실험: Tank damage

같은 캠페인, 같은 유닛, 같은 배치를 유지하고 `TANK_DAMAGE`만 바꾼다.

| Value | 실행 전 예측 | 기본 규칙의 실제 결과 |
|---:|---|---|
| `3` | baseline | Blue win, 9 ticks |
| `1` | 탱크가 약해진다 | Red win, 10 ticks |
| `6` | 더 빨리 이긴다 | Blue win, 7 ticks |

각 실행 전에 학생이 승패와 tick 방향을 예상하게 한다. 결과가 예상과 다르면
틀렸다고 하지 않고 “어떤 다른 variable이나 위치가 영향을 줬을까?”라고
묻는다.

핵심 질문:

- damage를 바꿨는데 cost는 왜 그대로였나?
- 같은 배치를 사용해야 하는 이유는 무엇인가?
- damage가 두 배가 되면 승리 속도도 항상 정확히 두 배가 되는가?

마지막에는 `TANK_DAMAGE = 3`으로 복구한다.

### 72–82분 — 학생 선택 실험

다음 중 하나를 학생이 고른다.

- `TANK_COST = 200`: 같은 budget으로 몇 대를 살 수 있는가?
- `TANK_MAX_HP = 20`: 승리 tick과 생존 HP 중 무엇이 바뀌는가?
- `TANK_RANGE = 4`: 첫 공격 시점이 어떻게 달라지는가?
- `TANK_NAME = "Iron Turtle"`: text가 UI 어디에 나타나는가?
- `SHOW_HISTORY_NOTE = False`: 어떤 UI만 사라지는가?
- `BATTLE_STEP_SECONDS = 0.18`: 화면은 빨라지지만 전투 tick 결과도 바뀌는가?

학생이 먼저 아래 문장을 완성한 다음 수정한다.

> I will change ______ from ______ to ______. I predict ______ because ______.

### 82–88분 — Exit ticket

노트북 마지막 질문에 말 또는 글로 답한다.

1. Variable은 무엇인가?
2. `TANK_COST = 400`에서 name과 value는 무엇인가?
3. `400`과 `"400"`은 왜 다른가?
4. 바꾼 variable과 관찰한 결과를 연결해 설명할 수 있는가?

학생의 문장을 그대로 기록한다. 용어가 완벽하지 않아도 이름과 값의 관계를
설명할 수 있으면 개념 이해로 본다.

### 88–90분 — 복구와 다음 수업 예고

설정 파일을 기본값으로 되돌리고 게임이 한 번 실행되는지 확인한다.

다음 수업 예고:

> 오늘은 Tank의 값들에 이름을 붙였다. 다음에는 HP가 공격받을 때 스스로
> 줄어드는 행동, 즉 method를 만들어본다.

## 게임 variable 지도

| Variable | Type | Default | 실제로 바뀌는 것 | 바뀌지 않는 것 | 권장 실험 범위 |
|---|---|---:|---|---|---|
| `GAME_TITLE` | `str` | `"DAWN TACTICS"` | 메뉴·창 제목 | 전투 규칙 | 1–30자 |
| `TANK_NAME` | `str` | `"Tank"` | 카드 이름 | 아이콘·수치 | 1–14자 |
| `*_BUDGET` | `int` | 500/1000/1200 | 미션 문구·시작 예산 | 유닛 성능 | 0–3000 |
| `TANK_COST` | `int` | 400 | 카드 가격·구매 가능 수 | HP·damage | 100–800 |
| `TANK_MAX_HP` | `int` | 10 | 시작 HP·체력 막대·생존성 | 공격 damage | 1–30 |
| `TANK_DAMAGE` | `int` | 3 | 공격당 피해·승패 가능성 | 가격·HP | 1–10 |
| `TANK_RANGE` | `int` | 2 | 공격을 시작하는 거리 | 공격 damage | 1–6 |
| `ANTI_TANK_DAMAGE_VS_HEAVY` | `int` | 5 | 대전차병의 Tank 피해 | 일반 보병 피해 | 1–10 |
| `BATTLE_STEP_SECONDS` | `float` | 0.42 | 화면에서 다음 tick까지 시간 | 동일 배치의 tick 규칙 | 0.15–1.0 |
| `SHOW_HISTORY_NOTE` | `bool` | `True` | History Note 표시 여부 | 캠페인·전투 | `True/False` |

코드가 허용하는 안전 범위는 권장 실험 범위보다 넓다. 수업에서는 결과가
관찰하기 좋은 권장 범위 안에서만 사용한다.

## 핵심 영어 어휘

| English | 수업에서 사용할 한국어 표현 |
|---|---|
| variable | 값을 기억하는 이름 |
| name | 왼쪽 이름표 |
| value | 저장되는 실제 값 |
| assignment | 오른쪽 값을 왼쪽 이름에 저장하기 |
| type | 값의 종류 |
| string | text value |
| integer | whole-number value |
| float | decimal을 가질 수 있는 number |
| boolean | `True/False` switch |
| predict | 실행 전에 결과 예상하기 |
| observe | 실행 결과 관찰하기 |
| reset | 기본값으로 복구하기 |

## 자주 생기는 오개념과 대응

| 상황 | 질문으로 돕기 |
|---|---|
| `=`를 수학의 “같다”로만 이해 | “오른쪽에서 왼쪽으로 어떤 값이 이동했을까?” |
| `400`과 `"400"`을 같다고 생각 | `type()` 결과와 실제 덧셈 가능 여부를 비교한다. |
| 노트북의 값을 바꾸면 게임도 바뀐다고 생각 | “두 프로그램이 같은 실행 공간을 쓰고 있을까?” |
| 파일을 저장하지 않거나 게임을 재시작하지 않음 | Save → Stop → Run 세 단계를 학생이 읽게 한다. |
| 여러 변수를 동시에 변경 | “결과의 원인을 하나로 설명할 수 있을까?” |
| seconds가 작을수록 느리다고 예상 | 한 tick을 기다리는 시간이라고 다시 표현한다. |
| 강한 수치가 항상 좋은 게임이라고 생각 | “모든 유닛이 HP 999라면 전략이 재미있을까?” |

## 문제 해결표

| 증상 | 먼저 확인할 것 |
|---|---|
| `SyntaxError` | `=` 또는 따옴표를 지웠는가? |
| `StudentSettingsError` | 오류에 나온 variable의 type과 안전 범위 |
| 값을 바꿨는데 게임이 그대로 | 올바른 파일인지, 저장했는지, 게임을 완전히 재시작했는지 |
| Notebook kernel을 찾지 못함 | `.venv` 선택 및 `.[lesson]` 설치 여부 |
| 게임이 너무 빠름 | `BATTLE_STEP_SECONDS`를 0.42로 복구 |
| 비교 결과가 매번 다름 | 캠페인·유닛 수·배치·나머지 설정이 같은지 |
| 노트북의 baseline과 결과가 다름 | 캠페인 화면에서 NORMAL을 선택했는지 |

## 형성평가 기록표

각 항목을 `독립 수행 / 힌트 후 수행 / 아직 어려움`으로 기록한다.

- name과 value 식별
- 네 type 중 실제 예시 분류
- 실행 전 변화 예측
- 오른쪽 value만 안전하게 편집
- 한 변수만 바꾼 통제 실험
- 관찰 결과를 해당 variable과 연결해 설명
- 기본값 복구

수업 후 부모님께는 점수보다 다음처럼 구체적인 행동을 공유한다.

> 새벽이는 `TANK_DAMAGE`를 3에서 1로 바꾸면 전투가 길어질 것이라고 먼저
> 예측했고, 같은 배치에서 승패가 바뀐 것을 확인한 뒤 damage가 전투 규칙을
> 바꾸지만 cost는 바꾸지 않는다고 설명했습니다.

## 선택형 10분 미션

컴퓨터 없이 새로운 유닛 카드 한 장을 만든다.

- English unit name
- cost
- HP
- damage
- range
- 각 값을 그렇게 정한 이유 한 문장

다음 수업에서는 이 카드의 variable을 Python object 안에 넣는 활동으로
연결한다.
