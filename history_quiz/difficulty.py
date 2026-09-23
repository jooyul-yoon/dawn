"""Progressive difficulty rules and accepted short answers for final questions."""


def level_for_question(number):
    """Return the lesson-like difficulty tier for a question's position."""
    if number <= 3:
        return "recruit"
    if number <= 7:
        return "analyst"
    return "commander"


def normalize(answer):
    """Make English and Korean typed answers easier to compare."""
    return " ".join(answer.casefold().replace("-", " ").split())


HARD_ANSWER_WORDS = {
    "cannae-08": ("flank", "flanks", "side", "sides", "측면"),
    "cannae-09": ("double envelopment", "envelopment", "양쪽 포위", "포위"),
    "cannae-10": ("terrain", "maneuver", "manoeuver", "지형", "기동"),
    "agincourt-08": ("terrain", "mud", "ground", "지형", "진흙"),
    "agincourt-09": ("medieval", "archers", "knights", "중세", "궁수", "기사"),
    "agincourt-10": ("terrain", "weapons", "formation", "지형", "무기", "대형"),
    "russia-08": ("moscow", "winter retreat", "모스크바", "겨울 후퇴"),
    "russia-09": ("supply", "logistics", "보급", "병참"),
    "russia-10": ("logistics", "political", "supply", "병참", "정치", "보급"),
    "britain-08": ("reaction time", "positioning", "reaction", "대응 시간", "위치"),
    "britain-09": ("communication", "information", "action", "통신", "정보", "행동"),
    "britain-10": ("information", "resources", "focus", "정보", "자원", "집중"),
    "midway-08": ("vulnerable", "transition", "refueling", "rearming", "취약", "전환", "급유", "재무장"),
    "midway-09": ("ambush", "intelligence", "information", "매복", "정보"),
    "midway-10": ("positioning", "information", "intelligence", "위치 선정", "정보"),
    "incheon-08": ("timing", "navigation", "reconnaissance", "타이밍", "항해", "정찰"),
    "incheon-09": ("surprise", "risk", "기습", "위험"),
    "incheon-10": ("tides", "terrain", "logistics", "조수", "지형", "병참"),
}


def matches_short_answer(question_id, answer):
    """Accept a concise idea or key term for an expert-level answer."""
    normalized_answer = normalize(answer)
    return any(
        normalize(keyword) in normalized_answer
        for keyword in HARD_ANSWER_WORDS[question_id]
    )
