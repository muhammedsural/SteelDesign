
# Definitions

# b_bf  : Kiriş başlık genişliği 
# d_b   : Kiriş enkesit yüksekliği
# R     : RBS kesitinin radiusu
# Z_rbs : RBS kesitinin plastik mukavemet momenti -mm^3
# Z_b   : Brüt kiriş kesitinin plastik mukavemet momenti -mm^3
# t_bf  : Kiriş başlık kalınlığı -mm
# S_h   : Plastik mafsal uzunluğu
# V_h   : Plastik mafsal bölgesindeki max kesme kuvveti
# Vuc   : Birleşimin kolon yüzündeki gerekli kesme kuvveti dayanımı
# M_f   : Kolon yüzünde oluşabilecek max moment
# M_pe  : 

def RBS_kontrol(a : float, b : float, c : float, Agirlik : float, d_b : float, b_bf : float) -> None:
    """_summary_

    Args:
        a (float): _description_
        b (float): _description_
        c (float): _description_
        Agirlik (float): _description_
        d_b (float): _description_
        b_bf (float): _description_
    """    
    if Agirlik > 450 : #ASCI da bu değer 610 kg/m
        print("Kesit agirligi siniri geçiyor kesit küçültülmeli")

    if d_b > 920:
        print("Kesit yüksekliği siniri geçiyor kesit küçültülmeli")

    if a < (0.5*b_bf):
        print(f"a = {a} < 0.5*b_bf = {0.5*b_bf} ==> a değiştirildi")
        a = 0.5*b_bf

    if a > (0.75*b_bf):
        print(f"a = {a} > 0.75*b_bf = {0.75*b_bf} ==> a değiştirildi")
        a = 0.75*b_bf

    if b < (0.65*d_b):
        print(f"b = {b} < 0.65*d_b = {0.65*d_b} ==> b değiştirildi")
        b = 0.65*d_b

    if b > (0.85*d_b):
        print(f"b = {b} > 0.85*d_b = {0.85*d_b} ==> b değiştirildi")
        b = 0.85*d_b

    if c < (0.1*b_bf):
        print(f"c = {c} < 0.1*b_bf = {0.1*b_bf} ==> c değiştirildi")
        c = 0.1*b_bf

    if c > (0.25*b_bf):
        print(f"c = {c} > 0.25*b_bf = {0.25*b_bf} ==> c değiştirildi")
        c = 0.25*b_bf

def Get_R(b : float, c : float) -> float:
    """_summary_

    Args:
        b (float): _description_
        c (float): _description_

    Returns:
        float: _description_
    """
    R = (4*c**2 + b**2)/(8*c)
    return R

def Get_Sh(a : float, b : float) -> float:
    """_summary_

    Args:
        a (float): _description_
        b (float): _description_

    Returns:
        float: _description_
    """
    Sh = a + 0.5*b
    return Sh

def Get_Zrbs (Wp_z : float, c : float, b_bf : float, d_b : float) -> float:
    """_summary_

    Args:
        Wp_z (float): _description_
        c (float): _description_
        b_bf (float): _description_
        d_b (float): _description_

    Returns:
        float: _description_
    """
    Z_rbs = Wp_z - (2*c*b_bf*(d_b-b_bf))
    return Z_rbs

def Get_Lh(L_beam : float, Sh : float) -> float:
    """_summary_

    Args:
        L_beam (float): _description_
        Sh (float): _description_

    Returns:
        float: _description_
    """
    L_h = L_beam - 2*Sh
    return L_h

# #Muhtemel plastik mafsaldaki max. moment
def ProbablyMaxMomentHingeRegion(Zrbs : float, Ry : float, Fy : float, Fu : float) -> float:
    """_summary_

    Args:
        Zrbs (float): _description_
        Ry (float): _description_
        Fy (float): _description_
        Fu (float): _description_

    Returns:
        float: _description_
    """
    C_pr = (Fy + Fu)/(2*Fy)
    if C_pr > 1.2:
        C_pr = 1.2
    print(f"Cpr = {C_pr}")   

    M_pr = round(C_pr * Ry * Fy * Zrbs * 10**-6,2)
    print(f"M_pr = C_pr * R_y * Fy * Z_rbs = {M_pr}kNm")
    return M_pr

# #Muhtemel plastik mafsaldaki max. kesme
def ProbablyMaxShearForceHingeRegion(Mpr : float, Lh : float, Vgravity : float) -> float:
    """_summary_

    Args:
        Mpr (float): _description_
        Lh (float): _description_
        Vgravity (float): _description_

    Returns:
        float: _description_
    """
    Vh = round((2*Mpr/(Lh/1000)) + Vgravity * 10**-3,2)
    print(f"Vh = (2*M_pr/L_h) + V_gravity = {Vh}kN")
    return Vh

# #Gerekli kiriş kesme dayanımı
def RequiredShearStrength(Vh : float, V_gravity : float) -> float:
    """_summary_

    Args:
        Vh (float): _description_
        V_gravity (float): _description_

    Returns:
        float: _description_
    """
    Vu = Vh + V_gravity
    return Vu

# #Muhtemel kolon yüzündeki max. moment
def ProbablyMaxMomentColumnFace(M_pr : float, Vh : float, S_h :float) -> float:
    """_summary_

    Args:
        M_pr (float): _description_
        Vh (float): _description_
        S_h (float): _description_

    Returns:
        float: _description_
    """
    Mf = round(M_pr + Vh*S_h * 10**-6,2)
    print(f"Mf = M_pr + Vh*S_h = {Mf}kNm")
    return Mf

# #Kiriş plastik moment kapasitesi
def BeamPlasticMomentCapacity(Ry : float, Fy : float, Z_b : float) -> float:
    """_summary_

    Args:
        Ry (float): _description_
        Fy (float): _description_
        Z_b (float): _description_

    Returns:
        float: _description_
    """
    M_pe = round(Ry * Fy * Z_b * 10**-6,2)
    print(f"M_pe = Ry * Fy * Z_b = {M_pe}kNm")
    return M_pe

# #Kiriş moment kapasitesi kontrolü
def CheckBeamMomentStrengt(Mf : float, M_pe : float, fi_d : float) -> None:
    """_summary_

    Args:
        Mf (float): _description_
        M_pe (float): _description_
        fi_d (float): _description_
    """
    if Mf <= fi_d * M_pe:
      print(f"fi_d * M_pe = {fi_d * M_pe} ≥ {Mf} = Mf Moment kapasitesi yeterlidir")
    else:
      print("Mf = {Mf} > {fi_d * M_pe} = fi_d * M_pe Moment kapasitesi yeterli değildir")

