"""Check the public map page before a merge.

Usage: python3 tools/check_page.py index.html <out.mjs>

The check stops with an error if:
- the page has no block that hides the rooms of the ending;
- a label, a caption or a button text of the page names the ending;
- the page has Russian text (the four Russian letters of the W A S D key handler are key codes).
It writes the module script of the page to <out.mjs>, so that "node --check" can read it.
"""
import re
import sys

ENDING_WORDS = re.compile(r"\bnest\b|shift canteen|\(draft\)|episode 5", re.I)
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
    if "const HIDE_MESH = /" not in text or "const HIDE_LABEL = /" not in text:
        faults.append("the block that hides the rooms of the ending is missing")
    hide_label = re.search(r"const HIDE_LABEL = /(.*?)/i;", text)
    hidden = re.compile(hide_label.group(1), re.I) if hide_label else None
    for pattern in (TEXT_CALLS, CAPTIONS, SHOT_TEXT):
        for match in pattern.finditer(text):
            words = match.group(1)
            if hidden and hidden.search(words):
                continue                      # the page hides this label
            if ENDING_WORDS.search(words):
                faults.append("text names the ending: " + words[:80])
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
    print("PASS check_page: the hide block is present, no text names the ending, no Russian text")


if __name__ == "__main__":
    main()
