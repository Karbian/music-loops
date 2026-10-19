'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const Core = require('../assets/core.js');

test('starts with two empty spaces, two sound choices, and no loop', () => {
  const state = Core.defaults();
  assert.deepEqual(state.pattern,[null,null]);
  assert.deepEqual(Core.palette(state.level),['piano','bell']);
  assert.equal(Core.isReady(state),false);
  assert.equal(state.mode,'once');
  assert.equal(state.settings.volume,18);
});
test('sequence order and counted loop preserve every sound and rest', () => {
  const state = Core.normalize({...Core.defaults(),level:'next',pattern:['piano','rest','bell','piano'],mode:'count'});
  const events = Core.events(state);
  assert.deepEqual(events.map(e=>e.sound),['piano','rest','bell','piano','piano','rest','bell','piano']);
  assert.deepEqual(events.map(e=>e.cycle),[1,1,1,1,2,2,2,2]);
  assert.deepEqual(events.map(e=>e.step),[0,1,2,3,0,1,2,3]);
});
test('incomplete patterns do not generate playback events', () => {
  assert.deepEqual(Core.events({...Core.defaults(),pattern:['piano',null]}),[]);
});
test('import is bounded, discards unknown content, and migrates older repeat settings', () => {
  const state = Core.normalize({schemaVersion:1,level:'first',pattern:['<script>','bell','drum'],mode:'while',settings:{volume:900,tempo:-10,language:'xx',showCode:'yes'}});
  assert.deepEqual(state.pattern,[null,'bell']);
  assert.equal(state.mode,'count');
  assert.equal(state.settings.volume,40);
  assert.equal(state.settings.tempo,60);
  assert.equal(state.settings.language,'es');
  assert.equal(Object.hasOwn(state.settings,'showCode'),false);
  assert.throws(()=>Core.normalize({schemaVersion:99}));
  assert.throws(()=>Core.normalize(null));
});
test('levels preserve available sounds and contain their sound vocabulary', () => {
  const bigger = Core.resize({...Core.defaults(),pattern:['piano','bell']},'explore');
  assert.equal(bigger.pattern.length,8);
  assert.deepEqual(bigger.pattern.slice(0,2),['piano','bell']);
  const smaller = Core.resize({...bigger,pattern:['drum','bell','piano','rest','bell','piano','bell','piano']},'first');
  assert.deepEqual(smaller.pattern,[null,'bell']);
});
test('picture rows show the same cards once or twice, preserving their order', () => {
  const state = {...Core.defaults(),pattern:['piano','bell']};
  assert.deepEqual(Core.pictureRows(state),[['piano','bell']]);
  const rows = Core.pictureRows({...state,mode:'count'});
  assert.deepEqual(rows,[['piano','bell'],['piano','bell']]);
  rows[0][0]='bell';
  assert.deepEqual(rows[1],['piano','bell']);
  assert.deepEqual(state.pattern,['piano','bell']);
  assert.deepEqual(Core.pictureRows({...state,pattern:['piano',null]}),[['piano',null]]);
});

function fixture() {
  let now = 0, id = 0;
  const tasks = new Map(), notes = [], steps = [], stops = [], errors = [];
  let readyCalls = 0, silenceCalls = 0;
  const clock = {now:()=>now,setTimeout:(fn,ms)=>{tasks.set(++id,{fn,time:now+ms});return id;},clearTimeout:id=>tasks.delete(id)};
  const window = {MusicLoops:Core};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/audio.js'),'utf8'),{window});
  const engine = {ready:async()=>{readyCalls++;},silence:()=>{silenceCalls++;},note:sound=>notes.push(sound)};
  const player = new window.MusicLoopsAudio.Player(engine,{start:()=>{},step:event=>steps.push(event),stop:reason=>stops.push(reason),error:error=>errors.push(error)},clock);
  function advance(ms) {
    const end = now + ms;
    for (;;) {
      const candidates = [...tasks.entries()].filter(([,task])=>task.time<=end).sort((a,b)=>a[1].time-b[1].time);
      if (!candidates.length) break;
      const [key,task] = candidates[0]; tasks.delete(key); now=task.time; task.fn();
    }
    now=end;
  }
  function flushLate() {
    const pending = [...tasks.entries()].filter(([,task])=>task.time<=now).sort((a,b)=>a[1].time-b[1].time)[0];
    if (pending) { tasks.delete(pending[0]); pending[1].fn(); }
  }
  return {player,engine,notes,steps,stops,errors,tasks,advance,flushLate,jump:ms=>{now+=ms;},readyCalls:()=>readyCalls,silenceCalls:()=>silenceCalls};
}
const playable = () => ({...Core.defaults(),pattern:['piano','bell'],settings:{...Core.defaults().settings,tempo:60}});
test('play once sounds in order, completes, and clears timers', async () => {
  const f=fixture(); await f.player.start(playable()); f.advance(2500);
  assert.deepEqual(f.notes,['piano','bell']);
  assert.deepEqual(f.stops,['complete']);
  assert.equal(f.player.running,false);
  assert.equal(f.tasks.size,0);
});
test('counted loop plays the identical sequence exactly twice', async () => {
  const f=fixture(); await f.player.start({...playable(),mode:'count'}); f.advance(5000);
  assert.deepEqual(f.notes,['piano','bell','piano','bell']);
  assert.deepEqual(f.stops,['complete']);
});
test('stop immediately silences and cancels all future beats', async () => {
  const f=fixture(); await f.player.start({...playable(),mode:'count'});
  f.player.stop('paused'); const count=f.notes.length; f.advance(10000);
  assert.equal(f.notes.length,count);
  assert.equal(f.tasks.size,0);
  assert.ok(f.silenceCalls()>=2);
});
test('pending audio activation cannot start music after Pause', async () => {
  const f=fixture(); let release;
  f.engine.ready=()=>new Promise(resolve=>{release=resolve;});
  const pending=f.player.start(playable()); f.player.stop('paused'); release(); await pending;
  assert.equal(f.player.running,false);
  assert.deepEqual(f.notes,[]);
  assert.equal(f.tasks.size,0);
});
test('pictures-only playback never requests audio', async () => {
  const f=fixture(); const state=playable(); state.settings.visualOnly=true;
  await f.player.start(state); f.advance(3000);
  assert.equal(f.readyCalls(),0);
  assert.deepEqual(f.notes,[]);
  assert.equal(f.steps.length,2);
});
test('older open-ended projects migrate to a finite loop and finish after two passes', async () => {
  const f=fixture(); const state=Core.normalize({...playable(),mode:'while',level:'explore',pattern:Array(8).fill('piano')});
  await f.player.start(state); f.advance(61000);
  assert.equal(f.player.running,false);
  assert.deepEqual(f.stops,['complete']);
  assert.equal(f.notes.length,16);
  assert.equal(f.tasks.size,0);
});
test('audio failure reports an error without starting a timer', async () => {
  const f=fixture(); f.engine.ready=async()=>{throw new Error('blocked');};
  await f.player.start(playable());
  assert.equal(f.errors.length,1);
  assert.equal(f.player.running,false);
  assert.equal(f.tasks.size,0);
});
test('a delayed tab stops instead of catching up with a burst of sounds', async () => {
  const f=fixture(); await f.player.start({...playable(),mode:'count'});
  f.jump(5000); f.flushLate();
  assert.deepEqual(f.notes,['piano']);
  assert.deepEqual(f.stops,['interrupted']);
  assert.equal(f.tasks.size,0);
});

test('C major contains all eight pitches from C4 to the octave C5', () => {
  const notes=Core.SCALES['c-major'].notes;
  assert.deepEqual(notes,['note-c4','note-d4','note-e4','note-f4','note-g4','note-a4','note-b4','note-c5']);
  const midi=notes.map(n=>Core.noteInfo(n).midi);
  assert.deepEqual(midi.slice(1).map((n,i)=>n-midi[i]),[2,2,1,2,2,2,1]);
  assert.equal(midi.at(-1)-midi[0],12);
});
test('A natural minor contains all eight pitches from A3 to the octave A4', () => {
  const notes=Core.SCALES['a-minor'].notes;
  assert.deepEqual(notes,['note-a3','note-b3','note-c4','note-d4','note-e4','note-f4','note-g4','note-a4']);
  const midi=notes.map(n=>Core.noteInfo(n).midi);
  assert.deepEqual(midi.slice(1).map((n,i)=>n-midi[i]),[2,1,2,2,1,2,2]);
  assert.equal(midi.at(-1)-midi[0],12);
});
test('scale notes have correctly tuned frequencies and exact octave ratios', () => {
  assert.equal(Core.frequencyFor('note-a4'),440);
  assert.equal(Core.frequencyFor('note-a3'),220);
  assert.ok(Math.abs(Core.frequencyFor('note-c4')-261.6255653005986)<1e-9);
  assert.equal(Core.frequencyFor('note-c5')/Core.frequencyFor('note-c4'),2);
  assert.equal(Core.frequencyFor('untrusted-note'),null);
});
test('selecting either scale creates a ready eight-card sequence without changing the old project', () => {
  const original=playable(), before=JSON.stringify(original);
  for (const collection of Object.keys(Core.SCALES)) {
    const state=Core.setCollection(original,collection);
    assert.equal(state.collection,collection);
    assert.equal(state.level,'explore');
    assert.equal(state.mode,'once');
    assert.equal(Core.isReady(state),true);
    assert.deepEqual(state.pattern,Core.SCALES[collection].notes);
    assert.deepEqual(Core.palette('first',collection),Core.SCALES[collection].notes);
  }
  assert.equal(JSON.stringify(original),before);
});
test('two-space scale activities retain the eight-note collection and can restore the complete scale', () => {
  const full=Core.setCollection(playable(),'c-major'), short=Core.resize(full,'first');
  assert.deepEqual(short.pattern,['note-c4','note-d4']);
  assert.equal(Core.palette(short.level,short.collection).length,8);
  assert.deepEqual(Core.example(short).pattern,full.pattern);
  assert.equal(Core.example(short).mode,'once');
});
test('version 1 projects migrate to version 2 while preserving the sequence and settings', () => {
  const old={schemaVersion:1,level:'first',pattern:['bell','piano'],mode:'count',settings:{language:'en',tempo:60,volume:11,visualOnly:true,highlight:false}};
  const migrated=Core.normalize(old);
  assert.equal(migrated.schemaVersion,2);
  assert.equal(migrated.collection,'sounds');
  assert.deepEqual(migrated.pattern,old.pattern);
  assert.deepEqual(migrated.settings,old.settings);
  assert.equal(migrated.mode,'count');
});
test('a version 2 scale survives JSON serialization with notes, pictures, and settings intact', () => {
  const state=Core.setCollection(playable(),'a-minor');state.mode='count';
  const restored=Core.normalize(JSON.parse(JSON.stringify(state)));
  assert.deepEqual(restored,state);
  assert.deepEqual(Core.pictureRows(restored),[state.pattern,state.pattern]);
  for(const note of ['note-c4','note-d4','note-e4','note-f4','note-g4','note-a4']) {
    assert.equal(Core.cardClass(note),'pitched tone-'+Core.noteInfo(note).letter);
  }
});
test('a scale import rejects cards outside that collection and ignores arbitrary note text', () => {
  const state=Core.normalize({...Core.setCollection(playable(),'c-major'),pattern:['note-b3','<img src=x>','note-c4','note-d4','note-e4','note-f4','note-g4','note-a4']});
  assert.deepEqual(state.pattern.slice(0,3),[null,null,'note-c4']);
  assert.equal(Core.isReady(state),false);
  assert.deepEqual(Core.palette('explore','sounds'),['piano','bell','drum','rest']);
});
test('each complete scale plays every pitch once, or twice in the same order', async () => {
  for(const collection of Object.keys(Core.SCALES)) {
    for(const mode of ['once','count']) {
      const f=fixture(), state=Core.setCollection(playable(),collection);state.mode=mode;
      await f.player.start(state);f.advance(18000);
      assert.deepEqual(f.notes,mode==='count'?[...state.pattern,...state.pattern]:state.pattern);
      assert.deepEqual(f.stops,['complete']);
      assert.equal(f.tasks.size,0);
    }
  }
});
test('Pause during a scale stops future notes and clears its active timers', async () => {
  const f=fixture(), state=Core.setCollection(playable(),'c-major');
  await f.player.start(state);f.advance(2000);f.player.stop('paused');
  const heard=[...f.notes];f.advance(20000);
  assert.deepEqual(heard,['note-c4','note-d4','note-e4']);
  assert.deepEqual(f.notes,heard);
  assert.equal(f.tasks.size,0);
});
test('the synthesizer sends each scale pitch to a distinct fundamental oscillator', async () => {
  const oscillators=[];
  const param=()=>({value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){},setTargetAtTime(){},cancelScheduledValues(){}});
  class AudioContext {
    constructor(){this.state='running';this.currentTime=0;this.destination={};}
    createGain(){return {gain:param(),connect(){},disconnect(){}};}
    createOscillator(){const node={frequency:param(),connect(){},disconnect(){},start(){},stop(){}};oscillators.push(node);return node;}
  }
  const window={MusicLoops:Core,AudioContext};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/audio.js'),'utf8'),{window});
  const engine=new window.MusicLoopsAudio.SoundEngine();await engine.ready();
  for(const collection of Object.keys(Core.SCALES)) {
    for(const sound of Core.SCALES[collection].notes){
      const offset=oscillators.length;engine.note(sound,1);
      assert.equal(oscillators[offset].frequency.value,Core.frequencyFor(sound));
      assert.equal(oscillators[offset+1].frequency.value,Core.frequencyFor(sound)*2);
      assert.equal(oscillators[offset+2].frequency.value,Core.frequencyFor(sound)*3);
    }
  }
  const count=oscillators.length;engine.setVolume(18,true);engine.note('note-c4',1);
  assert.equal(oscillators.length,count);
});
