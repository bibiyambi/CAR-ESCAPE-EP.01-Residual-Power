from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1]
source=(R/'tools/regenerate_vectors.py').read_text().split('record=paper')[0]
exec(source)
def doc(name,title1,title2,lines):
 body=paper+title(title1,title2)
 for i,line in enumerate(lines):body+=txt(line,78,212+i*71,26)
 write_svg('documents',name,body)
doc('original-ledger','원본 반입 장부','ORIGINAL / MISSING RECORD', ['01:28   M-01   반입          A / 마름모 01','01:56   M-03   반입          B / 원 03','02:05   M-05   출구 대기    윤서 / 공란','02:17   M-04   반입          C / 삼각 04','수정 이력: 02:18 M-05 인계 완료로 덮어씀','명단 제출 시 원본과 수정 이력을 함께 첨부'])
doc('modified-ledger','덮어쓴 수정 장부','MODIFIED / 02:18', ['01:28   M-01   반입','01:56   M-03   반입','02:17   M-04   반입','02:18   M-05   인계 완료','원본의 출구 대기 항목이 사라졌다.'])
doc('diagnostic-strip','감시 영상 진단 스트립','FRAME SEQUENCE / VERIFIED', ['02:05   프레임 05가 먼저 비어 있었다.','02:17   프레임 04에 차량이 반입됐다.','05 → 04 : 시각과 장면 순서가 일치한다.','원본 반입 장부와 수정 이력을 대조할 것.'])
for side,clock in [('left','02:05'),('right','02:17')]:
 letter='L' if side=='left' else 'R';body=paper+title('원본 녹음 조각 '+letter,'SOURCE '+letter+' / '+clock)
 for i in range(70):
  x=90+i*12;h=12+abs(math.sin(i*2.6)*math.cos(i*.41))*100;body+=f'<path d="M{x} {355-h}V{355+h}" stroke="#426b70" stroke-width="5"/>'
 body+=txt('원본 표식과 같은 채널 슬롯에 삽입',78,570,29)+txt('기록실 슬롯: L 02:05 / R 02:17',78,612,22)
 write_svg('documents','wave-'+side,body)
body=paper+title('출구 개방 도면','FRAME RELEASE / OPEN CORRIDOR')
body+='<path d="M105 350H875 M245 345V245H750V345 M245 355V460H750V355" stroke="#6a7f79" stroke-width="24" fill="none"/><path d="M105 350H875" stroke="#b48841" stroke-width="9"/><path d="M500 208V279M500 426V492" stroke="#aa624f" stroke-width="20"/>'
for x in [355,645]:body+=f'<path d="M{x} 183q-40 45 0 51q40-6 0-51Z" fill="#426c77"/>'
for x in [210,500,790]:body+=f'<path d="M{x-15} 188h30v35h-30Z" fill="none" stroke="#59645a" stroke-width="5"/>'
body+=txt('서쪽 회랑 → 중앙 교차 → 동쪽 출구',500,562,29,anchor='middle')+txt('두 번 남기고 멈춰 · 실제 왕복 횟수는 아님',500,610,23,anchor='middle')
write_svg('documents','gate-diagram',body)
doc('gate-token','출구 승인 토큰','LOCAL AUTHORIZATION / ROUTE C', ['경로 C 승인','운송 프레임 해제 확인','구조 명단 수신처 접수 확인','게임 대시보드에서 토큰 확인 후 시작'])
m=json.loads((R/'manifest.json').read_text())
for s in m['scenes']:
 for h in s['hotspots']:
  if s['chapter']>1:write_svg('masks',s['id']+'-'+h['id'],f'<path d="{h["path"]}" fill="white"/>',1672,941)
print('Created exact vector documents and new scene masks')
