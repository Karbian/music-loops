(function (root) {
  'use strict';
  const LEVELS = Object.freeze({ first: 2, next: 4, explore: 8 });
  const SOUNDS = Object.freeze(['piano', 'bell', 'drum', 'rest']);
  const finite = (value, fallback, min, max) => Number.isFinite(Number(value)) ? Math.max(min, Math.min(max, Number(value))) : fallback;
  function defaults() {
    return { schemaVersion: 1, level: 'first', pattern: [null, null], mode: 'once', settings: { language: 'es', tempo: 72, volume: 18, visualOnly: false, highlight: true } };
  }
  function normalize(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw) || raw.schemaVersion !== 1) throw new Error('Invalid music file');
    const state = defaults();
    state.level = Object.hasOwn(LEVELS, raw.level) ? raw.level : 'first';
    const source = Array.isArray(raw.pattern) ? raw.pattern : [];
    state.pattern = Array.from({ length: LEVELS[state.level] }, (_, i) => palette(state.level).includes(source[i]) ? source[i] : null);
    // Older saved projects with open-ended repetition become a finite picture loop.
    state.mode = raw.mode === 'count' || raw.mode === 'while' ? 'count' : 'once';
    const settings = raw.settings && typeof raw.settings === 'object' ? raw.settings : {};
    state.settings.language = settings.language === 'en' ? 'en' : 'es';
    const tempo = finite(settings.tempo, 72, 60, 90);
    state.settings.tempo = [60, 72, 90].includes(tempo) ? tempo : 72;
    state.settings.volume = Math.round(finite(settings.volume, 18, 0, 40));
    state.settings.visualOnly = settings.visualOnly === true;
    state.settings.highlight = settings.highlight !== false;
    return state;
  }
  function resize(state, level) {
    if (!Object.hasOwn(LEVELS, level)) return normalize(state);
    return normalize({ ...state, level, pattern: Array.from({ length: LEVELS[level] }, (_, i) => state.pattern[i] || null) });
  }
  function palette(level) { return level === 'first' ? ['piano', 'bell'] : level === 'next' ? ['piano', 'bell', 'rest'] : [...SOUNDS]; }
  function isReady(state) { return state.pattern.length > 0 && state.pattern.every(sound => SOUNDS.includes(sound)); }
  function eventAt(pattern, index) { return { sound: pattern[index % pattern.length], step: index % pattern.length, cycle: Math.floor(index / pattern.length) + 1 }; }
  function events(state) {
    if (!isReady(state)) return [];
    const count = state.mode === 'count' ? 2 : 1;
    return Array.from({ length: state.pattern.length * count }, (_, index) => eventAt(state.pattern, index));
  }
  function pictureRows(state) {
    return Array.from({ length: state.mode === 'count' ? 2 : 1 }, () => [...state.pattern]);
  }
  const api = { LEVELS, SOUNDS, defaults, normalize, resize, palette, isReady, eventAt, events, pictureRows };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.MusicLoops = api;
})(typeof window !== 'undefined' ? window : {});
