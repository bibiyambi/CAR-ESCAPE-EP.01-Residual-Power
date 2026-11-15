/* v2: read-only input normalization, fresh-session sequences, 15 puzzle rules. */
(function(root){'use strict';
const legacy=root.ResidualRules,Base=legacy.Game,copy=o=>JSON.parse(JSON.stringify(o));
const EXTRA=['diagnosticStrip','waveLeft','waveRight','originalLedger','smartKey','frameToken','gateDiagram','gateToken'];
const SEQUENCES={P01:['wiper','OFF','ACTIVE'],P05:['fan','LOW'],P08:['wiper','ACTIVE','OFF'],P09:['fan','LOW','MID'],P12:['wiper','OFF','ACTIVE','OFF'],P13:['fan','MID','LOW'],P14:['wiper','OFF','ACTIVE','OFF','ACTIVE','OFF']};
const DONE={P01:'wiperObserved',P05:'fogVisible',P08:'rainSequenceDone',P09:'ledgerLayersSeen',P12:'returnSequenceDone',P13:'circuitLayersSeen',P14:'gateSequenceDone'};
class InputSession {
 constructor(onComplete) {
  this.onComplete=onComplete;this.mode='SIMULATION';this.epoch=1;this.profile=null;
  this.safety=null;this.armed=null;this.pending=null;this.paused=false;
  this.step=0;this.last=null;this.lastTimestamp=-Infinity;
  this.status='단말기를 활성화해 주세요.';this.values={wiper:null,fan:null};
 }
 safe(now=Date.now()) {
  return Number.isFinite(now)&&!!this.safety&&this.safety.parked===true&&
   this.safety.quality==='VALID'&&Number.isFinite(this.safety.timestamp)&&
   now>=this.safety.timestamp&&now-this.safety.timestamp<=2000;
 }
 setSafety(packet,now=Date.now()) {
  this.safety=packet&&typeof packet==='object'?{...packet}:null;
  if(!this.safe(now))this.suspend(now,true);
  return this.safe(now);
 }
 reset(message='입력 순서를 새로 시작합니다.') {
  this.pending=null;this.step=0;this.last=null;this.lastTimestamp=-Infinity;this.status=message;
 }
 disarm(message='단말기를 활성화해 주세요.') {
  this.armed=null;this.reset(message);this.values={wiper:null,fan:null};
 }
 arm(id,now=Date.now()) {
  if(!SEQUENCES[id]||!Number.isFinite(now))return false;
  this.armed={id,at:now};this.reset('새 입력 대기 · 각 상태를 0.7초 유지');return true;
 }
 suspend(now=Date.now(),resetSequence=false) {
  if(!this.paused)this.epoch++;
  this.paused=true;this.pending=null;this.values={wiper:null,fan:null};
  if(this.armed)this.armed.at=now;
  if(resetSequence)this.reset('정차 신호를 다시 확인해야 합니다.');
  else this.status='일시정지 · 재개 후 새 입력을 기다립니다.';
 }
 resume(now=Date.now()) {
  if(!this.safe(now))return false;
  this.paused=false;this.pending=null;this.lastTimestamp=-Infinity;
  if(this.armed)this.armed.at=now;
  this.status=this.armed?'재개 완료 · 새로운 상태 입력 대기':'단말기를 활성화해 주세요.';
  return true;
 }
 preflight(now=Date.now()) {
  const p=this.profile,errors=[];
  if(!p||p.verified!==true)errors.push('차종별 신호 검증 프로필이 없습니다.');
  if(!p?.connected)errors.push('실제 차량 연결을 확인하지 못했습니다.');
  if(p?.permission!=='GRANTED')errors.push('차량 상태 읽기 권한이 확인되지 않았습니다.');
  if(!this.safe(now)||this.safety?.sourceMode!=='VEHICLE')errors.push('신선한 실제 정차 허용 신호가 필요합니다.');
  const w=p?.wiper,f=p?.fan;
  if(!Array.isArray(w?.off)||!Array.isArray(w?.active)||!w.off.length||!w.active.length||
   [...w.off,...w.active].some(x=>String(x).toUpperCase()==='AUTO')||w.off.some(x=>w.active.includes(x)))
   errors.push('와이퍼 OFF/작동 매핑이 검증되지 않았습니다.');
  if(!Array.isArray(f?.low)||!Array.isArray(f?.mid)||!f.low.length||!f.mid.length||f.low.some(x=>f.mid.includes(x)))
   errors.push('구분되는 두 풍량 구간이 필요합니다.');
  return errors;
 }
 switchMode(assist,now=Date.now()) {
  if(!assist){const errors=this.preflight(now);if(errors.length)return {ok:false,errors};}
  this.mode=assist?'SIMULATION':'VEHICLE';this.epoch++;this.values={wiper:null,fan:null};
  if(this.armed)this.armed.at=now;
  this.reset('조작 방식 변경 · 새 입력 대기');return {ok:true};
 }
 normalize(key,raw) {
  if(!['wiper','fan'].includes(key))return null;
  if(key==='wiper'&&String(raw).toUpperCase()==='AUTO')return null;
  const map=key==='wiper'?this.profile?.wiper:this.profile?.fan;
  if(!map)return null;
  for(const [field,values]of Object.entries(map))
   if(Array.isArray(values)&&values.includes(raw))return ({off:'OFF',active:'ACTIVE',low:'LOW',mid:'MID'})[field]||null;
  return null;
 }
 packet(key,value,now=Date.now()) {
  return {signalKey:key,normalizedValue:value,sourceMode:this.mode,sessionEpoch:this.epoch,
   timestamp:now,quality:'VALID',puzzleId:this.armed?.id,stepIndex:this.step,
   capabilityProfileId:this.mode==='VEHICLE'?this.profile?.id:'development-sim-v2'};
 }
 receive(p,now=Date.now()) {
  if(!p||typeof p!=='object'||Array.isArray(p)||!Number.isFinite(p.timestamp)||
   !Number.isFinite(now)||this.paused||!this.safe(now)||!this.armed)return false;
  const seq=SEQUENCES[this.armed.id];
  if(p.sourceMode!==this.mode||p.sessionEpoch!==this.epoch||p.puzzleId!==this.armed.id||
   p.stepIndex!==this.step||p.signalKey!==seq[0]||p.timestamp<this.armed.at||
   p.timestamp>now||now-p.timestamp>2000||p.timestamp<=this.lastTimestamp)return false;
  if(this.mode==='VEHICLE'&&(this.preflight(now).length||p.capabilityProfileId!==this.profile?.id))return false;
  this.lastTimestamp=p.timestamp;
  const domain=p.signalKey==='wiper'?['OFF','ACTIVE']:['LOW','MID'];
  if(p.quality!=='VALID'||!domain.includes(p.normalizedValue)) {
   this.pending=null;this.values[p.signalKey]=null;
   this.status='판독할 수 없는 상태 · 새 입력을 기다립니다.';return false;
  }
  const value=p.normalizedValue;this.values[p.signalKey]=value;
  // A return to the last stable value still cancels a different unfinished candidate.
  // This must happen BEFORE duplicate suppression.
  if(this.pending&&this.pending.value!==value)this.pending=null;
  if(value===this.last){this.status=`입력 ${this.step}개 확인 · 다음 상태 대기`;return false;}
  if(this.pending?.value===value){this.pending.packet={...p};return false;}
  this.pending={value,since:now,packet:{...p}};this.status='상태 안정화 중…';return true;
 }
 flush(now=Date.now()) {
  if(this.paused)return null;
  if(!this.safe(now)){this.suspend(now,true);return null;}
  if(!this.pending||!this.armed||now-this.pending.since<700)return null;
  if(this.mode==='VEHICLE'&&(this.preflight(now).length||this.pending.packet.capabilityProfileId!==this.profile?.id)) {
   this.pending=null;this.status='차량 읽기 연결을 다시 확인해야 합니다.';return {unavailable:true};
  }
  if(now-this.pending.packet.timestamp>2000){this.reset('입력이 만료되었습니다. 새 입력을 기다립니다.');return {expired:true};}
  const {value}=this.pending;this.pending=null;const seq=SEQUENCES[this.armed.id];this.last=value;
  if(value!==seq[this.step+1]) {
   this.step=0;this.status='순서가 일치하지 않습니다. 현재 입력 순서만 초기화했습니다.';return {wrong:true};
  }
  this.step++;this.status=`입력 ${this.step}개 확인 · 다음 상태 대기`;
  if(this.step===seq.length-1) {
   const id=this.armed.id;this.armed=null;this.status='입력 복원 완료 · 단서의 의미를 조사하세요.';
   this.onComplete(id);return {complete:id};
  }
  return {step:this.step};
 }
}
class Game extends Base{
 constructor(saved){super();this.state.schemaVersion=2;this.state.chapter=1;this.state.screenControlAssist=true;this.state.completedPuzzles=[];this.state.storyFlags={};this.input=new InputSession(id=>this.completeInput(id));if(saved)this.restore(saved);}
 add(...ids){for(const id of ids)if([...legacy.ITEMS,...EXTRA].includes(id)&&!this.has(id))this.state.inventory.push(id);}
 mark(id){if(!this.state.completedPuzzles.includes(id))this.state.completedPuzzles.push(id);}
 sync(){const f=this.f;f.bagMoved=!!f.rearBagMoved;f.transferRead=!!f.recordRead;f.leftDecoded=!!f.audioLeftDecoded;f.rightDecoded=!!f.audioRightDecoded;f.fogVisible=!!f.fogMessageVisible;f.wiperActivated=!!f.wiperObserved;for(const [id,yes]of Object.entries({P01:f.frameObserved,P02:f.bagLooted,P03:f.usbConnected&&f.manualJoined&&f.recordRead,P04:f.audioLeftDecoded&&f.audioRightDecoded,P05:f.messageRead,P06:f.seatToolCollected&&f.manualAssembled,P07:f.act1Complete,P08:f.diagnosticStrip,P09:f.falsificationFound,P10:f.recoveryLocation,P11:f.frameToken,P12:f.framePrimaryReleased,P13:f.frameReleased,P14:f.gateAuthorized,P15:f.gameComplete}))if(yes)this.mark(id);}
 completeInput(id){this.f[DONE[id]]=true;if(id==='P01'){this.f.wiperActivated=true;this.note('frameRain');}if(id==='P05'){this.v.fogProgress=1;this.f.fogMessageVisible=true;this.tryRead();}this.sync();}
 arm(id,now=Date.now()){return this.input.arm(id,now);}
 dispatch(type,value){
  if(type==='scene'){const n=Number(String(value).slice(1)),ch=n<=6?1:n<=10?2:3;if(/^S(0[1-9]|1[0-4])$/.test(value)&&n>=1&&n<=14&&ch<=this.state.chapter){this.state.currentScreen=value;return this.result('',true);}return this.result('앞 막의 목표를 완료해야 접근할 수 있다.');}
  if(type==='wiper'||type==='climate'||type==='belt')return this.result('이 조작은 입력 어댑터에서만 받습니다.');
  if(type==='escape'){if(!this.f.roofOpen)return this.result('위쪽 통로가 아직 닫혀 있다.');this.f.act1Complete=true;this.f.chapterComplete=true;this.state.chapterComplete=true;this.sync();return this.result('차 밖에 나왔다. 감시실의 전원이 살아 있다.',true,{ending:true});}
  if(type==='nextAct'){const next=Number(value);if(next===2&&this.f.act1Complete||next===3&&this.f.frameToken){this.state.chapter=next;this.state.currentScreen=next===2?'S07':'S11';this.runtime.paused=false;return this.result(next===2?'누락된 다섯 번째 기록을 찾아야 한다.':'준비해 둔 흔적을 따라 마지막 잠금을 풀자.',true);}return this.result('아직 이 구역에서 할 일이 남았다.');}
  if(type==='filmOrder'){if(!this.f.rainSequenceDone)return this.result('먼저 감시 영상을 복원해야 한다.');if(JSON.stringify(value)!=='["05","04"]')return this.result('입고 시각과 맞지 않는다. 빈 프레임과 반입 순서를 다시 비교하자.');this.f.diagnosticStrip=true;this.add('diagnosticStrip');this.note('film');this.sync();return this.result('05가 먼저 비었고, 04가 나중에 반입됐다. 진단 스트립을 얻었다.',true,{sound:'collect'});}
  if(type==='ledgerLink'){if(!this.f.ledgerLayersSeen||!this.f.diagnosticStrip)return this.result('영상 스트립과 두 장부 층을 먼저 확보하자.');if(value?.original!=='M05-0205'||value?.modified!=='M05-0218')return this.result('같은 회수 구역의 원본과 수정 행을 연결해야 한다.');this.f.falsificationFound=true;this.add('waveLeft','waveRight','originalLedger');this.note('forgery');this.sync();return this.result('M-05 출구 대기가 인계 완료로 바뀌었다. 원본 장부와 두 녹음 조각을 확보했다.',true,{sound:'collect'});}
  if(type==='wavePlace'){if(!this.f.falsificationFound)return this.result('기록 조각을 먼저 확보하자.');if(value?.L!=='waveLeft'||value?.R!=='waveRight')return this.result('조각의 원본 L/R 표식과 슬롯이 맞지 않는다.');this.f.wavePlaced=true;return this.result('두 녹음의 원본 채널이 맞물렸다.',true,{sound:'connect'});}
  if(type==='archiveRead'){if(!this.f.wavePlaced)return this.result('L/R 조각을 원본 채널에 맞춰야 한다.');if(value!=='L'&&value!=='R')return this.result('원본 채널 L 또는 R을 선택하자.');if(value==='L'){this.f.archiveLeftRead=true;this.note('archiveLeft');}if(value==='R'){this.f.archiveRightRead=true;this.note('archiveRight');}return this.result('선택한 원본 채널을 수첩에 옮겼다.',true);}
  if(type==='archiveOrder'){if(!this.f.archiveLeftRead||!this.f.archiveRightRead)return this.result('두 원본 채널을 모두 확인하자.');if(value!=='sendThenRecover')return this.result('“명단부터 보내.” 회수함은 그 뒤다.');this.f.yunseoMessageRead=true;this.f.recoveryLocation=true;this.note('yunseo');this.note('rainOrder');this.sync();return this.result('윤서는 협력자였다. 명단 송신 뒤 송신실 회수함을 조사하자.',true,{sound:'unlock'});}
  if(type==='manifest'){if(!this.f.recoveryLocation||!this.f.falsificationFound)return this.result('원본 장부와 윤서의 지시가 필요하다.');if(value?.A!=='M-01'||value?.B!=='M-03'||value?.C!=='M-04'||!value?.attach)return this.result('사진 뒷면의 화물 표식과 원본 장부를 맞추고 M-05 수정 이력을 첨부해야 한다.');this.f.manifestSent=true;this.note('manifest');this.sync();return this.result('구조 명단을 게임 속 수신처에 보냈다. 회수함 잠금이 해제됐다.',true,{sound:'unlock'});}
  if(type==='recovery'){if(!this.f.manifestSent)return this.result('회수함은 명단 송신 확인 뒤 열린다.');this.f.smartKeyCollected=true;this.f.frameToken=true;this.add('smartKey','frameToken');this.sync();return this.result('스마트키와 프레임 토큰을 얻었다.',true,{gained:['smartKey','frameToken'],ending:2,sound:'collect'});}
  if(type==='insertFrameToken'){if(!this.f.frameToken)return this.result('회수함의 프레임 토큰이 필요하다.');this.f.frameTokenInserted=true;return this.result('프레임 토큰을 꽂았다. 새 와이퍼 입력을 받을 준비가 됐다.',true);}
  if(type==='latch'){if(!this.f.returnSequenceDone)return this.result('세 위치를 먼저 복원해야 한다.');if(value!=='middle')return this.result('연결선이 이 잠금쇠를 통과하지 않는다.');this.f.framePrimaryReleased=true;this.note('latch');this.sync();return this.result('가운데 잠금쇠가 풀렸다. 보조 회로는 아직 닫혀 있다.',true,{sound:'unlock'});}
  if(type==='circuit'){if(!this.f.circuitLayersSeen||!this.f.framePrimaryReleased)return this.result('주 잠금을 풀고 상·하단 회로 층을 모두 읽자.');if(value!=='triangle')return this.result('두 회로에 공통으로 나타나는 접점을 찾아야 한다.');this.f.frameReleased=true;this.f.gateDiagram=true;this.add('gateDiagram');this.note('circuit');this.sync();return this.result('공통 삼각 접점이 이어졌다. 프레임이 완전히 해제됐다.',true,{sound:'unlock'});}
  if(type==='route'){if(!this.f.gateSequenceDone||!this.f.gateDiagram)return this.result('출구 도면과 복원된 경로를 함께 비교하자.');if(value!=='C')return this.result('두 경로 층과 도면의 개방 통로가 모두 겹치는 길이 아니다.');this.f.exitRouteSelected=true;this.f.gateAuthorized=true;this.add('gateToken');this.note('gate');this.sync();return this.result('경로 C 승인. 게임용 출구 토큰을 발급했다.',true,{sound:'unlock'});}
  if(type==='insertSmartKey'){if(!this.f.smartKeyCollected)return this.result('회수함의 스마트키가 필요하다.');this.f.smartKeyInserted=true;return this.result('게임 대시보드에 스마트키를 꽂았다.',true,{sound:'connect'});}
  if(type==='authorize'){if(!this.f.gateAuthorized)return this.result('출구 승인 토큰이 없다.');this.f.tokenConfirmed=true;return this.result('게임 출구 토큰을 확인했다.',true);}
  if(type==='ignition'){const needed=['manifestSent','frameReleased','gateAuthorized','smartKeyCollected','smartKeyInserted','tokenConfirmed'];const labels={manifestSent:'구조 명단 송신',frameReleased:'운송 프레임 해제',gateAuthorized:'출구 경로 승인',smartKeyCollected:'스마트키 확보',smartKeyInserted:'스마트키 삽입',tokenConfirmed:'출구 토큰 확인'};const missing=needed.filter(k=>!this.f[k]);if(missing.length)return this.result('아직 필요한 확인: '+missing.map(k=>labels[k]).join(' · '));this.f.act3Complete=true;this.f.gameComplete=true;this.sync();return this.result('탈출 성공.',true,{ending:3,sound:'motor'});}
  const r=super.dispatch(type,value);if(type==='record')r.message='M-04 · 02:17 반입 · 03:40 회수 예정 · 동승자 인계 훼손 · 보류.';if(type==='rearBelt')r.message=this.f.rearBeltReleased?'가방의 고정 끈을 풀었다.':'먼저 외투를 치우자.';if(type==='bagMove')r.message=this.f.rearBagMoved?'가방을 바닥으로 옮겼다. 지퍼를 조사할 수 있다.':'가방 고정 끈이 아직 걸려 있다.';this.sync();return r;
 }
 tick(dt){if(this.runtime.paused||!this.state.started||this.f.gameComplete)return {read:false,fogChanged:false};this.state.elapsedSec+=Math.min(.5,Math.max(0,dt));const prev=this.v.fogProgress;this.v.fogProgress=Math.max(0,prev-(this.input.values.fan==='MID'?.15:0)*dt);this.f.fogMessageVisible=this.v.fogProgress>=.95;this.f.mirrorAligned=Math.abs(this.v.mirrorAngle-14)<=4;return {read:this.tryRead(),fogChanged:prev!==this.v.fogProgress};}
 combine(a,b){const r=super.combine(a,b);this.sync();return r;}fold(d){const r=super.fold(d);this.sync();return r;}advanceAudio(dt){super.advanceAudio(dt);this.sync();}
 snapshot(){this.sync();const s=super.snapshot();s.schemaVersion=2;s.mode=s.screenControlAssist?'ON':'OFF';s.clues=[...s.observedClues];delete s.puzzleFlags.wiperActivated;delete s.puzzleFlags.driverBelt;s.storyFlags=copy(s.puzzleFlags);return s;}
 restore(saved){
  if(saved?.schemaVersion===1){super.restore(saved);this.state.schemaVersion=2;this.state.chapter=1;this.state.screenControlAssist=true;this.state.completedPuzzles=[];this.f.act1Complete=!!this.f.chapterComplete;this.f.wiperObserved=!!this.f.wiperActivated;delete this.f.driverBelt;if(!this.f.bagLooted){this.f.rearBeltReleased=false;this.f.rearBagMoved=false;}if(!this.f.messageRead){this.f.fogMessageVisible=false;this.v.fogProgress=0;}this.state.migratedFrom=1;}
  else if(saved?.schemaVersion===2&&Array.isArray(saved.inventory)&&saved.puzzleFlags&&saved.vehicleSim){const base={...saved,schemaVersion:1,currentScreen:'S01'};super.restore(base);this.state.schemaVersion=2;this.state.chapter=Number.isInteger(Number(saved.chapter))?Math.max(1,Math.min(3,Number(saved.chapter))):1;for(const [k,v]of Object.entries(saved.puzzleFlags))if(typeof v==='boolean')this.f[k]=v;this.state.currentScreen=/^S(0[1-9]|1[0-4])$/.test(saved.currentScreen)?saved.currentScreen:'S01';if(Number(this.state.currentScreen.slice(1))>(this.state.chapter===1?6:this.state.chapter===2?10:14))this.state.currentScreen='S01';this.state.inventory=[...new Set(saved.inventory.filter(x=>[...legacy.ITEMS,...EXTRA].includes(x)))];this.state.screenControlAssist=saved.screenControlAssist!==false;this.state.completedPuzzles=Array.isArray(saved.completedPuzzles)?[...new Set(saved.completedPuzzles.filter(x=>/^P(0[1-9]|1[0-5])$/.test(x)))]:[];}
  else throw new Error('INVALID_SAVE');
  this.input=new InputSession(id=>this.completeInput(id));this.input.mode=this.state.screenControlAssist?'SIMULATION':'VEHICLE';this.runtime.playing=false;this.runtime.paused=false;this.v.fogProgress=this.f.messageRead?1:0;this.sync();
 }
}
const api={...legacy,Game,InputSession,SEQUENCES,ITEMS:[...legacy.ITEMS,...EXTRA]};root.ResidualRules=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
