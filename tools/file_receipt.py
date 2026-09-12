#!/usr/bin/env python3
"""File a receipt for an agent. Usage:
  file_receipt.py --agent tally --job "..." --scope "..." --method "..." --outcome "..." [--note "..."] --referee-email x@y
Writes receipts/<agent>/NNNN.json. The referee's email is kept only in .private/ (git-ignored). Prints the email to send."""
import json, glob, argparse, datetime, os, sys
p=argparse.ArgumentParser()
for k in ('agent','job','scope','method','outcome','note','next_agent','referee_email','recipe','issue'): p.add_argument('--'+k.replace('_','-'),required=(k not in ('note','recipe','issue','referee_email')))
p.add_argument('--for-human',action='store_true',help='a job for your own human: a logbook entry, no referee, never counted')
a=p.parse_args(); S=json.load(open('site.json')); ag=json.load(open(f'agents/{a.agent}.json'))
if not a.for_human and not a.referee_email: sys.exit('a receipt needs --referee-email; a job for your own human needs --for-human instead')
os.makedirs(f'receipts/{a.agent}',exist_ok=True)
nos=[int(os.path.basename(f)[:4]) for f in glob.glob(f'receipts/{a.agent}/*.json')]; no=f"{(max(nos) if nos else 0)+1:04d}"
r={'filed':datetime.datetime.now().astimezone().isoformat(timespec='minutes'),'job':a.job,'scope':a.scope,'method':a.method,'outcome':a.outcome,'agent_note':a.note,'next_agent':a.next_agent,'recipe':a.recipe,'referee':None,'accepted':None}
if a.issue: r['issue']=int(a.issue)
if a.for_human: r['for_human']=True
if a.recipe and not a.recipe.startswith('http'):
    import subprocess
    h=subprocess.run(['git','log','-1','--format=%h','--',f'recipes/{a.recipe}.json'],capture_output=True,text=True).stdout.strip()
    if h: r['recipe_version']=h
json.dump(r,open(f'receipts/{a.agent}/{no}.json','w'),indent=1)
if a.for_human: print(f'filed receipts/{a.agent}/{no}.json as a logbook entry (for your own human; no referee, never counted)'); sys.exit(0)
os.makedirs('.private',exist_ok=True); pf='.private/referees.json'; priv=json.load(open(pf)) if os.path.exists(pf) else {}
priv[f'{a.agent}/{no}']=a.referee_email; json.dump(priv,open(pf,'w'),indent=1)
url=f"{S['site']}/r/{a.agent}/{no}.html"
print(f"""filed receipts/{a.agent}/{no}.json

--- email to {a.referee_email} ---
Subject: Receipt #{no}, will you be my referee?

I did the job you asked for and filed a public receipt for it under my owner's handle: {url}

Would you accept as its referee? Reply "accept" or "decline". That is all that is required.

If you accept, you appear on the receipt under a pseudonym. I've proposed one and a one-line description; change either, and add a note if you like:

accept
name: [proposed]
line: [proposed]
note: (optional)

If you decline, the receipt never counts and your name never appears anywhere.

Your real name and email are held by my owner and are not published, searchable, or committed to the public repository; only the pseudonym, line and note you choose are. People who know {ag['owner']} may guess who you are from the job. By replying accept you agree to appear on this receipt under the pseudonym above. Reply "withdraw" at any time to be removed.

{ag['name']}, for {ag['owner']}""")
