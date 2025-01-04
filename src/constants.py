from data import OoT_Data, MM_Data


oot_data = OoT_Data()
mm_data = MM_Data()

ootCSLegacyToNewCmdNames = {
    "CS_CAM_POS_LIST": "CS_CAM_EYE_SPLINE",
    "CS_CAM_FOCUS_POINT_LIST": "CS_CAM_AT_SPLINE",
    "CS_CAM_POS_PLAYER_LIST": "CS_CAM_EYE_SPLINE_REL_TO_PLAYER",
    "CS_CAM_FOCUS_POINT_PLAYER_LIST": "CS_CAM_AT_SPLINE_REL_TO_PLAYER",
    "CS_NPC_ACTION_LIST": "CS_ACTOR_CUE_LIST",
    "CS_PLAYER_ACTION_LIST": "CS_PLAYER_CUE_LIST",
    "CS_CMD_07": "CS_CAM_EYE",
    "CS_CMD_08": "CS_CAM_AT",
    "CS_CAM_POS": "CS_CAM_POINT",
    "CS_CAM_FOCUS_POINT": "CS_CAM_POINT",
    "CS_CAM_POS_PLAYER": "CS_CAM_POINT",
    "CS_CAM_FOCUS_POINT_PLAYER": "CS_CAM_POINT",
    "CS_NPC_ACTION": "CS_ACTOR_CUE",
    "CS_PLAYER_ACTION": "CS_PLAYER_CUE",
    "CS_CMD_09_LIST": "CS_RUMBLE_CONTROLLER_LIST",
    "CS_CMD_09": "CS_RUMBLE_CONTROLLER",
    "CS_TEXT_DISPLAY_TEXTBOX": "CS_TEXT",
    "CS_TEXT_LEARN_SONG": "CS_TEXT_OCARINA_ACTION",
    "CS_SCENE_TRANS_FX": "CS_TRANSITION",
    "CS_FADE_BGM_LIST": "CS_FADE_OUT_SEQ_LIST",
    "CS_FADE_BGM": "CS_FADE_OUT_SEQ",
    "CS_TERMINATOR": "CS_DESTINATION",
    "CS_LIGHTING_LIST": "CS_LIGHT_SETTING_LIST",
    "CS_LIGHTING": "L_CS_LIGHT_SETTING",
    "CS_PLAY_BGM_LIST": "CS_START_SEQ_LIST",
    "CS_PLAY_BGM": "L_CS_START_SEQ",
    "CS_STOP_BGM_LIST": "CS_STOP_SEQ_LIST",
    "CS_STOP_BGM": "L_CS_STOP_SEQ",
    "CS_BEGIN_CUTSCENE": "CS_HEADER",
    "CS_END": "CS_END_OF_SCRIPT",
}

ootCSListCommands = [
    "CS_ACTOR_CUE_LIST",
    "CS_PLAYER_CUE_LIST",
    "CS_CAM_EYE_SPLINE",
    "CS_CAM_AT_SPLINE",
    "CS_CAM_EYE_SPLINE_REL_TO_PLAYER",
    "CS_CAM_AT_SPLINE_REL_TO_PLAYER",
    "CS_CAM_EYE",
    "CS_CAM_AT",
    "CS_MISC_LIST",
    "CS_LIGHT_SETTING_LIST",
    "CS_RUMBLE_CONTROLLER_LIST",
    "CS_TEXT_LIST",
    "CS_START_SEQ_LIST",
    "CS_STOP_SEQ_LIST",
    "CS_FADE_OUT_SEQ_LIST",
    "CS_TIME_LIST",
    "CS_UNK_DATA_LIST",
    "CS_PLAY_BGM_LIST",
    "CS_STOP_BGM_LIST",
    "CS_LIGHTING_LIST",
    # new
    "CS_CAM_SPLINE_LIST",
    "CS_TRANSITION_LIST",
    "CS_DESTINATION_LIST",
    "CS_MOTION_BLUR_LIST",
    "CS_MODIFY_SEQ_LIST",
    "CS_CHOOSE_CREDITS_SCENES_LIST",
    "CS_TRANSITION_GENERAL_LIST",
    "CS_GIVE_TATL_LIST",
]

ootCSListEntryCommands = [
    "CS_ACTOR_CUE",
    "CS_PLAYER_CUE",
    "CS_CAM_POINT",
    "CS_MISC",
    "CS_LIGHT_SETTING",
    "CS_RUMBLE_CONTROLLER",
    "CS_TEXT",
    "CS_TEXT_NONE",
    "CS_TEXT_OCARINA_ACTION",
    "CS_START_SEQ",
    "CS_STOP_SEQ",
    "CS_FADE_OUT_SEQ",
    "CS_TIME",
    "CS_UNK_DATA",
    "CS_PLAY_BGM",
    "CS_STOP_BGM",
    "CS_LIGHTING",
    # some old commands need to remove 1 to the first argument to stay accurate
    "L_CS_LIGHT_SETTING",
    "L_CS_START_SEQ",
    "L_CS_STOP_SEQ",
    # new
    "CS_CAM_POINT_NEW",
    "CS_CAM_MISC",
    "CS_CAM_END",
    "CS_CAM_SPLINE", # technically a list but treating it as an entry
    "CS_TEXT_DEFAULT",
    "CS_TEXT_TYPE_1",
    "CS_TEXT_TYPE_3",
    "CS_TEXT_BOSSES_REMAINS",
    "CS_TEXT_ALL_NORMAL_MASKS",
    "CS_MOTION_BLUR",
    "CS_MODIFY_SEQ",
    "CS_CHOOSE_CREDITS_SCENES",
    "CS_TRANSITION_GENERAL",
    "CS_GIVE_TATL",
]

ootCSSingleCommands = [
    "CS_HEADER",
    "CS_END_OF_SCRIPT",
    # note: `CutsceneImport.correct_command_lists()` can move these ones in `ootCSListEntryCommands`
    "CS_TRANSITION",
    "CS_DESTINATION",
]

ootCSListAndSingleCommands = ootCSSingleCommands + ootCSListCommands
ootCSListAndSingleCommands.remove("CS_HEADER")
ootCutsceneCommandsC = ootCSSingleCommands + ootCSListCommands + ootCSListEntryCommands
