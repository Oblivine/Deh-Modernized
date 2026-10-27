(()=>{
'use strict';
const root=document.getElementById('x3-2008'),main=document.getElementById('ax-main'),native=window.DEHNative;
if(!root||!native)return;
let state=null,lastMessage='',active=null,descriptor=null,editing=false,dialMode=false,refreshQueued=false;
const byAction=(action)=>root.querySelector('[data-action="'+action+'"]');
const setText=(node,value)=>{if(node&&node.textContent!==String(value))node.textContent=String(value)};
const formatTime=n=>{n=Math.max(0,Math.floor(Number(n)||0));return String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0')};
function refresh(){
 refreshQueued=false;
 if(state){root.classList.add('native-ready');setText(root.querySelector('.mx-track-title'),state.title);setText(root.querySelector('.mx-track-artist'),state.album);setText(root.querySelector('.mx-track-index'),state.count?'TRACK '+String(state.index).padStart(2,'0')+' / '+String(state.count).padStart(2,'0'):'NO FILE');setText(root.querySelector('#mx-elapsed'),formatTime(state.position));setText(root.querySelector('.mx-track-time .ax-time-row span:last-child'),formatTime(state.duration));setText(root.querySelector('#mx-volume-readout'),state.volume+'%');
  for(const [action,pressed] of [['play',state.state==='playing'],['pause',state.state==='paused'],['stop',state.state==='stopped']]){const b=root.querySelector('#mx-playback-dock [data-action="'+action+'"]');if(b)b.setAttribute('aria-pressed',String(pressed));}
  if(state.message&&state.message!==lastMessage){lastMessage=state.message;native.showMessage(state.message)}else if(!state.message)lastMessage='';
 }
 const pageTitle=root.querySelector('#mx-page-title');const pane=main.querySelector('.ax-pane');
 if(pageTitle&&pane&&pageTitle.textContent==='Settings'&&!pane.querySelector('[data-action="native-settings"]')){const b=document.createElement('button');b.className='ax-menu-row';b.dataset.action='native-settings';b.innerHTML='<span>Android &amp; dial setup</span><span>Open ›</span>';const heading=pane.querySelector('.ax-heading');if(heading)heading.insertAdjacentElement('afterend',b);else pane.prepend(b)}
 if(dialMode&&descriptor&&(!active||!active.isConnected)){const n=locate(descriptor);if(n)focus(n,false)}
}
function schedule(){if(!refreshQueued){refreshQueued=true;requestAnimationFrame(refresh)}}
window.DEHAndroidUpdate=data=>{state=data;schedule()};
window.DEHReturnToPlayer=()=>{const b=byAction('nowplaying');if(b)b.click()};
new MutationObserver(schedule).observe(root,{subtree:true,childList:true,characterData:true});
const blocked={FM:'Radio uses the head unit manufacturer’s app.',BT:'Bluetooth music needs head unit integration.',PHONE:'Use the head unit phone app.',CP:'Open the head unit CarPlay app.',AA:'Open the head unit Android Auto app.',MIRROR:'Screen mirroring requires the head unit app.',AIRPLAY:'Wireless mirroring requires the head unit app.',CAM:'Camera integration is not available in this preview.',AV:'AV input requires the head unit app.'};
document.addEventListener('click',e=>{const b=e.target.closest('[data-action]');if(!b)return;const action=b.dataset.action,value=b.dataset.value;
 if(action==='native-apps'){e.preventDefault();e.stopImmediatePropagation();native.openApps();return}
 if(action==='native-settings'){e.preventDefault();e.stopImmediatePropagation();showSettings();return}
 if(action==='power'&&!root.querySelector('.ax-idle'))native.playback('pause');
 if(action==='volume'){e.preventDefault();e.stopImmediatePropagation();native.volumePanel();return}
 if(['play','pause','stop','previous','next'].includes(action)&&b.closest('#mx-playback-dock')){e.preventDefault();e.stopImmediatePropagation();native.playback(action);return}
 if(action==='source'){e.preventDefault();e.stopImmediatePropagation();if(value==='USB'||value==='SD')native.chooseMusic();else native.showMessage(blocked[value]||'This source needs head unit integration.');return}
 if(action==='audio'||action==='phone'||action==='devices'||action==='phonelink'||action==='swc'){e.preventDefault();e.stopImmediatePropagation();native.showMessage(action==='audio'?'Use the head unit audio settings; equalizer integration is not available yet.':'This feature needs head unit integration.');}
},true);
function options(){try{return JSON.parse(native.options())}catch(e){return {volumeNav:false,reverseDial:false,lastInput:'Unavailable'}}}
function showSettings(){
 if(document.getElementById('deh-dialog'))return;
 const dialog=document.createElement('div');dialog.id='deh-dialog';dialog.setAttribute('role','dialog');dialog.setAttribute('aria-label','Android and dial settings');dialog.setAttribute('aria-modal','true');
 const c=getComputedStyle(root);for(const name of ['--hot','--amber','--mid','--dim','--off','--ui-font'])dialog.style.setProperty(name,c.getPropertyValue(name));
 dialog.innerHTML='<div class="panel"><h2>ANDROID &amp; DIAL</h2><p>Turn a supported navigation dial to move between controls; press it to select. Volume keys stay as volume by default.</p><button data-option="volumeNav"></button><button data-option="reverseDial"></button><p>Last input: <strong id="deh-last-input"></strong></p><button data-command="home">Choose default Home app</button><button data-command="apps">Open Android apps</button><button data-command="close">Close</button></div>';
 document.body.appendChild(dialog);
 function update(){const v=options();for(const [key,label] of [['volumeNav','Use volume keys to navigate'],['reverseDial','Reverse rotary direction']]){const b=dialog.querySelector('[data-option="'+key+'"]');b.textContent=label+': '+(v[key]?'ON':'OFF');b.setAttribute('aria-pressed',String(!!v[key]))}setText(dialog.querySelector('#deh-last-input'),v.lastInput)}
 dialog.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.option){const v=options();native.setOption(b.dataset.option,!v[b.dataset.option]);update()}else if(b.dataset.command==='home')native.homeSettings();else if(b.dataset.command==='apps')native.openApps();else if(b.dataset.command==='close'){dialog.remove();active=null;descriptor=null;editing=false}});update();active=null;descriptor=null;if(dialMode)focus(dialog.querySelector('button'),false);
}
window.DEHInput=text=>{const el=document.querySelector('#deh-last-input');if(el)setText(el,text)};
function controls(){const area=document.getElementById('deh-dialog')||root;return [...area.querySelectorAll('button,input[type="range"],select')].filter(el=>!el.disabled&&el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden'&&getComputedStyle(el).display!=='none')}
function describe(el){return {action:el.dataset.action||'',value:el.dataset.value||'',key:el.dataset.key||'',index:el.dataset.index||'',option:el.dataset.option||'',command:el.dataset.command||'',tag:el.tagName}}
function locate(d){return controls().find(n=>{const a=describe(n);return Object.keys(d).every(k=>a[k]===d[k])})}
function focus(el,scroll=true){if(!el)return;if(active)active.classList.remove('dial-focus','dial-edit');active=el;descriptor=describe(el);el.classList.add(editing?'dial-edit':'dial-focus');el.focus({preventScroll:true});if(scroll)el.scrollIntoView({block:'nearest',inline:'nearest'})}
window.DEHNavigate=action=>{dialMode=true;let list=controls();if(!list.length)return;let index=list.indexOf(active);if(index<0){const n=(descriptor&&locate(descriptor))||list.find(x=>x.dataset.action==='play')||list[0];focus(n);return}if(action==='select'){if(active.matches('input[type="range"],select')){editing=!editing;focus(active);return}const d=describe(active);active.click();requestAnimationFrame(()=>{descriptor=d;const n=locate(d);if(n)focus(n,false)});return}const direction=action==='next'?1:-1;if(editing&&active.matches('input[type="range"],select')){const d=describe(active);if(active.tagName==='SELECT')active.selectedIndex=Math.max(0,Math.min(active.options.length-1,active.selectedIndex+direction));else if(direction>0)active.stepUp();else active.stepDown();active.dispatchEvent(new Event('input',{bubbles:true}));active.dispatchEvent(new Event('change',{bubbles:true}));requestAnimationFrame(()=>{descriptor=d;const n=locate(d);if(n)focus(n)});return}editing=false;focus(list[(index+direction+list.length)%list.length])};
window.DEHBack=()=>{const dialog=document.getElementById('deh-dialog');if(dialog){dialog.remove();active=null;descriptor=null;editing=false;return true}const title=root.querySelector('#mx-page-title');if(title&&title.textContent!=='Now playing'){const b=byAction('back');if(b)b.click();active=null;descriptor=null;editing=false;return true}return false};
root.addEventListener('touchstart',()=>{dialMode=false;editing=false;if(active)active.classList.remove('dial-focus','dial-edit');active=null;descriptor=null},{passive:true});
schedule();
})();
