(function (root) {
  'use strict';
  const LEVELS = Object.freeze({ first: 2, next: 4, explore: 8 });
  const BASIC_SOUNDS = Object.freeze(['piano', 'bell', 'drum', 'rest']);
  const NOTES = Object.freeze(Object.fromEntries([
    ['a3','a',57,3], ['b3','b',59,3], ['c4','c',60,4], ['d4','d',62,4],
    ['e4','e',64,4], ['f4','f',65,4], ['g4','g',67,4], ['a4','a',69,4],
    ['b4','b',71,4], ['c5','c',72,5]
  ].map(([id,letter,midi,octave]) => ['note-'+id,Object.freeze({letter,midi,octave})])));
  const SCALES = Object.freeze({
    'c-major': Object.freeze({ nameKey:'cMajor', notes:Object.freeze(['note-c4','note-d4','note-e4','note-f4','note-g4','note-a4','note-b4','note-c5']) }),
    'a-minor': Object.freeze({ nameKey:'aMinor', notes:Object.freeze(['note-a3','note-b3','note-c4','note-d4','note-e4','note-f4','note-g4','note-a4']) })
  });
  const SOUNDS = Object.freeze([...BASIC_SOUNDS,...Object.keys(NOTES)]);
  const finite = (value, fallback, min, max) => Number.isFinite(Number(value)) ? Math.max(min, Math.min(max, Number(value))) : fallback;
  function defaults() {
    return { schemaVersion: 2, collection:'sounds', level: 'first', pattern: [null, null], mode: 'once', settings: { language: 'es', tempo: 72, volume: 18, visualOnly: false, highlight: true } };
  }
  function normalize(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw) || ![1,2].includes(raw.schemaVersion)) throw new Error('Invalid music file');
    const state = defaults();
    state.collection = raw.schemaVersion === 2 && Object.hasOwn(SCALES,raw.collection) ? raw.collection : 'sounds';
    state.level = Object.hasOwn(LEVELS, raw.level) ? raw.level : 'first';
    const source = Array.isArray(raw.pattern) ? raw.pattern : [];
    state.pattern = Array.from({ length: LEVELS[state.level] }, (_, i) => palette(state.level,state.collection).includes(source[i]) ? source[i] : null);
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
  function palette(level, collection = 'sounds') {
    if (Object.hasOwn(SCALES,collection)) return [...SCALES[collection].notes];
    return level === 'first' ? ['piano', 'bell'] : level === 'next' ? ['piano', 'bell', 'rest'] : [...BASIC_SOUNDS];
  }
  function setCollection(state, collection) {
    if (collection === 'sounds') return normalize({...state,collection,level:'first',pattern:[null,null],mode:'once'});
    if (!Object.hasOwn(SCALES,collection)) return normalize(state);
    return normalize({...state,collection,level:'explore',pattern:[...SCALES[collection].notes],mode:'once'});
  }
  function example(state) {
    if (Object.hasOwn(SCALES,state.collection)) return setCollection(state,state.collection);
    return normalize({...state,pattern:state.pattern.map((_,index) => index % 2 === 0 ? 'piano' : 'bell')});
  }
  function noteInfo(sound) { return Object.hasOwn(NOTES,sound) ? NOTES[sound] : null; }
  function frequencyFor(sound) { const note = noteInfo(sound); return note ? 440 * 2 ** ((note.midi - 69) / 12) : null; }
  function cardClass(sound) { const note = noteInfo(sound); return note ? 'pitched tone-'+note.letter : BASIC_SOUNDS.includes(sound) ? sound : 'empty'; }
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
  const api = { LEVELS, SOUNDS, NOTES, SCALES, defaults, normalize, resize, palette, setCollection, example, noteInfo, frequencyFor, cardClass, isReady, eventAt, events, pictureRows };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.MusicLoops = api;
})(typeof window !== 'undefined' ? window : {});
