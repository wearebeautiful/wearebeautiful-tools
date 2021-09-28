#!/usr/bin/env python3

import sys
import os
import json

for file in sys.argv[1:]:
    with open(file, "r") as f:
        d = json.loads(f.read())
        d['released'] = "2020-09-19"
    with open(file, "w") as f:
        f.write(json.dumps(d, indent=4, sort_keys=True) + "\n")
