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
class AnchorMaterial:
    #                F_yb,F_ub
    M4_6    : list = field(default_factory=list)
    M4_8    : list = field(default_factory=list)
    M5_6    : list = field(default_factory=list)
    M5_8    : list = field(default_factory=list)
    M6_8    : list = field(default_factory=list)
    M8_8    : list = field(default_factory=list)
    M10_9   : list = field(default_factory=list)

AncMat = AnchorMaterial(M4_6  = [240,320 ],
                        M4_8  = [320,400 ],
                        M5_6  = [300,500 ],
                        M5_8  = [400,500 ],
                        M6_8  = [480,600 ],
                        M8_8  = [640,800 ],
                        M10_9 = [900,1000]
                    )

@dataclass
class Anchor:
    D_a         : float                                 
    L           : float                                 
    L1          : float                                 
    L2          : float                                 
    L3          : float                                 
    L4          : float    
    AnchorType  : CastInAnchorType | PostInAnchorType                              
    AnchorMat   : AnchorMaterial                        
    LocStart    : LocationStart                         
    # Nut : Nut
    # Washer : Washer
    # Plate  : Plate


class M12(Anchor):
    def __init__(self)->None:
        super().__init__(D_a=12, L=500, L1=38, L2=88, L3=100, L4=200, AnchorType=CastInAnchorType.HexHeadBoltWithWasher, AnchorMat=AncMat.M5_6, LocStart=LocationStart.Center)

class M16(Anchor):
    def __init__(self)->None:
        super().__init__(D_a=16, L=500, L1=38, L2=88, L3=100, L4=200, AnchorType=CastInAnchorType.HexHeadBoltWithWasher, AnchorMat=AncMat.M5_6, LocStart=LocationStart.Center)
        
class M20(Anchor):
    def __init__(self)->None:
        super().__init__(D_a=20, L=500, L1=38, L2=88, L3=100, L4=200, AnchorType=CastInAnchorType.HexHeadBoltWithWasher, AnchorMat=AncMat.M5_6, LocStart=LocationStart.Center)

class M22(Anchor):
    def __init__(self)->None:
        super().__init__(D_a=22, L=500, L1=38, L2=88, L3=100, L4=200, AnchorType=CastInAnchorType.HexHeadBoltWithWasher, AnchorMat=AncMat.M5_6, LocStart=LocationStart.Center)

class M24(Anchor):
    def __init__(self)->None:
        super().__init__(D_a=24, L=500, L1=38, L2=88, L3=100, L4=200, AnchorType=CastInAnchorType.HexHeadBoltWithWasher, AnchorMat=AncMat.M5_6, LocStart=LocationStart.Center)

class M27(Anchor):
    def __init__(self)->None:
        super().__init__(D_a=27, L=500, L1=38, L2=88, L3=100, L4=200, AnchorType=CastInAnchorType.HexHeadBoltWithWasher, AnchorMat=AncMat.M5_6, LocStart=LocationStart.Center)

class M30(Anchor):
    def __init__(self)->None:
        super().__init__(D_a=30, L=500, L1=38, L2=88, L3=100, L4=200, AnchorType=CastInAnchorType.HexHeadBoltWithWasher, AnchorMat=AncMat.M5_6, LocStart=LocationStart.Center)

# if __name__ == "__main__":
#     a1 = M12()
#     print(a1)