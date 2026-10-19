# Changes

## Audacity desktop edition of 2.0 — 2026-10-19

- Added a separate Python/Tk picture-card interface that drives an installed Audacity 3.x through local named pipes.
- Kept both complete scales, stable note pictures, two-space beginnings, one/two-pass picture loops, bilingual controls, and persistent communication cards.
- Audacity generates low-amplitude tuned tones with fades and appends each take without deleting earlier audio. Only the new take is selected for playback.
- Added active-track ownership checks, command capability checks, cancellable preparation, bounded replies, and explicit errors if stopping cannot be confirmed.
- Added platform launchers, adult setup instructions, JSON compatibility with the browser edition, 24 desktop unit checks, and five Tk interface checks.
- Kept the browser studio and its 25 behavior checks unchanged.

## 2.0.0 — 2026-10-19

- Added complete C major (C4–C5) and A natural minor (A3–A4) scales, eight notes each including the closing octave.
- Added a companion-controlled music collection selector and a Complete scale button.
- Gave every pitch a consistent picture and color, with arrows for octave differences. Shared pitches use the same image in both scales.
- Added a tuned piano-like sound for each scale note, using equal temperament with A4 = 440 Hz.
- Kept editable picture sequences, one- or two-pass repetition, visual-only mode, and immediate stop controls.
- Added schema 2 JSON exports, compatibility with schema 1 files, and separate version 2 browser saving with migration from the old project.
- Added scale theory, audio-frequency, JSON, and playback checks; 25 tests pass.

## 1.1.0 — 2026-10-19

- Used repeated picture rows to represent loops.
- Removed learner code-notation controls and open-ended repetition.

## 1.0.0 — 2026-10-19

- Created the original two-picture music studio and companion controls.
