"""Native UI acceptance test for the disposable residual-native AVD only (clears app data)."""
import argparse
import hashlib
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--adb', default='adb')
parser.add_argument('--serial', default='emulator-5554')
parser.add_argument('--skip-install', action='store_true', help='Use the same APK already installed on the disposable AVD')
args = parser.parse_args()
PACKAGE = 'io.bibiyambi.residualpower.development'
CAPTURES = ROOT / 'captures'
CAPTURES.mkdir(exist_ok=True)


def adb(*command, binary=False):
    timeout = 300 if command[0] == 'install' else 180
    return subprocess.check_output([args.adb, '-s', args.serial, *command], timeout=timeout, text=not binary)


def tree():
    adb('shell', 'uiautomator', 'dump', '/sdcard/residual-ui.xml')
    return ET.fromstring(adb('exec-out', 'cat', '/sdcard/residual-ui.xml'))


def find(text=None, **attributes):
    for node in tree().iter('node'):
        if (text is None or node.get('text') == text) and all(node.get(k) == v for k, v in attributes.items()):
            return node
    return None


def wait(text, seconds=30):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        node = find(text)
        if node is not None:
            return node
    raise AssertionError('UI text missing: ' + text)


def tap_node(node):
    assert node is not None, 'UI element missing'
    x1, y1, x2, y2 = map(int, re.findall(r'\d+', node.get('bounds')))
    adb('shell', 'input', 'tap', str((x1+x2)//2), str((y1+y2)//2))


def tap(text):
    tap_node(wait(text))
    print('UI:', text, flush=True)


def shot(name):
    (CAPTURES / name).write_bytes(adb('exec-out', 'screencap', '-p', binary=True))


def enable_and_resume(label):
    tap_node(find(checkable='true', checked='false'))
    tap(label)


def run():
    assert adb('shell', 'getprop', 'ro.kernel.qemu').strip() == '1'
    assert adb('emu', 'avd', 'name').splitlines()[0] in {'residual-native', 'residual-native-api28'}, 'Use a disposable residual-native AVD'
    apk = ROOT / 'app/build/outputs/apk/development/debug/app-development-debug.apk'
    if not args.skip_install:
        adb('install', '-r', str(apk))
    adb('shell', 'pm', 'clear', PACKAGE)
    adb('shell', 'am', 'start', '-W', '-n', PACKAGE + '/io.bibiyambi.residualpower.GameActivity')
    node = wait('눈을 뜬다')
    assert node.get('enabled') == 'false', 'Game must begin blocked'
    shot('native-blocked.png')
    enable_and_resume('눈을 뜬다')
    wait('01막 / S01')
    shot('native-start.png')
    tap('뒷좌석')
    for action in ['게임 외투 걷기', '가방 고정 끈 풀기', '가방을 바닥으로 옮기기', '가방 내용물 챙기기']:
        tap(action)
    tap('조수석')
    for action in ['글로브박스 열기', '서랍 내용물 챙기기', '인수 기록 읽기', '선바이저 조사']:
        tap(action)
    tap('메모리 카드'); tap('카드 리더기'); tap('조합')
    tap('USB 포트에 리더기 연결')
    tap('운전석 하단'); tap('게임 시트 조작')
    slider = find(**{'class': 'android.widget.SeekBar'})
    assert slider is not None
    x1, y1, x2, y2 = map(int, re.findall(r'\d+', slider.get('bounds')))
    adb('shell', 'input', 'tap', str(x2-2), str((y1+y2)//2))
    wait('게임 시트 · 100%')
    tap('닫기'); tap('레일 아래 도구 찾기')
    tap('천장'); tap('점검 커버 열기'); tap('삼각 도구 끼우기')
    tap('수동 소켓 회전'); tap('반시계 90°'); tap('시계 180°'); tap('닫기')
    tap('게임 선루프 열기'); tap('위쪽 통로로 탈출')
    wait('유리 흔적 판독부의 풍량 입력을 복원해야 탈출 경로를 확인할 수 있다.')
    tap('조수석'); tap('유리 흔적 판독부'); tap('단말 활성화'); tap('풍량 낮음')
    wait('입력 복원 완료 · 드러난 단서를 조사하세요.')
    tap('닫기'); tap('천장'); tap('위쪽 통로로 탈출')
    wait('1막 완료 · 감시실의 전원이 살아 있다.\n2·3막은 다음 네이티브 이식 단계입니다.')
    shot('native-act1-complete.png')
    tap('일시정지')
    wait('직접 재개')
    # A stopped process cannot restore authorization or automatically resume.
    adb('shell', 'am', 'force-stop', PACKAGE)
    adb('shell', 'am', 'start', '-W', '-n', PACKAGE + '/io.bibiyambi.residualpower.GameActivity')
    assert wait('직접 재개').get('enabled') == 'false'
    enable_and_resume('직접 재개')
    wait('1막 완료 · 감시실의 전원이 살아 있다.\n2·3막은 다음 네이티브 이식 단계입니다.')
    # Corruption detection must preserve bytes until explicit recovery.
    adb('shell', 'am', 'force-stop', PACKAGE)
    adb('shell', 'run-as', PACKAGE, 'sh', '-c', "'printf broken > files/native-save.json'")
    adb('shell', 'am', 'start', '-W', '-n', PACKAGE + '/io.bibiyambi.residualpower.GameActivity')
    tap('백업 복구 / 저장 재시도')
    saved = adb('exec-out', 'run-as', PACKAGE, 'cat', 'files/native-save.json')
    checksum, payload = saved.split('\n', 1)
    assert hashlib.sha256(payload.encode()).hexdigest() == checksum
    assert json.loads(payload)['schemaVersion'] == 1
    archives = adb('shell', 'run-as', PACKAGE, 'ls', 'files')
    assert 'native-save.preserved.' in archives
    print('PASS: blocked start, native exploration, combination, socket, P05 escape gate, completion, process restoration, explicit recovery')


try:
    run()
except Exception:
    shot('native-failure.png')
    raise
