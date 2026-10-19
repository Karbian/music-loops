(function (root) {
  'use strict';
  class SoundEngine {
    constructor() { this.context = null; this.master = null; this.voices = new Set(); this.volume = 18; this.muted = false; }
    async ready() {
      if (!this.context) {
        const AudioContext = root.AudioContext || root.webkitAudioContext;
        if (!AudioContext) throw new Error('Web Audio unavailable');
        this.context = new AudioContext();
        this.master = this.context.createGain();
        this.master.gain.value = this.muted ? 0 : this.volume / 100 * 0.65;
        this.master.connect(this.context.destination);
      }
      if (this.context.state !== 'running') await this.context.resume();
      if (this.context.state !== 'running') throw new Error('Audio could not start');
    }
    setVolume(volume, muted) {
      this.volume = Math.max(0, Math.min(40, Number(volume) || 0));
      this.muted = Boolean(muted);
      if (this.master && this.context) {
        const now = this.context.currentTime;
        this.master.gain.cancelScheduledValues(now);
        this.master.gain.setTargetAtTime(this.muted ? 0 : this.volume / 100 * .65, now, .012);
      }
    }
    note(sound, beatSeconds) {
      if (!this.context || this.context.state !== 'running' || sound === 'rest' || this.muted) return;
      const ctx = this.context, now = ctx.currentTime;
      const gain = ctx.createGain();
      const duration = Math.min(beatSeconds * .78, .65);
      const voice = { oscillators: [], gain };
      gain.connect(this.master);
      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(.42, now + .025);
      gain.gain.exponentialRampToValueAtTime(.001, now + duration);
      const partials = sound === 'bell' ? [[523.25,.65],[1046.5,.12]] : sound === 'drum' ? [[146.83,.7],[220,.09]] : [[261.63,.65],[523.25,.13],[784.88,.045]];
      partials.forEach(([frequency, amplitude]) => {
        const oscillator = ctx.createOscillator(), partial = ctx.createGain();
        oscillator.type = 'sine'; oscillator.frequency.value = frequency; partial.gain.value = amplitude;
        if (sound === 'drum') oscillator.frequency.exponentialRampToValueAtTime(frequency * .65, now + duration);
        oscillator.connect(partial); partial.connect(gain); oscillator.start(now); oscillator.stop(now + duration + .025);
        voice.oscillators.push({ oscillator, partial });
      });
      this.voices.add(voice);
      voice.oscillators[0].oscillator.onended = () => { voice.oscillators.forEach(({oscillator,partial}) => { oscillator.disconnect(); partial.disconnect(); }); gain.disconnect(); this.voices.delete(voice); };
    }
    silence() {
      if (!this.context) return;
      const now = this.context.currentTime;
      this.voices.forEach(voice => {
        voice.gain.gain.cancelScheduledValues(now);
        voice.gain.gain.setTargetAtTime(0, now, .004);
        voice.oscillators.forEach(({oscillator}) => { try { oscillator.stop(now + .018); } catch (_) { /* already ended */ } });
      });
    }
  }
  class Player {
    constructor(engine, callbacks, clock) {
      this.engine = engine; this.callbacks = callbacks; this.timer = null; this.guard = null;
      this.generation = 0; this.running = false;
      this.clock = clock || { setTimeout: (fn,ms) => setTimeout(fn,ms), clearTimeout: id => clearTimeout(id), now: () => performance.now() };
    }
    async start(state) {
      this.stop();
      const token = ++this.generation;
      if (!root.MusicLoops.isReady(state)) return;
      const pattern = [...state.pattern], mode = state.mode, beat = 60000 / state.settings.tempo;
      const count = mode === 'while' ? Infinity : pattern.length * (mode === 'count' ? 2 : 1);
      try { if (!state.settings.visualOnly) await this.engine.ready(); }
      catch (error) { if (token === this.generation) this.callbacks.error(error); return; }
      if (token !== this.generation) return;
      this.running = true;
      let index = 0;
      const started = this.clock.now();
      this.callbacks.start();
      this.guard = this.clock.setTimeout(() => this.stop('limit'), 60000);
      const tick = () => {
        if (!this.running || token !== this.generation) return;
        if (index >= count) { this.stop('complete'); return; }
        // Do not catch up with a burst of sounds after a suspended/throttled tab.
        if (this.clock.now() - started > index * beat + 1800) { this.stop('interrupted'); return; }
        const event = root.MusicLoops.eventAt(pattern, index);
        this.callbacks.step(event);
        if (!state.settings.visualOnly) this.engine.note(event.sound, beat / 1000);
        index += 1;
        this.timer = this.clock.setTimeout(tick, beat);
      };
      tick();
    }
    stop(reason) {
      ++this.generation; this.running = false;
      if (this.timer !== null) this.clock.clearTimeout(this.timer);
      if (this.guard !== null) this.clock.clearTimeout(this.guard);
      this.timer = null; this.guard = null; this.engine.silence();
      if (reason) this.callbacks.stop(reason);
    }
  }
  root.MusicLoopsAudio = { SoundEngine, Player };
})(typeof window !== 'undefined' ? window : {});
