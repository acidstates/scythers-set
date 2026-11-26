"""Check the public map page before a merge.

Usage: python3 tools/check_page.py index.html <out.mjs>

The check stops with an error in each of these cases:
- The page has a block that hides a part of the map. The public map shows the whole map.
- A part of the map is not in the page.
- A text of the ending is not in the page, or Play stops before the ending. The public map hides nothing.
- A label, a caption or a button text of the page has a draft word.
- The page has Russian text. The four Russian letters of the W A S D key handler are key codes.
It writes the module script of the page to <out.mjs>, so that "node --check" can read it.
"""
import re
import sys

# The marks of a block that hides a part of the map.
HIDE_MARKS = ("HIDE_MESH", "HIDE_LABEL", "pubhide", "btns.level2.style.display")
# One mesh name or one button for each part of the map that an older page did not show.
MAP_PARTS = (
    "'nestFloor'", "'canteenTableTops'", "'canteenCounterBody'", "'ventDraftKitchenHood'", "'signPlatesLevel2'",
    "'nestWetMass'", "'nestSpiderBodies'", "'glowNestWall'", "'corridorCoffeeMachine'", "'serverRacks'",
    "'ductHorizontal'", "'ventDraftRiser'", "'level2StairSteps'", "addBtn('level2', 'Level two')",
)
DRAFT_WORDS = re.compile(r"\(draft\)|episode 5", re.I)
# The words of the ending that an older page took out of the labels, and the last chapters of Play.
ENDING_TEXTS = (
    "'Shift canteen: the nest'", "the shift canteen (the nest)", "'Duct to the canteen hood, to the nest'",
    '"The canteen is the nest"', '"Black: the title. The film ends"',
)
# The text of a Play that stops before the ending.
PLAY_STOP = "not on the public map"
TEXT_CALLS = re.compile(r"(?:label|planLbl|lbl|ventLabel|addBtn)\((?:'[^']*', )?[`']([^`']*)[`']")
CAPTIONS = re.compile(r"cap\$\.innerHTML = '([^']*)'")
SHOT_TEXT = re.compile(r"txt: '([^']*)'")
KEYBOARD = re.compile(r"k === '[wsad]' \|\| k === '[цыфв]'")
CYRILLIC = re.compile(r"[Ѐ-ӿ]")


def main():
    page, out = sys.argv[1], sys.argv[2]
    with open(page, encoding="utf-8") as fh:
        text = fh.read()
    faults = []
    for mark in HIDE_MARKS:
        if mark in text:
            faults.append("the page hides a part of the map: " + mark)
    for part in MAP_PARTS:
        if part not in text:
            faults.append("a part of the map is not in the page: " + part)
    for words in ENDING_TEXTS:
        if words not in text:
            faults.append("a text of the ending is not in the page: " + words)
    if PLAY_STOP in text:
        faults.append("Play stops before the ending: " + PLAY_STOP)
    for pattern in (TEXT_CALLS, CAPTIONS, SHOT_TEXT):
        for match in pattern.finditer(text):
            words = match.group(1)
            if DRAFT_WORDS.search(words):
                faults.append("text has a draft word: " + words[:80])
    for number, line in enumerate(text.split("\n"), 1):
        if CYRILLIC.search(line) and not KEYBOARD.search(line):
            faults.append("Russian text in line %d" % number)
    module = re.search(r'<script type="module">(.*?)</script>', text, re.S)
    if not module:
        faults.append("the module script is missing")
    else:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(module.group(1))
    for fault in faults:
        print("FAIL", fault)
    if faults:
        raise SystemExit(1)
    print("PASS check_page: no block hides a part of the map, the %d map parts are in the page, "
          "the %d texts of the ending are in the page, Play runs to the end, "
          "no text has a draft word, no Russian text" % (len(MAP_PARTS), len(ENDING_TEXTS)))


if __name__ == "__main__":
    main()
