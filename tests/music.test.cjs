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
