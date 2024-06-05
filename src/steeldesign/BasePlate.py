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


# Betona ankrajlanmış birleşimlerde limit dayanımlar
# Tension
class SteelStrengthOfAnchorInTension:

    def NominalSteelStrengthOfAnchorInTension(self, A_se: float, f_ya : float,f_uta : float)-> float:
        """_summary_

        Args:
            A_se (float): is the effective cross-sectional area of an anchor in tension mm^2
            f_ya (float): specified yield strength of anchor steel, shall not exceed 1.9f_ya or 862MPa
            f_uta (float): specified tensile strength of anchor steel, shall not exceed 1.9f_ya or 862MPa

        Returns:
            float: N_sa
        """
        f_uta = min(f_uta,1.9*f_ya,862)
        return round(A_se * f_uta,3)

class ConcreteBreakoutStrengthOfAnchorInTension:
    def Psi_cpN_Get(self,Cac : float, Ca_min : float, h_ef: float) -> float:
        # ACI 318-19 17.6.2.6 Breakout splitting factor
        pass

    def Psi_cN_Get(self) -> float:
        # ACI 318-19 17.6.2.5 Breakout cracking factor, 1.25 for cast-in anchors, 1.4 for post-installed anchors,
        pass

    def Psi_edN_Get(self,C_a_min : float, h_ef : float) -> float:
        # ACI 318-19 17.6.2.4 breakout edge effect factor
        pass

    def Psi_ecN_Get(eN : float, h_ef:float)-> float:
        """ACI 318-19 17.6.2.3 Breakout eccentricity factor Psi_ec,N, shall be calculated by Eq.(17.6.2.3.1).

        Args:
            eN (float): Ankraj grubuna etkiyen bileşke kuvvetin yeri ile çekme ankrajların yükleme(geometrik merkezi) yeri arasındaki mesafe
            h_ef (float): _description_

        Returns:
            float: _description_
        """
        Psi_ecN = 1 / (1 + (eN/(1.5*h_ef)))
        return min(1.0,Psi_ecN)

    def BasicSingleAnchorBreakoutStrength(self,kc:float,lambda_a : float, f_c:float, h_ef:float)-> float:
        # 17.6.2.2.1 Basic concrete breakout strength of a single anchor in tension in cracked concrete, Nb, shall be calculated by Eq. (17.6.2.2.1), except as permitted in 17.6.2.2.3
        # ACI318-19 Eq.17.6.2.2.1 kc = 24 for cast-in anchors and 17 for post-installed anchors.
        Nb = kc * lambda_a * f_c**0.5 * h_ef**1.5
        return round(Nb,3)
    def BasicSingleAnchorBreakoutStrength2(self,kc:float,lambda_a : float, f_c:float, h_ef:float)-> float:
        # ACI318-19 17.6.2.2.3 For single cast-in headed studs and headed bolts with 11in(28cm) <= hef <= 25in(63.5cm), Nb shall be calculated by:
        Nb = 16 * lambda_a * f_c**0.5 * h_ef**(5/3)
        return round(Nb,3)
    
    def A_Nco(self,h_ef: float)-> float:
        """Ankraj tüm kenarlara mesafesi en az 1.5 h_ef ise ACI318-19 Eq.17.6.2.1.4

        Args:
            h_ef (float): _description_

        Returns:
            float: _description_
        """
        return 9*h_ef**2

    def ForSingleAnchor(self,A_Nc: float, A_Nco : float, Psi_edN : float, Psi_cN : float, Psi_cpN : float, Nb : float)-> float:
        """_summary_

        Args:
            A_Nc (float): projected concrete failure area of a single anchor or group of anchors, for calculation of strength in tension
            A_Nco (float): projected concrete failure area of a single anchor, for calculation of strength in tension if not limited by edge distance or spacing
            Psi_edN (float): Breakout edge effect factor used to modify tensile strength of anchors based on proximity to edges of concrete member
            Psi_cN (float): breakout cracking factor used to modify tensile strength of anchors based on the influence of cracks in concrete
            Psi_cpN (float): breakout splitting factor used to modify tensile strength of post-installed anchors intended use in uncracked concrete without reinforcement to account for splitting tensile stresses
            Nb (float): basic concrete breakout strength in tension of a single anchor in cracked concrete

        Returns:
            float: _description_
        """
        N_cb = (A_Nc/A_Nco) * Psi_edN * Psi_cN * Psi_cpN * Nb
        return round(N_cb,3)
    
    def ForGroupAnchor(self,A_Nc: float, A_Nco : float,Psi_ecN : float, Psi_edN : float, Psi_cN : float, Psi_cpN : float, Nb : float)-> float:
        """_summary_

        Args:
            A_Nc (float): projected concrete failure area of a single anchor or group of anchors, for calculation of strength in tension
            A_Nco (float): projected concrete failure area of a single anchor, for calculation of strength in tension if not limited by edge distance or spacing
            Psi_ecN (float): Breakout edge effect factor used to modify tensile strength of anchors based on proximity to edges of concrete member
            Psi_edN (float): Breakout edge effect factor used to modify tensile strength of anchors based on proximity to edges of concrete member
            Psi_cN (float): breakout cracking factor used to modify tensile strength of anchors based on the influence of cracks in concrete
            Psi_cpN (float): breakout splitting factor used to modify tensile strength of post-installed anchors intended use in uncracked concrete without reinforcement to account for splitting tensile stresses
            Nb (float): basic concrete breakout strength in tension of a single anchor in cracked concrete

        Returns:
            float: _description_
        """
        N_cb = (A_Nc/A_Nco) * Psi_ecN * Psi_edN * Psi_cN * Psi_cpN * Nb
        return round(N_cb,3)

class PulloutStrengthInTension:

    def Psi_cP_Get(self, IsConcCracked : bool)-> float:
        # 17.6.3.3 Pullout cracking factor,
        Psi_cP = 1.4
        if IsConcCracked:
            Psi_cP = 1.0
        return Psi_cP

class ConcreteSideFaceBlowoutStrengthOfHeadedAnchorInTension:
    pass

class BoundStrengthOfAdhesiveAnchorInTension:
    pass

# Shear

class SteelStrengthOfAnchorInShear:
    pass

class ConcreteBreakoutStrengthOfAnchorInShear:
    pass
class ConcretePryoutStrengthOfAnchorInShear:
    pass

# Tension-Shear Interaction




def main() -> None:
    conn = AnchorConnection(d=12.7, bf= 12.2, B= 240, N= 240, tf=10, P_axial=700, M=50, fck= 3)
    BasePlat = CheckBasePlate(Contn=conn, ReductionFactor=0.65)
    print(f' A1 ={BasePlat.A1}, N ={BasePlat.N}, ')

if __name__ == "__main__":
    main()