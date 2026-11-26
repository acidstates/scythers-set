"""Check the public map page before a merge.

Usage: python3 tools/check_page.py index.html <out.mjs>

The check stops with an error if:
- the page has no block that hides the rooms of the ending;
- the hide block does not match a mesh of the ending, or the page does not have that mesh;
- the hide block matches a mesh of the staff canteen (the canteen shows on the public map);
- a label, a caption or a button text of the page names the ending;
- the page has Russian text (the four Russian letters of the W A S D key handler are key codes).
It writes the module script of the page to <out.mjs>, so that "node --check" can read it.
"""
import re
import sys

ENDING_WORDS = re.compile(r"\bnest\b|\(draft\)|episode 5", re.I)
# The meshes that the public map does not show. The hide block must match each name.
ENDING_MESHES = (
    "nestWetMass", "nestRedDepth", "nestSpiderBodies", "nestSpiderMasks", "nestSpiderLimbs",
    "glowNestWall", "glowNestDepth",
    "corridorCoffeeCabinet", "corridorCoffeeMachine", "corridorCoffeeParts", "corridorCoffeeLamp", "corridorCoffeeCups",
    "ventDraftBranchSouth", "ventDraftBranchEast", "ventDraftServerDrop", "ventDraftServerGrate", "ventDraftLinkWest",
    "ventDraftRiser", "ventDraftL2Out", "ventDraftL2North", "ventDraftL2Corridor", "ventDraftL2South",
    "serverFloor", "serverNorthWall", "serverSouthWall", "serverEastWall", "serverDoorLeaf", "serverRacks",
    "serverVentGrate", "serverVentBars",
    "ductHorizontal", "ductVertical", "ductShaftOpening", "level2StairSteps", "stairTopLight",
)
# The meshes of the staff canteen: the room, the furniture, the kitchen hood and the signs of
# level two. The hide block must match none of them.
CANTEEN_MESHES = (
    "nestFloor", "nestNorthWall", "nestNorthWallEast", "nestNorthWallLintel", "nestWestWall", "nestEastWall",
    "nestSouthWall", "nestDoorFrameLeft", "nestDoorFrameRight", "nestDoorHeader",
    "canteenTableTops", "canteenTableLegs", "canteenBenchSeats", "canteenBenchLegs", "canteenCounterBody",
    "canteenCounterTop", "canteenTrayRail", "canteenTrayRailBrackets", "canteenFoodWells", "canteenTrays",
    "canteenRange", "canteenRangeTop", "canteenHoodSkirt", "ventDraftKitchenHood",
    "signPlatesLevel2", "signFacesLevel2",
)
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
    hide_mesh = re.search(r"const HIDE_MESH = /(.*?)/i;", text)
    if hide_mesh:
        hides = re.compile(hide_mesh.group(1), re.I)
        for name in ENDING_MESHES + CANTEEN_MESHES:
            if "'%s'" % name not in text:
                faults.append("the page has no mesh with the name " + name)
        for name in ENDING_MESHES:
            if not hides.search(name):
                faults.append("the hide block does not hide a mesh of the ending: " + name)
        for name in CANTEEN_MESHES:
            if hides.search(name):
                faults.append("the hide block hides a mesh of the canteen: " + name)
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
    print("PASS check_page: the hide block hides %d meshes of the ending and none of the %d canteen meshes, "
          "no text names the ending, no Russian text" % (len(ENDING_MESHES), len(CANTEEN_MESHES)))


if __name__ == "__main__":
    main()
