# Verification

## Automated checks

Run `node --test tests/*.test.cjs`. Tests cover state normalization, sequence order and rests, two-pass loops, level changes, pseudocode, pending audio cancellation, stop cancellation, visual-only playback, focus/suspension safeguards, and the 60-second loop guard with a controlled clock.

JavaScript syntax is checked with `node --check`. GitHub Actions runs these checks on pushes and pull requests.

## Browser review

Reviewed on 19 October 2026 in Chrome, against the published GitHub Pages application with versioned 1.0.0 assets. The isolated `?demo=1` session was used for the final review to preserve the main studio's saved sequence.

| Check | Observed result |
| --- | --- |
| Default studio | Two spaces, two illustrated sound choices, program hidden. |
| Keyboard editing | Enter selects a sound and places it in a space. Both steps retain their intended order. |
| Desktop at 1470 × 683 | The two-step sequence and listening controls fit above the fixed communication bar. |
| Listen and Pause | Playback enters the playing state. Pause opens its message. Returning shows Ready and leaves playback stopped. |
| Help and Finished | Correct large choice messages; Escape closes the dialog. The demo correctly describes its page-only data. |
| English and four steps | Labels change to English, four steps are present, and the program shows the two-pass FOR loop. |
| Pictures-only playback | The interface reports playback without sound; Stop returns it to stopped. The unit test also verifies no audio activation. |
| Eight-step program | WHILE program and Until I stop option appear. Cancellation and the 60-second cap are covered by automated tests. |
| Phone layout at 390 × 844 | No horizontal overflow. Sound buttons are 168 × 112; communication buttons are 114 × 56. Pause remains accessible and opens its message. |
| Static interface checks | 65 unique element IDs, 62 translated labels, and all static control references checked. |
| Automated behavior checks | All 14 tests pass; JavaScript syntax checks and GitHub Actions pass. |

The browser automation connection timed out waiting for the JSON download event. The app displayed its download status, but a full download → clear → import round trip was **not verified**. File validation and normalization are tested independently. Try that round trip in the learner's actual browser before relying on file transfer.

The managed local preview service could not start due to a container mount restriction. Visual and interaction checks therefore used the published GitHub Pages app. The preview screenshot in this repository is from that app. Auditory comfort and real device output volume require a human check.

## Remaining real-use checks

The developer checks do not establish individual usability or auditory comfort. A companion should try both sounds at the device's actual volume; confirm the pictures and communication cards are understood; observe whether two choices are comfortable; and check the learner's usual browser, touch device, and assistive technology. Synthesized tones are piano-like and bell-like rather than recordings of acoustic instruments. No professional accessibility audit or clinical validation is claimed.
