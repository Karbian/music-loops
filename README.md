# Mi Ritmo · Music Loops

A small, calm music studio for learning **sequences** and **loops** through pictures and sound. Built for Karbian. Inspired by the basic idea of a music step sequencer, with an original interface and synthesized sounds.

**[Open Mi Ritmo](https://karbian.github.io/music-loops/)** · [Companion guide](docs/ACCOMPANIMENT.md) · [Accessibility and design](docs/DESIGN.md)

## Start with two spaces

1. Choose **Piano** or **Bell**. Choosing a sound is silent.
2. Put the sound in space **1**, then space **2**. Tapping an occupied space replaces its sound.
3. Choose **Once** or **Twice**, then **Listen**.

The same sequence played twice makes a loop visible and audible. Nothing starts automatically. Stop, Pause, Help, and Finished stop playback. Returning from a communication card leaves music stopped.

Spanish is the default; **Companion → Language → English** changes the whole interface. The default is picture-first, with two sounds and two spaces. Difficulty is selected by observed comfort and support needs, without assuming an age or diagnosis.

## Features

- Large illustrated buttons, tap-to-place editing, no dragging required, native keyboard controls, visible focus, undo, and responsive layout.
- Two, four, or eight spaces, selected by the companion. No automatic promotion or scoring.
- Counted loop: twice. In the eight-space studio, an optional **Until I stop** mode illustrates a `WHILE` loop. It has a 60-second session limit.
- Optional `FOR` / `WHILE` program view, hidden by default.
- On-screen **Pause / Help / Finished** choice cards. They display a request to a nearby companion; they do not notify anyone remotely.
- Low initial app volume, adjustable volume, a persistent mute button, pictures-only mode, and an option to remove the moving step highlight.
- Browser-local autosave plus JSON download and import. Import never increases the existing volume. No accounts, analytics, microphone, recordings, third-party fonts, remote audio files, or student records.
- Stops on leaving the tab, window focus loss, settings changes, and Escape. Stale asynchronous audio starts are cancelled.

## Run

No installation or build step is needed. Open `index.html` in a modern browser. Audio starts only after pressing a listening control. Alternatively serve this directory:

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. Local-file storage behavior varies by browser; use a local server or GitHub Pages for consistent saving. Download the repository to use it without an internet connection; this release does not install an offline service worker.

For demonstrations or developer checks, add `?demo=1` to the URL. This starts a separate, empty, page-only session and does not read or overwrite the saved studio. JSON download is still available.

## GitHub Pages

The app uses only relative paths. In **Settings → Pages**, select **Deploy from a branch → main → /(root)**. Save. No custom domain, backend, billing service, or secrets are required. GitHub serves the public files; sequence JSON stays in the current browser until its user downloads or shares it.

## Check

```bash
node --test tests/*.test.cjs
node --check assets/app.js
node --check assets/audio.js
```

The tests exercise sequence ordering, counted loops, import validation, playback cancellation, silence on stop, and the session limit using a fake clock. They do not certify accessibility or assess suitability for an individual learner. See [verification notes](docs/QA.md).

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Studio, communication cards, companion settings |
| `assets/core.js` | Sequence state, validation, loop events, pseudocode |
| `assets/audio.js` | Synthesized sounds and cancellable player |
| `assets/app.js` | Interface, Spanish/English text, browser storage |
| `assets/styles.css` | Responsive layout and focus states |
| `docs/ACCOMPANIMENT.md` | Short introduction and suggested activities |

MIT license. This is an educational tool; its communication cards are not a crisis assessment or treatment system. It cannot predict distress. Start alongside the learner and adapt it with the adults who know her communication and sensory preferences.
