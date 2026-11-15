from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[1];A=R/'assets';entries=[]
for folder in ['backgrounds','cutouts','alpha','documents','masks','states','audio']:
 for p in sorted((A/folder).glob('*')):
  if not p.is_file() or p.suffix not in ['.svg','.png','.wav']:continue
  entries.append(dict(category=folder,name=p.stem,path=str(p.relative_to(R)),bytes=p.stat().st_size))
(R/'asset-index.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2))
css='''body{margin:0;background:#122731;color:#e9dec7;font:16px sans-serif}header{padding:44px 5%;background:#1c333b;border-bottom:1px solid #baa27555}h1{font-weight:400;font-size:34px;letter-spacing:.1em}p{line-height:1.8;color:#aec1b9}main{padding:30px 5%}nav{display:flex;flex-wrap:wrap;gap:10px}button{background:#203c45;color:#e5d8ba;border:1px solid #9a8865;padding:14px;cursor:pointer;border-radius:7px}button.on{background:#61583c}section{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:22px}article{background:#1b343e;border:1px solid #8e826044;border-radius:8px;overflow:hidden}article .image{height:230px;background:repeating-conic-gradient(#1c3540 0 25%,#25414a 0 50%) 0/24px 24px;display:flex;align-items:center;justify-content:center}img{max-width:100%;max-height:100%;object-fit:contain}article.alpha .image,article.masks .image{background:#356b73}article h3{font-size:17px;letter-spacing:.04em;color:#d4bc8c;margin:18px}article p{font-size:13px;margin:18px;word-break:break-all}a{color:#d9c493}audio{width:90%}h2{margin:36px 0 22px;font-weight:400}'''
cards=[]
for e in entries:
 path=html.escape(e['path']);cat=e['category'];name=html.escape(e['name']);content=f'<audio controls src="{path}"></audio>' if path.endswith('.wav') else f'<img loading="lazy" src="{path}" alt="{name}">'
 cards.append(f'<article class="{cat}" data-category="{cat}"><div class="image">{content}</div><h3>{name}</h3><p>{cat} / {e["bytes"]//1024} KB<br><a href="{path}" target="_blank">개별 에셋 열기</a></p></article>')
page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>잔류 전원 3막 에셋 도감</title><style>'+css+'</style><header><small>RESIDUAL POWER / PRODUCTION ASSETS v2</small><h1>잔류 전원 · 에셋 도감</h1><p>3막 통합 이미지·도면·윤곽 마스크·음향. 원본 투명 PNG는 assets/items에, 게임에서 사용하는 윤곽 정리본은 cutouts에 있습니다.<br>배경은 1672×941 원본 비율을 유지합니다. 생성 이미지와 정확한 퍼즐 정보는 분리했습니다.</p><nav>'+''.join(f'<button data-filter="{x}">{x}</button>' for x in ['all','backgrounds','cutouts','documents','alpha','masks','states','audio'])+'</nav></header><main><h2>'+str(len(entries))+' runtime and export assets</h2><section>'+''.join(cards)+'</section></main><script>document.querySelectorAll("[data-filter]").forEach(b=>b.onclick=()=>{document.querySelectorAll("[data-filter]").forEach(x=>x.classList.toggle("on",x===b));document.querySelectorAll("article").forEach(x=>x.hidden=b.dataset.filter!=="all"&&x.dataset.category!==b.dataset.filter);});</script></html>'
(R/'에셋도감.html').write_text(page)
print('Indexed',len(entries),'assets')
