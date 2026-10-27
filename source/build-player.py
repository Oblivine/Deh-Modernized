from pathlib import Path
import json,re,shutil,base64
from theme_palette import theme_palette
root=Path(__file__).resolve().parents[1]
source=root/'source'; dist=root/'dist'
base=(source/'base-player.js').read_text(encoding='utf-8')
views=(source/'base-views.js').read_text(encoding='utf-8')
# Keep all existing controls while simplifying the player.
views=views.replace("USB music","USB")
views=re.sub(r'^function clipCaption\(.*$', '''function clipCaption(){return `<div class="mx-animation-caption"><button data-action="clip-step" data-value="-1" aria-label="Previous animation">‹</button><button data-action="entertainment">Animations · ${esc(originalAssets[s.animation].name)} ›</button><button data-action="clip-step" data-value="1" aria-label="Next animation">›</button></div>`;}''',views,flags=re.M)
views=views.replace('''<div class="mx-source-line"><span class="mx-source-name">${s.source==='BT'?'Bluetooth':s.source==='SD'?'SD card':'USB'}</span><span class="mx-demo">Demo library · silent playback</span></div>''','')
views=re.sub(r'<div class="mx-secondary-controls">.*?</div></div>`;', '</div>`;',views)
views=views.replace('<input type="range" data-key="position" min="0" max="${t.duration}" value="${s.position}" aria-label="Track position">','')
gallery='''function entertainmentView(){const categories=['Movies','Backgrounds','Meters','Stills','Color'];const category=categories.includes(s.animationCategory)?s.animationCategory:'Movies';const list=animations.filter(([id])=>originalAssets[id].category===category);const size=root.clientWidth<520?4:6;const page=Math.min(Math.max(0,s.animationPage||0),Math.ceil(list.length/size)-1);return `<div class="ax-pane mx-gallery-pane">${head('Animations',Object.keys(originalAssets).length+' originals')}<nav class="mx-animation-tabs" aria-label="Animation categories">${categories.map(c=>button(c,'animation-category',`data-value="${c}" aria-pressed="${c===category}"`)).join('')}</nav><div class="mx-animation-gallery">${list.slice(page*size,(page+1)*size).map(([id,name])=>{const a=originalAssets[id];return button(`<img src="${a.still}" width="${a.width}" height="${a.height}" alt="${esc(name)} preview" decoding="async"><span>${esc(name)}</span>`,'animation',`data-value="${id}" aria-pressed="${s.animation===id}"`,'mx-animation-choice');}).join('')}</div><div class="mx-gallery-pagination">${button('‹ Previous','animation-page','data-value="-1" '+(page===0?'disabled':''))}<span class="ax-label">${page+1} / ${Math.ceil(list.length/size)}</span>${button('Next ›','animation-page','data-value="1" '+(page>=Math.ceil(list.length/size)-1?'disabled':''))}</div><div class="mx-gallery-footer">${button(icon(s.motion?'pause':'play')+(s.motion?'Pause motion':'Play motion'),'toggle','data-key="motion"')}<span class="mx-selected-clip">${esc(originalAssets[s.animation].name)}</span>${button('Show player','nowplaying')}</div><p class="mx-gallery-note">59 amber · 24 original color. Meter clips are recorded, not audio reactive.</p></div>`;}'''
views=re.sub(r'^function entertainmentView\(.*$',lambda _:gallery,views,flags=re.M)
views=views.replace("row('About this preview','about','Details')","row('About this preview','about','Details')")
# Put lab on page two, preserving six rows per page.
views=views.replace("toggle('Parking-brake detection','brake'),", "row('Hardware lab','lab','Memory / stress tests'),")
views=views.replace('Only their palette has been changed to amber.', '59 monochrome clips use amber; 24 color clips retain their original colors.')
views=views.replace('Radio, music playback and phone/camera connections are demonstrations.', 'Radio, music playback and phone/camera connections are silent demonstrations.')
views=views.replace('This is an interface prototype, not installable firmware. Hardware services and recovery still need verification.', 'This is an interface prototype, not installable firmware. Hardware services and recovery still need verification. Source: youxufkhan/carozerra. The 63 ms frame interval follows the reference player, not measured Pioneer hardware timing.')
# The clock and playback ticker only need one callback a second.
views=re.sub(r'^function loop\(.*$', '''function loop(){if(!root.isConnected){clearInterval(ticker);return;}if(document.hidden)return;if(s.playing&&!s.standby&&!s.call){s.position++;if(s.position>=tracks[s.track].duration){if(s.repeat===1)s.position=0;else if(s.track<2||s.repeat===2||s.shuffle){changeTrack(1);render();}else{s.position=0;s.playing=false;render();}}const pos=root.querySelector('[data-key="position"]');if(pos)pos.value=s.position;const elapsed=root.querySelector('#mx-elapsed');if(elapsed)elapsed.textContent=duration(s.position);}updateDim();}''',views,flags=re.M)
for line in ((source/'movie-views.js').read_text(encoding='utf-8-sig')+'\n'+(source/'theme-controls.js').read_text(encoding='utf-8-sig')+'\n'+(source/'skin-views.js').read_text(encoding='utf-8-sig')+'\n'+(source/'typeface-controls.js').read_text(encoding='utf-8-sig')).splitlines():
    match=re.match(r'function (\w+)\(',line)
    if match:views=re.sub(r'^function '+match[1]+r'\(.*$',lambda _:line,views,flags=re.M)
for line in views.splitlines():
    match=re.match(r'function (\w+)\(',line)
    if match:base=re.sub(r'^function '+match[1]+r'\(.*$',lambda _:line,base,flags=re.M)
base=base.replace("animation:'dolphins',fps:16", "animation:'dolphins',animationCategory:'Movies',animationPage:0,movieShuffle:false,illumination:'amber',typeface:'audiowide',displayTab:'color',labTab:'memory',labReserve:96,labPipeline:'stream',fps:16")
base=base.replace("const oel=()=>{", "const oel=()=>{")
base=re.sub(r'^const oel=.*$',lambda _:(source/'oel-view.js').read_text(encoding='utf-8-sig').strip(),base,flags=re.M)
base=base.replace("about:'About',reset:'Reset'", "about:'About',lab:'Hardware lab',reset:'Reset'")
base=base.replace("about:aboutView,reset:resetView", "about:aboutView,lab:labView,reset:resetView")
base=base.replace("case'about':case'reset':", "case'about':case'lab':case'reset':")
base=base.replace("case'animation':s.animation=v;", "case'animation-library':selectAnimationLibrary(v);return;case'animation-category':s.animationCategory=v;s.animationPage=0;break;case'animation-page':s.animationPage=Math.max(0,(s.animationPage||0)+Number(v));break;case'clip-step':{const ids=animations.map(a=>a[0]);s.animation=ids[(ids.indexOf(s.animation)+Number(v)+ids.length)%ids.length];break;}case'lab-tab':s.labTab=v;break;case'animation':s.animation=v;")
base=base.replace("render();requestAnimationFrame(loop);", "render();const ticker=setInterval(loop,1000);")
base=base.replace("if(['dayLevel','nightLevel','manualLevel'].includes(key))updateDim();", "if(['dayLevel','nightLevel','manualLevel'].includes(key))updateDim();if(key==='labReserve'){updateMemoryModel();}")
# Cache formatters instead of constructing three every second.
base=base.replace("function hours(){return Number(new Intl.DateTimeFormat('en-US',{hour:'2-digit',hourCycle:'h23',timeZone:'America/Chicago'}).format(now()));}","const hourFormatter=new Intl.DateTimeFormat('en-US',{hour:'2-digit',hourCycle:'h23',timeZone:'America/Chicago'});function hours(){return Number(hourFormatter.format(now()));}")
base=base.replace("function time(){return new Intl.DateTimeFormat('en-US',{hour:'2-digit',minute:'2-digit',hour12:!s.clock24,timeZone:'America/Chicago'}).format(now()).toUpperCase();}", "const clockFormatters=[true,false].map(hour12=>new Intl.DateTimeFormat('en-US',{hour:'2-digit',minute:'2-digit',hour12,timeZone:'America/Chicago'}));function time(){return clockFormatters[s.clock24?1:0].format(now()).toUpperCase();}")
# hourFormatter would be declared after initial restoration but before render.
base=base.replace('const defaults=','let typefaceRequestId=0,illuminationRequestId=0,movieShuffleTimer=null,animationLoading=false,movieShuffleKey=\'\',movieBag=[],movieBack=[],movieForward=[],animationRequestId=0,motionSource=\'\',motionStartedAt=0;\nconst movieIds=Object.keys(originalAssets).filter(id=>originalAssets[id].category===\'Movies\').sort((a,b)=>originalAssets[a].name.localeCompare(originalAssets[b].name,undefined,{numeric:true}));\nconst defaults=',1)
base=base.replace("if(reduced.matches&&!s.motionOverride)s.motion=false;","s.motion=true;")
base=base.replace("if(!sources.some(a=>a[0]===s.source))","s.motion=true;if(!sources.some(a=>a[0]===s.source))")
base=base.replace("function go(screen){","function go(screen){if(screen==='entertainment'){s.animationCategory='Movies';s.animationPage=0;}")
base=base.replace("case'clip-step':{const ids=animations.map(a=>a[0]);s.animation=ids[(ids.indexOf(s.animation)+Number(v)+ids.length)%ids.length];break;}","case'clip-step':stepMovie(Number(v));return;case'movie-shuffle':toggleMovieShuffle();return;")
base=base.replace("case'animation':s.animation=v;peaks.fill(0);wipeUntil=performance.now()+180;break;","case'animation':selectAnimation(v,{returnToPlayer:true});return;")
extra=(source/'lab-views.js').read_text(encoding='utf-8') if (source/'lab-views.js').exists() else 'function labView(){return pane("Hardware lab","<p>Preparing measured results.</p>");}'
extra+='\n'+(source/'control-dock.js').read_text(encoding='utf-8-sig')
base=base.replace('})();',extra+'\n'+(source/'movie-controls.js').read_text(encoding='utf-8-sig')+'\n'+''.join(line+'\n' for line in (source/'theme-controls.js').read_text(encoding='utf-8-sig').splitlines() if not line.startswith('function displayView('))+'\n'+''.join(line+'\n' for line in (source/'typeface-controls.js').read_text(encoding='utf-8-sig').splitlines() if not line.startswith('function displayView('))+'\n})();')
base=base.replace('function render(){',"function render(){normalizeAnimationLibrary();root.dataset.illumination=s.illumination;root.dataset.typeface=s.typeface;root.querySelectorAll('[data-action=\"animation-library\"]').forEach(n=>n.setAttribute('aria-pressed',activeAnimationLibrary()===n.dataset.value));const runningImages=[...main.querySelectorAll('.mx-animation img')];")
base=base.replace('paint();}',"const freshImages=[...main.querySelectorAll('.mx-animation img')];for(const old of runningImages){const fresh=freshImages.find(n=>n.className===old.className&&n.getAttribute('src')===old.getAttribute('src'));if(fresh)fresh.replaceWith(old);}updatePlaybackDock();paint();updateMemoryModel();armMovieShuffle();}")
base=base.replace("s.motion=true;if(!sources.some", "s.motion=true;if(!['amber','cyan'].includes(s.illumination))s.illumination='amber';if(!['audiowide','orbitron','accessories'].includes(s.typeface))s.typeface='audiowide';if(!sources.some")
base=base.replace("case'lab-tab':", "case'display-tab':s.displayTab=v;break;case'lab-tab':")
base=base.replace("const value=t.type==='range'?Number(t.value):t.value;", "if(key==='illumination'||key==='typeface')return;const value=t.type==='range'?Number(t.value):t.value;")
base=base.replace("root.addEventListener('change',e=>{const t=e.target,key=t.dataset.key;if(!key)return;", "root.addEventListener('change',e=>{const t=e.target,key=t.dataset.key;if(!key)return;if(key==='illumination'){changeIllumination(t.value);return;}if(key==='typeface'){changeTypeface(t.value);return;}")
base=base.replace("design:'X3 / 2008 amber touchscreen'", "design:'X3 / 2008 amber and cyan touchscreen',illumination:s.illumination")
base=base.replace("const a=originalAssets[id];return button", "const a=animationAsset(id);return button")
base=base.replace("function go(screen){","function go(screen,category='Movies'){").replace("if(screen==='entertainment'){s.animationCategory='Movies';","if(screen==='entertainment'){s.animationCategory=category;")
base=re.sub(r'^function icon\(.*$',lambda _:"function icon(name){return `<svg class=\"mx-skin-icon\" viewBox=\"0 0 24 24\" aria-hidden=\"true\"><use href=\"#mx-glyph-${name}\"></use></svg>`;}",base,flags=re.M)
base=base.replace("playing:false,repeat:0","playing:false,playbackStatus:'stopped',repeat:0")
base=base.replace("s.motion=true;if(!['amber'","s.playbackStatus=s.position>0?'paused':'stopped';s.motion=true;if(!['amber'")
base=base.replace("case'play':if(s.source==='FM')s.muted=!s.muted;", "case'pause':case'stop':if(s.source==='FM'){s.muted=true;}else if(['USB','SD','BT'].includes(s.source)){s.playing=false;s.playbackStatus=a==='pause'?'paused':'stopped';if(a==='stop')s.position=0;}else{notice('TRANSPORT IS HARDWARE DEPENDENT FOR THIS SOURCE');return;}break;case'play':if(s.source==='FM')s.muted=t.dataset.mode==='start'?false:!s.muted;")
base=base.replace("s.playing=!s.playing;", "s.playing=t.dataset.mode==='start'?true:!s.playing;s.playbackStatus=s.playing?'playing':'paused';")
base=re.sub(r'^function paint\(.*$',lambda _:"function paint(){}",base,flags=re.M)
base=base.replace("['eq','EQUALIZER']","['eq','EQ']").replace("['balance','Balance']","['balance','Stage']").replace("['delay','Time align']","['delay','Delay']").replace("['filter','Crossovers']","['filter','Filter']").replace("['loud','Bass & loudness']","['loud','Bass']")
base=base.replace("case'entertainment':",'').replace('entertainment:entertainmentView,','')
(source/'player.js').write_text(base,encoding='utf-8')
(dist/'player.js').write_text(base,encoding='utf-8')
markup=(source/'interface-template.html').read_text(encoding='utf-8')
assets=json.loads((source/'animation-assets.json').read_text(encoding='utf-8'))
cyan=json.loads((source/'cyan-animation-assets.json').read_text(encoding='utf-8'))
for k,a in cyan.items():assets[k].update(cyanAnimation=a['animation'],cyanStill=a['still'],cyanEncodedBytes=a['encodedBytes'])
public={k:{f:a[f] for f in ['name','file','frames','width','height','fps','durationMs','color','category','animation','still','encodedBytes','decodedRgbaBytes','streamDoubleRgbaBytes']}|({f:a[f] for f in ['cyanAnimation','cyanStill','cyanEncodedBytes']} if k in cyan else {}) for k,a in assets.items()}
markup=markup.replace('__ORIGINAL_ANIMATION_ASSETS__',json.dumps(public,separators=(',',':')))
markup=markup.replace('<script id="x3-2008-script">/* X3_2008_SCRIPT */</script>','<script src="assets/lucide.min.js"></script>\n<script src="assets/benchmark-results.js"></script>\n<script src="player.js"></script>')
css='''
#x3-2008 .mx-player-pane{justify-content:space-evenly;gap:7px;padding-top:12px;padding-bottom:12px}
#x3-2008 .mx-player-upper{gap:10px}
#x3-2008 .mx-animation-caption{margin:4px 0 0;display:grid;grid-template-columns:44px minmax(0,1fr) 44px 108px;gap:6px}
#x3-2008 .mx-animation-caption button{min-height:44px;padding:4px 6px;font-size:12px}
#x3-2008 .mx-animation-caption button[data-action="clip-step"]{font-size:23px;border:1px solid #57462c;border-radius:2px;background:#211e18}
#x3-2008 .mx-animation-caption button:hover{color:var(--hot);background:#392c1b}
#x3-2008 .mx-radio-pane{padding-top:4px;padding-bottom:4px}
#x3-2008 .mx-player-pane .mx-progress-block{margin-top:0}
#x3-2008 .mx-player-pane .mx-transport{margin-top:3px}
#x3-2008 .mx-movie-shuffle{font-size:12px!important;min-height:44px!important;gap:5px;border:1px solid #665132;background:#29251d}
#x3-2008 .mx-movie-list{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px}
#x3-2008 .mx-movie-choice{min-height:48px;padding:9px 6px;font-size:13px;justify-content:flex-start;text-align:left}
#x3-2008 .mx-movie-choice svg{flex-shrink:0;width:15px!important;height:15px!important}
#x3-2008 .mx-movie-choice span{overflow-wrap:anywhere}
@media(max-width:750px){#x3-2008 .mx-movie-list{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:480px){#x3-2008 .mx-movie-list{grid-template-columns:repeat(2,minmax(0,1fr))}#x3-2008 .mx-animation-caption{grid-template-columns:36px minmax(0,1fr) 36px 42px}#x3-2008 .mx-shuffle-label{display:none}#x3-2008 .mx-animation-caption button[data-action="clip-step"]{font-size:20px}}
#x3-2008 .mx-gallery-pane{padding-top:10px;padding-bottom:8px}
#x3-2008 .mx-gallery-pane .ax-heading{margin-bottom:9px;padding-bottom:7px;font-size:18px}
#x3-2008 .mx-animation-tabs{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:4px;margin-bottom:10px}
#x3-2008 .mx-animation-tabs button{min-height:38px;padding:7px 3px;font-size:12px}
#x3-2008 .mx-animation-choice{padding:7px;gap:5px;min-height:0;font-size:12px}
#x3-2008 .mx-animation-choice img{height:62px;aspect-ratio:auto;border:0}
#x3-2008 .mx-animation-choice span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
#x3-2008 .mx-gallery-pagination{display:grid;grid-template-columns:120px 1fr 120px;align-items:center;text-align:center;gap:8px;margin-top:8px}
#x3-2008 .mx-gallery-pagination button{min-height:36px;padding:7px;font-size:12px}
#x3-2008 .mx-gallery-footer{margin-top:8px}
#x3-2008 .mx-gallery-footer button{min-height:37px;padding:7px 12px;font-size:12px}
#x3-2008 .mx-selected-clip{color:var(--amber);font-size:12px;text-align:center}
#x3-2008 .mx-gallery-note{margin:8px 0 0;color:var(--dim);font-size:11px;line-height:1.35}
#x3-2008 .mx-lab-pane{padding-top:8px;padding-bottom:8px}
#x3-2008 .mx-lab-tabs{display:flex;gap:6px;margin-bottom:10px}
#x3-2008 .mx-lab-tabs button{flex:1;min-height:36px;padding:7px}
#x3-2008 .mx-lab-table{width:100%;border-collapse:collapse;font-size:12px;color:var(--mid)}
#x3-2008 .mx-lab-table td,#x3-2008 .mx-lab-table th{padding:7px 5px;border-bottom:1px solid #3d3529;text-align:left;font-weight:400}
#x3-2008 .mx-lab-table td:last-child{color:var(--hot);text-align:right;font-variant-numeric:tabular-nums}
#x3-2008 .mx-lab-note{font-size:12px;line-height:1.5;color:var(--mid);margin:9px 0}
#x3-2008 .mx-budget-track{height:20px;background:#332c23;margin:9px 0;overflow:hidden}
#x3-2008 .mx-budget-fill{display:block;height:100%;background:#bc7f32;max-width:100%}
#x3-2008 .mx-memory-result{color:var(--amber);font-size:16px;font-variant-numeric:tabular-nums}
@media(max-width:600px){#x3-2008 .mx-animation-choice img{height:55px}#x3-2008 .mx-animation-tabs{grid-template-columns:repeat(3,minmax(0,1fr))}#x3-2008 .mx-selected-clip{order:3;width:100%}}
@media(max-width:400px){#x3-2008 .mx-gallery-pagination{grid-template-columns:minmax(0,1fr) 42px minmax(0,1fr)}#x3-2008 .mx-animation-tabs button{font-size:11px}#x3-2008 .mx-animation-caption button{font-size:11px}#x3-2008 .mx-lab-table{font-size:11px}#x3-2008 .mx-lab-note{font-size:11px}}
'''
markup=markup.replace('<script id="x3-original-assets"', '<style>'+css+'</style>\n<script id="x3-original-assets"')
markup=markup.replace('<script id="x3-original-assets"','<style>'+(source/'screen-overlays.css').read_text(encoding='utf-8-sig')+'</style>\n<script id="x3-original-assets"')
markup=markup.replace('<script id="x3-original-assets"','<style>'+(source/'cybercore.css').read_text(encoding='utf-8-sig')+'</style>\n<script id="x3-original-assets"')
markup=markup.replace('<script id="x3-original-assets"','<style>'+(source/'liquid-chrome.css').read_text(encoding='utf-8-sig')+'</style>\n<script id="x3-original-assets"')
markup=markup.replace('<script id="x3-original-assets"','<style>'+(source/'typeface-style.css').read_text(encoding='utf-8-sig')+'</style>\n<script id="x3-original-assets"')
markup=markup.replace('<div class="mx-housing">',(source/'control-glyphs.svg').read_text(encoding='utf-8')+'<div class="mx-housing">',1)
markup=re.sub(r'<i data-lucide="([^"]+)"[^>]*></i>',lambda m:'<svg class="mx-skin-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#mx-glyph-'+m[1]+'"></use></svg>',markup)
markup=markup.replace('<script src="assets/lucide.min.js"></script>','')
markup=markup.replace('<script id="x3-original-assets"','<style>'+(source/'transport-keys.css').read_text(encoding='utf-8-sig')+'</style>\n<script id="x3-original-assets"')
markup=theme_palette(markup)
# Embed the compact font so local file previews also work under browser font CORS rules.
for font_name in ['accessories-urban','audiowide','orbitron']:
    font_data=base64.b64encode((dist/'assets/fonts'/(font_name+'.woff2')).read_bytes()).decode('ascii')
    markup=markup.replace("url('assets/fonts/"+font_name+".woff2')","url('data:font/woff2;base64,"+font_data+"')")
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>DEH Modernized · X3 Player</title><meta name="description" content="Interactive X3 interface with 83 original Carozerra clips, amber and cyan illumination, and original full-color animations. Private prototype and hardware feasibility lab."><meta name="color-scheme" content="dark"><link rel="icon" href="data:,"><style>html{background:#000}body{margin:0;padding:14px;max-width:1052px;margin-inline:auto}body,button,input,select{font-family:'Trebuchet MS','Segoe UI',Arial,sans-serif}@media(max-width:600px){body{padding:6px}}</style></head><body>'''+markup+'</body></html>'
(dist/'index.html').write_text(page,encoding='utf-8')
(dist/'assets/skins').mkdir(exist_ok=True)
for name in ['liquid-topbar.svg']:shutil.copyfile(source/name,dist/'assets/skins'/name)
# Control glyphs are embedded SVG symbols; no external icon runtime is required.
if not (dist/'assets/benchmark-results.js').exists():(dist/'assets/benchmark-results.js').write_text('window.X3_BENCHMARK=null;',encoding='utf-8')
print(json.dumps({'clips':len(assets),'htmlBytes':len(page.encode()),'scriptBytes':len(base.encode())}))
