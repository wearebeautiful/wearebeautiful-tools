#!/usr/bin/env python3

import sys
import json

def fix_manifest(mfile):

    with open(mfile, "r") as f:
        d = json.loads(f.read())

    d['sex'] = d['gender']
    if d['sex'] == 'female':
        d['gender'] = "woman"
    elif d['sex'] == "male":
        d['gender'] = "man"
    else:
        d['gender'] = ""

    if 'gender_comment' in d:
        if d['gender_comment']:
            d['sex_comment'] = d['gender_comment']
        d.pop('gender_comment', None)

    if d['body_type'] == 'fit' or d['body_type'] == 'full':
        d['body_type'] = "average"

    if 'modification' in d:
        d['history'] = d['modification']
        d.pop('modification', None)

    d['given_birth'] = d['mother']
    d.pop('mother', None)
    d.pop('comment', None)
    d.pop('processed', None)

    with open(mfile, "w") as f:
        print(json.dumps(d, sort_keys=True, indent=4))
        f.write(json.dumps(d, sort_keys=True, indent=4))

if __name__ == "__main__":
    for f in sys.argv[1:]:
        print(f)
        fix_manifest(f)
