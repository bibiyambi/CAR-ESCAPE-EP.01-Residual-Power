from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'source/act1-manifest.json').read_text())
m['scope']='3막 통합 / 퍼즐 15개 / 화면 조작 보조 ON 기본 / 읽기 전용 차량 어댑터 계약'
m['chapter']='01–03'
for s in m['scenes']:
 s['chapter']=1
 for h in s['hotspots']:
  h['name']=h['name'].replace('계기판과 안전벨트','게임 계기판').replace('와이퍼 레버','와이퍼 흔적 조사').replace('공조·오디오 디스플레이','게임 미디어 화면').replace('전동시트 스위치','게임 시트 스위치')
m['scenes'][2]['subtitle']='외투 아래에 숨은 가방'
def scene(id,name,subtitle,hotspots):
 return dict(id=id,name=name,subtitle=subtitle,chapter=2 if int(id[1:])<=10 else 3,asset='assets/backgrounds/'+id+'.png',hotspots=[dict(id=i,name=n,path=p) for i,n,p in hotspots])
m['scenes']+= [
scene('S07','감시실','누락된 다섯 번째 기록',[('surveillance','감시 영상 단말기','M86 225L959 273V450L83 459Z'),('filmDesk','필름 판독기','M777 475L989 474L1004 585L781 587Z'),('surveillanceNote','감시실 작업 메모','M476 554L741 555L826 590L445 594Z')]),
scene('S08','진단 기록','겹쳐진 원본과 수정본',[('ledgerTerminal','장부 진단 단말기','M507 193L1159 194L1157 555L509 555Z'),('ledgerBook','보관된 원본 장부','M1219 590L1559 626L1567 735L1224 710Z'),('filmReader','진단 스트립 투입구','M48 337L402 335L400 676L49 673Z')]),
scene('S09','음성 기록실','명단부터 보내',[('archive','음성 복원 단말기','M609 250L1113 250V507H609Z'),('tapes','원본 채널 슬롯','M650 541H1095V607H650Z'),('archiveNote','기록실 쪽지','M1268 536L1548 561L1532 608L1254 575Z')]),
scene('S10','송신실','키는 인계가 아니라 회수',[('transmission','구조 명단 단말기','M620 291H1191V587H620Z'),('photoBoard','사진과 화물 표식','M121 281H521V626H121Z'),('recoveryBox','회수함','M1319 399L1593 396V780H1318Z')]),
scene('S11','차량 귀환','마지막 시동을 위한 준비',[('returnTerminal','프레임 토큰 단말기','M816 512L1197 512L1214 687L807 688Z'),('latches','프레임의 세 잠금쇠','M509 246H1186V332H509Z'),('returnNote','차량에 남긴 표시','M972 796H1040V832H972Z')]),
scene('S12','프레임 진단','두 회로의 공통 접점',[('circuitTerminal','프레임 회로 진단','M473 131H1240L1266 154V551L1240 576H474L450 552V155Z'),('circuitSlots','상하 회로 판독부','M533 600H803L824 619V699L805 720H534L513 699V620Z M889 600H1166L1186 619V699L1166 720H890L868 699V620Z')]),
scene('S13','출구 단말기','두 번 남기고 멈춰',[('gateTerminal','출구 경로 단말기','M968 300L1501 302L1551 566L918 564Z'),('gateShutter','닫힌 시설 출구','M142 191H710V592H142Z'),('gateSlot','승인 토큰 발급구','M1121 660H1278V714H1121Z')]),
scene('S14','마지막 시동','돌아갈 준비가 끝났다',[('dashboard','게임 대시보드','M736 466H1258V657H736Z'),('keySlot','게임 스마트키 슬롯','M916 791H1045V822H916Z'),('startButton','게임 시동 버튼','M1082 774Q1143 753 1147 797Q1148 832 1104 831Q1073 829 1082 774Z')])]
newitems={
'diagnosticStrip':('진단 스트립','documents/diagnostic-strip.svg','05가 먼저 비었고 04가 나중에 반입됐다. 원본 장부 대조에 사용할 수 있다.'),
'waveLeft':('녹음 조각 L','documents/wave-left.svg','원본 L 채널 / 02:05 / 윤서의 파형 조각. 왼쪽 슬롯에 맞는 식별 표식.'),
'waveRight':('녹음 조각 R','documents/wave-right.svg','원본 R 채널 / 02:17 / 회수 지시가 담긴 파형 조각.'),
'originalLedger':('원본 반입 장부','documents/original-ledger.svg','사진 A/B/C의 화물 표식과 M-01·M-03·M-04 원본 기록을 연결한다. M-05 수정 이력도 남아 있다.'),
'smartKey':('회수된 스마트키','items/smartKey.png','게임 대시보드의 슬롯에 사용할 열쇠. 실제 차량 시동과 연동되지 않는다.'),
'frameToken':('프레임 토큰','items/frameToken.png','프레임 04의 토큰 판독기에 사용할 수 있다.'),
'gateDiagram':('출구 개방 도면','documents/gate-diagram.svg','개방 통로: 서쪽 회랑–중앙 교차–동쪽 출구. 빗방울 2개 뒤 정지 기호. 복원된 두 경로를 겹쳐야 한다.'),
'gateToken':('출구 승인 토큰','documents/gate-token.svg','경로 C 승인. 게임 대시보드에서 확인할 수 있다.')}
for k,(name,a,d) in newitems.items():m['items'][k]=dict(name=name,asset='assets/'+a,description=d)
m['notes']['occupancy']=['가방 고정 끈','게임 속 가방을 고정하던 끈을 풀었다. 실제 안전벨트 조작은 필요하지 않다.']
m['notes']['voiceLeft']=['왼쪽 목소리','“흔적은 지워도 남아.” 유리의 손자국을 가리키는 여자의 목소리.']
m['notes']['voiceRight']=['오른쪽 목소리','“끝까지 밀어. 그 아래.” 익숙한 남자의 목소리.']
m['notes'].update({
'frameRain':['갈라진 물막','와이퍼 OFF에서 작동으로 넘어가자 프레임 04가 드러났다.'],
'film':['누락된 프레임 05','02:05에 05가 비었고 02:17에 04가 반입됐다. 05는 이후 인계된 것이 아니다.'],
'forgery':['조작된 M-05 기록','원본 02:05 M-05 출구 대기가 수정본 02:18 M-05 인계 완료로 바뀌었다. 프레임은 그 전에 비어 있었다.'],
'yunseo':['윤서의 원본 지시','L: “05는 비어 있어. 명단부터 보내.” R: “키는 인계가 아니라 회수.” 명단 송신 후 송신실 회수함을 조사한다.'],
'rainOrder':['마지막 녹음의 기호','녹음 끝의 짧은 말: “두 번 남기고 멈춰.” 두 번의 작동 진입과 마지막 정지. 실제 와이퍼 왕복 횟수가 아니다.'],
'manifest':['명단 송신 확인','사진 A=M-01, B=M-03, C=M-04. 윤서의 M-05 수정 이력을 첨부했다. 이 송신은 게임 속 사건이다.'],
'latch':['주 잠금 해제','연결선은 가운데 잠금쇠를 지난다. 1막의 와이퍼 관찰과 별개로 새 순서를 입력해 해제했다.'],
'circuit':['공통 삼각 접점','상단과 하단에 공통인 삼각 접점을 연결해 운송 프레임을 해제했다.'],
'gate':['출구 승인','차단 구간을 피하고 두 기록 층과 도면이 겹치는 경로 C가 승인됐다.']})
m['notes'].update({'archiveLeft':['원본 L 채널','윤서: “05는 비어 있어. 명단부터 보내.” 원본 출처 02:05.'],'archiveRight':['원본 R 채널','“키는 인계가 아니라 회수.” 녹음 끝: “두 번 남기고 멈춰.” 원본 출처 02:17.']})
(R/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
# Preserve act-one renderer and tactile mechanisms; override only the versioned flows.
s=(R/'source/act1-app.js').read_text()
s=s.replace("const KEY='residual-power-save-v1'","const KEY='residual-power-save-v2'")
s=s.replace("const raw=localStorage.getItem(KEY)","const raw=localStorage.getItem(KEY)||localStorage.getItem('residual-power-save-v1')")
for name in ['renderWorld','interact','showBelt','showClimate','showMedia','showSettings','hintFor','playEnding','endRecords','begin','newGame','setHostState','sceneTo','syncPaused']:
 s=s.replace('function '+name+'(','function '+name+'Legacy(')
s=s.replace('안전벨트가 단단히 걸려 있다.','가방 전용 고정 끈이 단단히 걸려 있다.').replace('가방을 묶은 벨트','가방을 묶은 고정 끈').replace('고정 벨트 풀기','가방 고정 끈 풀기').replace('가방 고정 벨트','가방 고정 끈').replace('가방을 고정한 벨트','가방을 고정한 끈').replace('벨트로 고정된 가방','고정 끈에 묶인 가방').replace('벨트는 풀렸다.','가방 고정 끈은 풀렸다.').replace('자신의 벨트를 맸는데도 남아 있던 경고는 이쪽에서 들린다.','고정 끈은 가방에 달린 게임 속 부품이다.').replace('다시 눈을 뜨면, 유리의 흔적을 봐.','흔적은 지워도 남아.').replace('잊어도, 손은 기억할 거야.','끝까지 밀어. 그 아래.').replace('다시… 눈을… / 잊어도… 손은…','흔적은… 남아… / 끝까지… 그 아래…')
s=s.replace('보조 전원으로 앞뒤 위치를 바꿀 수 있다.','게임 속 시트를 앞뒤로 이동할 수 있다.').replace("'반사되는 흔적'","'게임 룸미러 · 반사되는 흔적'").replace('작은 각도 차이로 반사되는 곳이 달라진다.','이 거울은 게임 전용 장치다. 작은 각도 차이로 반사되는 곳이 달라진다.').replace("'전동시트 · 레일'","'게임 시트 · 레일'").replace("'수동 선루프 장치'","'게임 선루프 수동 장치'")
s=s.replace("if(now-warningAt>6500&&!game.runtime.paused&&(!f().driverBelt||!f().rearBagMoved))","if(false)")
s=s.replace("if(/^[1-6]$/.test(e.key))sceneTo(CONTENT.scenes[Number(e.key)-1].id)","if(/^[1-6]$/.test(e.key)){const visible=CONTENT.scenes.filter(s=>s.chapter===game.state.chapter);if(visible[Number(e.key)-1])sceneTo(visible[Number(e.key)-1].id)}")
s=s.replace("for(const [id,n]of [['sound-button'","for(const [id,n]of [['input-button','settings'],['sound-button'")
s=s.replace("pause?.04:endingActive","pause?0:endingActive").replace("externalPause||menuPause?.04:.42","externalPause||menuPause?0:.42")
s=s.replace("if(ambientGain)ambientGain.gain.value=muted?0:pause?0:endingActive?.65:.42;","if((menuPause||externalPause)&&archivePlayer)archivePlayer.pause();if(ambientGain)ambientGain.gain.value=muted?0:pause?0:endingActive?.65:.42;")
s=s.replace("if(leftGain&&rightGain)applyBalance();","if(leftGain&&rightGain)applyBalance();if(archivePlayer)archivePlayer.muted=muted;")
s=s.replace("if(result.message&&!opts.quiet)toast(result.message);","if(result.message&&!opts.quiet){toast(result.message);if(modalKind&&$('#panel .panel-body')){let feedback=$('#panel-feedback');if(!feedback){feedback=document.createElement('div');feedback.id='panel-feedback';feedback.className='puzzle-feedback';feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');$('#panel .panel-body').prepend(feedback);}feedback.textContent=result.message;}}")
s=s.replace("async function ensureAudio(){if(!audioContext)","async function ensureAudio(){if(externalPause)throw new Error('PAUSED');if(!audioContext)")
s=s.replace("const buffer=await audioBuffer(name),s=audioContext.createBufferSource()","const buffer=await audioBuffer(name);if(muted||externalPause)return;const s=audioContext.createBufferSource()")
ext=(R/'source/v2-app-extension.js').read_text()
marker="$('#view-nav').innerHTML=CONTENT.scenes.map"
pos=s.index(marker);s=s[:pos]+ext+'\n'+s[pos:]
s+='\ninitV2();\n'
(R/'app.js').write_text(s)
