from dataclasses import dataclass


@dataclass
class OoT_BaseElement:
    id: str
    key: str
    name: str
    index: int


@dataclass
class OoT_Data:
    """Contains data related to OoT, like actors or objects"""

    def __init__(self):
        from .enum_data import OoT_EnumData
        from .object_data import OoT_ObjectData
        from .actor_data import OoT_ActorData

        self.enumData = OoT_EnumData()
        self.objectData = OoT_ObjectData()
        self.actorData = OoT_ActorData()
