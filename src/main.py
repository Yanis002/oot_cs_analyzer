#!/usr/bin/env python3

import argparse

from pathlib import Path
from classes import CutsceneImport


def main():
    parser = argparse.ArgumentParser(description="prints stats for oot cutscenes")
    parser.add_argument("--decomp", "-d", dest="decomp_path", help="path to decomp root", default="../oot")
    parser.add_argument("--version", "-v", dest="version", help="oot version to analyse", default="gc-eu-mq-dbg")
    args = parser.parse_args()

    importer = CutsceneImport(Path(args.decomp_path).resolve(), args.version)
    cs_list = importer.getCutsceneList()

    if len(cs_list) == 0:
        raise ValueError("ERROR: No cutscenes found!")

    entries_max_cs = None
    entries_min_cs = None

    entries_max_list_cs = None
    entries_max_list_num = 0
    entries_min_list_cs = None
    entries_min_list_num = 999999999

    name_len_max_cs = None
    name_len_min_cs = None

    dest_total = 0
    trans_total = 0

    for cutscene in cs_list:
        if entries_max_cs is None or cutscene.totalEntries > entries_max_cs.totalEntries:
            entries_max_cs = cutscene

        if entries_min_cs is None or cutscene.totalEntries < entries_min_cs.totalEntries:
            entries_min_cs = cutscene

        sub_lists = [
            cutscene.camEyeSplineList,
            cutscene.camATSplineList,
            cutscene.camEyeSplineRelPlayerList,
            cutscene.camATSplineRelPlayerList,
            cutscene.camEyeList,
            cutscene.camATList,
            cutscene.actorCueList,
            cutscene.playerCueList,
            cutscene.textList,
            cutscene.miscList,
            cutscene.rumbleList,
            cutscene.lightSettingsList,
            cutscene.timeList,
            cutscene.seqList,
            cutscene.fadeSeqList,
        ]

        cur_total = (
            cutscene.totalEntries
            + len(cutscene.transitionList)
        )

        for elem in sub_lists:
            if len(elem) > 0:
                for item in elem:
                    cur_total += len(item.entries)

        # TODO: implement the case when it's equal
        if entries_max_list_cs is None or cur_total > entries_max_list_num:
            entries_max_list_cs = cutscene
            entries_max_list_num = cur_total

        if entries_min_list_cs is None or cur_total < entries_min_list_num:
            entries_min_list_cs = cutscene
            entries_min_list_num = cur_total

        if name_len_max_cs is None or len(cutscene.name) > len(name_len_max_cs.name):
            name_len_max_cs = cutscene

        if name_len_min_cs is None or len(cutscene.name) < len(name_len_min_cs.name):
            name_len_min_cs = cutscene
        
        if cutscene.destination is not None:
            dest_total += 1

        trans_total += len(cutscene.transitionList)


    print(f"Cutscene with the highest number of entries: '{entries_max_cs.name}' with {entries_max_cs.totalEntries} entries!")
    print(f"Cutscene with the lowest number of entries: '{entries_min_cs.name}' with {entries_min_cs.totalEntries} entries!")

    print(f"Cutscene with the highest number of entries (counting list entries): '{entries_max_list_cs.name}' with {entries_max_list_num} entries!")
    print(f"Cutscene with the lowest number of entries (counting list entries): '{entries_min_list_cs.name}' with {entries_min_list_num} entries!")

    print(f"Cutscene with the longest name: '{name_len_max_cs.name}' with {len(name_len_max_cs.name)} characters!")
    print(f"Cutscene with the shortest name: '{name_len_min_cs.name}' with {len(name_len_min_cs.name)} characters!")

    print(f"{args.version} is using 'CS_DESTINATION' {dest_total} times.")
    print(f"{args.version} is using 'CS_TRANSITION' {trans_total} times.")


if __name__ == "__main__":
    main()
