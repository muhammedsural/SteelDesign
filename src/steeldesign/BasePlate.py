
from dataclasses import dataclass, field

from steeldesign.Material import Steel,S235


@dataclass
class Plate:
    B : float
    N : float
    m : float
    n : float
    t : float
    Mat : Steel = field(default_factory=Steel)


if __name__=="__main__":
    s1 = S235()
    p1 = Plate(100,100,10,10,10,s1)
    print(p1)