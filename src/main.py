#!/usr/bin/env python3

import argparse

from pathlib import Path
from classes import CutsceneImport


def main():
    parser = argparse.ArgumentParser(description="prints stats for oot cutscenes")
    parser.add_argument("--decomp", "-d", dest="decomp_path", help="path to decomp root", default="../hackeroot")
    parser.add_argument("--version", "-v", dest="version", help="oot version to analyse", default="gc-eu-mq-dbg")
    args = parser.parse_args()

    is_mm = True

    if is_mm:
        importer = CutsceneImport(Path("../mm").resolve() / f"extracted/n64-us/assets/scenes", args.version, True)
    else:
        importer = CutsceneImport(Path(args.decomp_path).resolve() / "mod_assets/scenes", args.version, False)

    cs_list = importer.getCutsceneList()

    if len(cs_list) == 0:
        raise ValueError("ERROR: No cutscenes found!")

    for cutscene in cs_list:
        for sceneList in cutscene.creditsSceneList:
            for entry in sceneList.entries:
                print(cutscene.name, entry.type)


if __name__ == "__main__":
    main()
