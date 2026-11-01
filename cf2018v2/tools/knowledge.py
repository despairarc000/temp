"""Small stdlib ICM/graph/link validator. No network or original game access."""
from pathlib import Path
import argparse,csv,re
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
GROUPS={
 'producer':('vault/CURRENT.md','../cf2018/knowledge-system/vault/research/REPOSITORY_SOURCE_AUDIT.md','../cf2018/knowledge-system/vault/research/ADDRESS_APPLICATION.md','../cf2018/knowledge-system/vault/research/UPSTREAM_REQUEST_CHAIN.md'),
 'phone':('vault/WORKFLOW.md','../cf2018/knowledge-system/vault/research/PHONE_V381.md'),
 'source':('vault/SOURCES.md',),
 'auth':('vault/CURRENT.md','../cf2018/knowledge-system/vault/research/AUTH_RECEIVER.md'),
 'integrity':('../cf2018/knowledge-system/vault/research/INTEGRITY_NATIVE.md',),
 'timeline':('diary/INDEX.md',)}
ALIASES={'native':'producer','encoding':'producer','termux':'phone','pcapdroid':'phone','apk':'source','xapk':'source','obb':'source','dll':'integrity','ack':'auth','bingo':'auth','older':'timeline'}
def doctor():
 errors=[]
 for p in ROOT.rglob('*.md'):
  for raw in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',p.read_text()):
   if raw.startswith(('https:','http:','#')):continue
   target=(p.parent/raw.split('#')[0]).resolve()
   if not target.is_relative_to(REPO) or not target.exists():errors.append(str(p.relative_to(ROOT))+': '+raw)
 with (ROOT/'graphify/edges.tsv').open() as f:
  for edge in csv.DictReader(f,delimiter='\t'):
   for key in ('from','to'):
    p=(ROOT/edge[key]).resolve()
    if not p.is_relative_to(REPO) or not p.exists():errors.append('graph: '+edge[key])
 diary=(ROOT/'diary.md').read_text()
 if len(re.findall(r'^## R[0-9]+',diary,re.M))>30 or len(diary.encode())>8192:errors.append('rotate diary before adding entries')
 return errors
def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['route','doctor','graph']);p.add_argument('task',nargs='*');a=p.parse_args()
 if a.command=='doctor':
  errors=doctor();print('\n'.join(errors) if errors else 'PASS: links, graph and diary limits');raise SystemExit(bool(errors))
 if a.command=='graph':print((ROOT/'graphify/edges.tsv').read_text());return
 paths=['START.md','vault/CURRENT.md','diary.md']
 for word in re.findall('[a-z0-9]+',' '.join(a.task).lower()):paths.extend(GROUPS.get(ALIASES.get(word,word),()))
 if len(paths)==3:paths.append('icm/ROUTES.md')
 print('\n'.join(dict.fromkeys(paths)))
if __name__=='__main__':main()
