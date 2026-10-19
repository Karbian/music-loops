import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

from desktop import model
from desktop.pipe import AudacityError, PipeClient, PipeTimeout, decode_reply
from desktop.session import AudacitySession, Cancelled, note_commands
from desktop.tests.fakes import FakeAudacity


class ModelTests(unittest.TestCase):
    def test_starts_with_two_empty_spaces_and_two_pictures(self):
        state = model.defaults()
        self.assertEqual(state["pattern"], [None, None])
        self.assertEqual(model.palette(state), ["piano", "bell"])
        self.assertEqual(model.events(state), [])

    def test_two_complete_scales_and_exact_intervals(self):
        for key, midis, intervals in (
            ("c-major", [60, 62, 64, 65, 67, 69, 71, 72], [2, 2, 1, 2, 2, 2, 1]),
            ("a-minor", [57, 59, 60, 62, 64, 65, 67, 69], [2, 1, 2, 2, 1, 2, 2]),
        ):
            state = model.set_collection(model.defaults(), key)
            values = [model.NOTES[n][1] for n in state["pattern"]]
            self.assertEqual(values, midis)
            self.assertEqual([b - a for a, b in zip(values, values[1:])], intervals)
            self.assertEqual(len(model.events(state)), 8)
            state["mode"] = "count"
            self.assertEqual(model.events(state), state["pattern"] * 2)

    def test_frequency_is_tuned_and_octave_is_double(self):
        self.assertAlmostEqual(model.frequency("note-a4"), 440)
        self.assertAlmostEqual(model.frequency("note-a4") / model.frequency("note-a3"), 2)
        self.assertAlmostEqual(model.frequency("note-c5") / model.frequency("note-c4"), 2)

    def test_legacy_loop_is_finite_and_validation_discards_unknown_cards(self):
        raw = {"schemaVersion": 1, "level": "first", "pattern": ["piano", "bell"], "mode": "while"}
        self.assertEqual(model.events(model.normalize(raw)), ["piano", "bell"] * 2)
        raw.update(schemaVersion=2, collection="c-major", level="explore", pattern=["note-a3", "note-c4", 'Play:\nDelete:'])
        normalized = model.normalize(raw)
        self.assertEqual(normalized["pattern"][:3], [None, "note-c4", None])

    def test_bad_values_and_untrusted_objects_do_not_reach_commands(self):
        raw = model.defaults()
        raw.update(collection=[], level={})
        raw["settings"].update(volume=float("inf"), tempo="faster")
        state = model.normalize(raw)
        self.assertEqual(state["settings"]["volume"], 18)
        self.assertEqual(state["settings"]["tempo"], 72)
        self.assertEqual(state["collection"], "sounds")
        for invalid in (None, [], {}, {"schemaVersion": True}, {"schemaVersion": 9}):
            with self.assertRaises(ValueError):
                model.normalize(invalid)

    def test_json_round_trip_import_volume_limit_and_file_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sequence.json"
            state = model.set_collection(model.defaults(), "a-minor")
            model.save(path, state)
            self.assertEqual(model.load(path), state)
            self.assertEqual(model.load(path, current_volume=7)["settings"]["volume"], 7)
            path.write_text(" " * 51201)
            with self.assertRaises(ValueError):
                model.load(path)

    @unittest.skipUnless(shutil.which("node"), "Node is only needed for the web/desktop compatibility check")
    def test_web_and_desktop_have_identical_scale_and_default_data(self):
        root = Path(__file__).resolve().parents[2]
        script = "const m=require('./assets/core.js'); console.log(JSON.stringify({defaults:m.defaults(),scales:Object.fromEntries(Object.entries(m.SCALES).map(([k,v])=>[k,v.notes]))}));"
        web = json.loads(subprocess.check_output(["node", "-e", script], cwd=root, text=True))
        self.assertEqual(web["defaults"], model.defaults())
        self.assertEqual(web["scales"], {k: list(v) for k, v in model.SCALES.items()})


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeAudacity()
        self.session = AudacitySession(self.fake)
        self.cancel = threading.Event()

    def connect(self):
        self.session.connect(self.cancel)

    def test_connect_is_silent_and_only_claims_an_empty_project(self):
        self.connect()
        self.assertTrue(self.session.connected)
        self.assertFalse(any(c.startswith(("Tone:", "Play:")) for c in self.fake.commands))
        self.assertEqual(self.fake.tracks[0]["name"], self.session.track_name)

    def test_existing_music_is_not_modified(self):
        self.fake.tracks = [{"name": "An existing song", "kind": "wave", "channels": 1, "end": 42}]
        before = copy.deepcopy(self.fake.tracks)
        with self.assertRaises(AudacityError):
            self.connect()
        self.assertEqual(self.fake.tracks, before)
        self.assertNotIn("NewMonoTrack:", self.fake.commands)

    def test_missing_capability_refuses_before_creating_track(self):
        self.fake.available.remove("Tone")
        with self.assertRaisesRegex(AudacityError, "Tone"):
            self.connect()
        self.assertEqual(self.fake.tracks, [])

    def test_scale_tones_have_correct_frequencies_and_fades(self):
        self.connect()
        state = model.set_collection(model.defaults(), "c-major")
        take = self.session.render_and_play(state, self.cancel)
        tones = [c for c in self.fake.commands if c.startswith("Tone:")]
        self.assertEqual(len(tones), 8)
        for tone, sound in zip(tones, state["pattern"]):
            self.assertIn(f"Frequency={model.frequency(sound):.8f}", tone)
            self.assertIn("Amplitude=0.063000", tone)
        self.assertEqual(self.fake.commands.count("FadeIn:"), 8)
        self.assertEqual(self.fake.commands.count("FadeOut:"), 8)
        self.assertAlmostEqual(take.duration, 8 * 60 / 72)
        self.assertEqual(self.fake.commands[-1], "Play:")

    def test_two_pass_minor_scale_is_rendered_exactly_twice(self):
        self.connect()
        state = model.set_collection(model.defaults(), "a-minor")
        state["mode"] = "count"
        take = self.session.render_and_play(state, self.cancel)
        tones = [c for c in self.fake.commands if c.startswith("Tone:")]
        self.assertEqual(len(tones), 16)
        self.assertEqual(tones[:8], tones[8:])
        self.assertEqual(take.sounds, tuple(state["pattern"] * 2))

    def test_second_take_starts_after_previous_audio(self):
        self.connect()
        state = model.example(model.defaults())
        first = self.session.render_and_play(state, self.cancel)
        second = self.session.render_and_play(state, self.cancel)
        self.assertGreaterEqual(second.start, first.start + first.duration)
        self.assertAlmostEqual(second.start, round(first.duration, 6) + .25, places=5)
        self.assertFalse(any(c.split(":")[0] in {"Delete", "RemoveTracks", "Close", "OpenProject2", "SaveProject2"} for c in self.fake.commands))

    def test_cancelling_during_render_never_reaches_play(self):
        self.connect()
        self.fake.on_command = lambda command: self.cancel.set() if command.startswith("Tone:") else None
        with self.assertRaises(Cancelled):
            self.session.render_and_play(model.example(model.defaults()), self.cancel)
        self.assertNotIn("Play:", self.fake.commands)
        self.assertEqual(self.fake.commands[-1], "Stop:")

    def test_cancelling_immediately_before_play_never_reaches_play(self):
        self.connect()
        state = model.example(model.defaults())
        # Final full-take selection: it happens only after all rendering/fades.
        self.fake.on_command = lambda command: self.cancel.set() if command.startswith("Select:") and "End=1.666667" in command else None
        with self.assertRaises(Cancelled):
            self.session.render_and_play(state, self.cancel)
        self.assertNotIn("Play:", self.fake.commands)

    def test_cancel_during_play_ack_is_followed_by_stop(self):
        self.connect()
        self.fake.on_command = lambda command: self.cancel.set() if command == "Play:" else None
        with self.assertRaises(Cancelled):
            self.session.render_and_play(model.example(model.defaults()), self.cancel)
        index = self.fake.commands.index("Play:")
        self.assertEqual(self.fake.commands[index + 1], "Stop:")

    def test_active_project_change_refuses_generation(self):
        self.connect()
        self.fake.tracks[0]["name"] = "Another song"
        with self.assertRaises(AudacityError):
            self.session.render_and_play(model.example(model.defaults()), self.cancel)
        self.assertFalse(any(c.startswith("Tone:") for c in self.fake.commands))

    def test_incomplete_and_silent_sequences_never_generate_audio(self):
        self.connect()
        with self.assertRaises(ValueError):
            self.session.render_and_play(model.defaults(), self.cancel)
        state = model.example(model.defaults())
        state["settings"]["visualOnly"] = True
        with self.assertRaises(ValueError):
            self.session.render_and_play(state, self.cancel)
        self.assertNotIn("Play:", self.fake.commands)

    def test_rest_is_actual_zero_amplitude_and_volume_is_bounded(self):
        commands = note_commands("rest", 0, 1, 40)
        self.assertIn("Amplitude=0.000000", commands[1])
        self.assertEqual(len(commands), 2)
        self.assertIn("Amplitude=0.140000", note_commands("piano", 0, 1, 40)[1])

    def test_broken_connection_does_not_claim_to_have_stopped(self):
        self.fake.broken = True
        with self.assertRaisesRegex(AudacityError, "Press Stop"):
            self.session.stop()


class MemoryChannel:
    def __init__(self, chunks):
        self.chunks, self.sent, self.closed = list(chunks), [], False

    def send(self, data, _deadline):
        self.sent.append(data)

    def receive(self, _deadline):
        if not self.chunks:
            raise PipeTimeout("No reply")
        return self.chunks.pop(0)

    def close(self):
        self.closed = True


class ProtocolTests(unittest.TestCase):
    def test_chunked_crlf_json_and_status_are_parsed(self):
        channel = MemoryChannel([b'\r\n\r\n[{"name": "Track"}]\r\n\r\nBatch', b'Command finished: OK\r\n\r\n'])
        result = PipeClient(channel).command("GetInfo: Type=Tracks Format=JSON")
        self.assertEqual(json.loads(result), [{"name": "Track"}])

    def test_failure_is_not_treated_as_success(self):
        with self.assertRaises(AudacityError):
            decode_reply("Command not found\nBatchCommand finished: Failed!")
        with self.assertRaises(AudacityError):
            decode_reply("")

    def test_timeout_invalidates_pipe_and_late_reply_cannot_be_reused(self):
        channel = MemoryChannel([])
        client = PipeClient(channel, timeout=.01)
        with self.assertRaises(PipeTimeout):
            client.command("Stop:")
        channel.chunks.append(b"BatchCommand finished: OK\n\n")
        with self.assertRaises(AudacityError):
            client.command("Play:")
        self.assertEqual(len(channel.sent), 1)
        self.assertTrue(channel.closed)

    def test_command_injection_and_oversize_requests_are_rejected(self):
        channel = MemoryChannel([])
        client = PipeClient(channel)
        for text in ("Play:\nDelete:", "Stop:\0Play:", "x" * 1025):
            with self.assertRaises(ValueError):
                client.command(text)
        self.assertEqual(channel.sent, [])


if __name__ == "__main__":
    unittest.main()
