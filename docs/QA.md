# Verification

## Automated checks

Run `node --test tests/*.test.cjs`. Tests cover state normalization, sequence order and rests, two-pass loops, level changes, pending audio cancellation, stop cancellation, visual-only playback, focus/suspension safeguards, and delayed tab interruption with a controlled clock.

JavaScript syntax is checked with `node --check`. GitHub Actions runs these checks on pushes and pull requests.

## Browser review

The current 1.1.0 revision uses picture rows to represent a sequence played once or twice. The code view and open-ended repeat option from the initial prototype have been removed. Saved older projects are normalized into a finite repetition while preserving valid instrument cards.

Revised browser results are recorded after publication.

## Remaining checks

The browser automation connection previously timed out while waiting for a JSON download event. A complete download → clear → import transfer remains unverified. Validation and normalization are tested independently. Check that transfer in the actual device browser before relying on it.

The developer checks do not establish individual usability or auditory comfort. A companion should confirm that the instrument pictures, sounds, and communication cards are understood; test the real output volume; and use the learner's usual supports. No professional accessibility audit or clinical validation is claimed.
