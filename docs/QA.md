# Verification

## Automated checks

Run `node --test tests/*.test.cjs`. Tests cover state normalization, sequence order and rests, two-pass loops, level changes, pseudocode, pending audio cancellation, stop cancellation, visual-only playback, focus/suspension safeguards, and the 60-second loop guard with a controlled clock.

JavaScript syntax is checked with `node --check`. GitHub Actions runs these checks on pushes and pull requests.

## Browser review

Browser verification results are recorded here before the first release.

## Remaining real-use checks

The developer checks do not establish individual usability or auditory comfort. A companion should try both sounds at the device's actual volume; confirm the pictures and communication cards are understood; observe whether two choices are comfortable; and check the learner's usual browser, touch device, and assistive technology. Synthesized tones are piano-like and bell-like rather than recordings of acoustic instruments. No professional accessibility audit or clinical validation is claimed.
