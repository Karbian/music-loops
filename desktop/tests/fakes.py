"""A protocol simulator, not a substitute for checking an installed Audacity."""
import json
import re

from desktop.session import AudacitySession


class FakeAudacity:
    def __init__(self):
        self.commands = []
        self.tracks = []
        self.selection = (0, 0)
        self.broken = False
        self.on_command = lambda command: None
        self.available = AudacitySession.REQUIRED.copy()

    def command(self, command):
        self.commands.append(command)
        self.on_command(command)
        if command == "GetInfo: Type=Commands Format=JSON":
            return json.dumps([{"id": name} for name in self.available])
        if command == "GetInfo: Type=Tracks Format=JSON":
            return json.dumps(self.tracks)
        if command == "NewMonoTrack:":
            self.tracks.append({"name": "Audio", "kind": "wave", "channels": 1, "start": 0, "end": 0})
        elif command.startswith("SetTrackStatus:"):
            self.tracks[0]["name"] = re.search(r'Name="([^"]+)"', command)[1]
        elif command.startswith("Select:"):
            self.selection = tuple(float(re.search(key + r"=([0-9.]+)", command)[1]) for key in ("Start", "End"))
        elif command.startswith("Tone:"):
            self.tracks[0]["end"] = max(self.tracks[0]["end"], self.selection[1])
        return ""

    def close(self):
        self.broken = True
