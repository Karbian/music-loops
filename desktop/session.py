"""Append-only Audacity takes, with cancellation checked before every request."""
from dataclasses import dataclass
import math
import uuid

from . import model
from .pipe import AudacityError, PipeClient, json_reply


class Cancelled(Exception):
    pass


@dataclass(frozen=True)
class Take:
    start: float
    duration: float
    beat: float
    sounds: tuple


def select_region(start, end):
    return f"Select: Track=0 TrackCount=1 Mode=Set Start={start:.6f} End={end:.6f} RelativeTo=ProjectStart"


def note_commands(sound, start, beat, volume):
    end = start + beat
    amplitude = 0 if sound == "rest" else volume / 100 * 0.35
    commands = [select_region(start, end),
                f"Tone: Frequency={model.frequency(sound):.8f} Amplitude={amplitude:.6f} Waveform=Sine Interpolation=Linear"]
    if amplitude:
        attack = 0.008 if sound == "drum" else 0.025
        decay = 0.04 if sound == "drum" else 0.18
        commands += [select_region(start, start + attack), "FadeIn:",
                     select_region(start + beat * decay, end), "FadeOut:"]
    return commands


class AudacitySession:
    REQUIRED = {"GetInfo", "Select", "SetTrackStatus", "Tone", "FadeIn", "FadeOut"}

    def __init__(self, client=None):
        self.client = client
        self.track_name = "MiRitmo-" + uuid.uuid4().hex[:12]
        self.connected = False

    def _command(self, command, cancel):
        if cancel.is_set():
            raise Cancelled()
        return self.client.command(command)

    def _tracks(self, cancel):
        tracks = json_reply(self._command("GetInfo: Type=Tracks Format=JSON", cancel))
        if not isinstance(tracks, list) or not all(isinstance(t, dict) for t in tracks):
            raise AudacityError("Unexpected track information.")
        return tracks

    def _owned(self, cancel):
        tracks = self._tracks(cancel)
        if (len(tracks) != 1 or tracks[0].get("name") != self.track_name
                or tracks[0].get("kind") != "wave" or tracks[0].get("channels") != 1):
            self.connected = False
            raise AudacityError("Use the companion's unchanged mono track. Open a new empty Audacity project and connect again.")
        end = tracks[0].get("end")
        if not isinstance(end, (int, float)) or not math.isfinite(end) or end < 0 or end > 3600:
            raise AudacityError("Start a new empty project for another session.")
        return end

    def connect(self, cancel):
        self.connected = False
        if self.client is None:
            self.client = PipeClient()
        self._command("Stop:", cancel)
        commands = json_reply(self._command("GetInfo: Type=Commands Format=JSON", cancel))
        ids = {c.get("id") for c in commands if isinstance(c, dict)} if isinstance(commands, list) else set()
        missing = self.REQUIRED - ids
        if missing:
            raise AudacityError("This Audacity installation is missing: " + ", ".join(sorted(missing)))
        tracks = self._tracks(cancel)
        if not tracks:
            self._command("NewMonoTrack:", cancel)
            self._command(f'SetTrackStatus: Name="{self.track_name}" Selected=1 Focused=1', cancel)
        self._owned(cancel)
        self.connected = True

    def render_and_play(self, state, cancel):
        state = model.normalize(state)
        sounds = model.events(state)
        if not sounds:
            raise ValueError("Fill the picture spaces before listening.")
        if state["settings"]["visualOnly"] or state["settings"]["volume"] == 0:
            raise ValueError("Silent sequences are shown by the picture window.")
        if not self.connected:
            raise AudacityError("Connect to Audacity in Companion first.")
        self._command("Stop:", cancel)
        start = self._owned(cancel)
        # A gap separates takes; no earlier audio is selected for editing.
        start = start + 0.25 if start else 0.0
        beat = 60 / state["settings"]["tempo"]
        take = Take(start, beat * len(sounds), beat, tuple(sounds))
        try:
            for index, sound in enumerate(sounds):
                self._owned(cancel)
                for command in note_commands(sound, start + index * beat, beat, state["settings"]["volume"]):
                    self._command(command, cancel)
            self._owned(cancel)
            self._command(select_region(start, start + take.duration), cancel)
            self._command("Play:", cancel)
            if cancel.is_set():
                self.stop()
                raise Cancelled()
            return take
        except Exception:
            # A partly generated take stays in Audacity but is never resumed.
            self.stop()
            raise

    def stop(self):
        if self.client is not None:
            if getattr(self.client, "broken", False):
                raise AudacityError("The connection is unavailable. Press Stop in Audacity, then restart both apps.")
            self.client.command("Stop:")

    def close(self):
        if self.client is not None:
            self.client.close()
