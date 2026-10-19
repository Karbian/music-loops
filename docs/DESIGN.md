# Design and accessibility

Mi Ritmo applies the following design choices as a starting point for trying the tool with its learner, not as a claim of individual suitability or full WCAG conformance.

| Choice | Implementation |
| --- | --- |
| Recognizable steps | Choose a sound → put it in a space → listen; numbered sections and visible sequence. |
| Small initial choice set | Two instrument pictures and two spaces. The same images recur in the palette, sequence, and repeated picture rows. More complexity is offered deliberately by a companion. |
| User control over audio | No autoplay or audio on selection/placement; separate preview and Listen controls; mute, volume, and immediate Stop. |
| Predictability | No pop-up rewards, advertisements, timers, flashing effects, or surprise sounds. Finite repetition throughout. |
| Communication | Persistent Pause, Help, and Finished controls with large on-screen messages; no remote notification or emotion inference. |
| Correctable choices | Replace any step; undo; preserve the sequence through pauses; autosave and portable JSON. |
| Motor and keyboard access | Native buttons, select controls, no required drag/drop, visible focus, generous targets, dialog keyboard handling. |
| Visual alternatives | Words plus distinct pictures and shapes; optional pictures-only playback; the changing step border can be turned off. |
| Language | Complete Spanish and English interface; simple short labels and a separate companion area. |
| Visible repetition | The repeat choice shows two identical rows of the actual instrument pictures. Playback highlights the matching picture in each row. |
| Data minimization | No learner identity, diagnosis, emotion log, microphone, analytics, or server-side sequence storage. |

## Primary references

- W3C WAI, [Make Each Step Clear](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o1p04-clear-steps/).
- W3C WAI, [Use Clear and Understandable Content](https://www.w3.org/WAI/WCAG2/supplemental/objectives/o3-clear-content/).
- W3C WAI, [Help Users Focus](https://www.w3.org/WAI/WCAG2/supplemental/objectives/o5-user-focus/).
- W3C WAI, [Limit Interruptions](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o5p01-minimal-interruptions/).
- W3C WAI, [Understanding Audio Control](https://www.w3.org/WAI/WCAG21/Understanding/audio-control).
- MDN, [Web Audio API best practices](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices).

These references inform implementation choices. They are not evidence that music prevents distress, or that a particular icon is understood by this learner. Confirm recognition, comfort, and choice-making with her and her support team.

The learning representation is image-card sequencing, building on the familiar approach described by the teacher with mTiny. Reading or interpreting programming notation is not part of the learner activity.
