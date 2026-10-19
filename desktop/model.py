"""The same portable sequence format used by the web edition."""
import copy
import json
import math
from pathlib import Path

LEVELS = {"first": 2, "next": 4, "explore": 8}
BASIC = ("piano", "bell", "drum", "rest")
NOTES = {
    "note-" + key: (letter, midi, octave)
    for key, letter, midi, octave in (
        ("a3", "a", 57, 3), ("b3", "b", 59, 3), ("c4", "c", 60, 4),
        ("d4", "d", 62, 4), ("e4", "e", 64, 4), ("f4", "f", 65, 4),
        ("g4", "g", 67, 4), ("a4", "a", 69, 4), ("b4", "b", 71, 4),
        ("c5", "c", 72, 5),
    )
}
SCALES = {
    "c-major": tuple("note-" + n for n in ("c4", "d4", "e4", "f4", "g4", "a4", "b4", "c5")),
    "a-minor": tuple("note-" + n for n in ("a3", "b3", "c4", "d4", "e4", "f4", "g4", "a4")),
}


def defaults():
    return {"schemaVersion": 2, "collection": "sounds", "level": "first",
            "pattern": [None, None], "mode": "once",
            "settings": {"language": "es", "tempo": 72, "volume": 18,
                         "visualOnly": False, "highlight": True}}


def palette(state):
    collection = state["collection"]
    if collection in SCALES:
        return list(SCALES[collection])
    return list({"first": BASIC[:2], "next": ("piano", "bell", "rest"),
                 "explore": BASIC}[state["level"]])


def number(value, fallback, low, high):
    try:
        result = float(value)
        return max(low, min(high, result)) if math.isfinite(result) else fallback
    except (TypeError, ValueError, OverflowError):
        return fallback


def normalize(raw):
    if not isinstance(raw, dict) or type(raw.get("schemaVersion")) is not int or raw["schemaVersion"] not in (1, 2):
        raise ValueError("Choose a Mi Ritmo version 1 or 2 JSON file.")
    state = defaults()
    if raw["schemaVersion"] == 2 and isinstance(raw.get("collection"), str) and raw["collection"] in SCALES:
        state["collection"] = raw["collection"]
    if isinstance(raw.get("level"), str) and raw["level"] in LEVELS:
        state["level"] = raw["level"]
    source = raw.get("pattern") if isinstance(raw.get("pattern"), list) else []
    allowed = palette(state)
    state["pattern"] = [source[i] if i < len(source) and source[i] in allowed else None
                        for i in range(LEVELS[state["level"]])]
    state["mode"] = "count" if raw.get("mode") in ("count", "while") else "once"
    settings = raw.get("settings") if isinstance(raw.get("settings"), dict) else {}
    state["settings"]["language"] = "en" if settings.get("language") == "en" else "es"
    tempo = number(settings.get("tempo", 72), 72, 60, 90)
    state["settings"]["tempo"] = int(tempo) if tempo in (60, 72, 90) else 72
    state["settings"]["volume"] = int(number(settings.get("volume", 18), 18, 0, 40) + 0.5)
    state["settings"]["visualOnly"] = settings.get("visualOnly") is True
    state["settings"]["highlight"] = settings.get("highlight") is not False
    return state


def set_collection(state, collection):
    result = copy.deepcopy(state)
    if collection in SCALES:
        result.update(collection=collection, level="explore", pattern=list(SCALES[collection]), mode="once")
    elif collection == "sounds":
        result.update(collection=collection, level="first", pattern=[None, None], mode="once")
    return normalize(result)


def example(state):
    if state["collection"] in SCALES:
        return set_collection(state, state["collection"])
    result = copy.deepcopy(state)
    result["pattern"] = ["piano" if i % 2 == 0 else "bell" for i in range(len(result["pattern"]))]
    return normalize(result)


def events(state):
    if not state["pattern"] or not all(sound in palette(state) for sound in state["pattern"]):
        return []
    return state["pattern"] * (2 if state["mode"] == "count" else 1)


def frequency(sound):
    if sound in NOTES:
        return 440 * 2 ** ((NOTES[sound][1] - 69) / 12)
    return {"piano": 261.6255653, "bell": 880.0, "drum": 98.0, "rest": 440.0}[sound]


def load(path, current_volume=40):
    path = Path(path)
    if path.stat().st_size > 51200:
        raise ValueError("Mi Ritmo files must be at most 50 KB.")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(raw, dict) or not isinstance(raw.get("pattern"), list)
            or not isinstance(raw.get("level"), str) or raw["level"] not in LEVELS):
        raise ValueError("Invalid Mi Ritmo sequence.")
    result = normalize(raw)
    result["settings"]["volume"] = min(current_volume, result["settings"]["volume"])
    return result


def save(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(normalize(state), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
