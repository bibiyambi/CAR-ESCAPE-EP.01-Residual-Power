from pathlib import Path
import json,re,xml.etree.ElementTree as ET,wave
from PIL import Image
R=Path(__file__).resolve().parents[1];m=json.loads((R/'manifest.json').read_text());a=json.loads((R/'alpha.json').read_text());checks={}
checks['scenes']=len(m['scenes'])==14
checks['all_scene_backgrounds']=all((R/s['asset']).is_file() for s in m['scenes'])
checks['all_item_assets']=all((R/x['asset']).is_file() for x in m['items'].values())
checks['aspect_1672_941']=all(Image.open(p).size==(1672,941) for p in (R/'assets/backgrounds').glob('*.png'))
checks['true_alpha_11']=len(a)==11 and all(x['fullyTransparentFraction']>.2 for x in a.values())
checks['all_cutouts_have_clip']=all('<clipPath' in p.read_text() and 'clip-rule="evenodd"' in p.read_text() for p in (R/'assets/cutouts').glob('*.svg'))
checks['svg_parse']=True
for p in (R/'assets').rglob('*.svg'):ET.parse(p)
checks['stereo_recording']=wave.open(str(R/'assets/audio/stereo-recording.wav')).getnchannels()==2
checks['all_voices']=all((R/'assets/audio'/(n+'.wav')).is_file() for n in ['archive-L','archive-R','archive-final'])
html=(R/'standalone.html').read_text()
checks['standalone_has_no_remote_runtime']=not re.search(r'<(?:script|link|img)[^>]+(?:src|href)=["\']https?://',html)
checks['standalone_has_no_placeholders']='__ASSETS__' not in html and '__ENGINE__' not in html
checks['12_profiles']=len(json.loads((R/'profiles.json').read_text()))==12
checks['screen_controls_OFF_hidden']='if(!game.state.screenControlAssist)return' in (R/'app.js').read_text() and 'b.hidden=!game.state.screenControlAssist' in (R/'app.js').read_text()
counts={folder:len(list((R/'assets'/folder).glob('*'))) for folder in ['backgrounds','items','cutouts','alpha','documents','masks','states','audio']}
report={'version':2,'checks':checks,'counts':counts,'allPassed':all(checks.values()),'limits':['Native Pleos binding and real-vehicle checks are not implemented','45–60 minute duration is a design target, not measured user playtime']}
(R/'validation/v2-static-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert report['allPassed']
