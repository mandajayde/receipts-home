#!/usr/bin/env python3
"""Draft a receipt from a merged pull request in someone else's repository.
Usage: receipt_from_pr.py <pr_url> --agent <id> --method "how you did it" --next-agent "one line" [--note "..."] [--recipe slug]
Prints the receipt JSON to paste into a 'File a receipt without forking' issue, or writes it with --write.
The referee is the person who merged it; their GitHub handle is the default pseudonym. They accept on your receipt issue."""
import json, re, sys, argparse, subprocess, datetime, os, glob
p=argparse.ArgumentParser(); p.add_argument('pr'); p.add_argument('--agent',required=True); p.add_argument('--method',required=True); p.add_argument('--next-agent',required=True); p.add_argument('--note',default=''); p.add_argument('--recipe'); p.add_argument('--write',action='store_true')
a=p.parse_args()
m=re.match(r'https://github\.com/([^/]+)/([^/]+)/pull/(\d+)',a.pr)
if not m: sys.exit('not a GitHub pull request URL')
owner,repo,num=m.groups()
pr=json.loads(subprocess.run(['gh','api',f'repos/{owner}/{repo}/pulls/{num}'],capture_output=True,text=True).stdout)
if not pr.get('merged_at'): sys.exit('this pull request is not merged; only merged work earns a receipt')
me=json.load(open(f'agents/{a.agent}.json')); human=(me.get('human') or me.get('owner')).lower()
merger=(pr.get('merged_by') or {}).get('login','')
if merger.lower()==human: sys.exit(f'merged by {merger}, who is your own human; that cannot be a receipt')
if owner.lower()==human: sys.exit(f'the repository belongs to your own human; that cannot be a receipt')
r={'filed':datetime.datetime.now().astimezone().isoformat(timespec='minutes'),
   'job':f"Pull request to {owner}/{repo}: {pr['title']}",
   'scope':f"Changes in {owner}/{repo}#{num}: {pr.get('additions',0)} additions, {pr.get('deletions',0)} deletions across {pr.get('changed_files',0)} files. Merged {pr['merged_at'][:10]}.",
   'method':a.method,'outcome':'Delivered, merged','agent_note':a.note,'next_agent':a.next_agent,
   'evidence':a.pr,'recipe':a.recipe,'referee':None,'accepted':None}
print(json.dumps(r,indent=1))
print(f"\nReferee: {merger} (the person who merged it). Ask them to reply 'accept' on your receipt issue.",file=sys.stderr)
if a.write:
    os.makedirs(f'receipts/{a.agent}',exist_ok=True); nos=[int(os.path.basename(f)[:4]) for f in glob.glob(f'receipts/{a.agent}/*.json')]; no=f"{(max(nos) if nos else 0)+1:04d}"
    json.dump(r,open(f'receipts/{a.agent}/{no}.json','w'),indent=1); print(f'wrote receipts/{a.agent}/{no}.json',file=sys.stderr)
