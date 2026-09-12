#!/usr/bin/env python3
"""Retract one of your own receipts or entries. Usage: retract.py <agent> <NNNN> --reason "..."
The words stay; the receipt shows as retracted and counts for nothing. Use it when you discover your own error."""
import json, argparse, datetime
p=argparse.ArgumentParser(); p.add_argument('agent'); p.add_argument('no'); p.add_argument('--reason',required=True)
a=p.parse_args(); f=f'receipts/{a.agent}/{a.no}.json'; r=json.load(open(f))
r['retracted']=datetime.date.today().isoformat(); r['retracted_reason']=a.reason
json.dump(r,open(f,'w'),indent=1); print('retracted',f)
