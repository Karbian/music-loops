# Mi Ritmo 2.0 · Music Loops

A calm music studio for learning **sequences and loops with picture cards**. Choose an instrument picture, place its card in the sequence, and listen. Repeating shows **two identical rows of pictures**, making the loop visible.

**[Open Mi Ritmo 2.0](https://karbian.github.io/music-loops/?v=2.0.0)** · [Companion guide](docs/ACCOMPANIMENT.md) · [Complete scales](docs/SCALES.md) · [Accessibility and design](docs/DESIGN.md)

## Audacity desktop edition

**[Download and set up the Audacity edition](desktop/README.md)** to use a separate picture-card window with **Audacity 3.x generating and playing the music**. It includes both complete scales, two-space activities, finite visual loops, persistent Pause / Help / Finished cards, Spanish and English, and compatible JSON files. Python with Tkinter and Audacity's `mod-script-pipe` module are required; launchers are provided for Windows, macOS, and Linux. Earlier audio takes remain in Audacity for an adult to save.

The desktop connection has protocol simulations and Tk checks; live audio on an installed Audacity still needs a device check. The browser edition above remains available separately.

## Two complete scales

In **Acompañante → Material musical**, choose **Do mayor** or **La menor natural**. In English, use **Companion → Music collection → C major / A natural minor**.

| Scale | Eight notes, including the octave |
| --- | --- |
| C major | C4 · D4 · E4 · F4 · G4 · A4 · B4 · C5 |
| A natural minor | A3 · B3 · C4 · D4 · E4 · F4 · G4 · A4 |

Selecting a scale silently loads its complete eight-card sequence. Each pitch has a consistent picture, color, and real tuned piano-like sound. The same pitch keeps its picture in either scale. Arrows distinguish lower or upper octaves. Select **Listen**, edit individual cards, or repeat the complete scale twice with the matching picture rows. **Complete scale** restores all eight ascending notes after edits; it leaves sound stopped.

The default remains the two-picture activity. A companion chooses when to introduce the scales. Existing version 1 saved projects and JSON files migrate to version 2. Version 2 saves separately, keeping the old browser project available as a migration source.

## Start with pictures

1. Choose the **piano picture** or **bell picture**. Choosing and placing cards is silent.
2. Put a card in each of the two large spaces.
3. Point to the picture row and press the triangle to listen.
4. Choose the repeat-arrow option. Two matching picture rows show the same music happening again.

The instrument picture stays the same in the palette, the sequence, and the repeat preview. A border can follow the card currently playing. Short labels support companions and screen readers; the activity can be demonstrated through pictures and actions.

This follows a picture-card sequencing approach familiar from activities such as mTiny. It is an independent music-learning project with original illustrations and sounds; no mTiny assets are copied.

## Features

- Two sound pictures and two spaces initially; a companion can later offer four or eight spaces.
- Finite repetition: once or twice. The repeated picture rows match the playback order.
- Image-led interaction throughout the studio and companion settings.
- Persistent **Pause / Help / Finished** picture buttons show a choice and stop sound. Returning leaves music stopped. These cards display requests to a nearby companion and do not send remote notifications.
- Large touch targets, keyboard access, visible focus, tap-to-place editing, and undo. No dragging is required.
- Gentle initial app volume, mute, volume settings, optional visual-only playback, and optional step highlighting.
- Spanish and English. Use **Acompañante → Idioma → English** to switch.
- Browser-local autosave and JSON sequence download/import. No names, accounts, analytics, microphone, or recordings.
- No scores, countdowns, automatic level promotion, reward animations, or sound on selection.

Choose complexity from what the learner does comfortably with pictures. Start alongside her and agree on the meaning of each communication card.

## Run and publish

No installation or build step is needed. Open `index.html` in a modern browser, or serve this directory:

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. For GitHub Pages use **Settings → Pages → Deploy from a branch → main → /(root)**. All app paths are relative. Downloading the repository allows local use without an internet connection. Browser saving is more consistent on a local server or GitHub Pages than on file URLs.

Add `?demo=1&v=2.0.0` to try an empty, page-only demonstration without reading or overwriting the saved studio. Change the version on asset URLs in `index.html` after future releases to refresh cached files.

## Verification

```bash
node --test tests/*.test.cjs
node --check assets/app.js
node --check assets/audio.js
```

All 25 tests pass. They cover both scales' exact notes and intervals, octave tuning, actual synthesizer frequencies, picture rows, sound order, finite repetition, old save migration, JSON round trips, validation, stop cancellation, visual-only playback, and delayed tab interruption. [Verification notes](docs/QA.md) distinguish automated checks, browser checks, and remaining device checks.

| File | Purpose |
| --- | --- |
| `index.html` | Picture-card studio and companion controls |
| `assets/core.js` | Card sequences, picture rows, validation |
| `assets/audio.js` | Synthesized sounds and cancellable playback |
| `assets/app.js` | Interface, translation, local saving |
| `assets/styles.css` | Responsive layout and focus states |

MIT license. Educational tool; the cards show choices and cannot predict distress or replace existing communication supports.
