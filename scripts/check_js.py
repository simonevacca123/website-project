"""Verifica la sintassi di tutti gli script pubblici con Node, senza eseguirli."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
files = {'app.js', 'contenuti.js'} | {name for name in json.loads((ROOT / 'scripts/public-files.json').read_text()) if name.endswith('.js')}
for name in sorted(files):
    subprocess.run(['node', '--check', str(ROOT / name)], check=True)
print(f'PASS: sintassi di {len(files)} script pubblici.')
