/* Residual Power — deterministic puzzle rules. No vehicle/network commands. */
(function(root){'use strict';
const ITEMS=['photo','manualA','manualB','card','reader','usb','manualJoined','foldNote','manualFolded','tool'];
const FLAGS=['wiperActivated','frameObserved','driverBelt','coatMoved','rearBeltReleased','rearBagMoved','bagLooted','gloveboxOpen','readerCollected','recordRead','manualJoined','usbConnected','audioLeftDecoded','audioRightDecoded','fogMessageVisible','mirrorAligned','messageRead','seatToolCollected','foldNoteCollected','manualAssembled','roofCoverOpen','toolInserted','roofUnlocked','roofOpen','chapterComplete'];
const clone=o=>JSON.parse(JSON.stringify(o)),clamp=(v,a,b)=>Math.max(a,Math.min(b,Number(v)||0));
function fresh(){return {schemaVersion:1,currentScreen:'S01',started:false,inventory:[],observedClues:[],puzzleFlags:Object.fromEntries(FLAGS.map(k=>[k,false])),vehicleSim:{ac:true,recirc:false,temp:22,fan:1,seatPosition:50,balance:0,mirrorAngle:-20,fogProgress:0},audioProgress:{position:0,duration:7,leftHeard:0,rightHeard:0},elapsedSec:0,chapterComplete:false,metrics:{wrongTurns:0,wrongUses:0,hints:0,actions:0}};}
class Game{
 constructor(saved){this.state=fresh();this.runtime={playing:false,paused:false,seatMoving:false,rotationStep:0,foldStep:0};if(saved)this.restore(saved);}
 get f(){return this.state.puzzleFlags}get v(){return this.state.vehicleSim}get a(){return this.state.audioProgress}
 has(id){return this.state.inventory.includes(id)}
 add(...ids){for(const id of ids)if(ITEMS.includes(id)&&!this.has(id))this.state.inventory.push(id);}
 remove(...ids){this.state.inventory=this.state.inventory.filter(x=>!ids.includes(x));}
 note(id){if(!this.state.observedClues.includes(id))this.state.observedClues.push(id);}
 result(message,changed=false,extra={}){if(changed)this.state.metrics.actions++;return {message,changed,...extra};}
 dispatch(type,value){
  switch(type){
   case 'start':this.state.started=true;return this.result('시야가 조금씩 돌아온다.',true);
   case 'scene':if(/^S0[1-6]$/.test(value)){this.state.currentScreen=value;return this.result('',true)}break;
   case 'wiper':this.f.wiperActivated=true;return this.result('물막이 갈라진다. 앞유리 너머에 무언가 있다.',true,{sound:'wiper'});
   case 'frame':if(!this.f.wiperActivated)return this.result('빗물이 시야를 가린다. 와이퍼를 움직여 보자.');this.f.frameObserved=true;this.note('frame');return this.result('프레임 04. 카메라는 이쪽을 향하고 있다.',true);
   case 'belt':this.f.driverBelt=!this.f.driverBelt;return this.result(this.f.driverBelt?'벨트는 맸다. 그런데 다른 좌석의 경고가 남아 있다.':'운전석 벨트를 풀었다.',true,{sound:'latch'});
   case 'coat':if(this.f.coatMoved)return this.result('치워 둔 외투다.');this.f.coatMoved=true;return this.result('외투 아래에 무거운 가방이 있다.',true,{sound:'cloth'});
   case 'rearBelt':if(!this.f.coatMoved)return this.result('먼저 외투를 살펴봐야 한다.');if(this.f.rearBeltReleased)return this.result('가방을 묶던 벨트는 이미 풀렸다.');this.f.rearBeltReleased=true;return this.result('가방을 고정한 벨트를 풀었다. 아직 좌석 위에 무게가 남아 있다.',true,{sound:'latch'});
   case 'bagMove':if(!this.f.coatMoved)return this.result('외투가 덮여 있다.');if(!this.f.rearBeltReleased)return this.result('벨트가 가방을 붙잡고 있다.');if(this.f.rearBagMoved)return this.result('바닥에 내려놓은 가방이다.');this.f.rearBagMoved=true;this.note('occupancy');return this.result('가방을 내리자 뒷좌석 점유 표시가 꺼졌다.',true,{sound:'cloth'});
   case 'bagLoot':if(!this.f.rearBagMoved)return this.result('먼저 가방을 좌석에서 내려놓자.');if(this.f.bagLooted)return this.result('가방 안에서 더 찾을 것은 없다.');this.f.bagLooted=true;this.add('photo','manualA','card');this.note('photo');return this.result('훼손된 사진, 안내서 조각 A, 메모리 카드를 얻었다.',true,{gained:['photo','manualA','card'],sound:'collect'});
   case 'glove':this.f.gloveboxOpen=!this.f.gloveboxOpen;return this.result(this.f.gloveboxOpen?'글로브박스는 잠겨 있지 않았다.':'서랍을 닫았다.',true,{sound:'latch'});
   case 'gloveLoot':if(!this.f.gloveboxOpen)return this.result('서랍이 닫혀 있다.');if(this.f.readerCollected)return this.result('필요한 물건은 챙겼다. 인수 기록은 다시 읽을 수 있다.');this.f.readerCollected=true;this.add('reader','manualB');return this.result('카드 리더기와 안내서 조각 B를 얻었다.',true,{gained:['reader','manualB'],sound:'collect'});
   case 'record':if(!this.f.gloveboxOpen)return this.result('서랍 안에 기록이 있다.');this.f.recordRead=true;this.note('record');return this.result('M-04 · 최종 운행 02:17 · 회수 예정 03:40 · 상태 보류.',true);
   case 'climate':for(const k of ['ac','recirc'])if(typeof value?.[k]==='boolean')this.v[k]=value[k];if(value?.temp!==undefined)this.v.temp=clamp(value.temp,18,30);if(value?.fan!==undefined)this.v.fan=clamp(value.fan,0,3);return this.result('',true);
   case 'mirror':this.v.mirrorAngle=clamp(value,-30,30);this.f.mirrorAligned=Math.abs(this.v.mirrorAngle-14)<=4;this.tryRead();return this.result('',true);
   case 'seat':if(this.runtime.seatMoving)return this.result('시트가 움직이는 중이다.');this.v.seatPosition=clamp(value,0,100);return this.result(this.v.seatPosition>=99?'앞쪽 레일 끝에 닿았다. 뒤에서 아래 공간을 살펴볼 수 있다.':'시트 위치가 바뀌었다.',true,{sound:'motor'});
   case 'tool':if(this.runtime.seatMoving)return this.result('움직임이 멈춘 뒤 살펴보자.');if(this.v.seatPosition<99)return this.result('시트 밑은 아직 좁다. 레일을 더 이동할 수 있다.');if(this.f.seatToolCollected)return this.result('도구는 이미 챙겼다.');this.f.seatToolCollected=true;this.add('tool');this.note('tool');return this.result('삼각형 손잡이의 수동 도구를 얻었다.',true,{gained:['tool'],sound:'collect'});
   case 'visor':if(this.f.foldNoteCollected)return this.result('거울 테두리에 접는 방향이 새겨져 있다.');this.f.foldNoteCollected=true;this.add('foldNote');this.note('fold');return this.result('왼쪽을 안으로, 아래를 위로. 안내서와 같은 점선이다.',true,{gained:['foldNote']});
   case 'usb':if(value!=='usb'||!this.has('usb'))return this.wrongUse();if(this.f.usbConnected)return this.result('리더기는 이미 연결되어 있다.');this.f.usbConnected=true;this.note('voices');return this.result('손상된 녹음 1개가 인식됐다. 두 음성이 겹쳐 들린다.',true,{sound:'connect'});
   case 'cover':if(this.f.roofCoverOpen)return this.result('커버 안에 삼각 소켓이 있다.');this.f.roofCoverOpen=true;return this.result('조명 뒤 커버를 열었다. 삼각형 소켓이 드러났다.',true,{sound:'latch'});
   case 'insert':if(!this.f.roofCoverOpen)return this.result('점검 커버가 닫혀 있다.');if(value!=='tool'||!this.has('tool'))return this.wrongUse();if(this.f.toolInserted)return this.result('도구는 소켓에 끼워져 있다.');this.f.toolInserted=true;this.runtime.rotationStep=0;return this.result('홈이 맞물렸다. 정해진 방향으로 돌릴 수 있다.',true,{sound:'latch'});
   case 'rotate':if(!this.f.toolInserted)return this.result('소켓에 맞는 도구가 필요하다.');if(this.f.roofUnlocked)return this.result('수동 잠금이 이미 해제됐다.');{
    const angle=Number(value),expected=this.runtime.rotationStep===0?-90:180;
    if(Math.abs(angle-expected)<=12){this.runtime.rotationStep++;if(this.runtime.rotationStep===2){this.f.roofUnlocked=true;this.note('roof');return this.result('잠금쇠가 풀렸다. 이제 유리를 밀 수 있다.',true,{sound:'unlock'})}return this.result('첫 번째 잠금쇠가 움직였다.',true,{sound:'latch'})}
    this.runtime.rotationStep=0;this.state.metrics.wrongTurns++;return this.result('걸리는 소리. 회전 순서가 처음으로 돌아갔다. 도구는 그대로다.',true,{sound:'wrong'});
   }
   case 'roof':if(!this.f.roofUnlocked)return this.result('모터가 짧게 돌다 멈춘다. 수동 장치가 잠겨 있다.',false,{sound:'motorFail'});if(this.f.roofOpen)return this.result('머리 위로 빗소리가 쏟아진다.');this.f.roofOpen=true;return this.result('선루프가 열렸다.',true,{sound:'motor'});
   case 'escape':if(!this.f.roofOpen)return this.result('위쪽 통로가 아직 닫혀 있다.');if(this.f.chapterComplete)return this.result('1막은 이미 끝났다.');this.f.chapterComplete=true;this.state.chapterComplete=true;return this.result('차 밖에 나왔다. 아직 여기서 나간 건 아니다.',true,{ending:true});
  }
  return this.result('지금은 반응하지 않는다.');
 }
 wrongUse(){this.state.metrics.wrongUses++;return this.result('모양이 맞지 않는다. 다른 곳에 쓸 수 있을 것 같다.');}
 combine(a,b){
  if(!this.has(a)||!this.has(b)||a===b)return this.wrongUse();const key=[a,b].sort().join('+');
  if(key==='card+reader'){this.remove('card','reader');this.add('usb');return this.result('카드를 리더기에 끼웠다. USB 포트에 연결할 수 있다.',true,{gained:['usb'],sound:'connect'})}
  if(key==='manualA+manualB'){this.remove('manualA','manualB');this.add('manualJoined');this.f.manualJoined=true;return this.result('찢어진 안내서를 맞췄다. 점선과 어긋난 도형이 남아 있다.',true,{gained:['manualJoined'],sound:'paper'})}
  if(key==='foldNote+manualJoined')return this.result('테두리의 표시와 안내서의 점선이 같다.',false,{openFold:true});
  return this.wrongUse();
 }
 fold(direction){
  if(!this.has('manualJoined')||!this.has('foldNote'))return this.result('안내서와 접기 표시를 함께 살펴보자.');
  const expected=this.runtime.foldStep===0?'left':'bottom';
  if(direction!==expected){this.runtime.foldStep=0;return this.result('기호가 이어지지 않는다. 다시 펼쳤다.',false,{resetFold:true,sound:'paper'})}
  this.runtime.foldStep++;
  if(this.runtime.foldStep===2){this.remove('manualJoined');this.add('manualFolded');this.f.manualAssembled=true;this.note('manual');return this.result('삼각 소켓 · 반시계 90° · 시계 180°. 두 도형이 하나로 이어졌다.',true,{gained:['manualFolded'],sound:'paper'})}
  return this.result('왼쪽 기호가 중앙에 포개졌다.',false,{sound:'paper'});
 }
 tryRead(){if(this.f.fogMessageVisible&&this.f.mirrorAligned&&!this.f.messageRead){this.f.messageRead=true;this.note('glass');return true}return false;}
 tick(dt){if(this.runtime.paused||!this.state.started||this.f.chapterComplete)return {read:false,fogChanged:false};dt=clamp(dt,0,10);this.state.elapsedSec+=dt;
  const prev=this.v.fogProgress,valid=!this.v.ac&&this.v.recirc&&this.v.temp>=26&&this.v.fan>0;
  this.v.fogProgress=clamp(prev+dt*(valid?.2:-.1),0,1);this.f.fogMessageVisible=this.v.fogProgress>=.95;this.f.mirrorAligned=Math.abs(this.v.mirrorAngle-14)<=4;
  const read=this.tryRead();return {read,fogChanged:Math.abs(prev-this.v.fogProgress)>.001};
 }
 setBalance(n){this.v.balance=clamp(n,-100,100);}
 startAudio(fromStart=false){if(!this.f.usbConnected)return false;if(fromStart||this.a.position>=this.a.duration-.05){this.a.position=0;this.a.leftHeard=0;this.a.rightHeard=0}this.runtime.playing=true;return true;}
 advanceAudio(dt){if(!this.runtime.playing||this.runtime.paused)return;const d=Math.min(Math.max(0,dt),this.a.duration-this.a.position);this.a.position+=d;
  if(this.v.balance<=-80)this.a.leftHeard+=d;else if(!this.f.audioLeftDecoded)this.a.leftHeard=0;
  if(this.v.balance>=80)this.a.rightHeard+=d;else if(!this.f.audioRightDecoded)this.a.rightHeard=0;
  if(this.a.position>=this.a.duration-.01){this.runtime.playing=false;if(this.a.leftHeard>=this.a.duration-.25){this.f.audioLeftDecoded=true;this.note('voiceLeft')}if(this.a.rightHeard>=this.a.duration-.25){this.f.audioRightDecoded=true;this.note('voiceRight')}}
 }
 snapshot(){const s=clone(this.state);s.audioProgress.position=clamp(s.audioProgress.position,0,s.audioProgress.duration);return s;}
 restore(saved){if(!saved||saved.schemaVersion!==1||!Array.isArray(saved.inventory)||!saved.puzzleFlags||!saved.vehicleSim)throw new Error('INVALID_SAVE');const s=fresh();
  s.started=!!saved.started;s.currentScreen=/^S0[1-6]$/.test(saved.currentScreen)?saved.currentScreen:'S01';s.inventory=[...new Set(saved.inventory.filter(id=>ITEMS.includes(id)))];s.observedClues=Array.isArray(saved.observedClues)?[...new Set(saved.observedClues.filter(v=>typeof v==='string'))]:[];
  for(const key of FLAGS)s.puzzleFlags[key]=!!saved.puzzleFlags[key];for(const key of ['ac','recirc'])s.vehicleSim[key]=saved.vehicleSim[key]!==undefined?!!saved.vehicleSim[key]:s.vehicleSim[key];
  for(const [key,min,max]of [['temp',18,30],['fan',0,3],['seatPosition',0,100],['balance',-100,100],['mirrorAngle',-30,30],['fogProgress',0,1]])if(Number.isFinite(saved.vehicleSim[key]))s.vehicleSim[key]=clamp(saved.vehicleSim[key],min,max);
  for(const key of ['position','duration','leftHeard','rightHeard'])if(Number.isFinite(saved.audioProgress?.[key]))s.audioProgress[key]=Math.max(0,saved.audioProgress[key]);s.audioProgress.duration=clamp(s.audioProgress.duration,1,60);s.audioProgress.position=Math.min(s.audioProgress.position,s.audioProgress.duration);
  s.elapsedSec=Math.max(0,Number(saved.elapsedSec)||0);s.chapterComplete=s.puzzleFlags.chapterComplete;for(const key of Object.keys(s.metrics))s.metrics[key]=Math.max(0,Number(saved.metrics?.[key])||0);this.state=s;this.runtime.playing=false;this.runtime.rotationStep=0;this.runtime.foldStep=0;this.f.mirrorAligned=Math.abs(this.v.mirrorAngle-14)<=4;this.f.fogMessageVisible=this.v.fogProgress>=.95;
 }
}
const api={Game,fresh,ITEMS,FLAGS};root.ResidualRules=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
