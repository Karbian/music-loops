(function () {
  'use strict';
  const Core = window.MusicLoops;
  const $ = id => document.getElementById(id);
  const TEXT = {
    es: {
      skip:'Ir a mi música',adult:'Acompañante',yourStudio:'TU PEQUEÑO ESTUDIO',title:'Tu música, a tu ritmo.',subtitle:'Elige. Crea. Escucha.',
      choose:'Elige un sonido',preview:'Escuchar este sonido',place:'Ponlo en un espacio',undo:'Deshacer',mySequence:'MI SECUENCIA',inOrder:'Primero un sonido. Después, otro.',
      listen:'Escucha tu música',howMany:'¿Cuántas veces?',once:'Una vez',twice:'Dos veces',untilStop:'Hasta parar',play:'Escuchar',stop:'Parar',mute:'Silenciar',unmute:'Activar sonido',softSound:'Sonido suave',silent:'Sin sonido',
      behindMusic:'DETRÁS DE TU MÚSICA',codeTitle:'Tu secuencia es un programa.',saved:'Se guarda en este dispositivo.',notSaved:'No se pudo guardar aquí. Descarga una copia.',ownPace:'Sin prisa. Puedes cambiar de idea.',
      iCanSay:'Puedo decir:',pause:'Pausa',help:'Ayuda',done:'Terminé',myChoice:'MI ELECCIÓN',return:'Volver a mi música',nothingStarts:'La música sigue en silencio.',
      pauseTitle:'Quiero una pausa',pauseCopy:'Puedes descansar. Tu música te espera.',helpTitle:'Necesito ayuda',helpCopy:'Puedes mostrar esta pantalla a quien te acompaña.',doneTitle:'Terminé por ahora',doneCopy:'Puedes dejarlo aquí. Tu secuencia está guardada en este dispositivo.',doneUnsaved:'Puedes dejarlo aquí. La secuencia sigue aquí mientras esta página permanezca abierta.',
      adultSpace:'ESPACIO DEL ACOMPAÑANTE',settings:'Ajustar la experiencia',settingsIntro:'Empieza con lo que hace con comodidad. Tú decides cuándo ofrecer más.',
      level:'Espacios y sonidos',levelFirst:'2 espacios · 2 sonidos',levelNext:'4 espacios · 3 sonidos',levelExplore:'8 espacios · 4 sonidos',levelNote:'Al ampliar se conserva la secuencia. Al reducir, los pasos que sobran se pueden recuperar con Deshacer.',
      language:'Idioma',tempo:'Velocidad',slow:'Lenta · 60',steady:'Tranquila · 72',walking:'Caminando · 90',volume:'Volumen',visualOnly:'Solo imágenes (sin sonido)',highlight:'Marcar el espacio que suena',showCode:'Mostrar el programa (FOR / WHILE)',
      whileNote:'“Hasta parar” aparece solo con 8 espacios. Se detiene al pulsar Parar, Pausa, Ayuda o Terminé; también al cambiar de pestaña. Límite de sesión: 60 segundos.',
      smallActivities:'Pequeñas actividades',activityOne:'Elige un sonido y ponlo en los dos espacios.',activityTwo:'Cambia el segundo sonido y escucha el orden.',activityThree:'Elige “Dos veces”. Es la misma secuencia que vuelve a empezar: un bucle.',
      example:'Poner un ejemplo',clear:'Vaciar espacios',keepMusic:'Conservar la música',localNote:'La secuencia y los ajustes se guardan en este navegador. Puedes descargar una copia sin nombres ni datos personales.',export:'Descargar secuencia',import:'Abrir secuencia',guide:'Guía de acompañamiento ↗',
      adultNote:'Las tarjetas muestran una elección en esta pantalla; no envían avisos. Acuerda su significado con ella y responde a su elección.',back:'Volver al estudio',close:'Cerrar',
      piano:'Piano',bell:'Campana',drum:'Tambor',rest:'Silencio',add:'Pon aquí',step:'Espacio',steps:'pasos',empty:'vacío',selectFirst:'Elige un sonido arriba.',
      fillTwo:'Completa los dos espacios.',fillAll:'Completa los espacios.',ready:'Tu secuencia está lista.',playing:'Escuchando tu secuencia.',playingSilent:'Mostrando tu secuencia sin sonido.',complete:'Tu secuencia terminó.',stopped:'La música se detuvo.',paused:'La música está en pausa.',limit:'Sesión terminada. Puedes escuchar otra vez.',interrupted:'La música se detuvo. Puedes volver a escuchar.',audioError:'No se pudo activar el sonido. Puedes usar “Solo imágenes” en Acompañante.',
      loopOnce:'Tu secuencia suena una vez.',loopTwice:'La misma secuencia vuelve a empezar. Eso es un bucle.',loopWhile:'Tu secuencia vuelve a empezar hasta pulsar Parar (máximo 60 segundos).',
      placed:'Sonido colocado.',selected:'Ahora elige un espacio.',previewed:'Escuchando el sonido elegido.',previewSilent:'Este sonido está seleccionado. El audio está apagado.',exported:'Copia descargada.',imported:'Secuencia abierta. No se inicia la música.',invalidFile:'No pudimos abrir ese archivo. Elige una copia JSON de Mi Ritmo (máximo 50 KB).',undoDone:'Cambio deshecho.',exampleDone:'Ejemplo listo. Pulsa Escuchar cuando quieras.',cleared:'Espacios vacíos.',
      repeatLabel:'Repeticiones',communicationLabel:'Puedo decir',stepPlaying:'Suena ahora',mutedStatus:'Audio silenciado.',unmutedStatus:'Audio disponible al pulsar Escuchar.'
    },
    en: {
      skip:'Go to my music',adult:'Companion',yourStudio:'YOUR LITTLE STUDIO',title:'Your music, at your pace.',subtitle:'Choose. Create. Listen.',
      choose:'Choose a sound',preview:'Listen to this sound',place:'Put it in a space',undo:'Undo',mySequence:'MY SEQUENCE',inOrder:'First one sound. Then another.',
      listen:'Listen to your music',howMany:'How many times?',once:'Once',twice:'Twice',untilStop:'Until I stop',play:'Listen',stop:'Stop',mute:'Mute',unmute:'Unmute',softSound:'Soft sound',silent:'No sound',
      behindMusic:'BEHIND YOUR MUSIC',codeTitle:'Your sequence is a program.',saved:'Saved on this device.',notSaved:'Could not save here. Download a copy.',ownPace:'Take your time. You can change your mind.',
      iCanSay:'I can say:',pause:'Pause',help:'Help',done:'Finished',myChoice:'MY CHOICE',return:'Back to my music',nothingStarts:'The music stays silent.',
      pauseTitle:'I want a break',pauseCopy:'You can rest. Your music can wait.',helpTitle:'I need help',helpCopy:'You can show this screen to your companion.',doneTitle:'I am finished for now',doneCopy:'You can leave it here. Your sequence is saved on this device.',doneUnsaved:'You can leave it here. Your sequence stays here while this page remains open.',
      adultSpace:'COMPANION SPACE',settings:'Adjust the experience',settingsIntro:'Start with what feels comfortable. You decide when to offer more.',
      level:'Spaces and sounds',levelFirst:'2 spaces · 2 sounds',levelNext:'4 spaces · 3 sounds',levelExplore:'8 spaces · 4 sounds',levelNote:'Adding spaces keeps the sequence. After reducing spaces, Undo can recover the removed steps.',
      language:'Language',tempo:'Speed',slow:'Slow · 60',steady:'Steady · 72',walking:'Walking · 90',volume:'Volume',visualOnly:'Pictures only (no sound)',highlight:'Mark the space that is playing',showCode:'Show the program (FOR / WHILE)',
      whileNote:'“Until I stop” appears only with 8 spaces. Stop, Pause, Help, Finished, and leaving the tab stop it. Each session is limited to 60 seconds.',
      smallActivities:'Small activities',activityOne:'Choose one sound and put it in both spaces.',activityTwo:'Change the second sound and listen to the order.',activityThree:'Choose “Twice”. The same sequence starts again: a loop.',
      example:'Add an example',clear:'Empty the spaces',keepMusic:'Keep the music',localNote:'The sequence and settings are saved in this browser. Download a copy with no names or personal details.',export:'Download sequence',import:'Open sequence',guide:'Companion guide ↗',
      adultNote:'The cards show a choice on this screen; they do not send notifications. Agree on their meaning together and respond to her choice.',back:'Back to the studio',close:'Close',
      piano:'Piano',bell:'Bell',drum:'Drum',rest:'Rest',add:'Put it here',step:'Space',steps:'steps',empty:'empty',selectFirst:'Choose a sound above.',
      fillTwo:'Fill both spaces.',fillAll:'Fill the spaces.',ready:'Your sequence is ready.',playing:'Playing your sequence.',playingSilent:'Showing your sequence without sound.',complete:'Your sequence has finished.',stopped:'The music has stopped.',paused:'The music is paused.',limit:'Session finished. You can listen again.',interrupted:'The music stopped. You can listen again.',audioError:'Sound could not start. You can choose “Pictures only” in Companion.',
      loopOnce:'Your sequence plays once.',loopTwice:'The same sequence starts again. That is a loop.',loopWhile:'Your sequence starts again until you press Stop (up to 60 seconds).',
      placed:'Sound placed.',selected:'Now choose a space.',previewed:'Playing the selected sound.',previewSilent:'This sound is selected. Audio is off.',exported:'Copy downloaded.',imported:'Sequence opened. Music stays silent.',invalidFile:'We could not open that file. Choose a Mi Ritmo JSON copy (up to 50 KB).',undoDone:'Change undone.',exampleDone:'Example ready. Press Listen when you want.',cleared:'Spaces are empty.',
      repeatLabel:'Repetitions',communicationLabel:'I can say',stepPlaying:'Playing now',mutedStatus:'Audio muted.',unmutedStatus:'Sound is available when you press Listen.'
    }
  };
  const STORAGE = 'mi-ritmo-v1';
  let state = Core.defaults(), selected = null, history = [], muted = false, previewGeneration = 0, saved = true, currentStep = -1, messageType = null, previousFocus = null;
  try { const raw = localStorage.getItem(STORAGE); if (raw) state = Core.normalize(JSON.parse(raw)); } catch (_) { saved = false; }
  const t = key => TEXT[state.settings.language][key] || key;
  const icon = (name, css = 'icon') => '<svg class="'+css+'" aria-hidden="true"><use href="#i-'+name+'"/></svg>';
  const engine = new window.MusicLoopsAudio.SoundEngine();
  const player = new window.MusicLoopsAudio.Player(engine, {
    start() { $('play').disabled = true; $('play-status').textContent = t(state.settings.visualOnly || muted ? 'playingSilent' : 'playing'); },
    step(event) {
      currentStep = event.step;
      document.querySelectorAll('.step').forEach((button, index) => {
        const active = index === event.step;
        button.classList.toggle('current', active && state.settings.highlight);
        if (active) button.setAttribute('aria-current', 'step'); else button.removeAttribute('aria-current');
      });
    },
    stop(reason) { currentStep = -1; document.querySelectorAll('.step').forEach(button => { button.classList.remove('current'); button.removeAttribute('aria-current'); }); $('play').disabled = !Core.isReady(state); $('play-status').textContent = t(reason === 'complete' ? 'complete' : reason === 'limit' ? 'limit' : reason === 'interrupted' ? 'interrupted' : 'stopped'); },
    error() { $('play-status').textContent = t('audioError'); $('play').disabled = !Core.isReady(state); }
  });
  function persist() { try { localStorage.setItem(STORAGE, JSON.stringify(state)); saved = true; } catch (_) { saved = false; } $('save-status').textContent = t(saved ? 'saved' : 'notSaved'); }
  function snapshot() { history.push(JSON.parse(JSON.stringify(state))); if (history.length > 25) history.shift(); }
  function halt(reason) { ++previewGeneration; player.stop(reason); engine.silence(); }
  function refreshStatus() { $('play-status').textContent = Core.isReady(state) ? t('ready') : t(state.pattern.length === 2 ? 'fillTwo' : 'fillAll'); }
  function render() {
    const focused = document.activeElement && document.activeElement.dataset.focus;
    document.documentElement.lang = state.settings.language;
    document.querySelectorAll('[data-i18n]').forEach(element => { element.textContent = t(element.dataset.i18n); });
    $('sound-palette').innerHTML = Core.palette(state.level).map(sound => '<button class="sound-button '+sound+'" data-sound="'+sound+'" data-focus="sound-'+sound+'" aria-pressed="'+(selected === sound)+'">'+icon(sound,'instrument')+'<span>'+t(sound)+'</span>'+icon('check','icon selection-check')+'</button>').join('');
    $('sequence').dataset.length = state.pattern.length;
    $('sequence').innerHTML = state.pattern.map((sound, index) => '<button class="step '+(sound ? 'filled '+sound : '')+'" data-step="'+index+'" data-focus="step-'+index+'" aria-label="'+t('step')+' '+(index+1)+': '+(sound ? t(sound) : t('empty'))+'"><span class="step-number">'+(index+1)+'</span>'+icon(sound || 'plus',sound ? 'instrument' : 'step-plus')+'<span class="step-name">'+t(sound || 'add')+'</span></button>').join('');
    $('filled-count').textContent = state.pattern.filter(Boolean).length+' / '+state.pattern.length;
    $('level-label').textContent = state.pattern.length+' '+t('steps');
    $('preview-sound').disabled = !selected;
    $('undo').disabled = history.length === 0;
    $('play').disabled = !Core.isReady(state) || player.running;
    $('loop-options').setAttribute('aria-label', t('repeatLabel'));
    document.querySelector('.communication').setAttribute('aria-label',t('communicationLabel'));
    document.querySelectorAll('[data-loop]').forEach(button => { button.setAttribute('aria-pressed',String(state.mode === button.dataset.loop)); button.hidden = button.dataset.loop === 'while' && state.level !== 'explore'; });
    $('loop-explanation').textContent = t(state.mode === 'once' ? 'loopOnce' : state.mode === 'count' ? 'loopTwice' : 'loopWhile');
    $('stop').setAttribute('aria-label',t('stop'));
    $('settings-close').setAttribute('aria-label',t('close'));
    $('mute').setAttribute('aria-pressed',String(muted));
    $('mute').innerHTML = icon(muted || state.settings.visualOnly ? 'mute' : 'sound')+'<span>'+t(muted ? 'unmute' : 'mute')+'</span>';
    $('sound-label').textContent = t(muted || state.settings.visualOnly || state.settings.volume === 0 ? 'silent' : 'softSound');
    $('code-panel').hidden = !state.settings.showCode;
    $('code-output').textContent = Core.pseudocode(state, TEXT[state.settings.language]);
    $('setting-level').value = state.level; $('setting-language').value = state.settings.language;
    $('setting-tempo').value = String(state.settings.tempo); $('setting-volume').value = String(state.settings.volume);
    $('volume-output').textContent = state.settings.volume+'%';
    $('setting-visual').checked = state.settings.visualOnly; $('setting-highlight').checked = state.settings.highlight; $('setting-code').checked = state.settings.showCode;
    engine.setVolume(state.settings.volume,muted || state.settings.visualOnly);
    refreshStatus(); persist();
    if (focused) { const element = document.querySelector('[data-focus="'+focused+'"]'); if (element) element.focus({preventScroll:true}); }
  }
  function change(mutator, message) { halt(); snapshot(); mutator(); state = Core.normalize(state); render(); if (message) $('play-status').textContent = t(message); }
  $('sound-palette').addEventListener('click', event => {
    const button = event.target.closest('[data-sound]'); if (!button) return;
    halt(); selected = button.dataset.sound; render(); $('play-status').textContent = t('selected');
  });
  $('sequence').addEventListener('click', event => {
    const button = event.target.closest('[data-step]'); if (!button) return;
    if (!selected) { $('play-status').textContent = t('selectFirst'); return; }
    change(() => { state.pattern[Number(button.dataset.step)] = selected; },'placed');
    if (Core.isReady(state)) refreshStatus();
  });
  $('preview-sound').addEventListener('click', async () => {
    if (!selected) return;
    halt(); const token = ++previewGeneration, sound = selected;
    if (state.settings.visualOnly || muted || state.settings.volume === 0) { $('play-status').textContent = t('previewSilent'); return; }
    try { await engine.ready(); if (token !== previewGeneration || $('communication-dialog').open || $('settings-dialog').open || document.hidden) return; engine.note(sound,.7); $('play-status').textContent = t('previewed'); }
    catch (_) { if (token === previewGeneration) $('play-status').textContent = t('audioError'); }
  });
  $('loop-options').addEventListener('click', event => {
    const button = event.target.closest('[data-loop]'); if (!button || button.hidden) return;
    halt(); state.mode = button.dataset.loop; render();
  });
  $('play').addEventListener('click', () => { if (!Core.isReady(state) || player.running) return; ++previewGeneration; engine.silence(); $('play').disabled = true; player.start(JSON.parse(JSON.stringify(state))); });
  $('stop').addEventListener('click', () => halt('stopped'));
  $('mute').addEventListener('click', () => { halt(); muted = !muted; render(); $('play-status').textContent = t(muted ? 'mutedStatus' : 'unmutedStatus'); });
  $('undo').addEventListener('click', () => { if (!history.length) return; halt(); state = history.pop(); if (!Core.palette(state.level).includes(selected)) selected = null; render(); $('play-status').textContent = t('undoDone'); });
  function showMessage(type) {
    halt('paused'); previousFocus = document.activeElement; messageType = type;
    $('message-symbol').innerHTML = icon(type === 'pause' ? 'pause' : type === 'help' ? 'help' : 'check');
    $('message-title').textContent = t(type+'Title');
    $('message-copy').textContent = t(type === 'done' && !saved ? 'doneUnsaved' : type+'Copy');
    if (!$('communication-dialog').open) $('communication-dialog').showModal();
  }
  ['pause','help','done'].forEach(type => $(type+'-card').addEventListener('click', () => showMessage(type)));
  $('message-return').addEventListener('click', () => $('communication-dialog').close());
  $('communication-dialog').addEventListener('close', () => { messageType = null; if (previousFocus) previousFocus.focus(); refreshStatus(); });
  $('communication-dialog').addEventListener('cancel', () => { halt(); });
  $('settings-open').addEventListener('click', () => { halt(); $('file-status').textContent = ''; $('settings-dialog').showModal(); });
  $('settings-close').addEventListener('click', () => $('settings-dialog').close());
  $('settings-finish').addEventListener('click', () => $('settings-dialog').close());
  $('settings-dialog').addEventListener('close', () => { halt(); $('settings-open').focus(); refreshStatus(); });
  $('setting-level').addEventListener('change', event => change(() => { state = Core.resize(state,event.target.value); if (!Core.palette(state.level).includes(selected)) selected = null; }));
  $('setting-language').addEventListener('change', event => { halt(); state.settings.language = event.target.value; render(); });
  $('setting-tempo').addEventListener('change', event => { halt(); state.settings.tempo = Number(event.target.value); render(); });
  $('setting-volume').addEventListener('input', event => { state.settings.volume = Number(event.target.value); engine.setVolume(state.settings.volume, muted || state.settings.visualOnly); $('volume-output').textContent = state.settings.volume+'%'; persist(); });
  $('setting-volume').addEventListener('change', () => render());
  [['setting-visual','visualOnly'],['setting-highlight','highlight'],['setting-code','showCode']].forEach(([id,key]) => $(id).addEventListener('change',event => { halt(); state.settings[key] = event.target.checked; render(); }));
  $('example').addEventListener('click', () => change(() => { state.pattern = Array.from({length:state.pattern.length},(_,index) => index % 2 === 0 ? 'piano' : 'bell'); },'exampleDone'));
  $('clear').addEventListener('click', () => change(() => { state.pattern = state.pattern.map(() => null); },'cleared'));
  $('export').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(state,null,2)],{type:'application/json'}), url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = 'mi-ritmo.json'; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url),1000); $('file-status').textContent = t('exported');
  });
  $('import').addEventListener('change',async event => {
    const file = event.target.files[0]; if (!file) return;
    halt();
    try {
      if (file.size > 51200) throw new Error('File too large');
      const raw = JSON.parse(await file.text());
      if (raw.schemaVersion !== 1 || !Array.isArray(raw.pattern) || !Object.hasOwn(Core.LEVELS,raw.level)) throw new Error('Invalid file');
      const next = Core.normalize(raw);
      // An imported project must never raise the listener's chosen volume.
      next.settings.volume = Math.min(state.settings.volume,next.settings.volume);
      snapshot(); state = next; selected = null; render(); $('file-status').textContent = t('imported');
    } catch (_) { $('file-status').textContent = t('invalidFile'); }
    event.target.value = '';
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) halt('interrupted'); });
  window.addEventListener('pagehide', () => halt());
  window.addEventListener('blur', () => { if (player.running) halt('interrupted'); });
  document.addEventListener('keydown',event => { if (event.key === 'Escape') halt('stopped'); });
  render();
})();
