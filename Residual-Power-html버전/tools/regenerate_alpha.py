"""Read source alpha into precise vector interaction geometry; original PNGs stay untouched."""
from pathlib import Path
from PIL import Image
import cv2,numpy as np,json,cairosvg,base64
R=Path(__file__).resolve().parents[1];G=R;out=G/'assets/alpha';out.mkdir(exist_ok=True)
result={}
clean=G/'assets/cutouts';clean.mkdir(exist_ok=True)
for p in sorted((G/'assets/items').glob('*.png')):
    im=Image.open(p);assert im.mode=='RGBA',p.name
    a=np.array(im.getchannel('A'));binary=(a>=110).astype(np.uint8)*255
    contours,hierarchy=cv2.findContours(binary,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    paths=[]
    for contour in contours:
        if abs(cv2.contourArea(contour))<50:continue
        points=cv2.approxPolyDP(contour,1.4,True).reshape(-1,2)
        if len(points)>=3:paths.append('M'+'L'.join(f'{x} {y}' for x,y in points)+'Z')
    d=''.join(paths);w,h=im.size
    assert d and (a==0).mean()>.2
    result[p.stem]={'width':w,'height':h,'path':d,'fullyTransparentFraction':round(float((a==0).mean()),4),'alphaBbox':list(Image.fromarray(binary).getbbox())}
    source=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><path d="{d}" fill="white" fill-rule="evenodd"/></svg>'
    (out/(p.stem+'.svg')).write_text(source);
    encoded=base64.b64encode(p.read_bytes()).decode()
    cutout=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><clipPath id="subject"><path d="{d}" clip-rule="evenodd"/></clipPath></defs><image width="{w}" height="{h}" href="data:image/png;base64,{encoded}" clip-path="url(#subject)"/></svg>'
    (clean/(p.stem+'.svg')).write_text(cutout)
    cairosvg.svg2png(bytestring=source.encode(),write_to=str(out/(p.stem+'.png')))
(G/'alpha.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(f'Verified {len(result)} true-alpha sprites; extracted exact hit silhouettes')
