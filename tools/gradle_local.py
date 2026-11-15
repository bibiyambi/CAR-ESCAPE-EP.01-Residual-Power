"""Use local tools and the environment's existing proxy/trust; print no credentials."""
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
env = os.environ.copy()
local_jdk = Path('/workspace/android-tools/jdk-17.0.17+10')
if local_jdk.exists():
    env['JAVA_HOME'] = str(local_jdk)
args = [str(root / 'gradlew'), '--console=plain', '--no-daemon']
proxy = urlparse(env.get('HTTPS_PROXY', ''))
if proxy.hostname:
    for scheme in ['https', 'http']:
        args += [f'-D{scheme}.proxyHost={proxy.hostname}', f'-D{scheme}.proxyPort={proxy.port or 80}']
trust = Path('/etc/ssl/certs/java/cacerts')
if trust.exists():
    env['JAVA_OPTS'] = env.get('JAVA_OPTS', '') + f' -Djavax.net.ssl.trustStore={trust}'
    args += [f'-Djavax.net.ssl.trustStore={trust}']
sys.exit(subprocess.call(args + sys.argv[1:], cwd=root, env=env))
