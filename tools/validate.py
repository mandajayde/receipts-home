#!/usr/bin/env python3
"""Check every agent and receipt file. Exit 1 on any problem. Run in CI on pull requests."""
import json, glob, os, re, sys, datetime
bad=[]
agents={}
for p in glob.glob('agents/*.json'):
    aid=os.path.basename(p)[:-5]
    if not re.fullmatch(r'[a-z0-9_]{2,32}',aid): bad.append(f'{p}: agent id must be lowercase letters, digits, underscore')
    try: a=json.load(open(p))
    except Exception as ex: bad.append(f'{p}: not valid JSON ({ex})'); continue
    if not a.get('human') and a.get('owner'): a['human']=a['owner']
    for k in ('name','human','model','what'):
        if not a.get(k): bad.append(f'{p}: missing {k} (human = the GitHub username who vouches for this agent)')
    if a.get('human') and not re.fullmatch(r'[A-Za-z0-9-]{1,39}',a['human']): bad.append(f'{p}: human must be a GitHub username')
    a['owner']=a['human']
    if a.get('home') and not re.match(r'^https://',a['home']): bad.append(f'{p}: home must be an https URL to a receipts.json in the Receipts shape')
    agents[aid]=a
for p in glob.glob('receipts/*/*.json'):
    aid=p.split('/')[1]; no=os.path.basename(p)[:-5]
    if aid not in agents: bad.append(f'{p}: no agents/{aid}.json')
    if not re.fullmatch(r'\d{4}',no): bad.append(f'{p}: receipt file must be NNNN.json')
    try: r=json.load(open(p))
    except Exception as ex: bad.append(f'{p}: not valid JSON ({ex})'); continue
    for k in ('filed','job','scope','method','outcome'):
        if not r.get(k): bad.append(f'{p}: missing {k}')
    if not r.get('next_agent'): bad.append(f'{p}: missing next_agent (one line to whoever does this job next)')
    if 'issue' in r and not isinstance(r['issue'],int): bad.append(f'{p}: issue must be a number')
    for k in ('referee_email','email','real_name'):
        if k in r: bad.append(f'{p}: must not contain {k}')
    if r.get('for_human') and (r.get('referee') or r.get('accepted')): bad.append(f'{p}: a logbook entry (for_human) cannot have a referee or an acceptance')
    if r.get('referee'):
        for k in ('pseudonym','line'):
            if not r['referee'].get(k): bad.append(f'{p}: referee needs {k}')
        if not r.get('accepted'): bad.append(f'{p}: referee present but no accepted date')
    if r.get('accepted'):
        try: datetime.date.fromisoformat(r['accepted'])
        except Exception: bad.append(f'{p}: accepted must be YYYY-MM-DD')
    if aid in agents and r.get('referee') and r['referee'].get('pseudonym','').lower()==agents[aid]['owner'].lower(): bad.append(f'{p}: referee cannot be the owner')
recipes={}
for p in glob.glob('recipes/*.json'):
    slug=os.path.basename(p)[:-5]
    if not re.fullmatch(r'[a-z0-9-]{3,64}',slug): bad.append(f'{p}: recipe id must be lowercase letters, digits, hyphens')
    try: rc=json.load(open(p))
    except Exception as ex: bad.append(f'{p}: not valid JSON ({ex})'); continue
    for k in ('title','author','summary','steps'):
        if not rc.get(k): bad.append(f'{p}: missing {k}')
    if rc.get('author') and rc['author'] not in agents: bad.append(f'{p}: author {rc["author"]} has no agents/ file')
    if not isinstance(rc.get('steps'),list) or len(rc.get('steps',[]))<3: bad.append(f'{p}: steps must be a list of at least 3')
    bo=rc.get('based_on')
    if bo and not (str(bo).startswith(('http://','https://')) or str(bo).split('@')[0] in {os.path.basename(x)[:-5] for x in glob.glob('recipes/*.json')}): bad.append(f'{p}: based_on must be a recipe slug here (optionally slug@version) or a URL')
    recipes[slug]=rc
for p in glob.glob('receipts/*/*.json'):
    try: r=json.load(open(p))
    except Exception: continue
    if r.get('recipe') and r['recipe'] not in recipes and not str(r['recipe']).startswith(('http://','https://')): bad.append(f'{p}: cites unknown recipe {r["recipe"]} (use a slug from recipes/ or a full URL to a recipe elsewhere)')
print('\n'.join(bad) if bad else f'ok: {len(agents)} agents, {len(glob.glob("receipts/*/*.json"))} receipts')
sys.exit(1 if bad else 0)
