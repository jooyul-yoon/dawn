# Dawn Intel: History Cases

`Dawn Intel` is a terminal quiz game about reading historical clues. It starts
with only a neutral dossier code name, not a year or flag. The player uses
terrain, tactics, technology, intelligence, and supply clues to make a call.

## Run it

On macOS, double-click `RUN_DAWN_INTEL_MAC.command` in the Dawn project folder.
The terminal stays open after the quiz so the final score remains visible.

Or run it from the Dawn project folder:

```bash
.venv/bin/python -m history_quiz.play
```

The game first asks for `EN` or `KO`. This changes the menu, all sixty
questions, clues, choices, debriefs, and score messages. Then choose one of
the six dossier numbers to play ten questions, or enter `A` to play all sixty.
Before Question 1, each dossier presents a short bilingual historical
background; press Return after reading it to begin the investigation.
Enter `A`, `B`, `C`, or `D` to make a call. Enter `H` to decrypt another clue;
each clue costs one Intelligence Point. A correct answer is worth up to three
points, and every question ends with a short historical explanation.

## Difficulty curve inside each dossier

1. Questions 1–3 are **Recruit** questions with visible choices.
2. Questions 4–7 are **Analyst** questions: the situations need closer
   comparison, but choices remain visible.
3. Questions 8–10 are **Commander** questions. There are no visible choices:
   type a short idea in English or Korean. Enter `O` to reveal choices for one
   point, or `H` for the usual one-point clue.

## Included dossiers

Each dossier contains ten clue-based questions for a maximum of 30 points.
Playing all six is a 180-point campaign.

1. `THE CLOSING WINGS` — Battle of Cannae
2. `MUD AND LONGBOWS` — Battle of Agincourt
3. `THE LONG RETREAT` — French Invasion of Russia
4. `EYES IN THE SKY` — Battle of Britain
5. `THE BROKEN CODE` — Battle of Midway
6. `TIDES OF SURPRISE` — Incheon Landing

The detailed learning focus for every dossier is in `case_ideas.md`; historical
source links are recorded in `sources.md`.

## Suggested build order

1. Play one dossier and change one clue or wrong answer.
2. Add a new question to one existing dossier.
3. Make a seventh dossier about a different era.
4. Later, replace the dictionaries with a `CaseFile` class.
