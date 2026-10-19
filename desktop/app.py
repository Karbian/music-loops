"""Run with python -m desktop.app, or with the platform launcher."""
import copy
from pathlib import Path
import queue
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from . import model
from .pictures import INK, PAPER, PictureButton, draw
from .session import AudacitySession, Cancelled, Take
from .text import TEXT

BACKGROUND = "#f4f2eb"
SETUP_URL = "https://github.com/Karbian/music-loops/blob/main/desktop/README.md"


class Worker:
    """One FIFO worker: a queued Stop always precedes any later Listen."""
    def __init__(self, session):
        self.session, self.tasks, self.results = session, queue.Queue(), queue.Queue()
        threading.Thread(target=self.run, daemon=True).start()

    def submit(self, token, kind, state, cancel):
        self.tasks.put((token, kind, state, cancel))

    def run(self):
        while True:
            token, kind, state, cancel = self.tasks.get()
            try:
                if kind == "stop":
                    self.session.stop()
                    result = None
                elif kind == "connect":
                    self.session.connect(cancel)
                    result = None
                elif kind == "play":
                    result = self.session.render_and_play(state, cancel)
                elif kind == "close":
                    self.session.stop()
                    self.session.close()
                    self.results.put((token, kind, None, None))
                    return
                self.results.put((token, kind, result, None))
            except Cancelled:
                self.results.put((token, kind, None, "cancelled"))
            except Exception as exc:
                self.session.connected = False
                self.results.put((token, kind, None, str(exc)))


class Studio:
    def __init__(self, root, session=None, save_path=None):
        self.root = root
        self.save_path = Path(save_path) if save_path else Path.home() / ".mi-ritmo" / "desktop-v2.json"
        self.state = model.defaults()
        self.saved = True
        if self.save_path.exists():
            try:
                self.state = model.load(self.save_path)
            except (OSError, ValueError, TypeError):
                self.saved = False
        self.selected = None
        self.history = []
        self.session = session if session is not None else AudacitySession()
        self.worker = Worker(self.session)
        self.cancel = threading.Event()
        self.token, self.busy, self.closing = 0, False, False
        self.view, self.message = "studio", None
        self.started = None
        self.take = None
        self.status_key = "ready"
        self.error_detail = ""
        self.step_cards, self.preview_cards = [], []
        self.root.title("Mi Ritmo 2.0 · Audacity")
        self.root.geometry("1100x820")
        self.root.minsize(960, 700)
        self.root.configure(bg=BACKGROUND)
        self.root.option_add("*Font", "TkDefaultFont 13")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Escape>", lambda _e: self.halt())
        self.header = tk.Frame(root, bg=BACKGROUND)
        self.header.pack(fill="x", padx=24, pady=(16, 6))
        self.footer = tk.Frame(root, bg=PAPER, padx=14, pady=10)
        self.footer.pack(side="bottom", fill="x")
        self.status = tk.StringVar(value=self.t("ready"))
        self.status_label = tk.Label(root, textvariable=self.status, bg=BACKGROUND, fg=INK,
                                     anchor="w", padx=24, pady=8)
        self.status_label.pack(side="bottom", fill="x")
        self.transport = tk.Frame(root, bg=BACKGROUND, padx=24, pady=4)
        self.transport.pack(side="bottom", fill="x")
        container = tk.Frame(root, bg=BACKGROUND)
        container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(container, bg=BACKGROUND, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(self.canvas, bg=BACKGROUND, padx=24, pady=8)
        self.body_id = self.canvas.create_window(0, 0, window=self.body, anchor="nw")
        self.body.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.body_id, width=e.width))
        self.root.bind("<MouseWheel>", self.wheel)
        self.root.bind("<Button-4>", lambda _e: self.canvas.yview_scroll(-1, "units"))
        self.root.bind("<Button-5>", lambda _e: self.canvas.yview_scroll(1, "units"))
        self.render()
        self.root.after(40, self.poll)

    def t(self, key):
        return TEXT[self.state["settings"]["language"]].get(key, key)

    def label(self, sound):
        return self.t(model.NOTES[sound][0] if sound in model.NOTES else sound or "empty")

    def wheel(self, event):
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def text(self, parent, value, size=14, bold=False, **kw):
        label = tk.Label(parent, text=value, bg=parent["bg"], fg=INK,
                         font=("TkDefaultFont", size, "bold" if bold else "normal"), **kw)
        label.pack(anchor="w", pady=(4, 8))
        return label

    def button(self, parent, label, command, enabled=True):
        return tk.Button(parent, text=label, command=command, bg=PAPER, fg=INK,
                         activebackground="#e0eeeb", padx=14, pady=10,
                         relief="flat", highlightthickness=2, highlightcolor="#294f85",
                         state="normal" if enabled else "disabled")

    def set_status(self, key):
        self.status_key = key
        self.status.set(self.t(key))

    def persist(self):
        try:
            model.save(self.save_path, self.state)
            self.saved = True
        except OSError:
            self.saved = False

    def render(self):
        focused = self.root.focus_get()
        focus_key = getattr(focused, "focus_key", None)
        for frame in (self.header, self.body, self.footer, self.transport):
            for child in frame.winfo_children():
                child.destroy()
        self.step_cards, self.preview_cards = [], []
        tk.Label(self.header, text="Mi Ritmo", bg=BACKGROUND, fg=INK,
                 font=("TkDefaultFont", 24, "bold")).pack(side="left")
        tk.Label(self.header, text="  2.0 · Audacity", bg=BACKGROUND, fg="#557c72").pack(side="left")
        self.button(self.header, self.t("adult"), self.show_settings).pack(side="right")
        tk.Label(self.footer, text=self.t("say"), bg=PAPER, fg=INK,
                 font=("TkDefaultFont", 15, "bold")).pack(side="left", padx=(0, 20))
        for key in ("pause", "help", "done"):
            card = PictureButton(self.footer, key, self.t(key), lambda k=key: self.communicate(k), width=156, height=87)
            card.focus_key = "communication-" + key
            card.pack(side="left", padx=8)
        if self.message:
            self.render_message()
        elif self.view == "settings":
            self.render_settings()
        else:
            self.render_studio()
        self.status.set(self.t(self.status_key))
        def restore(parent):
            for child in parent.winfo_children():
                if focus_key and getattr(child, "focus_key", None) == focus_key:
                    child.focus_set()
                restore(child)
        restore(self.root)

    def render_studio(self):
        self.text(self.body, self.t("title"), 23, True)
        if self.state["collection"] in model.SCALES:
            self.text(self.body, self.t(self.state["collection"]), 16, True)
        self.text(self.body, self.t("choose"), 15, True)
        palette_row = tk.Frame(self.body, bg=BACKGROUND)
        palette_row.pack(anchor="w")
        sounds = model.palette(self.state)
        width = 98 if len(sounds) > 4 else 126
        for sound in sounds:
            card = PictureButton(palette_row, sound, self.label(sound), lambda s=sound: self.choose(s),
                                 width=width, height=104, selected=self.selected == sound)
            card.focus_key = "sound-" + sound
            card.pack(side="left", padx=(0, 8), pady=4)
        row = tk.Frame(self.body, bg=BACKGROUND)
        row.pack(fill="x", pady=(10, 0))
        self.text(row, self.t("place"), 15, True)
        sequence = tk.Frame(self.body, bg=BACKGROUND)
        sequence.pack(anchor="w")
        width = 98 if len(self.state["pattern"]) > 4 else 126
        for i, sound in enumerate(self.state["pattern"]):
            card = PictureButton(sequence, sound, self.label(sound), lambda index=i: self.place(index),
                                 width=width, height=114, number=i + 1)
            card.focus_key = "step-" + str(i)
            card.pack(side="left", padx=(0, 8), pady=4)
            self.step_cards.append(card)
        mode = tk.Frame(self.body, bg=BACKGROUND)
        mode.pack(fill="x", pady=(12, 4))
        for key in ("once", "count"):
            card = PictureButton(mode, key, self.t(key), lambda k=key: self.set_mode(k),
                                 width=125, height=88, selected=self.state["mode"] == key)
            card.focus_key = "mode-" + key
            card.pack(side="left", padx=(0, 12))
        previews = tk.Frame(mode, bg=BACKGROUND)
        previews.pack(side="left", padx=(12, 0))
        for cycle in range(2 if self.state["mode"] == "count" else 1):
            row = tk.Frame(previews, bg=BACKGROUND)
            row.pack(anchor="w", pady=2)
            for index, sound in enumerate(self.state["pattern"]):
                mini = PictureButton(row, sound, "", lambda: None, width=42, height=40, enabled=False)
                mini.pack(side="left", padx=2)
                self.preview_cards.append((cycle, index, mini))
        controls = self.transport
        self.play_card = PictureButton(controls, "play", self.t("play"), self.play, width=155, height=80, enabled=not self.busy)
        self.play_card.focus_key = "play"
        self.play_card.pack(side="left", padx=(0, 12))
        stop_card = PictureButton(controls, "stop", self.t("stop"), self.halt, width=125, height=80)
        stop_card.focus_key = "stop"
        stop_card.pack(side="left", padx=(0, 24))
        self.button(controls, self.t("undo"), self.undo, bool(self.history)).pack(side="left", padx=4)
        self.button(controls, self.t("scale" if self.state["collection"] in model.SCALES else "example"),
                    lambda: self.change(model.example(self.state))).pack(side="left", padx=4)

    def render_message(self):
        panel = tk.Frame(self.body, bg=PAPER, padx=40, pady=35)
        panel.pack(fill="both", expand=True, pady=20)
        icon = tk.Canvas(panel, width=170, height=170, bg=PAPER, highlightthickness=0)
        draw(icon, self.message, 10, 10, 150)
        icon.pack(pady=10)
        self.text(panel, self.t(self.message + "_title"), 28, True)
        self.text(panel, self.t(self.message + "_copy"), 18, wraplength=740, justify="left")
        self.text(panel, self.t("silent_return"), 15)
        self.button(panel, self.t("back"), self.return_to_studio).pack(anchor="w", pady=20)

    def render_settings(self):
        self.text(self.body, self.t("adult"), 23, True)
        self.text(self.body, self.t("connected" if self.session.connected else "not_connected"), 16, True)
        self.text(self.body, self.t("connection_note"), wraplength=840, justify="left")
        connection = tk.Frame(self.body, bg=BACKGROUND)
        connection.pack(anchor="w", pady=(0, 8))
        self.button(connection, self.t("connect"), self.connect, not self.busy).pack(side="left", padx=(0, 12))
        self.button(connection, self.t("setup"), lambda: webbrowser.open(SETUP_URL)).pack(side="left")
        if self.error_detail:
            self.text(self.body, self.error_detail, 12, wraplength=840, justify="left")
        choices = (
            ("collection", ("sounds", "c-major", "a-minor"), self.state["collection"], lambda value: self.change(model.set_collection(self.state, value))),
            ("level", ("first", "next", "explore"), self.state["level"], self.resize),
            ("language", ("es", "en"), self.state["settings"]["language"], lambda value: self.setting("language", value)),
            ("speed", (60, 72, 90), self.state["settings"]["tempo"], lambda value: self.setting("tempo", value)),
        )
        form = tk.Frame(self.body, bg=BACKGROUND)
        form.pack(anchor="w", pady=8)
        for row_number, (key, values, current, action) in enumerate(choices):
            tk.Label(form, text=self.t(key), bg=BACKGROUND, fg=INK).grid(row=row_number, column=0, sticky="w", padx=(0, 20), pady=9)
            names = [str(model.LEVELS[v]) if key == "level" else ("Español" if v == "es" else "English") if key == "language" else self.t(str(v)) for v in values]
            widget = ttk.Combobox(form, values=names, state="readonly", width=34)
            widget.current(values.index(current))
            widget.grid(row=row_number, column=1, sticky="w", pady=9)
            widget.bind("<<ComboboxSelected>>", lambda _e, w=widget, vals=values, fn=action: fn(vals[w.current()]))
        volume_row = tk.Frame(self.body, bg=BACKGROUND)
        volume_row.pack(anchor="w")
        self.text(volume_row, self.t("volume"), 13)
        volume = tk.Scale(volume_row, from_=0, to=40, orient="horizontal", length=350,
                          bg=BACKGROUND, fg=INK, highlightthickness=0)
        volume.set(self.state["settings"]["volume"])
        volume.pack(anchor="w")
        def volume_changed(_value):
            self.state["settings"]["volume"] = volume.get()
            self.persist()
        volume.configure(command=volume_changed)
        for key, name in (("visualOnly", "visual_only"), ("highlight", "highlight")):
            value = tk.BooleanVar(value=self.state["settings"][key])
            tk.Checkbutton(self.body, text=self.t(name), variable=value, bg=BACKGROUND, fg=INK,
                           command=lambda k=key, v=value: self.setting(k, v.get()), pady=7).pack(anchor="w")
        self.text(self.body, self.t("takes"), 12, wraplength=840, justify="left")
        self.text(self.body, self.t("adult_note"), 12, wraplength=840, justify="left")
        files = tk.Frame(self.body, bg=BACKGROUND)
        files.pack(anchor="w", pady=10)
        for key, action in (("save", self.export_file), ("open", self.import_file),
                            ("clear", lambda: self.change({**self.state, "pattern": [None] * len(self.state["pattern"])}))):
            self.button(files, self.t(key), action).pack(side="left", padx=(0, 10))
        self.text(self.body, self.t("saved" if self.saved else "unsaved"), 12)
        self.button(self.body, self.t("back"), self.return_to_studio).pack(anchor="w", pady=12)

    def halt(self, status="stopped"):
        if self.closing:
            return self.token
        self.cancel.set()  # Immediate and independent of a blocked audio request.
        self.token += 1
        self.started = self.take = None
        self.busy = True
        self.worker.submit(self.token, "stop", None, threading.Event())
        self.set_status(status)
        self.mark(-1)
        return self.token

    def change(self, state):
        self.halt()
        self.history.append(copy.deepcopy(self.state))
        self.history = self.history[-25:]
        self.state = model.normalize(state)
        if self.selected not in model.palette(self.state):
            self.selected = None
        self.persist()
        self.set_status("ready")
        self.render()

    def choose(self, sound):
        self.halt()
        self.selected = sound
        self.set_status("selected")
        self.render()

    def place(self, index):
        if self.selected is None:
            self.set_status("choose_first")
            return
        state = copy.deepcopy(self.state)
        state["pattern"][index] = self.selected
        self.change(state)

    def resize(self, level):
        state = copy.deepcopy(self.state)
        state["level"] = level
        self.change(state)

    def setting(self, name, value):
        state = copy.deepcopy(self.state)
        state["settings"][name] = value
        self.change(state)

    def set_mode(self, mode):
        self.change({**self.state, "mode": mode})

    def undo(self):
        if self.history:
            self.halt()
            self.state = self.history.pop()
            self.selected = None
            self.persist()
            self.render()

    def communicate(self, message):
        self.halt()
        self.message = message
        self.render()
        self.canvas.yview_moveto(0)

    def show_settings(self):
        self.halt()
        self.message = None
        self.view = "settings"
        self.render()
        self.canvas.yview_moveto(0)

    def return_to_studio(self):
        self.halt()
        self.message, self.view = None, "studio"
        self.set_status("silent_return")
        self.render()
        self.canvas.yview_moveto(0)

    def connect(self):
        if self.busy:
            return
        self.token += 1
        self.cancel = threading.Event()
        self.busy = True
        self.error_detail = ""
        self.worker.submit(self.token, "connect", None, self.cancel)
        self.set_status("connecting")
        self.render()

    def play(self):
        if self.busy or self.message or self.view != "studio":
            return
        sounds = model.events(self.state)
        if not sounds:
            self.set_status("fill")
            return
        silent = self.state["settings"]["visualOnly"] or self.state["settings"]["volume"] == 0
        if not silent and not self.session.connected:
            self.set_status("connect_first")
            return
        self.token += 1
        self.cancel = threading.Event()
        self.busy = True
        if silent:
            beat = 60 / self.state["settings"]["tempo"]
            self.begin(Take(0, beat * len(sounds), beat, tuple(sounds)))
        else:
            self.worker.submit(self.token, "play", copy.deepcopy(self.state), self.cancel)
            self.set_status("preparing")
        self.render()

    def begin(self, take):
        self.take, self.started = take, time.monotonic()
        self.set_status("visual" if self.state["settings"]["visualOnly"] or self.state["settings"]["volume"] == 0 else "playing")

    def mark(self, event_index):
        if not self.state["settings"]["highlight"]:
            event_index = -1
        length = len(self.state["pattern"])
        for i, card in enumerate(self.step_cards):
            card.mark(event_index >= 0 and i == event_index % length)
        for cycle, index, card in self.preview_cards:
            card.mark(event_index >= 0 and cycle == event_index // length and index == event_index % length)

    def poll(self):
        while True:
            try:
                token, kind, result, error = self.worker.results.get_nowait()
            except queue.Empty:
                break
            if token != self.token:
                continue
            if self.closing:
                if error:
                    messagebox.showerror("Mi Ritmo", self.t("stop_failed") + "\n\n" + error)
                self.root.destroy()
                return
            if error and error != "cancelled":
                self.error_detail = error
                self.busy = False
                self.set_status("stop_failed" if kind == "stop" else "error")
            elif kind == "play" and not self.cancel.is_set() and result is not None:
                self.begin(result)
            else:
                self.busy = False
                if kind == "connect" and not error:
                    self.set_status("connected")
            self.render()
        if self.started is not None and self.take is not None:
            elapsed = time.monotonic() - self.started
            if elapsed >= self.take.duration:
                self.halt("complete")
                self.render()
            else:
                self.mark(int(elapsed / self.take.beat))
        self.root.after(40, self.poll)

    def export_file(self):
        self.halt()
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="mi-ritmo-v2.json", filetypes=[("Mi Ritmo JSON", "*.json")])
        if path:
            try:
                model.save(path, self.state)
            except OSError as exc:
                messagebox.showerror("Mi Ritmo", str(exc))

    def import_file(self):
        self.halt()
        path = filedialog.askopenfilename(filetypes=[("Mi Ritmo JSON", "*.json")])
        if path:
            try:
                self.change(model.load(path, self.state["settings"]["volume"]))
            except (OSError, ValueError, TypeError):
                messagebox.showerror("Mi Ritmo", self.t("invalid"))

    def close(self):
        if self.closing:
            return
        self.cancel.set()
        self.started = self.take = None
        self.token += 1
        self.closing, self.busy = True, True
        self.persist()
        self.set_status("closing")
        self.worker.submit(self.token, "close", None, threading.Event())


def main():
    root = tk.Tk()
    Studio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
