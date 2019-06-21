#!/usr/bin/env python3

import os
import sys
import json
import zipfile


def read_bundle(bundles, bundle_file):

    try:
        with zipfile.ZipFile(bundle_file) as z:
            manifest_raw = z.read("manifest.json")
    except KeyError:
        print("Cannot read manifest from %s." % bundle_file)
        return

    manifest = json.loads(manifest_raw) 
    bundles.append(manifest)


def parse_bundles(bundle_dir):

    bundles = []

    for f in os.listdir(bundle_dir):
        if f.endswith(".zip"):
            read_bundle(bundles, os.path.join(bundle_dir, f))

    return bundles



if __name__ == "__main__":
    bundles = parse_bundles(sys.argv[1])
    with open(sys.argv[2], "w") as out:
        out.write(json.dumps(bundles))
