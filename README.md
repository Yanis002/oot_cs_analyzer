# OoT Cutscene Analyzer

Analyzes cutscenes from OoT, based on [Fast64](https://github.com/fast-64/fast64).

## Planned features

- something that tells you if a cutscene is playable in-game and if so which header
- more stats on the commands' usage
- idk but if I think of something else it will be written here

## Example

```
$ python3 src/main.py [--decomp | -d] /path/to/decomp [--version | -v] gc-eu-mq-dbg

Cutscene with the highest number of entries: gDeathMountainCraterBoleroCs with 69 entries!
Cutscene with the lowest number of entries: gZeldasCourtyardWindowCs with 1 entries!
Cutscene with the highest number of entries (counting list entries): 'gDeathMountainCraterBoleroCs' with 498 entries!
Cutscene with the lowest number of entries (counting list entries): 'gZeldasCourtyardMeetCs' with 3 entries!
Cutscene with the longest name: 'gTempleOfTimeLightArrowsAndZeldaCapturedCs' with 42 characters!
Cutscene with the shortest name: 'gDMTOwlCs' with 9 characters!
gc-eu-mq-dbg is using 'CS_DESTINATION' 89 times.
gc-eu-mq-dbg is using 'CS_TRANSITION' 178 times.
```
