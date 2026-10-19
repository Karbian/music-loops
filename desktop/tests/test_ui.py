"""Tk smoke checks. Use xvfb-run on Linux; these use a fake audio backend."""
from pathlib import Path
import tempfile
import threading
import time
import unittest

try:
    import tkinter as tk
    from desktop.app import Studio
except ImportError:
    tk = None

from desktop import model
from desktop.session import AudacitySession
from desktop.tests.fakes import FakeAudacity


@unittest.skipIf(tk is None, "Tkinter is not installed")
class InterfaceTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("A display or xvfb-run is required: " + str(exc))
        self.temp = tempfile.TemporaryDirectory()
        self.fake = FakeAudacity()
        self.session = AudacitySession(self.fake)
        self.app = Studio(self.root, self.session, Path(self.temp.name) / "sequence.json")
        self.root.update()

    def tearDown(self):
        if hasattr(self, "app"):
            self.app.cancel.set()
            self.app.worker.submit(-1, "close", None, threading.Event())
            self.root.destroy()
            self.temp.cleanup()

    def settle(self):
        deadline = time.monotonic() + 3
        while self.app.busy and time.monotonic() < deadline:
            self.root.update()
            time.sleep(.005)
        self.assertFalse(self.app.busy)
        self.root.update()

    def test_picture_placement_is_silent_and_repeats_show_two_rows(self):
        self.assertEqual(len(self.app.step_cards), 2)
        self.app.choose("piano")
        self.app.place(0)
        self.app.choose("bell")
        self.app.place(1)
        self.app.set_mode("count")
        self.settle()
        self.assertEqual(self.app.state["pattern"], ["piano", "bell"])
        self.assertEqual(len(self.app.preview_cards), 4)
        self.assertNotIn("Play:", self.fake.commands)

    def test_both_scales_render_all_eight_pictures_and_restore(self):
        for key in model.SCALES:
            self.app.change(model.set_collection(self.app.state, key))
            self.settle()
            self.assertEqual(len(self.app.step_cards), 8)
            self.assertEqual([c.sound for c in self.app.step_cards], list(model.SCALES[key]))
            self.app.resize("first")
            self.settle()
            self.assertEqual(len(self.app.step_cards), 2)
            self.app.change(model.example(self.app.state))
            self.settle()
            self.assertEqual(len(self.app.step_cards), 8)

    def test_communication_during_preparation_cancels_pending_play(self):
        self.session.connect(threading.Event())
        self.app.change(model.example(self.app.state))
        self.settle()
        rendering, release = threading.Event(), threading.Event()
        def wait_on_tone(command):
            if command.startswith("Tone:"):
                rendering.set()
                release.wait(2)
        self.fake.on_command = wait_on_tone
        self.app.play()
        self.assertTrue(rendering.wait(1))
        self.app.communicate("help")
        self.assertEqual(self.app.message, "help")
        release.set()
        self.settle()
        self.assertNotIn("Play:", self.fake.commands)
        self.app.return_to_studio()
        self.settle()
        self.assertIsNone(self.app.started)
        self.assertNotIn("Play:", self.fake.commands)

    def test_pictures_only_needs_no_connection_and_return_stays_silent(self):
        state = model.example(self.app.state)
        state["settings"]["visualOnly"] = True
        self.app.change(state)
        self.settle()
        self.app.play()
        self.assertIsNotNone(self.app.started)
        self.app.communicate("pause")
        self.settle()
        self.assertIsNone(self.app.started)
        self.app.return_to_studio()
        self.settle()
        self.assertNotIn("Play:", self.fake.commands)

    def test_english_settings_and_persistent_stop_controls_fit_minimum_window(self):
        self.root.geometry("960x700")
        self.app.state = model.set_collection(self.app.state, "c-major")
        self.app.state["settings"]["language"] = "en"
        self.app.render()
        self.root.update()
        self.assertEqual(self.app.t("help"), "Help")
        for widget in self.app.footer.winfo_children() + self.app.transport.winfo_children():
            self.assertTrue(widget.winfo_ismapped())
            self.assertLessEqual(widget.winfo_rootx() + widget.winfo_width(), self.root.winfo_rootx() + self.root.winfo_width())
            self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(), self.root.winfo_rooty() + self.root.winfo_height())
        self.app.show_settings()
        self.settle()
        self.assertEqual(self.app.view, "settings")


if __name__ == "__main__":
    unittest.main()
