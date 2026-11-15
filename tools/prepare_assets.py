"""Copy only the first native milestone's assets; never copy SDK information or JS."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
args = parser.parse_args()
source = args.source.resolve()
target = ROOT / 'app/build/generated/nativeAssets'
if not source.is_dir():
    # Portable local export: use only the explicitly packaged, checksum-verified seed.
    seed = ROOT / '.local/native-assets'
    checksums = seed / 'portable-sha256.json'
    if not checksums.is_file():
        raise SystemExit('Game source pack was not found. Set -PgameSource=/absolute/path/to/source-pack.')
    entries = json.loads(checksums.read_text())
    for relative, expected in entries.items():
        src = seed / relative
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise SystemExit('Invalid portable asset path')
        if hashlib.sha256(src.read_bytes()).hexdigest() != expected:
            raise SystemExit('Portable asset checksum mismatch: ' + relative)
    for relative in entries:
        dst = target / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(seed / relative, dst)
    print(f'Prepared {len(entries)} verified portable native asset files')
    raise SystemExit(0)
manifest = json.loads((source / 'manifest.json').read_text())
target.mkdir(parents=True, exist_ok=True)
paths = [f'assets/backgrounds/{name}.png' for name in [
    'S01', 'S02', 'S03', 'S04', 'S05', 'S06', 'S02-open', 'S05-forward', 'S06-open', 'END']]
paths += ['assets/audio/stereo-recording.wav']
paths += [str(p.relative_to(source)) for p in (source / 'assets/fonts').glob('*') if p.suffix != '.woff2']
copies = {relative: relative for relative in paths}
for name in ['photo', 'manualA', 'manualB', 'card', 'reader', 'usb', 'manualJoined', 'foldNote', 'manualFolded', 'tool']:
    relative = manifest['items'][name]['asset']
    # Use the supplied PNG rendering of document SVGs; no browser/SVG runtime needed.
    if relative.endswith('.svg'):
        relative = relative[:-4] + '.png'
    copies[f'assets/items/{name}.png'] = relative
hashes = {}
for relative, original in copies.items():
    src = source / original
    dst = target / relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or hashlib.sha256(dst.read_bytes()).digest() != hashlib.sha256(src.read_bytes()).digest():
        shutil.copyfile(src, dst)
    hashes[relative] = hashlib.sha256(src.read_bytes()).hexdigest()
(target / 'notes.json').write_text(json.dumps(manifest['notes'], ensure_ascii=False))
(target / 'asset-sha256.json').write_text(json.dumps(hashes, indent=2))
print(f'Prepared {len(copies)} native assets; no HTML, JavaScript, or SDK credentials')
