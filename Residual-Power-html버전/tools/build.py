"""python tools/build.py — rebuild using Python standard library only."""
from pathlib import Path
import json,base64
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets'
style=((ROOT/'style.css').read_text(encoding='utf-8')+'\n'+(ROOT/'style-v2.css').read_text(encoding='utf-8')).replace('__FONT__','data:font/woff2;base64,'+base64.b64encode((A/'fonts/residual.woff2').read_bytes()).decode())
runtime=[]
for folder,ext in [('backgrounds','png'),('cutouts','svg'),('documents','svg'),('states','svg'),('audio','wav')]:runtime.extend(sorted((A/folder).glob('*.'+ext)))
def uri(p):return 'data:'+{'.png':'image/png','.svg':'image/svg+xml','.wav':'audio/wav'}[p.suffix]+';base64,'+base64.b64encode(p.read_bytes()).decode()
template=(ROOT/'source/template.html').read_text(encoding='utf-8')
for key,value in [('STYLE',style),('ENGINE',(ROOT/'engine.js').read_text(encoding='utf-8')+'\n'+(ROOT/'engine-v2.js').read_text(encoding='utf-8')),('APP',(ROOT/'app.js').read_text(encoding='utf-8')),('CONTENT',(ROOT/'manifest.json').read_text(encoding='utf-8')),('ALPHA',(ROOT/'alpha.json').read_text(encoding='utf-8')),('RECORDING',(A/'audio/recording.json').read_text(encoding='utf-8')),('PROFILES',(ROOT/'profiles.json').read_text(encoding='utf-8'))]:template=template.replace('__'+key+'__',value)
relative={str(p.relative_to(ROOT)):uri(p) if p.suffix=='.wav' else str(p.relative_to(ROOT)) for p in runtime}
embedded={str(p.relative_to(ROOT)):uri(p) for p in runtime}
(ROOT/'index.html').write_text(template.replace('__ASSETS__',json.dumps(relative,ensure_ascii=False)),encoding='utf-8')
(ROOT/'standalone.html').write_text(template.replace('__ASSETS__',json.dumps(embedded,ensure_ascii=False)),encoding='utf-8')
print('Built index.html and standalone.html')
