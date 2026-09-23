from history_quiz.backgrounds import BACKGROUNDS
from history_quiz.difficulty import HARD_ANSWER_WORDS, level_for_question
from history_quiz.play import play_dossier, play_question, run_quiz
from history_quiz.korean import KOREAN_DOSSIERS
from history_quiz.questions import DOSSIERS


def scripted_input(answers):
    iterator = iter(answers)
    return lambda _prompt: next(iterator)


def answers_for(dossiers, language="en"):
    answers = []
    for dossier in dossiers:
        answers.append("")
        for number, question in enumerate(dossier["questions"], start=1):
            if level_for_question(number) == "commander":
                keywords = HARD_ANSWER_WORDS[question["id"]]
                if language == "ko":
                    answers.append(next(keyword for keyword in keywords if any("가" <= char <= "힣" for char in keyword)))
                else:
                    answers.append(next(keyword for keyword in keywords if keyword.isascii()))
            else:
                answers.append(question["answer"])
    return answers


def test_six_dossiers_each_have_ten_complete_questions():
    assert len(DOSSIERS) == 6
    assert sum(len(dossier["questions"]) for dossier in DOSSIERS) == 60

    question_ids = set()
    for dossier in DOSSIERS:
        assert len(dossier["questions"]) == 10
        for question in dossier["questions"]:
            assert question["id"] not in question_ids
            question_ids.add(question["id"])
            assert len(question["choices"]) == 4
            assert question["answer"] in question["choices"]
            assert len(question["hints"]) == 1
            assert question["debrief"]


def test_korean_translation_covers_every_player_facing_question():
    assert set(KOREAN_DOSSIERS) == {dossier["id"] for dossier in DOSSIERS}

    for dossier in DOSSIERS:
        korean_dossier = KOREAN_DOSSIERS[dossier["id"]]
        assert korean_dossier["code_name"]
        assert set(korean_dossier["questions"]) == {
            question["id"] for question in dossier["questions"]
        }
        for question in dossier["questions"]:
            korean_question = korean_dossier["questions"][question["id"]]
            assert tuple(korean_question["choices"]) == tuple(question["choices"])
            assert korean_question["prompt"]
            assert korean_question["hints"]
            assert korean_question["debrief"]


def test_every_dossier_has_a_bilingual_background_briefing():
    dossier_ids = {dossier["id"] for dossier in DOSSIERS}
    assert set(BACKGROUNDS["en"]) == dossier_ids
    assert set(BACKGROUNDS["ko"]) == dossier_ids
    for language in ("en", "ko"):
        assert all(BACKGROUNDS[language][dossier_id] for dossier_id in dossier_ids)


def test_difficulty_rises_from_guided_to_no_options():
    assert [level_for_question(number) for number in range(1, 11)] == [
        "recruit",
        "recruit",
        "recruit",
        "analyst",
        "analyst",
        "analyst",
        "analyst",
        "commander",
        "commander",
        "commander",
    ]


def test_correct_answer_without_hint_earns_three_points():
    output = []
    dossier = DOSSIERS[0]
    question = dossier["questions"][0]

    score = play_question(
        dossier,
        question,
        1,
        10,
        input_fn=scripted_input([question["answer"]]),
        output_fn=output.append,
    )

    assert score == 3
    assert any("+3 Intelligence Points" in line for line in output)


def test_hint_costs_one_point_before_a_correct_answer():
    output = []
    dossier = DOSSIERS[1]
    question = dossier["questions"][0]

    score = play_question(
        dossier,
        question,
        1,
        10,
        input_fn=scripted_input(["H", question["answer"]]),
        output_fn=output.append,
    )

    assert score == 2
    assert any("DECRYPTED CLUE (-1 point)" in line for line in output)


def test_commander_question_accepts_a_short_analysis_without_choices():
    output = []
    dossier = DOSSIERS[0]
    question = dossier["questions"][7]

    score = play_question(
        dossier,
        question,
        8,
        10,
        input_fn=scripted_input(["flank"]),
        output_fn=output.append,
    )

    assert score == 3
    assert any("COMMANDER — NO OPTIONS" in line for line in output)
    assert not any(line.startswith("  A.") for line in output)


def test_commander_can_reveal_choices_for_one_point():
    output = []
    dossier = DOSSIERS[0]
    question = dossier["questions"][7]

    score = play_question(
        dossier,
        question,
        8,
        10,
        input_fn=scripted_input(["O", question["answer"]]),
        output_fn=output.append,
    )

    assert score == 2
    assert any("OPTIONS DECRYPTED (-1 point)" in line for line in output)


def test_one_dossier_can_earn_thirty_points():
    output = []
    dossier = DOSSIERS[2]

    score = play_dossier(
        dossier,
        input_fn=scripted_input(answers_for((dossier,))),
        output_fn=output.append,
    )

    assert score == 30
    assert any("DOSSIER COMPLETE" in line and "30/30" in line for line in output)
    assert any(line.startswith("MISSION BACKGROUND:") for line in output)


def test_all_six_dossiers_can_earn_180_points():
    output = []

    score = run_quiz(
        DOSSIERS,
        language="en",
        input_fn=scripted_input(["A", *answers_for(DOSSIERS)]),
        output_fn=output.append,
    )

    assert score == 180
    assert "FINAL INTELLIGENCE SCORE: 180/180" in output


def test_language_selection_runs_the_korean_game_text():
    output = []
    first_dossier = DOSSIERS[0]

    score = run_quiz(
        DOSSIERS,
        input_fn=scripted_input(["KO", "1", *answers_for((first_dossier,), language="ko")]),
        output_fn=output.append,
    )

    assert score == 30
    assert "DAWN INTEL: 역사 사건 파일" in output
    assert any(line.startswith("사건 배경:") for line in output)
    assert any(line.startswith("역사 해설:") for line in output)
    assert "최종 정보 점수: 30/30" in output
