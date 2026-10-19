"""Original vector pictures, keeping the web edition's note-to-image mapping."""
import math
import tkinter as tk

from .model import NOTES

INK = "#283e49"
PAPER = "#fffdf8"
COLORS = {"c": "#f9ecd1", "d": "#e0eff8", "e": "#e3f0df", "f": "#f6e1e0",
          "g": "#eee5f6", "a": "#e1e8fa", "b": "#f8e0e9",
          "piano": "#e0eeeb", "bell": "#fbefcc", "drum": "#f6e2d8", "rest": "#e8eaf1"}


def color(sound):
    return COLORS.get(NOTES[sound][0] if sound in NOTES else sound, PAPER)


def draw(canvas, kind, x, y, size):
    """Draw with a 100-unit coordinate system in a Tk Canvas."""
    note = NOTES.get(kind)
    symbol = note[0] if note else kind

    def coords(points):
        return [value for px, py in points for value in (x + px * size / 100, y + py * size / 100)]

    def line(points, fill=INK, width=3, **kw):
        return canvas.create_line(*coords(points), fill=fill, width=max(1, width * size / 100), **kw)

    def poly(points, fill=INK, **kw):
        return canvas.create_polygon(*coords(points), fill=fill, **kw)

    def oval(box, fill, outline=INK):
        return canvas.create_oval(*coords([(box[0], box[1]), (box[2], box[3])]),
                                  fill=fill, outline=outline, width=max(1, 2 * size / 100))

    def rect(box, fill=INK):
        return canvas.create_rectangle(*coords([(box[0], box[1]), (box[2], box[3])]), fill=fill, outline=INK, width=2)

    if symbol == "c":  # Sun
        oval((29, 29, 71, 71), "#e5b246")
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            line([(50 + 29 * math.cos(a), 50 + 29 * math.sin(a)),
                  (50 + 40 * math.cos(a), 50 + 40 * math.sin(a))], width=4)
    elif symbol == "d":
        poly([(50, 10), (25, 49), (25, 68), (35, 81), (50, 86), (65, 81), (75, 68), (75, 49)],
             fill="#75b7d4", smooth=True, outline=INK, width=2)
        line([(36, 60), (37, 69), (45, 74)], fill=PAPER, width=4, smooth=True)
    elif symbol == "e":
        poly([(16, 78), (17, 41), (43, 18), (86, 15), (83, 56), (57, 80)],
             fill="#8eb783", smooth=True, outline=INK, width=2)
        line([(17, 83), (74, 28)], width=3)
        line([(43, 58), (43, 38)], width=2)
        line([(49, 52), (68, 52)], width=2)
    elif symbol == "f":
        points = []
        for i in range(10):
            a = math.radians(-90 + i * 36)
            radius = 40 if i % 2 == 0 else 18
            points.append((50 + radius * math.cos(a), 53 + radius * math.sin(a)))
        poly(points, fill="#d78e8e", outline=INK, width=2)
    elif symbol == "g":
        for i in range(5):
            a = math.radians(-90 + i * 72)
            cx, cy = 50 + 23 * math.cos(a), 50 + 23 * math.sin(a)
            oval((cx - 17, cy - 17, cx + 17, cy + 17), "#b49acb")
        oval((36, 36, 64, 64), "#f0ce77")
    elif symbol == "a":
        poly([(72, 15), (42, 15), (20, 37), (20, 64), (40, 85), (66, 85), (85, 67),
              (61, 70), (43, 57), (42, 37)], fill="#91a6d6", smooth=True, outline=INK, width=2)
    elif symbol == "b":
        poly([(50, 85), (13, 50), (14, 26), (31, 17), (50, 32), (69, 17), (86, 26), (87, 50)],
             fill="#d78fa8", smooth=True, outline=INK, width=2)
    elif symbol == "piano":
        rect((13, 23, 87, 78), PAPER)
        for xx in (28, 43, 58, 73):
            line([(xx, 24), (xx, 77)], width=2)
        for xx in (22, 37, 67):
            rect((xx, 23, xx + 9, 56))
    elif symbol == "bell":
        poly([(18, 71), (28, 58), (28, 38), (36, 24), (50, 20), (64, 24), (72, 38), (72, 58), (82, 71)],
             fill="#e7bd59", smooth=True, outline=INK, width=3)
        line([(19, 72), (81, 72)], width=4)
        oval((43, 75, 57, 86), INK)
        oval((45, 12, 55, 23), "#e7bd59")
    elif symbol == "drum":
        rect((20, 38, 80, 77), "#db9c82")
        oval((20, 64, 80, 87), "#db9c82")
        oval((20, 26, 80, 49), PAPER)
        line([(20, 15), (69, 41)], width=4)
        line([(80, 12), (35, 41)], width=4)
    elif symbol in ("pause", "rest"):
        rect((29, 24, 42, 76))
        rect((58, 24, 71, 76))
    elif symbol == "play":
        poly([(29, 17), (83, 50), (29, 83)])
    elif symbol == "stop":
        rect((25, 25, 75, 75))
    elif symbol == "help":
        oval((15, 15, 85, 85), "#e9d7a5")
        canvas.create_text(x + size / 2, y + size / 2, text="?", fill=INK,
                           font=("TkDefaultFont", max(12, int(size * .43)), "bold"))
    elif symbol in ("done", "check"):
        line([(19, 53), (41, 76), (83, 27)], width=8, capstyle=tk.ROUND, joinstyle=tk.ROUND)
    elif symbol in ("once", "count"):
        rows = (37,) if symbol == "once" else (30, 68)
        for yy in rows:
            for xx in (23, 46, 69):
                rect((xx, yy - 9, xx + 14, yy + 5), "#9ebeb4")
        if symbol == "count":
            line([(85, 29), (94, 29), (94, 69), (85, 69)], width=3)
    else:
        line([(26, 50), (74, 50)], fill="#8f9c9f", width=4)
        line([(50, 26), (50, 74)], fill="#8f9c9f", width=4)
    if note and note[2] != 4:
        upward = note[2] == 5
        px, py = x + size * .88, y + size * .16
        direction = -1 if upward else 1
        canvas.create_line(px, py - direction * size * .07, px, py + direction * size * .07,
                           fill=INK, width=2, arrow=tk.LAST)


class PictureButton(tk.Canvas):
    """Large, focusable, click / Enter / Space target; no drag required."""
    def __init__(self, parent, sound, label, command, width=112, height=112, selected=False,
                 number=None, enabled=True):
        super().__init__(parent, width=width, height=height, bg=color(sound),
                         highlightthickness=3, highlightbackground="#557c72" if selected else color(sound),
                         highlightcolor="#294f85", takefocus=1 if enabled else 0,
                         cursor="hand2" if enabled else "arrow", borderwidth=0)
        self.sound, self.label, self.action = sound, label, command
        self.enabled, self.selected = enabled, selected
        self.w, self.h = width, height
        self.number = number
        self.redraw()
        self.bind("<Button-1>", self.activate)
        self.bind("<Return>", self.activate)
        self.bind("<space>", self.activate)

    def redraw(self):
        self.delete("all")
        size = min(self.w * .63, self.h - 36) if self.label else min(self.w * .78, self.h - 8)
        draw(self, self.sound, (self.w - size) / 2, 7, size)
        if self.number is not None:
            self.create_text(10, 11, text=str(self.number), anchor="nw", fill=INK,
                             font=("TkDefaultFont", 10, "bold"))
        if self.selected:
            self.create_text(self.w - 12, 11, text="✓", anchor="ne", fill=INK,
                             font=("TkDefaultFont", 12, "bold"))
        if self.label:
            self.create_text(self.w / 2, self.h - 18, text=self.label, fill=INK,
                             font=("TkDefaultFont", 12, "bold"), width=self.w - 8)

    def activate(self, _event=None):
        if self.enabled:
            self.focus_set()
            self.action()
        return "break"

    def mark(self, active):
        self.configure(highlightbackground="#294f85" if active else "#557c72" if self.selected else color(self.sound))
