"""Run Dawn Intel from the terminal."""

if __package__:
    from .backgrounds import BACKGROUNDS
    from .difficulty import level_for_question, matches_short_answer
    from .questions import DOSSIERS
    from .korean import KOREAN_DOSSIERS
else:
    from backgrounds import BACKGROUNDS
    from difficulty import level_for_question, matches_short_answer
    from questions import DOSSIERS
    from korean import KOREAN_DOSSIERS


MESSAGES = {
    "en": {
        "title": "DAWN INTEL: HISTORY CASES",
        "intro": "Read the situation. Make your call. Use H only when you need a clue.",
        "dossiers": "AVAILABLE DOSSIERS",
        "all": "ALL DOSSIERS",
        "questions": "questions",
        "choose_dossier": "Choose a dossier",
        "invalid_dossier": "Please enter a dossier number, or A.",
        "opening": "OPENING DOSSIER",
        "maximum": "historical situation questions. Maximum score",
        "question": "QUESTION",
        "call": "Your call [A-D, or H for a clue]",
        "clue": "DECRYPTED CLUE (-1 point)",
        "no_clues": "All available clues have been decrypted.",
        "invalid_answer": "Please enter A, B, C, D, or H.",
        "correct": "Correct.",
        "points": "Intelligence Points",
        "wrong": "Not this time. The answer was",
        "debrief": "HISTORICAL DEBRIEF",
        "complete": "DOSSIER COMPLETE",
        "final": "FINAL INTELLIGENCE SCORE",
        "level": "LEVEL",
        "recruit": "RECRUIT — GUIDED",
        "analyst": "ANALYST — THINK IT THROUGH",
        "commander": "COMMANDER — NO OPTIONS",
        "commander_instruction": "Type a short analysis. Enter O to decrypt choices for -1 point.",
        "commander_call": "Your analysis [type answer, O options, H clue]",
        "options": "OPTIONS DECRYPTED (-1 point)",
        "hard_wrong": "That analysis does not fit this situation.",
        "background": "MISSION BACKGROUND",
        "ready": "Press Return when you are ready to investigate",
    },
    "ko": {
        "title": "DAWN INTEL: 역사 사건 파일",
        "intro": "상황을 읽고 판단하세요. 힌트가 필요할 때만 H를 누르세요.",
        "dossiers": "선택 가능한 사건 파일",
        "all": "모든 사건 파일",
        "questions": "문제",
        "choose_dossier": "사건 파일 선택",
        "invalid_dossier": "사건 파일 번호나 A를 입력하세요.",
        "opening": "사건 파일 열기",
        "maximum": "개의 역사 상황 문제. 최고 점수",
        "question": "문제",
        "call": "답 선택 [A-D, 힌트는 H]",
        "clue": "해독한 단서 (-1점)",
        "no_clues": "더 열 수 있는 단서가 없습니다.",
        "invalid_answer": "A, B, C, D, H 중 하나를 입력하세요.",
        "correct": "정답!",
        "points": "정보 점수",
        "wrong": "아쉽습니다. 정답은",
        "debrief": "역사 해설",
        "complete": "사건 파일 완료",
        "final": "최종 정보 점수",
        "level": "난이도",
        "recruit": "신병 — 안내형",
        "analyst": "분석관 — 생각하기",
        "commander": "지휘관 — 선택지 없음",
        "commander_instruction": "짧은 분석 답을 입력하세요. O를 누르면 -1점으로 선택지를 엽니다.",
        "commander_call": "분석 답 입력 [직접 답, O 선택지, H 힌트]",
        "options": "선택지 해독 (-1점)",
        "hard_wrong": "그 분석은 이 상황에 맞지 않습니다.",
        "background": "사건 배경",
        "ready": "읽은 뒤 Return을 눌러 사건 조사를 시작하세요",
    },
}


def choose_language(input_fn=input, output_fn=print):
    """Ask for English or Korean before any player-facing game text appears."""
    output_fn("SELECT LANGUAGE / 언어 선택")
    output_fn("  EN. English")
    output_fn("  KO. 한국어")
    while True:
        choice = input_fn("Language [EN/KO]: ").strip().upper()
        if choice in {"EN", "E", "1"}:
            return "en"
        if choice in {"KO", "K", "2"}:
            return "ko"
        output_fn("Please enter EN or KO. / EN 또는 KO를 입력하세요.")


def display_dossier(dossier, language):
    if language == "ko":
        return KOREAN_DOSSIERS[dossier["id"]]
    return dossier


def display_question(dossier, question, language):
    if language == "ko":
        return KOREAN_DOSSIERS[dossier["id"]]["questions"][question["id"]]
    return question


def show_menu(dossiers, language, output_fn=print):
    """Show neutral dossier code names without revealing historical answers."""
    messages = MESSAGES[language]
    output_fn(f"\n{messages['dossiers']}")
    for number, dossier in enumerate(dossiers, start=1):
        translated = display_dossier(dossier, language)
        output_fn(f"  {number}. {translated['code_name']} — {len(dossier['questions'])} {messages['questions']}")
    output_fn(f"  A. {messages['all']} — {sum(len(dossier['questions']) for dossier in dossiers)} {messages['questions']}")


def choose_dossiers(dossiers, language, input_fn=input, output_fn=print):
    """Return one selected dossier or all dossiers when the player chooses A."""
    messages = MESSAGES[language]
    show_menu(dossiers, language, output_fn)
    while True:
        choice = input_fn(f"\n{messages['choose_dossier']} [1-{len(dossiers)}, A]: ").strip().upper()
        if choice == "A":
            return dossiers
        if choice.isdigit() and 1 <= int(choice) <= len(dossiers):
            return (dossiers[int(choice) - 1],)
        output_fn(f"{messages['invalid_dossier']} 1-{len(dossiers)}, A.")


def show_question(dossier, question, number, total, language, output_fn=print):
    """Print one question without showing the answer or the event name."""
    messages = MESSAGES[language]
    translated_dossier = display_dossier(dossier, language)
    translated_question = display_question(dossier, question, language)
    level = level_for_question(number)
    output_fn("")
    output_fn("=" * 60)
    output_fn(f"{translated_dossier['code_name']} — {messages['question']} {number}/{total}")
    output_fn("=" * 60)
    output_fn(f"{messages['level']}: {messages[level]}")
    output_fn(translated_question["prompt"])
    output_fn("")
    if level == "commander":
        output_fn(messages["commander_instruction"])
    else:
        show_choices(translated_question, output_fn)


def show_choices(question, output_fn=print):
    """Show choices only when the question's difficulty permits it."""
    for letter, choice in question["choices"].items():
        output_fn(f"  {letter}. {choice}")


def show_background(dossier, language, input_fn=input, output_fn=print):
    """Give the player the historical situation before the first question."""
    messages = MESSAGES[language]
    translated_dossier = display_dossier(dossier, language)
    output_fn("")
    output_fn("-" * 60)
    output_fn(f"{messages['background']}: {translated_dossier['code_name']}")
    output_fn("-" * 60)
    output_fn(BACKGROUNDS[language][dossier["id"]])
    input_fn(f"\n{messages['ready']}... ")


def play_question(dossier, question, number, total, language="en", input_fn=input, output_fn=print):
    """Play one question and return its earned Intelligence Points."""
    messages = MESSAGES[language]
    translated_question = display_question(dossier, question, language)
    level = level_for_question(number)
    commander_mode = level == "commander"
    choices_revealed = not commander_mode
    points = 3
    hint_index = 0
    show_question(dossier, question, number, total, language, output_fn)

    while True:
        prompt = messages["commander_call"] if commander_mode and not choices_revealed else messages["call"]
        answer = input_fn(f"\n{prompt}: ").strip().upper()
        if answer == "H":
            if hint_index < len(translated_question["hints"]):
                points -= 1
                output_fn(f"\n{messages['clue']}: {translated_question['hints'][hint_index]}")
                hint_index += 1
            else:
                output_fn(f"\n{messages['no_clues']}")
            continue

        if commander_mode and not choices_revealed:
            if answer == "O":
                points -= 1
                choices_revealed = True
                output_fn(f"\n{messages['options']}:")
                show_choices(translated_question, output_fn)
                continue
            if matches_short_answer(question["id"], answer):
                output_fn("")
                output_fn(f"{messages['correct']} +{points} {messages['points']}")
                output_fn(f"{messages['debrief']}: {translated_question['debrief']}")
                return points

            output_fn("")
            output_fn(messages["hard_wrong"])
            output_fn(f"{messages['debrief']}: {translated_question['debrief']}")
            return 0

        if answer not in question["choices"]:
            output_fn(messages["invalid_answer"])
            continue

        output_fn("")
        if answer == question["answer"]:
            output_fn(f"{messages['correct']} +{points} {messages['points']}")
            earned_points = points
        else:
            correct_choice = translated_question["choices"][question["answer"]]
            output_fn(f"{messages['wrong']} {question['answer']}: {correct_choice}")
            earned_points = 0

        output_fn(f"{messages['debrief']}: {translated_question['debrief']}")
        return earned_points


def play_dossier(dossier, language="en", input_fn=input, output_fn=print):
    """Play all ten questions in a selected dossier and return its score."""
    messages = MESSAGES[language]
    translated_dossier = display_dossier(dossier, language)
    questions = dossier["questions"]
    output_fn("")
    output_fn("#" * 60)
    output_fn(f"{messages['opening']}: {translated_dossier['code_name']}")
    output_fn(f"{len(questions)} {messages['maximum']}: {len(questions) * 3}.")
    output_fn("#" * 60)
    show_background(dossier, language, input_fn, output_fn)

    score = 0
    for number, question in enumerate(questions, start=1):
        score += play_question(dossier, question, number, len(questions), language, input_fn, output_fn)

    output_fn("")
    output_fn(f"{messages['complete']}: {translated_dossier['code_name']} — {score}/{len(questions) * 3}")
    return score


def run_quiz(dossiers=DOSSIERS, language=None, input_fn=input, output_fn=print):
    """Show the menu, play selected dossiers, and return the final score."""
    selected_language = language or choose_language(input_fn, output_fn)
    messages = MESSAGES[selected_language]
    output_fn(messages["title"])
    output_fn(messages["intro"])
    selected_dossiers = choose_dossiers(dossiers, selected_language, input_fn, output_fn)

    score = 0
    maximum_score = 0
    for dossier in selected_dossiers:
        score += play_dossier(dossier, selected_language, input_fn, output_fn)
        maximum_score += len(dossier["questions"]) * 3

    output_fn("")
    output_fn("=" * 60)
    output_fn(f"{messages['final']}: {score}/{maximum_score}")
    output_fn("=" * 60)
    return score


if __name__ == "__main__":
    run_quiz()
