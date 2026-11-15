"""Check current Git candidates and optional APK; never print credential values.

Pattern checks are heuristic. This script does not scan Git history.
"""
import argparse
from pathlib import Path
import subprocess
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--apk', type=Path)
args = parser.parse_args()
private = ROOT / 'private/pleos.properties'
values = [line.split('=', 1)[1].strip().encode() for line in private.read_text().splitlines()
          if '=' in line and line.split('=', 1)[1].strip()
          and not line.lstrip().startswith(('#', '!'))] if private.exists() else []
patterns = {
    'private key': rb'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----',
    'GitHub token': rb'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
    'AWS access key': rb'(?<![A-Za-z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Za-z0-9])',
    'OpenAI key': rb'(?<![A-Za-z0-9_/-])sk-(?:proj-)?[A-Za-z0-9_-]{20,}',
    'credential in URL': rb'https?://[^\s/@:\x22\x27<>]+:[^\s/@\x22\x27<>]+@',
    'credential assignment': (
        rb'(?im)^\s*(?:(?:export|val|var|const)\s+)?[\x22\x27]?'
        rb'(?:api[_-]?key|client[_-]?secret|access[_-]?token|storePassword|keyPassword)'
        rb'[\x22\x27]?\s*[:=]\s*[\x22\x27]?[A-Za-z0-9_./+=-]{12,}'),
}
private_dirs = {'.local', 'private', 'sdk', '.idea', '.gradle', '.kotlin', 'build'}
private_suffixes = {'.aar', '.jar', '.jks', '.keystore', '.p12', '.pfx', '.pem', '.key', '.apk', '.aab', '.apks'}
private_names = {'local.properties', '.gradle-local.properties', 'keystore.properties',
                 'signing.properties', 'secrets.properties', 'credentials.properties'}


def scan(data, label):
    if any(value in data for value in values):
        errors.append(label + ': configured private value')
    for kind, pattern in patterns.items():
        if re.search(pattern, data):
            errors.append(label + ': ' + kind)


files = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).split(b'\0')
errors = []
count = 0
for name in files:
    if not name:
        continue
    relative = Path(name.decode())
    label = relative.as_posix()
    if label != 'gradle/wrapper/gradle-wrapper.jar' and (
        private_dirs.intersection(relative.parts) or relative.suffix.lower() in private_suffixes
        or relative.name in private_names or relative.name.startswith('.env')
        or ('pleos' in relative.name.lower() and 'sdk' in relative.name.lower()
            and ('정보' in relative.name or '정보' in relative.name))
    ):
        errors.append(label + ': prohibited Git candidate')
    path = ROOT / relative
    if not path.is_file():
        continue
    count += 1
    scan(path.read_bytes(), label)
    if path.suffix == '.docx':
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                if member.endswith(('.xml', '.rels')):
                    scan(archive.read(member), label + ':' + member)
if private.exists():
    subprocess.run(['git', 'check-ignore', '--quiet', str(private)], cwd=ROOT, check=True)
if args.apk:
    with zipfile.ZipFile(args.apk) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            data = archive.read(info)
            scan(data, 'APK:' + info.filename)
            if info.filename.startswith('assets/') and info.filename.endswith(('.html', '.js', '.properties', '.aar', '.md')):
                # License files are .txt; no SDK docs or web runtime may be packaged.
                errors.append('unexpected asset:' + info.filename)
if errors:
    raise SystemExit('Private-material check FAILED:\n' + '\n'.join(sorted(set(errors))))
print(f'PASS: {count} Git candidate files' + (' and APK contents' if args.apk else '')
      + '; no prohibited paths or secret-pattern matches')
print(f'Known-value matching: {len(values)} configured values' if values
      else 'Known-value matching skipped: no configured local Pleos values')
print('Scope: current working files; Git history and unrecognized secret formats are not covered.')
