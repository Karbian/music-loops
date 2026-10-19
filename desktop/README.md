# Mi Ritmo 2.0 · Audacity edition

A desktop picture-card studio that uses **Audacity 3.x as its audio engine**. The learner chooses images, puts them in spaces, and hears the sequence once or twice. Two identical picture rows show the loop. There is no learner code view.

This is an independent companion application, not a modified or bundled copy of Audacity. Audacity generates the tones, applies fades, plays the selected take, and holds the audio for an adult to save. The learner works in the Mi Ritmo window.

**[Download the project ZIP](https://github.com/Karbian/music-loops/archive/refs/heads/main.zip)** · [Browser edition](https://karbian.github.io/music-loops/?v=2.0.0) · [Accompaniment guide](../docs/ACCOMPANIMENT.md)

## Adult setup

1. Install **Audacity 3.x with `mod-script-pipe`** and **Python 3.10 or later with Tkinter**. Use [Audacity's official downloads](https://www.audacityteam.org/download/) / [official releases](https://github.com/audacity/audacity/releases), and [python.org](https://www.python.org/downloads/). Check that your Audacity build has the Modules setting below; this integration targets the 3.x scripting interface. A newer build without that module cannot connect.
2. In Audacity, open **Edit → Preferences → Modules** on Windows/Linux, or **Audacity → Settings/Preferences → Modules** on macOS. Set **mod-script-pipe → Enabled**, click OK, and **restart Audacity**. The companion does not change this setting for you.
3. Save and close other Audacity projects. Leave **one new empty project window** open. Close Audacity's welcome dialogs. Keep this project active during the activity; do not edit its tracks from another window while the companion is preparing music.
4. Extract the **whole ZIP**. Open one of the launchers inside `desktop`:

   | Computer | Launcher |
   | --- | --- |
   | Windows | `Start-Windows.bat` |
   | macOS | `Start-macOS.command` |
   | Linux | `Start-Linux.sh` |

   Or open a terminal in the extracted project folder and run `python -m desktop.app` (Windows) or `python3 -m desktop.app` (macOS/Linux). No pip packages are required. On Linux, the distribution may package Tk separately as `python3-tk`. On macOS, the python.org installer includes Tk; a system or package-manager Python may need a separate Tk installation. If double-clicking a macOS/Linux launcher does not execute it, use the terminal command.
5. In Mi Ritmo, open **Acompañante → Conectar con Audacity**. Choose **Idioma → English** for **Companion → Connect to Audacity**. Connection creates one named mono track and stays silent.
6. Before the activity, choose a low **computer/speaker volume**, add an example, listen yourself, and test **Stop**, **Pause**, **Help**, and **Finished**. The app's low tone amplitude does not control the speaker volume. Offer the pictures she already understands, then adjust from what feels comfortable.

Audacity's scripting module lets other local programs control Audacity. Enable it only on a trusted personal computer; disable it in Modules when it is no longer needed. This app uses fixed local named pipes and opens no network port or web service. See the [official scripting guide](https://manual.audacityteam.org/man/scripting.html).

## Her picture activity

1. Choose the piano or bell picture. Nothing sounds on selection.
2. Put that picture in a space, then fill the other space.
3. Press the **triangle / Listen**. Audacity prepares the take first, then plays it.
4. Choose the card with **two rows**, then Listen. The same picture sequence plays twice.

**Pause / Help / Finished** stay at the bottom. Any of them stops sound, cancels pending preparation, and shows her choice in a large picture. Returning stays silent. These are choices shown to a nearby companion; they do not send a remote notification. Agree together on what they mean and respond to her choice.

Tap or click to place pictures; dragging is unnecessary. Tab moves between controls, and Enter or Space activates picture cards. Escape stops. Listen and Stop remain below the scrolling studio; communication cards remain visible. Canvas pictures have keyboard focus but are not claimed to provide full screen-reader support.

## Two complete scales

In **Companion → Music collection**, choose either scale. Choosing a scale silently fills all eight spaces; **Complete scale** restores it after editing.

| Scale | Complete ascending sequence |
| --- | --- |
| C major / Do mayor | C4 · D4 · E4 · F4 · G4 · A4 · B4 · C5 |
| A natural minor / La menor natural | A3 · B3 · C4 · D4 · E4 · F4 · G4 · A4 |

Each note keeps the same picture in either scale. C is a sun, D a drop, E a leaf, F a star, G a flower, A a moon, and B a heart. A down arrow marks octave 3; an up arrow marks octave 5. Pitches use equal temperament with A4 = 440 Hz. Both scales include the closing octave.

The companion can offer **2, 4, or 8 spaces**, tempos of **60, 72, or 90**, optional picture highlighting, and **Pictures only** without connecting to Audacity. The default is still two images and two spaces. Complexity follows her demonstrated understanding; the app does not infer a diagnosis or learning age.

This edition uses soft sine tones with fades. Piano, bell, and drum pictures cue contrasting pitches/envelopes; they are not recordings of those instruments. Scale notes are tuned tones. The browser edition has its own piano-like synthesizer.

## Keep the sequence and audio

- Sequences and settings autosave to `.mi-ritmo/desktop-v2.json` in the current user's home folder. There is no account, microphone use, analytics, or personal-name field.
- **Companion → Save JSON copy / Open JSON sequence** transfers sequences between the desktop and browser editions. Version 1 imports migrate to finite repetition. Import never raises the current chosen volume.
- Each Listen **appends a take** after earlier audio, separated by a short gap. Only the new take is selected for playback. There are no delete, overwrite, project-close, or automatic audio-save commands.
- To keep audio, an adult uses Audacity's **Save Project** or **Export Audio**. The current take stays selected after Stop; choose to export the current selection if that is what you want. A JSON copy contains the pictures and settings, not audio.
- On a later app launch, save the prior audio and open a new empty Audacity project before connecting. A new session refuses to claim an existing track. Start a fresh Audacity project after about an hour of accumulated takes.

The track-name check helps catch an accidental project switch, but the scripting interface cannot lock Audacity to one project. Do not switch, rename, or edit tracks during preparation. Existing takes and any partly prepared take remain available in Audacity; Undo in Mi Ritmo changes picture sequences only.

## Troubleshooting

| What happens | What to check |
| --- | --- |
| The window does not open | Install Python with Tkinter; run `python -m tkinter` to check Tk. Use `python3` on macOS/Linux. Keep the complete extracted project together. |
| Audacity cannot connect | Use a build with `mod-script-pipe`, enable it, restart, and keep one empty project window open. Run both apps as the same ordinary user. |
| Module is absent | This companion targets Audacity 3.x. A build without its scripting module cannot connect. Pictures-only mode and the browser edition remain available. |
| Existing-track / wrong-project message | Save that music first. Open a fresh empty project and Connect. The app will not clear an existing song. |
| A command or effect is missing | The connection checks `GetInfo`, `Select`, `SetTrackStatus`, `Tone`, `FadeIn`, and `FadeOut`. Use a compatible installation with these built-in commands enabled. |
| No audio | Check Audacity's playback device and system volume, track mute/gain, and Mi Ritmo's volume and Pictures-only setting. |
| Preparing takes a moment | Audacity generates and fades the notes before playback. Pause cancels future commands and prevents pending Listen from starting. |
| Audacity is busy, stopped replying, or its pipe broke | **Press Stop in Audacity directly.** Restart both apps and reconnect in an empty project. A command already in progress cannot always be interrupted; the app waits up to 12 seconds for each reply and never reuses a late reply as another command's result. |
| Picture border slightly trails audio | Highlighting is timed from Audacity's Play acknowledgement, rather than its audio clock. It is an approximate guide. |

## Developer checks

From the repository root:

```bash
python -m unittest desktop.tests.test_desktop -v
python -m unittest desktop.tests.test_ui -v
node --test tests/music.test.cjs
```

The 24 desktop logic/protocol tests use a simulated backend and check exact pitches, both complete scales, one/two passes, append-only takes, project ownership, cancellation, timeouts, JSON migration, and browser compatibility. Five Tk interface tests exercise picture placement, both eight-picture scales, communication during preparation, silent playback, settings, and the persistent controls. On Linux use `xvfb-run -a python3 -m unittest desktop.tests.test_ui -v`; without a display the interface tests are explicitly skipped.

GitHub Actions runs the desktop unit tests on Windows, macOS, and Linux, plus the Tk checks on a Linux virtual display. **These simulations do not establish live Audacity audio or individual usability.** See [QA notes](../docs/QA.md) and check the actual computer before using this edition with her.

### Technical references

- [Audacity scripting guide](https://manual.audacityteam.org/man/scripting.html)
- [Audacity command reference](https://manual.audacityteam.org/man/scripting_reference.html)
- [Official pipe-protocol sample](https://github.com/audacity/audacity/blob/master/au3/scripts/piped-work/pipe_test.py)

The front end is original MIT-licensed code. Audacity is installed separately under its own license; no Audacity source, plugin binary, or branding asset is included. This project has no affiliation with Audacity or mTiny.

## Inicio rápido en español

Instala Audacity **3.x con mod-script-pipe** y Python con Tkinter. En **Preferencias → Módulos**, activa **mod-script-pipe** y reinicia Audacity. Guarda y cierra otros proyectos; deja un único proyecto vacío. Descomprime todo el proyecto y abre el lanzador de tu sistema dentro de `desktop`.

En Mi Ritmo, pulsa **Acompañante → Conectar con Audacity**. Después, elige una imagen, colócala en cada espacio y pulsa **Escuchar**. La tarjeta de dos filas repite la secuencia dos veces. **Pausa / Ayuda / Terminé** paran la música y muestran su elección; volver no inicia el sonido.

En **Material musical**, elige **Do mayor** o **La menor natural** para cargar las ocho notas. Puedes volver a dos espacios o usar **Solo imágenes**. Cada escucha añade una toma en Audacity; guarda el audio desde Audacity y las imágenes con **Guardar copia JSON**. Si Audacity no responde, pulsa **Stop en Audacity** y reinicia ambas aplicaciones.
