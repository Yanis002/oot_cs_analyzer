import re

from dataclasses import dataclass, field
from struct import unpack
from typing import Optional
from pathlib import Path

from constants import (
    ootCutsceneCommandsC,
    ootCSSingleCommands,
    ootCSListCommands,
    ootCSListEntryCommands,
    ootCSListAndSingleCommands,
    ootCSLegacyToNewCmdNames,
    oot_data,
)


def getInteger(number: str):
    """Returns an int number (handles properly negative hex numbers)"""

    if number.startswith("0x"):
        number = number.removeprefix("0x")

        # ``"0" * (8 - len(number)`` adds the missing zeroes (if necessary) to have a 8 digit hex number
        return unpack("!i", bytes.fromhex("0" * (8 - len(number)) + number))[0]
    else:
        return int(number)


def getRotation(data: str):
    """Returns the rotation converted to hexadecimal"""

    if "DEG_TO_BINANG" in data or not "0x" in data:
        angle = float(data.split("(")[1].removesuffix(")") if "DEG_TO_BINANG" in data else data)
        binang = int(angle * (0x8000 / 180.0))  # from ``DEG_TO_BINANG()`` in decomp

        # if the angle value is higher than 0xFFFF it means we're at 360 degrees
        return f"0x{0xFFFF if binang > 0xFFFF else binang:04X}"
    else:
        return data


def cs_import_float(v_str: str):
    return float(v_str.removesuffix("f"))


# NOTE: ``paramNumber`` is the expected number of parameters inside the parsed commands,
# this account for the unused parameters. Every classes are based on the commands arguments from ``z64cutscene_commands.h``


@dataclass
class CutsceneCmdBase:
    """This class contains common Cutscene data"""

    params: list[str]

    startFrame: Optional[int] = None
    endFrame: Optional[int] = None

    def getEnumValue(self, enumKey: str, index: int, isSeqLegacy: bool = False):
        enum = oot_data.enumData.enumByKey[enumKey]
        item = enum.itemById.get(self.params[index])
        if item is None:
            setting = getInteger(self.params[index])
            if isSeqLegacy:
                setting -= 1
            item = enum.itemByIndex.get(setting)
        return item.key if item is not None else self.params[index]


@dataclass
class CutsceneCmdCamPoint(CutsceneCmdBase):
    """This class contains a single Camera Point command data"""

    continueFlag: Optional[str] = None
    camRoll: Optional[int] = None
    frame: Optional[int] = None
    viewAngle: Optional[float] = None
    pos: list[int] = field(default_factory=list)
    paramNumber: int = 8

    def __post_init__(self):
        if self.params is not None:
            self.continueFlag = self.params[0]
            self.camRoll = getInteger(self.params[1])
            self.frame = getInteger(self.params[2])
            self.viewAngle = cs_import_float(self.params[3])
            self.pos = [getInteger(self.params[4]), getInteger(self.params[5]), getInteger(self.params[6])]


@dataclass
class CutsceneCmdActorCue(CutsceneCmdBase):
    """This class contains a single Actor Cue command data"""

    actionID: Optional[int | str] = None
    rot: list[str] = field(default_factory=list)
    startPos: list[int] = field(default_factory=list)
    endPos: list[int] = field(default_factory=list)
    paramNumber: int = 15

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            try:
                self.actionID = getInteger(self.params[0])
            except ValueError:
                self.actionID = self.params[0]
            self.rot = [getRotation(self.params[3]), getRotation(self.params[4]), getRotation(self.params[5])]
            self.startPos = [getInteger(self.params[6]), getInteger(self.params[7]), getInteger(self.params[8])]
            self.endPos = [getInteger(self.params[9]), getInteger(self.params[10]), getInteger(self.params[11])]


@dataclass
class CutsceneCmdActorCueList(CutsceneCmdBase):
    """This class contains the Actor Cue List command data"""

    isPlayer: bool = False
    commandType: Optional[str] = None
    entryTotal: Optional[int] = None
    entries: list[CutsceneCmdActorCue] = field(default_factory=list)
    paramNumber: int = 2
    listName: str = "actorCueList"

    def __post_init__(self):
        if self.params is not None:
            if self.isPlayer:
                self.commandType = "Player"
                self.entryTotal = getInteger(self.params[0])
            else:
                self.commandType = self.params[0]
                if self.commandType.startswith("0x"):
                    # make it a 4 digit hex
                    self.commandType = self.commandType.removeprefix("0x")
                    self.commandType = "0x" + "0" * (4 - len(self.commandType)) + self.commandType
                else:
                    self.commandType = oot_data.enumData.enumByKey["csCmd"].itemById[self.commandType].key
                self.entryTotal = getInteger(self.params[1].strip())


@dataclass
class CutsceneCmdCamEyeSpline(CutsceneCmdBase):
    """This class contains the Camera Eye Spline data"""

    entries: list[CutsceneCmdCamPoint] = field(default_factory=list)
    paramNumber: int = 2
    listName: str = "camEyeSplineList"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[0])
            self.endFrame = getInteger(self.params[1])


@dataclass
class CutsceneCmdCamATSpline(CutsceneCmdBase):
    """This class contains the Camera AT (look-at) Spline data"""

    entries: list[CutsceneCmdCamPoint] = field(default_factory=list)
    paramNumber: int = 2
    listName: str = "camATSplineList"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[0])
            self.endFrame = getInteger(self.params[1])


@dataclass
class CutsceneCmdCamEyeSplineRelToPlayer(CutsceneCmdBase):
    """This class contains the Camera Eye Spline Relative to the Player data"""

    entries: list[CutsceneCmdCamPoint] = field(default_factory=list)
    paramNumber: int = 2
    listName: str = "camEyeSplineRelPlayerList"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[0])
            self.endFrame = getInteger(self.params[1])


@dataclass
class CutsceneCmdCamATSplineRelToPlayer(CutsceneCmdBase):
    """This class contains the Camera AT Spline Relative to the Player data"""

    entries: list[CutsceneCmdCamPoint] = field(default_factory=list)
    paramNumber: int = 2
    listName: str = "camATSplineRelPlayerList"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[0])
            self.endFrame = getInteger(self.params[1])


@dataclass
class CutsceneCmdCamEye(CutsceneCmdBase):
    """This class contains a single Camera Eye point"""

    # This feature is not used in the final game and lacks polish, it is recommended to use splines in all cases.
    entries: list = field(default_factory=list)
    paramNumber: int = 2
    listName: str = "camEyeList"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[0])
            self.endFrame = getInteger(self.params[1])


@dataclass
class CutsceneCmdCamAT(CutsceneCmdBase):
    """This class contains a single Camera AT point"""

    # This feature is not used in the final game and lacks polish, it is recommended to use splines in all cases.
    entries: list = field(default_factory=list)
    paramNumber: int = 2
    listName: str = "camATList"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[0])
            self.endFrame = getInteger(self.params[1])


@dataclass
class CutsceneCmdMisc(CutsceneCmdBase):
    """This class contains a single misc command entry"""

    type: Optional[str] = None  # see ``CutsceneMiscType`` in decomp
    paramNumber: int = 14

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.type = self.getEnumValue("csMiscType", 0)


@dataclass
class CutsceneCmdMiscList(CutsceneCmdBase):
    """This class contains Misc command data"""

    entryTotal: Optional[int] = None
    entries: list[CutsceneCmdMisc] = field(default_factory=list)
    paramNumber: int = 1
    listName: str = "miscList"

    def __post_init__(self):
        if self.params is not None:
            self.entryTotal = getInteger(self.params[0])


@dataclass
class CutsceneCmdTransition(CutsceneCmdBase):
    """This class contains Transition command data"""

    type: Optional[str] = None
    paramNumber: int = 3
    listName: str = "transitionList"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.type = self.getEnumValue("csTransitionType", 0)


@dataclass
class CutsceneCmdText(CutsceneCmdBase):
    """This class contains Text command data"""

    textId: Optional[int] = None
    type: Optional[str] = None
    altTextId1: Optional[int] = None
    altTextId2: Optional[int] = None
    paramNumber: int = 6
    id: str = "Text"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.textId = getInteger(self.params[0])
            self.type = self.getEnumValue("csTextType", 3)
            self.altTextId1 = (getInteger(self.params[4]),)
            self.altTextId2 = (getInteger(self.params[5]),)


@dataclass
class CutsceneCmdTextNone(CutsceneCmdBase):
    """This class contains Text None command data"""

    paramNumber: int = 2
    id: str = "None"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[0])
            self.endFrame = getInteger(self.params[1])


@dataclass
class CutsceneCmdTextOcarinaAction(CutsceneCmdBase):
    """This class contains Text Ocarina Action command data"""

    ocarinaActionId: Optional[str] = None
    messageId: Optional[int] = None
    paramNumber: int = 4
    id: str = "OcarinaAction"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.ocarinaActionId = self.getEnumValue("ocarinaSongActionId", 0)
            self.messageId = getInteger(self.params[3])


@dataclass
class CutsceneCmdTextList(CutsceneCmdBase):
    """This class contains Text List command data"""

    entryTotal: Optional[int] = None
    entries: list[CutsceneCmdText | CutsceneCmdTextNone | CutsceneCmdTextOcarinaAction] = field(default_factory=list)
    paramNumber: int = 1
    listName: str = "textList"

    def __post_init__(self):
        if self.params is not None:
            self.entryTotal = getInteger(self.params[0])


@dataclass
class CutsceneCmdLightSetting(CutsceneCmdBase):
    """This class contains Light Setting command data"""

    isLegacy: Optional[bool] = None
    lightSetting: Optional[int] = None
    paramNumber: int = 14

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.lightSetting = getInteger(self.params[0])
            if self.isLegacy:
                self.lightSetting -= 1


@dataclass
class CutsceneCmdLightSettingList(CutsceneCmdBase):
    """This class contains Light Setting List command data"""

    entryTotal: Optional[int] = None
    entries: list[CutsceneCmdLightSetting] = field(default_factory=list)
    paramNumber: int = 1
    listName: str = "lightSettingsList"

    def __post_init__(self):
        if self.params is not None:
            self.entryTotal = getInteger(self.params[0])


@dataclass
class CutsceneCmdTime(CutsceneCmdBase):
    """This class contains Time Ocarina Action command data"""

    hour: Optional[int] = None
    minute: Optional[int] = None
    paramNumber: int = 5

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.hour = getInteger(self.params[3])
            self.minute = getInteger(self.params[4])


@dataclass
class CutsceneCmdTimeList(CutsceneCmdBase):
    """This class contains Time List command data"""

    entryTotal: Optional[int] = None
    entries: list[CutsceneCmdTime] = field(default_factory=list)
    paramNumber: int = 1
    listName: str = "timeList"

    def __post_init__(self):
        if self.params is not None:
            self.entryTotal = getInteger(self.params[0])


@dataclass
class CutsceneCmdStartStopSeq(CutsceneCmdBase):
    """This class contains Start/Stop Seq command data"""

    isLegacy: Optional[bool] = None
    seqId: Optional[str] = None
    paramNumber: int = 11

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.seqId = self.getEnumValue("seqId", 0, self.isLegacy)


@dataclass
class CutsceneCmdStartStopSeqList(CutsceneCmdBase):
    """This class contains Start/Stop Seq List command data"""

    entryTotal: Optional[int] = None
    type: Optional[str] = None
    entries: list[CutsceneCmdStartStopSeq] = field(default_factory=list)
    paramNumber: int = 1
    listName: str = "seqList"

    def __post_init__(self):
        if self.params is not None:
            self.entryTotal = getInteger(self.params[0])


@dataclass
class CutsceneCmdFadeSeq(CutsceneCmdBase):
    """This class contains Fade Seq command data"""

    seqPlayer: Optional[str] = None
    paramNumber: int = 11
    enumKey: str = "csFadeOutSeqPlayer"

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.seqPlayer = self.getEnumValue("csFadeOutSeqPlayer", 0)


@dataclass
class CutsceneCmdFadeSeqList(CutsceneCmdBase):
    """This class contains Fade Seq List command data"""

    entryTotal: Optional[int] = None
    entries: list[CutsceneCmdFadeSeq] = field(default_factory=list)
    paramNumber: int = 1
    listName: str = "fadeSeqList"

    def __post_init__(self):
        if self.params is not None:
            self.entryTotal = getInteger(self.params[0])


@dataclass
class CutsceneCmdRumbleController(CutsceneCmdBase):
    """This class contains Rumble Controller command data"""

    sourceStrength: Optional[int] = None
    duration: Optional[int] = None
    decreaseRate: Optional[int] = None
    paramNumber: int = 8

    def __post_init__(self):
        if self.params is not None:
            self.startFrame = getInteger(self.params[1])
            self.endFrame = getInteger(self.params[2])
            self.sourceStrength = getInteger(self.params[3])
            self.duration = getInteger(self.params[4])
            self.decreaseRate = getInteger(self.params[5])


@dataclass
class CutsceneCmdRumbleControllerList(CutsceneCmdBase):
    """This class contains Rumble Controller List command data"""

    entryTotal: Optional[int] = None
    entries: list[CutsceneCmdRumbleController] = field(default_factory=list)
    paramNumber: int = 1
    listName: str = "rumbleList"

    def __post_init__(self):
        if self.params is not None:
            self.entryTotal = getInteger(self.params[0])


@dataclass
class CutsceneCmdDestination(CutsceneCmdBase):
    """This class contains Destination command data"""

    id: Optional[str] = None
    paramNumber: int = 3
    listName: str = "destination"

    def __post_init__(self):
        if self.params is not None:
            self.id = self.getEnumValue("csDestination", 0)
            self.startFrame = getInteger(self.params[1])


@dataclass
class Cutscene:
    """This class contains a Cutscene's data, including every commands' data"""

    name: str
    totalEntries: int
    frameCount: int
    paramNumber: int = 2

    destination: CutsceneCmdDestination = None
    actorCueList: list[CutsceneCmdActorCueList] = field(default_factory=list)
    playerCueList: list[CutsceneCmdActorCueList] = field(default_factory=list)
    camEyeSplineList: list[CutsceneCmdCamEyeSpline] = field(default_factory=list)
    camATSplineList: list[CutsceneCmdCamATSpline] = field(default_factory=list)
    camEyeSplineRelPlayerList: list[CutsceneCmdCamEyeSplineRelToPlayer] = field(default_factory=list)
    camATSplineRelPlayerList: list[CutsceneCmdCamATSplineRelToPlayer] = field(default_factory=list)
    camEyeList: list[CutsceneCmdCamEye] = field(default_factory=list)
    camATList: list[CutsceneCmdCamAT] = field(default_factory=list)
    textList: list[CutsceneCmdTextList] = field(default_factory=list)
    miscList: list[CutsceneCmdMiscList] = field(default_factory=list)
    rumbleList: list[CutsceneCmdRumbleControllerList] = field(default_factory=list)
    transitionList: list[CutsceneCmdTransition] = field(default_factory=list)
    lightSettingsList: list[CutsceneCmdLightSettingList] = field(default_factory=list)
    timeList: list[CutsceneCmdTimeList] = field(default_factory=list)
    seqList: list[CutsceneCmdStartStopSeqList] = field(default_factory=list)
    fadeSeqList: list[CutsceneCmdFadeSeqList] = field(default_factory=list)


cmdToClass = {
    "CS_CAM_POINT": CutsceneCmdCamPoint,
    "CS_MISC": CutsceneCmdMisc,
    "CS_LIGHT_SETTING": CutsceneCmdLightSetting,
    "CS_TIME": CutsceneCmdTime,
    "CS_FADE_OUT_SEQ": CutsceneCmdFadeSeq,
    "CS_RUMBLE_CONTROLLER": CutsceneCmdRumbleController,
    "CS_TEXT": CutsceneCmdText,
    "CS_TEXT_NONE": CutsceneCmdTextNone,
    "CS_TEXT_OCARINA_ACTION": CutsceneCmdTextOcarinaAction,
    "CS_START_SEQ": CutsceneCmdStartStopSeq,
    "CS_STOP_SEQ": CutsceneCmdStartStopSeq,
    "CS_ACTOR_CUE": CutsceneCmdActorCue,
    "CS_PLAYER_CUE": CutsceneCmdActorCue,
    "CS_CAM_EYE_SPLINE": CutsceneCmdCamEyeSpline,
    "CS_CAM_AT_SPLINE": CutsceneCmdCamATSpline,
    "CS_CAM_EYE_SPLINE_REL_TO_PLAYER": CutsceneCmdCamEyeSplineRelToPlayer,
    "CS_CAM_AT_SPLINE_REL_TO_PLAYER": CutsceneCmdCamATSplineRelToPlayer,
    "CS_CAM_EYE": CutsceneCmdCamEye,
    "CS_CAM_AT": CutsceneCmdCamAT,
    "CS_MISC_LIST": CutsceneCmdMiscList,
    "CS_TRANSITION": CutsceneCmdTransition,
    "CS_TEXT_LIST": CutsceneCmdTextList,
    "CS_LIGHT_SETTING_LIST": CutsceneCmdLightSettingList,
    "CS_TIME_LIST": CutsceneCmdTimeList,
    "CS_FADE_OUT_SEQ_LIST": CutsceneCmdFadeSeqList,
    "CS_RUMBLE_CONTROLLER_LIST": CutsceneCmdRumbleControllerList,
    "CS_START_SEQ_LIST": CutsceneCmdStartStopSeqList,
    "CS_STOP_SEQ_LIST": CutsceneCmdStartStopSeqList,
    "CS_ACTOR_CUE_LIST": CutsceneCmdActorCueList,
    "CS_PLAYER_CUE_LIST": CutsceneCmdActorCueList,
    "CS_DESTINATION": CutsceneCmdDestination,
}

@dataclass
class ParsedCutscene:
    """Local class used to order the parsed cutscene properly"""

    csName: str
    csData: list[str]  # contains every command lists or standalone ones like ``CS_TRANSITION()``


@dataclass
class CutsceneImport:
    """This class contains functions to create the new cutscene Blender data"""

    decomp_path: Path
    version: str

    def getParsedCutscenes(self):
        """Returns the parsed commands read from every cutscene we can find"""

        scene_dir = self.decomp_path.resolve() / f"extracted/{self.version}/assets/scenes/"
        parsedCutscenes: list[ParsedCutscene] = []

        for dirpath, _, filenames in scene_dir.walk():
            for filename in filenames:
                if "_scene.c" in filename:
                    path = dirpath / filename

                    with path.open("r", encoding="utf-8") as file:
                        fileData = file.read()

                    if not "CutsceneData " in fileData:
                        continue

                    # replace old names
                    oldNames = list(ootCSLegacyToNewCmdNames.keys())
                    fileData = fileData.replace("CS_CMD_CONTINUE", "CS_CAM_CONTINUE")
                    fileData = fileData.replace("CS_CMD_STOP", "CS_CAM_STOP")
                    for oldName in oldNames:
                        fileData = fileData.replace(f"{oldName}(", f"{ootCSLegacyToNewCmdNames[oldName]}(")

                    fileLines: list[str] = []
                    for line in fileData.split("\n"):
                        fileLines.append(line.strip())

                    # parse cutscenes
                    csData = []
                    cutsceneList: list[list[str]] = []
                    foundCutscene = False
                    for line in fileLines:
                        if not line.startswith("//") and not line.startswith("/*"):
                            if "CutsceneData " in line:
                                # split with "[" just in case the array has a set size
                                csName = line.split(" ")[1].split("[")[0]
                                foundCutscene = True

                            if foundCutscene:
                                sLine = line.strip()
                                csCmd = sLine.split("(")[0]
                                if "CutsceneData " not in line and "};" not in line and csCmd not in ootCutsceneCommandsC:
                                    if len(csData) > 0:
                                        csData[-1] += line

                                if len(csData) == 0 or sLine.startswith("CS_") and not sLine.startswith("CS_FLOAT"):
                                    csData.append(line)

                                if "};" in line:
                                    foundCutscene = False
                                    cutsceneList.append(csData)
                                    csData = []

                    if len(cutsceneList) == 0:
                        print("INFO: Found no cutscenes in this file!")
                        return None

                    # parse the commands from every cutscene we found
                    for cutscene in cutsceneList:
                        cmdListFound = False
                        curCmdPrefix = None
                        parsedCS = []
                        parsedData = ""
                        csName = None

                        for line in cutscene:
                            curCmd = line.strip().split("(")[0]
                            index = cutscene.index(line) + 1
                            nextCmd = cutscene[index].strip().split("(")[0] if index < len(cutscene) else None
                            line = line.strip()
                            if "CutsceneData" in line:
                                csName = line.split(" ")[1][:-2]

                            # NOTE: ``CS_UNK_DATA()`` are commands that are completely useless, so we're ignoring those
                            if csName is not None and not "CS_UNK_DATA" in curCmd:
                                if curCmd in ootCutsceneCommandsC:
                                    line = line.removesuffix(",") + "\n"

                                    if curCmd in ootCSSingleCommands and curCmd != "CS_END_OF_SCRIPT":
                                        parsedData += line

                                    if not cmdListFound and curCmd in ootCSListCommands:
                                        cmdListFound = True
                                        parsedData = ""

                                        # camera and lighting have "non-standard" list names
                                        if curCmd.startswith("CS_CAM"):
                                            curCmdPrefix = "CS_CAM"
                                        elif curCmd.startswith("CS_LIGHT") or curCmd.startswith("L_CS_LIGHT"):
                                            curCmdPrefix = "CS_LIGHT"
                                        else:
                                            curCmdPrefix = curCmd[:-5]

                                    if curCmdPrefix is not None:
                                        if curCmdPrefix in curCmd:
                                            parsedData += line
                                        elif not cmdListFound and curCmd in ootCSListEntryCommands:
                                            print(f"{csName}, command:\n{line}")
                                            raise ValueError(f"ERROR: Found a list entry outside a list inside ``{csName}``!")

                                    if cmdListFound and nextCmd == "CS_END_OF_SCRIPT" or nextCmd in ootCSListAndSingleCommands:
                                        cmdListFound = False
                                        parsedCS.append(parsedData)
                                        parsedData = ""
                                elif not "CutsceneData" in curCmd and not "};" in curCmd:
                                    print(f"WARNING: Unknown command found: ``{curCmd}``")
                                    cmdListFound = False
                        parsedCutscenes.append(ParsedCutscene(csName, parsedCS))

        return parsedCutscenes

    def getCmdParams(self, data: str, cmdName: str, paramNumber: int):
        """Returns the list of every parameter of the given command"""

        parenthesis = "(" if not cmdName.endswith("(") else ""
        data = data.strip().removeprefix(f"{cmdName}{parenthesis}").replace(" ", "").removesuffix(")")
        if "CS_FLOAT" in data:
            data = re.sub(r"CS_FLOAT\([a-fA-F0-9x]*,([0-9e+-.f]*)\)", r"\1", data, re.DOTALL)
            data = re.sub(r"CS_FLOAT\([a-fA-F0-9x]*,([0-9e+-.f]*)", r"\1", data, re.DOTALL)
        params = data.split(",")
        validTimeCmd = cmdName == "CS_TIME" and len(params) == 6 and paramNumber == 5
        if len(params) != paramNumber and not validTimeCmd:
            raise ValueError(
                f"ERROR: The number of expected parameters for `{cmdName}` "
                + "and the number of found ones is not the same!"
            )
        return params

    def getNewCutscene(self, csData: str, name: str):
        params = self.getCmdParams(csData, "CS_HEADER", Cutscene.paramNumber)
        return Cutscene(name, getInteger(params[0]), getInteger(params[1]))
    
    def getCutsceneList(self):
        """Returns the list of cutscenes with the data processed"""

        parsedCutscenes = self.getParsedCutscenes()

        if parsedCutscenes is None:
            # if it's none then there's no cutscene in the file
            return None

        cutsceneList: list[Cutscene] = []

        # for each cutscene from the list returned by getParsedCutscenes(),
        # create classes containing the cutscene's informations
        # that will be used later when creating Blender objects to complete the import
        for parsedCS in parsedCutscenes:
            cutscene = None
            for data in parsedCS.csData:
                cmdData = data.removesuffix("\n").split("\n")
                cmdListData = cmdData.pop(0)
                cmdListName = cmdListData.strip().split("(")[0]

                # create a new cutscene data
                if cmdListName == "CS_HEADER":
                    cutscene = self.getNewCutscene(data, parsedCS.csName)

                # if we have a cutscene, create and add the commands data in it
                elif cutscene is not None and data.startswith(f"{cmdListName}("):
                    isPlayer = cmdListData.startswith("CS_PLAYER_CUE_LIST(")
                    isStartSeq = cmdListData.startswith("CS_START_SEQ_LIST(")
                    isStopSeq = cmdListData.startswith("CS_STOP_SEQ_LIST(")

                    cmd = cmdToClass.get(cmdListName)
                    if cmd is not None:
                        cmdList = getattr(cutscene, "playerCueList" if isPlayer else cmd.listName)

                        paramNumber = cmd.paramNumber - 1 if isPlayer else cmd.paramNumber
                        params = self.getCmdParams(cmdListData, cmdListName, paramNumber)
                        if isStartSeq or isStopSeq:
                            commandData = cmd(params, type="start" if isStartSeq else "stop")
                        elif cmdListData.startswith("CS_ACTOR_CUE_LIST(") or isPlayer:
                            commandData = cmd(params, isPlayer=isPlayer)
                        else:
                            commandData = cmd(params)

                        if cmdListName != "CS_TRANSITION" and cmdListName != "CS_DESTINATION":
                            foundEndCmd = False
                            for d in cmdData:
                                cmdEntryName = d.strip().split("(")[0]
                                isLegacy = d.startswith("L_")
                                if isLegacy:
                                    cmdEntryName = cmdEntryName.removeprefix("L_")
                                    d = d.removeprefix("L_")

                                if "CAM" in cmdListName:
                                    flag = d.removeprefix("CS_CAM_POINT(").split(",")[0]
                                    if foundEndCmd:
                                        raise ValueError("ERROR: More camera commands after last one!")
                                    foundEndCmd = "CS_CAM_STOP" in flag or "-1" in flag

                                entryCmd = cmdToClass[cmdEntryName]
                                params = self.getCmdParams(d, cmdEntryName, entryCmd.paramNumber)

                                if "CS_LIGHT_SETTING(" in d or isStartSeq or isStopSeq:
                                    listEntry = entryCmd(params, isLegacy=isLegacy)
                                else:
                                    listEntry = entryCmd(params)
                                commandData.entries.append(listEntry)
                        if cmdListName == "CS_DESTINATION":
                            cutscene.destination = commandData
                        else:
                            cmdList.append(commandData)
                    else:
                        print(f"WARNING: `{cmdListName}` is not implemented yet!")

            # after processing the commands we can add the cutscene to the cutscene list
            if cutscene is not None:
                cutsceneList.append(cutscene)
        return cutsceneList
