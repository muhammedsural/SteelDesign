from math import sqrt
from dataclasses import dataclass, field

@dataclass
class AnchorConnection:
    """
    d       : Kolon kesit boyu
    bf      : Kolon kesit eni
    B       : Taban plakasi genisliği
    N       : Taba plakasi yuksekligi
    tf      : Taban plakasi kalinligi
    P_axial : Gelen eksenel yük
    M       : Gelen moment
    fck     : Beton karakteristik dayanimi

    """
    d       : float = field(default_factory=float)
    bf      : float = field(default_factory=float)
    B       : int = field(default_factory=int)
    N       : int = field(default_factory=int)
    tf      : int = field(default_factory=int)
    P_axial : float = field(default_factory=float)
    M       : float = field(default_factory=float)
    fck     : float = field(default_factory=float)

@dataclass
class CheckBasePlate:
    Contn  : AnchorConnection = field(default_factory=AnchorConnection)
    ReductionFactor : float = field(default_factory=float)

    def __post_init__(self) -> None:
        self.A1 = self.FindRequiredBasePlateAreaForConcentricAxialCompressiveLoad(Case=1)    
        self.N  = self.FindApproxBasePlateHeight()

    def FindRequiredBasePlateAreaForConcentricAxialCompressiveLoad(self,Case : int) -> float:
        """
        A1 : Taban plakasi alani
        A2 : Beton yüzey alani

        Case 1 : A1 = A2
        Case 2 : A2 >= 4A1
        Case 3 : A1 < A2 < 4A1

        """
        if Case == 1:
            A1 = self.Contn.P_axial / (self.ReductionFactor * 0.85 * self.Contn.fck)
        elif Case == 2:
            A1 = self.Contn.P_axial / (2*(self.ReductionFactor * 0.85 * self.Contn.fck))

        return round(A1,0)

    def FindApproxBasePlateHeight(self) -> float:
        delta = (0.95*self.Contn.d - self.Contn.bf)/2
        N = round(sqrt(self.A1) + delta,0)

        while N%5 != 0:
            N = N+1

        return round(N,0)
    

    def RequiredBasePlateAreaForAxialLoad(self):
        #A1 : Taban plakası alanı
        #A2 : Beton yüzey alanı

        pass

    def find_BasePlateDim():

        pass

    def find_criteccantiristy():
        pass

    def find_eccantiristy():
        pass

    def find_BearingLength():
        pass

    def find_BasePlateThickness():
        pass


def main() -> None:
    conn = AnchorConnection(d=12.7, bf= 12.2, B= 240, N= 240, tf=10, P_axial=700, M=50, fck= 3)
    BasePlat = CheckBasePlate(Contn=conn, ReductionFactor=0.65)
    print(f' A1 ={BasePlat.A1}, N ={BasePlat.N}, ')

if __name__ == "__main__":
    main()