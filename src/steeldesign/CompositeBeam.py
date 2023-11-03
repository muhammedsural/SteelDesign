from handcalcs import handcalc

@handcalc(precision=5,jupyter_display=True)
def calc_stud_full_interaction(b_f : float, d : float, beam_length : float,beam_As : float,beam_aralik : float,f_ck : float,Y_con:float,Fy : float =345):
    """
    Tam etkileşimli kompozit kiriş stud çivisi sayısını hesaplar

    Arguments:
        b_f -- Çelik kiriş başlık genişliği mm
        d -- Çelik kiriş yüksekliği mm
        beam_length -- Kiriş uzunluğu m
        beam_As -- Çelik kiriş alanı mm2
        beam_aralik -- Çelik kirişlerin aralıkları m
        f_ck -- Beton karakteristik dayanımı Mpa 
        Y_con -- Beton örtüsü yüksekliği mm

    Keyword Arguments:
        Fy -- Çelik beklenen akma dayanımı (default: {345})

    Returns:
        Tasarım Momenti
    
    Extras:
        b1 ve b2 için eşit aralık kabulü yapıldı
    """
    T = beam_As*Fy /10**3  #kN
    b1 = 2 * beam_length * 1/8 
    b2 = 2 * beam_aralik * 1/2

    b = min(b1,b2) 

    alpha = T / (0.85 * f_ck * b) 
    A_conc = Y_con * b 
    Y2 = Y_con - 0.5*alpha 
    Y1 = (beam_As * Fy - (0.85 * f_ck * A_conc)) / (2 * Fy * b_f) 
    
    
    x = (0.85 * f_ck * A_conc *(Y1 + Y2)) / 10**6 
    y = (2* Fy * b_f *Y1 * (Y1 /2)) / 10**6 
    z = (beam_As * Fy * (d /2 - Y1)) / 10**6 

    Phi_Mn = ( x + y + z) * 0.9  

    return Phi_Mn

def check_conc_available_stress(f_ck : float) -> bool:
    if 20 <= f_ck and f_ck<70:
        return True
    else:
        return False

def check_steel_available_stress(Fy : float) -> bool:
    if Fy <= 460:
        return True
    else:
        print(f"Çelik sınıfı yönetmelik şartını sağlamamaktadır => {Fy} > {460} ")
        False

def check_trapez_dimension(Trapez : list,Stud : list) -> bool:
    Ok = 0
    if Trapez[0] > 75 or Trapez[1] < 50:
        print(f" {Trapez[0]} > 75 ; {Trapez[1]} < 50")
        Ok = 1
    
    h_ck = Stud[1] - Trapez[2] - Trapez[0]
    if h_ck < 38:
        print(f" {h_ck} < 38")
        Ok = 1

    h_ck2 = Trapez[3] - Trapez[2] - Stud[0]
    if h_ck2 < 12:
        print(f" {h_ck2} < 12")
        Ok = 1

    if Trapez[3] - Trapez[0] < 50:
        print(f" {Trapez[3] - Trapez[0]} < 50")
        Ok = 1
    
    if Ok == 1:
        return False
    if Ok == 0:
        return True

def check_Stud(Stud : list,Beam : list) -> bool:
    if Stud[0] < 19:
        return False
    if Stud[0] > 2.5*Beam[4]:
        return False
    if Stud[1] < 4 * Stud[0]:
        return False
    else: 
        return True

def calc_deflection(Beam : list,L : float , Pg : float,Pq : float,w_g : float = 1,E : float = 20_000):
    delta_1 = ((2 * Pg * L**3 * 10**3 / (28*E*Beam[6]*10**4)) + (5*w_g*L**4/(384*E*Beam[6]*10**4)))/10
    delta_2 = (2* Pq * L**3 * 10**3 / (28*E*Beam[6]*10**4))/10
    print(f"{delta_1} + {delta_2} = {delta_1+delta_2}")
    delta_yapım = delta_1 + delta_2

    return delta_yapım

def check_deflection(Beam : list,L : float , Pg : float,Pq : float,w_g : float = 1.,E : float = 20_000) :
    delta_1 = ((2 * Pg * L**3 * 10**3 / (28*E*Beam[6]*10**4)) + (5*w_g*L**4/(384*E*Beam[6]*10**4)))/10
    delta_2 = (2* Pq * L**3 * 10**3 / (28*E*Beam[6]*10**4))/10

    delta_yapım = delta_1 + delta_2

    if delta_1 > L/360:
        print(f"Sehim sınırı sağlanamadı => {delta_1}>{L/360}\nBu koşulun sağlanamadığı durumda çelik kirişe ters sehim verilmesi veya yapım aşamasında geçici destek kullanımı ile çelik kirişin düşey yerdeğiştirmesi azaltılabilir. (Bkz. Kaynak Yayınlar, AISC Design Guide 3).")
    if delta_yapım > L/300:
        print(f"Toplam sehim sınırı aşıldı kesit büyütülmeli veya mesnet koşulları değiştirilmeli.{delta_yapım} > {L/300} ")
    else:
        print(f"Sehim kontrolü sağlandı {delta_yapım} <= {L/300}. \nAyrıca, beton gerekli dayanımına ulaşıncaya kadar, \nçelik enkesitin yapım aşamasındaki sabit ve hareketli yükler altındaki eğilme dayanımı, \nYönetmelik Bölüm 9 da verilen kurallar gözönüne alınarak kontrol edilmelidir")

@handcalc(jupyter_display=True)
def efektif_doseme_genisligi(Length:float, Space:float):
    b1 = 2 * Length * 1/8 #mm Eşit aralık kabul edildi 
    b2 = 2 * Space  * 1/2 #mm Eşit aralık kabul edildi
    b = min(b1,b2) #mm
    return b


# def yapim_asamasi_sehimi(Pg : float, Pq : float, L : float, Ix : float, E:float = 200_000, wg: float = 1.) -> float:
#     """Basit mesnetli kompozit kiriş için yapım aşaması sehim hesabı

#     Args:
#         Pg (float): Ölü yük
#         L (float): Kiriş uzunluğu
#         Ix (float): Kiriş atalet momenti
#         E (float, optional): Kiriş malzemesinin elastisite modülü. Defaults to 200_000. birim : N/mm2
#         wg (float, optional): Kiriş ağırlığı birim:kN/m. Defaults to 1. 

#     Returns:
#         delta_1 (float): Yapım aşamasındaki sehim
#     """

#     #Ölü yük etkisi
#     a = 2*(Pg * L**3 / (28 * E * Ix))
#     b = (5 * wg * L**4 / (384 * E * Ix))
#     delta_1 = a + b

#     if delta_1 > (L / 360):
#         print(f"Ölü yük durumunda sehim sınırı sağlanamadı => {round(delta_1,2)}mm > {round(L/360,2)}mm çelik kirişe ters sehim verilmesi veya yapım aşamasında geçici destek kullanımı ile çelik kirişin düşey yerdeğiştirmesi azaltılabilir.")

#     #hareketli yük etkisi
#     delta_2 = (2 * Pq * L **3 / (28 * E * Ix))

#     #total etki
#     delta = delta_1 + delta_2

#     if delta > (L/300):
#         print(f"Yapım aşaması sehim sınırı sağlanamadı kiriş boyutu arttırılabilir. => {round(delta,2)}mm > {round(L/300,2)}mm" )
#     return round(delta,2)

# def efektif_doseme_genisligi(L : float, Lu : float) -> float:
#     """Efektif kompozit döşeme genişliği hesabı

#     Args:
#         L (float): Kiriş uzunluğu birim : m
#         Lu (float): Kiriş aralığı birim : m

#     Returns:
#         b_eff float: efektif döşeme genişliği birim : m
#     """
#     b1 = L/8
#     b2 = Lu/2

#     b = 2*min(b1,b2)

#     return b

# def beton_alanı(h_c_üs : float, b_eff : float, h_r : float) -> float:
#     """Yaklaşık beton örtü alanı

#     Returns:
#         Ac float: net beton örtü alanı
#     """
#     Ac = (b_eff * h_c_üs) + (0.5 * b_eff * h_r)
#     print(f"Ac = ({b_eff} * {h_c_üs}) + (0.5 * {b_eff} * {h_r}) = {Ac}mm2")
#     return Ac

# def kompozit_kiris_eğilme_kapasitesi(Fy : float, Beam : dict, f_ck : float, Ac : float, b_eff : float) -> float:
   
#     C_conc  = 0.85 * f_ck * Ac
#     C_steel = Fy * Beam["Area"]
    

#     if C_conc < C_steel : 
#         print(f"Kompozit döşeme kısmi etkileşimlidir. Plastik tarafsız eksen Çelik kirişin başlık veya gövdesindedir.")
#         M_n = 0.

#     else:
#         print("Plastik tarafsız eksen beton bloğun içindedir. Tam etkileşimli")

#         C = min(C_conc,C_steel) #N
#         print(f"C ={C} ")

#         a = C/(0.85 * f_ck * b_eff)
#         print(f"a = {a}")
        
#         y = Beam["d"]/2 + (h_c - a/2) 
#         print(f"y = {y}")

#         M_n = C * y

#     return round(M_n,2)

# def Kompozit_kirişe_gelen_egilme_momenti(Pu : float):
#     pass