# Verification

## Automated checks

Run `node --test tests/*.test.cjs`. Tests cover state normalization, sequence order and rests, two-pass loops, level changes, pending audio cancellation, stop cancellation, visual-only playback, focus/suspension safeguards, and delayed tab interruption with a controlled clock.

JavaScript syntax is checked with `node --check`. GitHub Actions runs these checks on pushes and pull requests.

## Browser review

The current 1.1.0 revision uses picture rows to represent a sequence played once or twice. The code view and open-ended repeat option from the initial prototype have been removed. Saved older projects are normalized into a finite repetition while preserving valid instrument cards.

The initial studio was reviewed in Chrome at 1470 × 683 and 390 × 844, including keyboard editing, sound playback, Pause / Help / Finished, English labels, and visual-only playback. Those checks predate the picture-row revision.

The selected browser connection failed during the final 1.1.0 review. Automatic approval review rejected opening a different browser because it would switch away from the selected browser after its connection failed. **The new picture-row layout and its live highlighting are not visually verified.** No previous screenshot is presented as proof of this revision.

The revised source passes all 14 behavior tests, JavaScript syntax checks, and static checks for translated labels, element references, valid asset paths, and removal of learner code-notation controls. GitHub Actions and Pages publication completed successfully for the functional 1.1.0 commit.

## Remaining checks

The browser automation connection previously timed out while waiting for a JSON download event. A complete download → clear → import transfer remains unverified. Validation and normalization are tested independently. Check that transfer in the actual device browser before relying on it.

The developer checks do not establish individual usability or auditory comfort. A companion should confirm that the instrument pictures, sounds, and communication cards are understood; test the real output volume; and use the learner's usual supports. No professional accessibility audit or clinical validation is claimed.
