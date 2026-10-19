"""Bounded, serialized local named-pipe requests. No network listener or shell."""
import json
import os
import queue
import re
import select
import stat
import sys
import threading
import time


class AudacityError(Exception):
    pass


class PipeTimeout(AudacityError):
    pass


def decode_reply(reply):
    """A blank line frames a reply; the final status must explicitly say OK."""
    lines = reply.replace("\r", "").replace("\0", "").strip().splitlines()
    if not lines or lines[-1].strip() != "BatchCommand finished: OK":
        raise AudacityError("Audacity rejected a command: " + " ".join(lines)[-400:])
    return "\n".join(lines[:-1]).strip()


def json_reply(reply):
    try:
        return json.loads(reply)
    except (ValueError, TypeError) as exc:
        raise AudacityError("Audacity returned unreadable information.") from exc


class LocalChannel:
    """Fixed local pipe names from Audacity's documented protocol."""
    def __init__(self):
        self.writer = self.reader = None
        self.closed = threading.Event()
        self.chunks = queue.Queue()
        self.windows = sys.platform == "win32"
        try:
            if self.windows:
                self._windows_open()
            else:
                base = "/tmp/audacity_script_pipe."
                names = [base + suffix + str(os.getuid()) for suffix in ("to.", "from.")]
                for name in names:
                    info = os.lstat(name)
                    if not stat.S_ISFIFO(info.st_mode) or info.st_uid != os.getuid():
                        raise AudacityError("The Audacity pipe is not owned by this local user.")
                self.writer = os.open(names[0], os.O_WRONLY | os.O_NONBLOCK)
                self.reader = os.open(names[1], os.O_RDONLY | os.O_NONBLOCK)
        except (OSError, AudacityError) as exc:
            self.close()
            raise AudacityError("Open Audacity with mod-script-pipe enabled, then connect again.") from exc

    def _windows_open(self):
        # Open in a daemon so even a stalled local server cannot freeze the UI.
        result = queue.Queue()

        def opener():
            writer = reader = None
            try:
                writer = open(r"\\.\pipe\ToSrvPipe", "wb", buffering=0)
                reader = open(r"\\.\pipe\FromSrvPipe", "rb", buffering=0)
                if self.closed.is_set():
                    writer.close()
                    reader.close()
                else:
                    result.put((writer, reader))
            except OSError as exc:
                if writer is not None:
                    writer.close()
                if reader is not None:
                    reader.close()
                result.put(exc)

        threading.Thread(target=opener, daemon=True).start()
        try:
            opened = result.get(timeout=3)
        except queue.Empty as exc:
            self.closed.set()
            raise AudacityError("Audacity did not open its local pipes.") from exc
        if isinstance(opened, Exception):
            raise opened
        self.writer, self.reader = opened
        read_stream = self.reader

        def reader_loop():
            try:
                while not self.closed.is_set():
                    chunk = read_stream.read(4096)
                    if not chunk:
                        raise OSError("Audacity closed its pipe.")
                    self.chunks.put(chunk)
            except (OSError, ValueError) as exc:
                self.chunks.put(exc)

        threading.Thread(target=reader_loop, daemon=True).start()

    def send(self, data, deadline):
        if self.windows:
            # Bound even a stalled Windows write without blocking the UI worker.
            result = queue.Queue()
            write_stream = self.writer
            def write():
                try:
                    result.put(write_stream.write(data))
                except (OSError, ValueError) as exc:
                    result.put(exc)
            threading.Thread(target=write, daemon=True).start()
            try:
                sent = result.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty as exc:
                raise PipeTimeout("Audacity did not accept a command.") from exc
            if isinstance(sent, Exception):
                raise AudacityError("The Audacity write pipe failed.") from sent
            if sent != len(data):
                raise AudacityError("Audacity received an incomplete command.")
            return
        offset = 0
        while offset < len(data):
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([], [self.writer], [], remaining)[1]:
                raise PipeTimeout("Audacity did not accept a command.")
            offset += os.write(self.writer, data[offset:])

    def receive(self, deadline):
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise PipeTimeout("Audacity did not reply. Use Stop in Audacity, then restart the companion.")
            if self.windows:
                try:
                    chunk = self.chunks.get(timeout=remaining)
                except queue.Empty as exc:
                    raise PipeTimeout("Audacity did not reply. Use Stop in Audacity.") from exc
                if isinstance(chunk, Exception):
                    raise AudacityError("Audacity closed its pipe.") from chunk
                return chunk
            if select.select([self.reader], [], [], min(remaining, 0.1))[0]:
                chunk = os.read(self.reader, 4096)
                if chunk:
                    return chunk
                # Audacity may still be opening the other end during connection.
                self.closed.wait(min(remaining, 0.02))

    def close(self):
        self.closed.set()
        for stream in (self.writer, self.reader):
            if stream is not None:
                try:
                    stream.close() if self.windows else os.close(stream)
                except (OSError, ValueError):
                    pass
        self.writer = self.reader = None


class PipeClient:
    def __init__(self, channel=None, timeout=12):
        self.channel = channel if channel is not None else LocalChannel()
        self.timeout = timeout
        self.lock = threading.Lock()
        self.broken = False
        self.buffer = b""

    def command(self, command):
        if not isinstance(command, str) or any(c in command for c in "\r\n\0") or len(command) > 1024:
            raise ValueError("Only one bounded Audacity command is allowed.")
        with self.lock:
            if self.broken:
                raise AudacityError("Restart Audacity and the companion after a broken connection.")
            deadline = time.monotonic() + self.timeout
            ending = "\r\n\0" if sys.platform == "win32" else "\n"
            try:
                self.channel.send((command + ending).encode("utf-8"), deadline)
                while True:
                    self.buffer = self.buffer.lstrip(b"\r\n\0")
                    # Accept blank lines inside payloads; frame at final status.
                    cleaned = self.buffer.replace(b"\r", b"").replace(b"\0", b"")
                    terminal = re.search(rb"(?m)^BatchCommand finished: [^\n]*\n\n", cleaned)
                    if terminal:
                        message, extra = cleaned[:terminal.end()], cleaned[terminal.end():]
                        if extra.strip():
                            raise AudacityError("Unexpected extra data on Audacity's pipe.")
                        self.buffer = b""
                        return decode_reply(message.decode("utf-8"))
                    self.buffer += self.channel.receive(deadline)
                    if len(self.buffer) > 2_000_000:
                        raise AudacityError("Audacity's reply is too large.")
            except (OSError, UnicodeError, AudacityError) as exc:
                # Never attach a late reply to the next command after a timeout.
                self.close()
                if isinstance(exc, AudacityError):
                    raise
                raise AudacityError("The local Audacity connection was interrupted.") from exc

    def close(self):
        self.broken = True
        self.channel.close()
