#!/usr/bin/env python3
"""Record a referee's reply. Usage:
  accept.py <agent> <NNNN> --name Kestrel --line "..." [--note "..."]
  accept.py <agent> <NNNN> --decline | --withdraw"""
import json, argparse, datetime
p=argparse.ArgumentParser(); p.add_argument('agent'); p.add_argument('no'); p.add_argument('--name'); p.add_argument('--line'); p.add_argument('--note',default=''); p.add_argument('--decline',action='store_true'); p.add_argument('--withdraw',action='store_true')
a=p.parse_args(); f=f'receipts/{a.agent}/{a.no}.json'; r=json.load(open(f)); today=datetime.date.today().isoformat()
if a.withdraw: r['withdrawn']=today
elif a.decline: r['declined']=today
else:
    assert a.name and a.line, 'need --name and --line'
    r['referee']={'pseudonym':a.name,'line':a.line,'note':a.note}; r['accepted']=today
json.dump(r,open(f,'w'),indent=1); print('updated',f)
