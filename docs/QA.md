# Verification

## Audacity desktop edition

`python -m unittest desktop.tests.test_desktop -v` passes 24 unit/protocol checks. They include exact C-major and A-natural-minor pitches, octave tuning, eight/16-note takes, fade commands, bounded tone amplitude, zero-amplitude rest commands, append-only positioning, ownership refusal, missing-command refusal, cancellation at preparation and Play acknowledgement, invalidation after a timeout, legacy migration, bounded JSON import, and a browser/desktop scale-data comparison.

Five additional Tk checks in `desktop.tests.test_ui` cover picture placement, both complete scale layouts and restoration, cancellation by Help while generation is pending, pictures-only playback and silent return, English settings, and on-screen placement of persistent controls at 960 × 700. They require Tk and a display. The local build environment has Tk but no display; these tests are skipped locally. GitHub Actions runs them with Xvfb and runs the desktop unit tests on Windows, macOS, and Linux.

GitHub Actions has passed all five Tk checks on its virtual display, the 24 desktop unit checks on all three operating systems, and the 25 existing browser logic checks. The interface job requires Tk rather than accepting skipped GUI tests. It uses a simulated Audacity backend throughout.

Audacity itself is not installed in the local build environment. Protocol simulations and Tk checks are not live Audacity validation. **An installed Audacity 3.x session, actual output device/volume, Windows/macOS pipe behavior, manual audio save/export, and auditory comfort remain to be checked on the target computer.** The desktop's live picture border uses estimated time, not Audacity's audio clock. Canvas cards have keyboard bindings and focus borders; full screen-reader accessibility is not established.

Before the activity, a companion should connect in an empty Audacity project, listen to both complete scales once and twice, try Pause while Preparing and during sound, verify Help/Finished and silent return, save/reopen a JSON copy, and save a take from Audacity. Keep one project active throughout; ownership checks are not an atomic lock against another person editing Audacity. A stalled Audacity command can delay Stop; use Audacity's own Stop if the local connection is unresponsive.

## Automated checks

Run `node --test tests/*.test.cjs`. Tests cover state normalization, sequence order and rests, two-pass loops, level changes, pending audio cancellation, stop cancellation, visual-only playback, focus/suspension safeguards, and delayed tab interruption with a controlled clock.

JavaScript syntax is checked with `node --check`. GitHub Actions runs these checks on pushes and pull requests.

## Version 2.0 checks

All 25 behavior tests pass, including both scales' full note sequences and interval patterns, correctly tuned frequencies, direct oscillator-frequency checks for every note, repeated eight-note playback, stopping within a scale, restoration of the complete scale, legacy migration, and schema 2 JSON round trips. JavaScript syntax and static interface references are checked separately.

This revision has not received live browser visual or auditory review. Prior browser and transfer limitations are documented below. A human should check the real device volume and whether the new picture set is comfortable and understood.

## Earlier browser review

The earlier 1.1.0 revision uses picture rows to represent a sequence played once or twice. The code view and open-ended repeat option from the initial prototype have been removed. Saved older projects are normalized into a finite repetition while preserving valid instrument cards.

The initial studio was reviewed in Chrome at 1470 × 683 and 390 × 844, including keyboard editing, sound playback, Pause / Help / Finished, English labels, and visual-only playback. Those checks predate the picture-row revision.

The selected browser connection failed during the final 1.1.0 review. Automatic approval review rejected opening a different browser because it would switch away from the selected browser after its connection failed. **The new picture-row layout and its live highlighting are not visually verified.** No previous screenshot is presented as proof of this revision.

The revised source passes all 14 behavior tests, JavaScript syntax checks, and static checks for translated labels, element references, valid asset paths, and removal of learner code-notation controls. GitHub Actions and Pages publication completed successfully for the functional 1.1.0 commit.

## Remaining checks

The browser automation connection previously timed out while waiting for a JSON download event. A complete download → clear → import transfer remains unverified. Validation and normalization are tested independently. Check that transfer in the actual device browser before relying on it.

The developer checks do not establish individual usability or auditory comfort. A companion should confirm that the instrument pictures, sounds, and communication cards are understood; test the real output volume; and use the learner's usual supports. No professional accessibility audit or clinical validation is claimed.
