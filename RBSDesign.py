
# Definitions

# b_bf : Kiriş başlık genişliği 
# d_b  : Kiriş enkesit yüksekliği
# R    : RBS kesitinin radiusu
# Z_rbs : RBS kesitinin plastik mukavemet momenti -mm^3
# Z_b   : Brüt kiriş kesitinin plastik mukavemet momenti -mm^3
# t_bf : Kiriş başlık kalınlığı -mm
# S_h : Plastik mafsal uzunluğu
# V_h : Plastik mafsal bölgesindeki max kesme kuvveti
# Vuc = Birleşimin kolon yüzündeki gerekli kesme kuvveti dayanımı
# M_f : Kolon yüzünde oluşabilecek max moment
# M_pe : 

def RBS_kontrol(a,b,c,Agirlik,d_b,b_bf):
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

    R = (4*c**2 + b**2)/(8*c)
    return R

def Get_Sh(a : float, b : float) -> float:

    Sh = a + 0.5*b
    return Sh

def Get_Zrbs (Wp_z : float, c : float, b_bf : float, d_b : float) -> float:

    Z_rbs = Wp_z - (2*c*b_bf*(d_b-b_bf))
    return Z_rbs

def Get_Lh(L_beam : float, Sh : float) -> float:
    L_h = L_beam - 2*Sh
    return L_h

# #Muhtemel plastik mafsaldaki max. moment
def ProbablyMaxMomentHingeRegion(Zrbs : float, Ry : float, Fy : float, Fu : float) -> float:
    C_pr = (Fy + Fu)/(2*Fy)
    if C_pr > 1.2:
        C_pr = 1.2
    print(f"Cpr = {C_pr}")   

    M_pr = round(C_pr * Ry * Fy * Zrbs * 10**-6,2)
    print(f"M_pr = C_pr * R_y * Fy * Z_rbs = {M_pr}kNm")
    return M_pr

# #Muhtemel plastik mafsaldaki max. kesme
def ProbablyMaxShearForceHingeRegion(Mpr : float, Lh : float, Vgravity : float) -> float:
    Vh = round((2*Mpr/(Lh/1000)) + Vgravity * 10**-3,2)
    print(f"Vh = (2*M_pr/L_h) + V_gravity = {Vh}kN")
    return Vh

# #Gerekli kiriş kesme dayanımı
# Vu = Vh + V_gravity

# #Muhtemel kolon yüzündeki max. moment
# Mf = round(M_pr + Vh*S_h * 10**-6,2)
# print(f"Mf = M_pr + Vh*S_h = {Mf}kNm")

# #Kiriş plastik moment kapasitesi
# M_pe = round(Ry * Fy * Z_b * 10**-6,2)
# print(f"M_pe = Ry * Fy * Z_b = {M_pe}kNm")

# #Kiriş moment kapasitesi kontrolü

# if Mf <= fi_d * M_pe:
#     print(f"fi_d * M_pe = {fi_d * M_pe} ≥ {Mf} = Mf Moment kapasitesi yeterlidir")
# else:
#     print("Mf = {Mf} > {fi_d * M_pe} = fi_d * M_pe Moment kapasitesi yeterli değildir")

# #Kesme kuvvetleri gövde kesitinde karşılandığı kabul edilirse kiriş için
# import math
# Aw = tw * d_b
# h = d_b - 2*b_bf
# web_slenderness_ratio = h/tw
# kv = 5.34

# chck_point1 = 2.24* math.sqrt(E/Fy)
# chck_point2 = 1.10 * math.sqrt(kv*E/Fy)
# chck_point3 = 1.37 * math.sqrt(kv*E/Fy)

# if web_slenderness_ratio <= chck_point2 or web_slenderness_ratio <= chck_point1:
#     Cv1 = 1.0
#     Vnominal = 0.6 * Fy * Aw * Cv1  
# if web_slenderness_ratio > chck_point2 and web_slenderness_ratio <= chck_point3:
#     Cv1 = chck_point2/web_slenderness_ratio
#     Vnominal = 0.6 * Fy * Aw * Cv1 
# if web_slenderness_ratio > chck_point3:
#     Cv2 = (1.51 * kv * E)/(web_slenderness_ratio**2 * Fy)
#     x = (Cv2 + (1-Cv2)/(1.15*((a/h)+math.sqrt(1+(a/h)**2))))
#     Vnominal = 0.6 * Fy * Aw * x
