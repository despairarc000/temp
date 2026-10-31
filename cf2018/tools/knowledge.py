#!/usr/bin/env python3
"""CF2018 knowledge routing, Graphify and Vault validation (stdlib)."""
from pathlib import Path
from collections import deque
import argparse, csv, re

ROOT=Path(__file__).resolve().parents[1]
BASE=["AGENTS.md","NAVIGATION.md","IDEA_PLAN.md","knowledge-system/vault/CHECKPOINT.md","coordination/CURRENT_HANDOFF.md"]
ROUTES={
 "v38":(["v38","datahead","serializer","sequence"],["knowledge-system/vault/research/V38_SOURCE_AUDIT.md","knowledge-system/vault/research/V38_BLOCKER.md","knowledge-system/vault/research/SERVER_PATH.md"]),
 "tgcp":(["tgcp","ack","syn","apollo","handshake","framing"],["knowledge-system/vault/research/TGCP.md","knowledge-system/vault/research/ACK_RECEIVER.md","knowledge-system/vault/EVIDENCE.md"]),
 "auth":(["auth","authentication","bingo","session","0x2001","0x2002","2001","2002","callback","connected","connection","routed","address","0x4013","4013"],["knowledge-system/vault/research/SERVER_PATH.md","knowledge-system/vault/research/ADDRESS_APPLICATION.md","knowledge-system/vault/research/CONNECTION_CALLBACKS.md","knowledge-system/vault/research/AUTH_RECEIVER.md","knowledge-system/vault/research/BINGO_SESSION.md","knowledge-system/vault/research/ACK_SESSION.md","coordination/incoming/CF18-05/PHONE_V12_RESULT.md","knowledge-system/vault/EVIDENCE.md"]),
 "bridge":(["pcapdroid","termux","socks5","vpn","tcp","relay","dns"],["TECHNICAL_PLAN.md","knowledge-system/vault/EVIDENCE.md"]),
 "startup":(["startup","mono","dll","apk","crash","integrity","protected","assembly","checksum"],["knowledge-system/vault/research/STARTUP.md","knowledge-system/vault/research/INTEGRITY_NATIVE.md","sources/DRIVE_MANIFEST.md"]),
 "sources":(["drive","obb","asset","native","libapollo","source","provenance","mirror","signature","hash"],["sources/DRIVE_MANIFEST.md","sources/SOURCE_PROVENANCE.md"]),
 "gameplay":(["bot","tdm","bomb","gameplay","offline","lobby"],["IMPLEMENTATION_PLAN.md","knowledge-system/vault/specs/ACCEPTANCE.md"]),
 "handoff":(["continue","status","next","checkpoint"],["knowledge-system/vault/CHECKPOINT.md","knowledge-system/vault/OPEN_QUESTIONS.md"]),
 "knowledge":(["graphify","icm","vault","graph"],["knowledge-system/icm/ICM.md","knowledge-system/graphify/GRAPHIFY.md","knowledge-system/vault/INDEX.md"])}
LINK=re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')
REQUIRED=BASE+["README.md","TECHNICAL_PLAN.md","IMPLEMENTATION_PLAN.md","sources/DRIVE_MANIFEST.md","knowledge-system/vault/INDEX.md","knowledge-system/graphify/edges.tsv"]
def docs(root=ROOT):
 return sorted(root.rglob("*.md"))
def refs(p):
 for raw in LINK.findall(p.read_text(encoding="utf-8")):
  raw=raw.strip().split(" ",1)[0].strip("<>")
  if raw.startswith(("http:","https:","mailto:","#")): continue
  raw=raw.split("#",1)[0]
  if raw: yield raw,(p.parent/raw).resolve()
def edges(root=ROOT):
 results=set()
 for p in docs(root):
  for raw,dst in refs(p):
   if dst.is_file() and dst.is_relative_to(root.resolve()) and dst.suffix==".md":
    results.add((p.relative_to(root).as_posix(),dst.relative_to(root).as_posix(),"doc-link"))
 path=root/"knowledge-system/graphify/edges.tsv"
 if path.exists():
  with path.open(encoding="utf-8") as file:
   for e in csv.DictReader(file,delimiter="\t"):
    results.add((e["from"],e["to"],e["relation"]+" ["+e["status"]+"]"))
 return sorted(results)
def doctor(root=ROOT):
 root=root.resolve()
 issues=["missing: "+s for s in REQUIRED if not (root/s).is_file()]
 for p in docs(root):
  for raw,target in refs(p):
   if not target.is_relative_to(root): issues.append("escaping link: "+str(p)+" -> "+raw)
   elif not target.is_file(): issues.append("broken link: "+str(p)+" -> "+raw)
 for a,b,_ in edges(root):
  for name in (a,b):
   if not (root/name).is_file(): issues.append("bad graph node: "+name)
 index=root/"knowledge-system/vault/INDEX.md"
 if index.is_file():
  seen=set(); q=deque([index])
  while q:
   p=q.popleft().resolve()
   if p in seen or not p.is_file(): continue
   seen.add(p)
   q.extend(t for _,t in refs(p) if t.is_file() and t.suffix==".md")
  for p in docs(root):
   if p.relative_to(root).as_posix().startswith("knowledge-system/vault/") and p.resolve() not in seen:
    issues.append("vault unreachable: "+str(p.relative_to(root)))
 return sorted(set(issues))
def route(task):
 words=set(re.findall(r"[a-z0-9]+",task.lower()))
 ranks=[]; paths=list(BASE)
 for name,(keys,docs_) in ROUTES.items():
  score=len(words.intersection(keys))
  if score: ranks.append((name,score)); paths.extend(docs_)
 if not ranks: paths+=["knowledge-system/vault/INDEX.md","knowledge-system/vault/OPEN_QUESTIONS.md"]
 return sorted(ranks,key=lambda x:(-x[1],x[0])),list(dict.fromkeys(paths))
def graph():
 e=edges()
 return "# CF2018 Graphify\n\nDerived direct Markdown links and curated edge list; no inferred semantics.\n\n"+"\n".join("| "+a+" | "+b+" | "+r+" |" for a,b,r in e)+"\n"
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
 sub.add_parser("doctor")
 sub.add_parser("graph").add_argument("--output")
 sub.add_parser("route").add_argument("task",nargs="+")
 args=p.parse_args()
 if args.cmd=="doctor":
  issues=doctor()
  if issues: print("\n".join(issues));raise SystemExit(1)
  print("PASS: required files, links, vault and graph")
 elif args.cmd=="route":
  names,paths=route(" ".join(args.task));print("Routes:",names)
  print("\n".join(x for x in paths if (ROOT/x).is_file()))
 else:
  result=graph()
  if args.output:
   out=(ROOT/args.output).resolve()
   if not out.is_relative_to(ROOT): raise SystemExit("invalid graph output path")
   out.parent.mkdir(parents=True,exist_ok=True);out.write_text(result,encoding="utf-8")
  else: print(result)
if __name__=="__main__": main()
