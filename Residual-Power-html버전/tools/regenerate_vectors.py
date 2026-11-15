from pathlib import Path
import json,html
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import fitz
import cairosvg

R=Path(__file__).resolve().parents[1];G=R;A=G/'assets'
FONT=G/'assets/fonts/NanumGothic-source.ttf'
font=TTFont(FONT);glyphs=font.getGlyphSet();cmap=font.getBestCmap();upem=font['head'].unitsPerEm
def txt(st,x,y,size=24,color='#263d49',anchor='start'):
    width=sum(font['hmtx'].metrics.get(cmap.get(ord(c),'.notdef'),(0,0))[0] for c in st)*size/upem
    if anchor=='middle':x-=width/2
    if anchor=='end':x-=width
    out=[];offset=0
    for c in st:
        name=cmap.get(ord(c),'.notdef');pen=SVGPathPen(glyphs);glyphs[name].draw(pen);d=pen.getCommands()
        if d:out.append(f'<path transform="translate({x+offset:.3f} {y}) scale({size/upem:.6f} {-size/upem:.6f})" d="{d}" fill="{color}"/>')
        offset+=font['hmtx'].metrics[name][0]*size/upem
    return ''.join(out)
def svg(body,w=1000,h=720):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
def write_svg(folder,name,body,w=1000,h=720,png=True):
    p=A/folder/(name+'.svg');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(svg(body,w,h))
    if png:
        cairosvg.svg2png(url=str(p),write_to=str(p.with_suffix('.png')))
    return str(p.relative_to(G))
paper='<defs><linearGradient id="paper" x2="1" y2="1"><stop stop-color="#f5ead2"/><stop offset="1" stop-color="#cdb58c"/></linearGradient><pattern id="grain" width="13" height="11" patternUnits="userSpaceOnUse"><path d="M0 3h5M8 9h3" stroke="#9f8253" stroke-opacity=".09"/></pattern></defs><path d="M34 24L967 31L976 682L953 698L36 691L24 675Z" fill="url(#paper)" stroke="#b29668" stroke-width="3"/><path d="M34 24L967 31L976 682L953 698L36 691L24 675Z" fill="url(#grain)"/><path d="M66 152H932M66 635H932" stroke="#9d8159" stroke-width="2"/>'
title=lambda a,b:txt(a,70,87,39)+txt(b,72,128,19,'#7a684f')
tri='<path d="M487 190L574 338H400Z" fill="none" stroke="#385f69" stroke-width="10" stroke-linejoin="round"/><circle cx="487" cy="289" r="16" fill="none" stroke="#385f69" stroke-width="6"/>'
record=paper+title('차량 인수 기록','VEHICLE TRANSFER / RESEARCH FLEET')
for y,a,b in [(220,'차량 식별','M-04'),(305,'최종 운행','02:17'),(390,'회수 예정','03:40'),(475,'동승자 인계','██████  훼손'),(560,'차량 상태','보류')]:
    record+=txt(a,78,y,25,'#74614a')+txt(b,430,y,34)+f'<path d="M75 {y+25}H925" stroke="#b39a70" stroke-width="1"/>'
record+=txt('회수 담당자 서명란 훼손 · 원본 재발급 불가',75,666,19,'#78634c')
write_svg('documents','transfer-record',record)
base=paper+title('M-04 수동 개방 안내','잔류 전원 차단 시 · 비상 점검용')
base+='<path d="M333 165V615M72 480H925" stroke="#9a7146" stroke-width="3" stroke-dasharray="12 10"/>'
base+=tri+'<path d="M205 277A72 72 0 0 0 308 332M245 205L205 277L292 285M650 540A115 115 0 0 1 837 451M802 384L837 451L756 454" fill="none" stroke="#3a636b" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
base+=txt('접기 전에는 일부 선이 어긋나 있습니다.',74,666,19,'#7c6347')
base+='<circle cx="325" cy="217" r="9" fill="#b67842"/><circle cx="355" cy="217" r="9" fill="#b67842"/><path d="M457 472l13-20 13 20M457 494l13-20 13 20" fill="none" stroke="#b67842" stroke-width="5"/>'
write_svg('documents','manual-joined',base)
# The two complementary silhouettes share the same torn edge.
tear='M498 20L479 73L509 102L491 145L507 198L478 244L502 289L482 332L511 389L487 430L509 477L480 526L505 580L488 625L508 698'
for name,path in [('manual-A','M20 20H498'+tear[7:]+'H20Z'),('manual-B',tear+'H980V20Z')]:
    clip=f'<defs><clipPath id="piece"><path d="{path}"/></clipPath></defs>'
    write_svg('documents',name,clip+f'<g clip-path="url(#piece)">{base}</g>')
fold=paper+title('거울 테두리의 표시','VANITY MIRROR / FOLD MARK')
fold+='<path d="M188 230H804V555H188Z M392 230V555M188 447H804" fill="none" stroke="#45636a" stroke-width="4" stroke-dasharray="12 8"/><path d="M245 327H442L416 302M442 327L416 352M604 516V391L579 417M604 391L629 417" fill="none" stroke="#b8793f" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'
fold+=txt('1',265,398,40)+txt('2',657,511,40)+txt('왼쪽 1/3을 안으로 → 아래 1/3을 위로',500,611,29,anchor='middle')
write_svg('documents','fold-mark',fold)
folded=paper+title('수동 개방 경로','점검 커버 → 삼각 소켓 → 회전 순서')+tri
folded+='<path d="M219 386A92 92 0 1 0 346 274M219 386L225 312M219 386L289 378 M687 293A107 107 0 1 1 756 485M756 485L829 476M756 485L761 412" fill="none" stroke="#37616a" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
folded+=txt('01',220,230,24,'#9c713f')+txt('02',690,230,24,'#9c713f')+txt('반시계 90°',277,550,38,anchor='middle')+txt('시계 180°',739,550,38,anchor='middle')+txt('도구를 꽂고 순서대로 회전한 뒤 유리를 밀어 개방',500,667,24,anchor='middle')
write_svg('documents','manual-folded',folded)

S={
'S01':{'name':'전면 운전석','subtitle':'금속 프레임에 고정된 차','hotspots':[
 ['wiper','와이퍼 레버','M681 622L762 613Q782 611 784 638L779 659L689 674Z'],
 ['cluster','계기판과 안전벨트','M242 554Q262 492 373 482L530 493Q601 513 635 581L626 620L268 620Z'],
 ['frame','프레임과 감시 카메라','M1304 94L1418 94L1475 268L1443 297L1332 181Z'],
 ['mirror','룸미러','M735 128L1035 131Q1065 136 1069 169L1062 205Q1059 233 1023 235L728 230Q701 226 704 190L705 155Q707 134 735 128Z'],
 ['media','중앙 디스플레이','M837 499L1180 499Q1204 500 1208 527L1221 668Q1217 695 1186 698L829 697Q800 697 801 673L803 526Q806 502 837 499Z'],
 ['usb','USB 포트','M984 800H1028V827H984Z'],
 ['roofView','천장 조명','M737 2H1089L1062 79L758 76Z']
 ]},
'S02':{'name':'조수석','subtitle':'잠기지 않은 서랍','hotspots':[
 ['glove','글로브박스','M697 649L1080 606L1097 652L1084 751L793 804L675 736Z'],
 ['climate','공조·오디오 디스플레이','M284 421L563 416Q581 417 585 441L610 580Q610 601 584 605L293 621Q275 620 275 598L273 445Q272 425 284 421Z'],
 ['visor','선바이저','M787 33L1113 66Q1151 77 1152 112L1110 144L775 95Z'],
 ['usb','USB 포트','M451 711L496 707L499 741L451 746Z'],
 ['door','막힌 조수석 문','M1205 507L1323 530L1372 578L1290 580L1223 554Z']
 ]},
'S03':{'name':'뒷좌석','subtitle':'빈자리에서 울리는 경고','hotspots':[
 ['rearGlass','뒷유리의 흔적','M356 127Q411 113 570 121L1242 125Q1289 127 1304 166L1304 309L380 316L349 178Z'],
 ['underSeat','운전석 아래로','M1090 840L1336 775L1408 937H1035Z']
 ]},
'S04':{'name':'룸미러·오디오','subtitle':'서로 겹쳐진 두 목소리','hotspots':[
 ['mirror','룸미러 각도','M392 208L1250 204Q1340 208 1365 262L1380 431Q1360 491 1280 505L383 503Q315 499 298 445L290 292Q303 222 392 208Z'],
 ['audio','오디오 밸런스','M666 608L1177 609Q1202 609 1207 635L1219 789Q1217 813 1191 820L649 817Q620 813 623 787L629 638Q633 612 666 608Z']
 ]},
'S05':{'name':'운전석 하단','subtitle':'레일 끝에 남겨진 물건','hotspots':[
 ['seat','전동시트 스위치','M189 483L281 461L310 417Q322 395 352 403L370 419L348 492L315 510L189 526L173 514Z'],
 ['gap','레일 아래 공간','M636 569L1083 602L1224 740L775 849L611 733Z']
 ]},
'S06':{'name':'천장','subtitle':'위쪽에 남은 출구','hotspots':[
 ['roof','선루프','M141 62Q187 45 333 49L1439 54Q1581 67 1568 151L1391 576Q1363 620 1291 619L374 620Q296 616 271 554L84 164Q74 96 141 62Z'],
 ['cover','조명 뒤 점검 커버','M767 744L906 744Q921 748 920 769L912 832Q908 846 890 847L772 846Q755 844 754 827L748 765Q747 746 767 744Z']
 ]}}
for sid,s in S.items():
    s['id']=sid;s['asset']='assets/backgrounds/'+sid+'.png'
    s['hotspots']=[dict(id=h[0],name=h[1],path=h[2]) for h in s['hotspots']]
    for h in s['hotspots']:write_svg('masks',sid+'-'+h['id'],f'<path d="{h["path"]}" fill="white"/>',1672,941)
# Exact seat controls change location after the seat moves.
write_svg('masks','S05-seat-forward','<path d="M390 454L484 435L507 395Q519 380 544 389L563 407L541 478L391 496L373 486Z" fill="white"/>',1672,941)
write_svg('masks','rear-belt','<path d="M341 416L357 401L661 711L643 729Z" fill="white"/><path d="M628 683L667 674L681 706L643 720Z" fill="white"/>',1672,941)
write_svg('masks','windshield','<path d="M110 81L1532 75Q1599 79 1598 141L1478 450L220 475L104 188Z" fill="white"/>',1672,941)
write_svg('masks','rear-window','<path d="M356 127Q411 113 570 121L1242 125Q1289 127 1304 166L1304 309L380 316L349 178Z" fill="white"/>',1672,941)
socket='<defs><linearGradient id="metal"><stop stop-color="#ddbb78"/><stop offset=".5" stop-color="#8a612e"/><stop offset="1" stop-color="#e6bc73"/></linearGradient></defs><path d="M750 741H922V852H750Z" fill="#100e0b" stroke="#6e5032" stroke-width="8"/><path d="M836 764L872 826H800Z" fill="url(#metal)" stroke="#b08a4c" stroke-width="4" stroke-linejoin="round"/><path d="M835 788L850 814H821Z" fill="#181b1b" stroke="#523e22" stroke-width="3"/>'
write_svg('states','roof-socket-open',socket,1672,941)
visor='<rect x="788" y="117" width="358" height="235" rx="21" fill="#95846d" stroke="#c4ad8b" stroke-width="6"/><rect x="825" y="145" width="279" height="162" rx="9" fill="#233e48" stroke="#d6c49e" stroke-width="8"/><path d="M800 161H824M1106 283H1134M815 326H1115" stroke="#c4d1ce" stroke-width="4" stroke-dasharray="5 6"/>'
write_svg('states','visor-down',visor,1672,941)

items={
'photo':{'name':'훼손 사진','asset':'assets/items/photo.png','description':'모르는 여자. 그런데 함께 찍힌 차는 이 차와 닮았다. 찢긴 쪽에는 누가 있었을까.'},
'manualA':{'name':'안내서 조각 A','asset':'assets/documents/manual-A.svg','description':'삼각형의 일부와 점선. 다른 절반이 있어야 뜻을 알 수 있다.'},
'manualB':{'name':'안내서 조각 B','asset':'assets/documents/manual-B.svg','description':'끝이 맞아떨어지는 찢어진 종이. 화살표가 중간에서 끊겨 있다.'},
'card':{'name':'메모리 카드','asset':'assets/items/card.png','description':'표면에 작은 파형이 그려져 있다. 이 차의 USB에는 바로 꽂을 수 없다.'},
'reader':{'name':'카드 리더기','asset':'assets/items/reader.png','description':'옆면의 슬롯은 메모리 카드와 같은 크기다. USB 단자가 있다.'},
'usb':{'name':'카드+리더기','asset':'assets/items/reader.png','description':'메모리 카드를 넣은 리더기. 중앙 USB 포트에 사용할 수 있다.'},
'manualJoined':{'name':'맞춘 안내서','asset':'assets/documents/manual-joined.svg','description':'두 조각이 하나가 됐다. 어긋난 선과 점선은 무엇을 뜻할까.'},
'foldNote':{'name':'접기 표시','asset':'assets/documents/fold-mark.svg','description':'왼쪽 부분을 안으로, 아래 부분을 위로. 안내서의 점선과 같은 간격이다.'},
'manualFolded':{'name':'접은 개방 도면','asset':'assets/documents/manual-folded.svg','description':'천장 커버 뒤 삼각 소켓. 반시계 90도 다음 시계 180도. 마지막으로 유리를 민다.'},
'tool':{'name':'삼각 수동 도구','asset':'assets/items/tool.png','description':'닳은 황동 손잡이. 천장 부품의 삼각 기호와 같다.'}}
notes={
'frame':['프레임 04','차가 금속 운송 프레임 안에 고정돼 있다. 감시 카메라가 이 차를 향한다. 옆문은 열 수 없고 위쪽에만 여유가 있다.'],
'occupancy':['빈 좌석의 무게','경고는 사람이 아니라 가방의 무게를 감지하고 있었다. 가방에는 누군가 일부러 남긴 물건이 있다.'],
'photo':['훼손된 사진','사진 속 여자와 차. 낯선 얼굴인데도 손이 먼저 사진을 뒤집으려 했다.'],
'record':['인수 기록','M-04 / 최종 운행 02:17 / 회수 예정 03:40 / 동승자 인계 훼손 / 상태 보류. 이 시각은 기록이며 카운트다운이 아니다.'],
'voices':['손상된 녹음','좌우 채널에 서로 다른 목소리가 들어 있다. 오디오 밸런스로 나누어 들을 수 있다.'],
'voiceLeft':['왼쪽 목소리','“다시 눈을 뜨면, 유리의 흔적을 봐.” 낮게 말하는 여자의 목소리.'],
'voiceRight':['오른쪽 목소리','“잊어도, 손은 기억할 거야.” 이상하게 익숙한 남자의 목소리.'],
'glass':['거울 속 문장','“끝까지. 그 아래.” 문장 밑의 그림은 시트 레일이다. 운전석을 앞으로 끝까지 보내고 뒤에서 확인하라는 뜻 같다.'],
'tool':['레일 아래의 도구','시트 끝까지 이동하자 손이 들어가는 공간이 생겼다. 도구의 삼각 기호와 천장 점검 기호가 같다.'],
'fold':['테두리의 접기 표시','안내서 왼쪽 1/3을 가운데로, 아래 1/3을 위로 접는다.'],
'manual':['완성된 수동 도면','삼각 소켓에 도구를 넣고 반시계 90도 → 시계 180도. 도면은 천장 점검 커버의 위치를 가리킨다.'],
'roof':['위쪽의 문','수동 잠금 장치가 해제됐다. 선루프를 밀어 열면 위로 빠져나갈 수 있다.']}
manifest={'title':'잔류 전원','subtitle':'RESIDUAL POWER','chapter':'01','artStyle':'cognac-amber-teal-painted','scope':'차량 밀실 1막 / 가상 차량 조작 / 퍼즐 7개','scenes':list(S.values()),'items':items,'notes':notes,'canvas':[1672,941],'sprites':{'bag':{'asset':'assets/items/bag.png','box':[235,352,500,417]},'bagMoved':{'asset':'assets/items/bag.png','box':[718,692,295,246]},'coat':{'asset':'assets/items/coat.png','box':[243,397,510,287]},'tool':{'asset':'assets/items/tool.png','box':[810,632,178,119]}}}
(G/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Wrote documents, transparent part masks, state overlays and manifest')
