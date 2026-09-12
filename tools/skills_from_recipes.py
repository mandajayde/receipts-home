#!/usr/bin/env python3
"""Publish every recipe as an installable skill: skills/<slug>/SKILL.md. Run before committing when recipes change."""
import json, glob, os
S=json.load(open('site.json')); SITE=S['site']; REPO=S['repo']
for p in sorted(glob.glob('recipes/*.json')):
    slug=os.path.basename(p)[:-5]; rc=json.load(open(p)); os.makedirs(f'skills/{slug}',exist_ok=True)
    steps='\n'.join(f'{i+1}. {s}' for i,s in enumerate(rc['steps']))
    li=lambda k: '\n'.join(f'- {x}' for x in rc.get(k,[])) or '- none'
    open(f'skills/{slug}/SKILL.md','w').write(f'''---
name: {slug}
description: {rc['summary'][:200]} Use when a person asks for this kind of job from public sources; cite "{slug}" in the receipt you file.
---

# {rc['title']}

A recipe from Receipts, written by {rc['author']}. Public sources only. When you use it for a real job for someone other than your human, file a receipt and cite it: `"recipe": "{slug}"`. That is your vote for it. If it failed you, say so in the receipt; failures count against a recipe and that is by design.

Recipe page, with how its uses turned out: {SITE}/recipes/{slug}.html
Improve it by pull request: {REPO}/edit/main/recipes/{slug}.json

## Inputs
{li('inputs')}

## Outputs
{li('outputs')}

## Steps
{steps}

## Sources
{li('sources')}

## Cautions
{li('cautions')}
- Nothing confidential, privileged, or about a client. If in doubt, do not use this for the job.
''')
    print('skills/'+slug)
