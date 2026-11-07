"""One-time conversion of owned public captures into sanitized editable content."""
from pathlib import Path
import json
from build import sanitize,ROUTES
p=Path(__file__).resolve().parents[1];out=p/'content/pages';out.mkdir(exist_ok=True)
for f in (p/'capture').glob('*.json'):
 if f.stem not in ROUTES and not f.stem.startswith('post-'):continue
 d=json.loads(f.read_text())
 if not isinstance(d,dict)or'html'not in d:continue
 d['html']=sanitize(d)
 d['bodyClass']=d['bodyClass'].replace(' loggedin ',' ')
 (out/f.name).write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('Sanitized editable pages',len(list(out.glob('*.json'))))
