from dataclasses import dataclass, field
from enum import Enum

from steeldesign.Material import Steel,S235

class CastInAnchorType(Enum):
    # ACI318-19 Fig.R2.1
    HexHeadBoltWithWasher = 1
    L_bolt = 2
    J_bolt = 3
    WeldedHeadedStud = 4

class PostInAnchorType(Enum):
    # ACI318-19 Fig.R2.1
    Adhesive = 1
    Andercut = 2
    SleeveType = 3 #TorqueControlledExpansion
    StudType = 4   #TorqueControlledExpansion
    DisplacementControlledExpansion = 5
    Screw = 6

class LocationStart(Enum):
    StartToEnd = 1
    Center = 2
    EndToStart = 3

@dataclass
class Anchor:
    D_a : float
    L1  : float
    L2  : float
    L3  : float
    L4  : float
    Mat : Steel
    LocStart : LocationStart 
    # Nut : Nut
    # Washer : Washer
    # Plate  : Plate