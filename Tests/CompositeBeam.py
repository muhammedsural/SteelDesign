# Rib : Hadve
# Camber : Ters sehim
# concrete cover above the top of the headed stud anchors. Hadve Uzerinde Kalan Stud Boyutları Kontrolu

def StudCheck(Ds : float, tf : float, Hs : float, IsWebAlignmentWelded : bool = False)-> bool:
    """_summary_

    Args:
        Ds (float): _description_
        tf (float): _description_
        Hs (float): Stud çivisi yüksekliği
        IsWebAlignmentWelded (bool, optional): _description_. Defaults to False.

    Returns:
        bool: _description_
    """

    if Ds > 2.5*tf or Ds > 19:
        print(f"Ds = {Ds}mm > 2.5*tf = {2.5*tf}mm X - TurkishSteelStructureCode ")
        print(f"Ds = {Ds}mm > 19mm X - TurkishSteelStructureCode 12.8.1")
        return False
    if Hs < 4*Ds:
        print(f"Hs = {Hs}mm < 4*Ds = {4*Ds}mm X - TurkishSteelStructureCode 12.8.2")
        return False
    if IsWebAlignmentWelded:
        print("Stud çivisi gövde hizasında bağlandığı için bu kontrollere gerek yoktur.")
        return True
    print(f"Ds = {Ds}mm ≤ 2.5*tf = {2.5*tf}mm √ - TurkishSteelStructureCode ")
    print(f"Ds = {Ds}mm ≤ 19mm √ - TurkishSteelStructureCode 12.8.1")
    print(f"Hs = {Hs}mm ≥ 4*Ds = {4*Ds}mm √ - TurkishSteelStructureCode 12.8.2")
    return True

def StudSpaceCheck(Ds : float, s : float, Ycon : float) -> bool:
    """_summary_

    Args:
        Ds (float): _description_
        s (float): _description_
        Ycon (float): _description_

    Returns:
        bool: _description_
    """

    if s < 6*Ds or s > 8*Ycon or s >914:
        print(f"s = {s}mm < {6*Ds}mm X")
        print(f"s = {s}mm > {8*Ycon}mm X")
        print(f"s = {s}mm > 914mm X")
        return False
    print(f"s = {s}mm ≥ {6*Ds}mm √")
    print(f"s = {s}mm ≤ {8*Ycon}mm √")
    print(f"s = {s}mm ≤ 914mm √")
    return True

def DistanceBetweenTwoStudsCheck(x : float, Ds : float)-> bool:

    if x < 4*Ds:
        return False
    return True

def ConcreteCoverAboveTopOfHeadedStudAnchorsChecks(hr : float, t_sac : float, h_stud: float, Ycon : float) -> bool:
    """_summary_

    Args:
        hr (float): Hadve yüksekliği
        h_stud (float): Stud çivisi yüksekliği
        Ycon (float): Çelik kesit üst başlığından en üst beton lifine olan mesafe

    Returns:
        bool: _description_
    """
    if h_stud-hr-t_sac < 38 or Ycon - h_stud < 13 or Ycon - hr < 50:
        print(f"h_stud-hr-t_sac = {h_stud-hr-t_sac}mm < 38mm X - TurkishSteelStructureCode 12.4.2.3")
        print(f"Ycon - h_stud-t_sac = {Ycon - h_stud-t_sac}mm < 13mm X - TurkishSteelStructureCode 12.4.2.3")
        print(f"Ycon - hr = {Ycon - hr}mm < 50mm X - TurkishSteelStructureCode 12.4.2.3")
        return False
    print(f"h_stud-hr-t_sac = {h_stud-hr-t_sac}mm ≥ 38mm √ - TurkishSteelStructureCode 12.4.2.3")
    print(f"Ycon - h_stud-t_sac = {Ycon - h_stud-t_sac}mm ≥ 13mm √ - TurkishSteelStructureCode 12.4.2.3")
    print(f"Ycon - hr = {Ycon - hr}mm ≥ 50mm √ - TurkishSteelStructureCode 12.4.2.3")
    return True

def MetalDeckCheck(hr : float, wr : float)-> bool:
    """_summary_

    Args:
        hr (float): Hadve yüksekliği
        wr (float): Hadve genişliği

    Returns:
        bool: _description_
    """
    if hr > 75 or wr < 50 :
        print(f"hr = {hr}mm > 75mm X - TurkishSteelStructureCode 12.4.2.3")
        print(f"wr = {wr}mm < 50mm X - TurkishSteelStructureCode 12.4.2.3")
        return False
    print(f"hr = {hr}mm ≤ 75mm √ - TurkishSteelStructureCode 12.4.2.3")
    print(f"wr = {wr}mm ≥ 50mm √ - TurkishSteelStructureCode 12.4.2.3")
    return True

def ConcAvailableStressCheck(f_ck : float) -> bool:
    if 20 <= f_ck and f_ck<70:
        print(f"20 N/mm^2 ≤ {f_ck} N/mm^2 < 70 N/mm^2 √ - TurkishSteelStructureCode 12.2.3(a)")
        return True
    else:
        print(f"20 ≤ {f_ck} < 70 X - TurkishSteelStructureCode 12.2.3(a)")
        return False

def SteelAvailableStressCheck(Fy : float) -> bool:
    if Fy <= 460:
        print(f"{Fy} N/mm^2 ≤ 460 N/mm^2 √ - TurkishSteelStructureCode 12.2.3(c)")
        return True
    else:
        print(f"Çelik sınıfı yönetmelik şartını sağlamamaktadır => {Fy} > {460} X - TurkishSteelStructureCode 12.2.3(c)")
        False

def ConcreteYoungModules(fck : float,wc : float = 2320)-> float:
    """_summary_

    Args:
        fck (float): MPa
        wc (float, optional): . Defaults to 2320 kg/m^3.

    Returns:
        float: _description_
    """
    Ec = 0.043 * wc **1.5 * fck**0.5
    return Ec

def RatioYoungModules(Ec : float,Es : float = 2*10**5)-> float:
    """_summary_

    Args:
        Ec (float): MPa
        Es (float, optional): MPa. Defaults to 2*10**5.
        

    Returns:
        float: _description_
    """
    return round(Es/Ec,3)

def ChengedConcToSteelArea(n : float, Ac)-> float:
    return round(Ac/n,3)

def CrushConcCapacity(fck : float, Ac : float)-> float:
    return round(0.85*fck*Ac,3)

def YieldBeamCapacity(fy : float, As : float)-> float:
    return round(fy*As,3)

def OneStudShearCapacity(Asa : float, fck : float, Ec : float, Rg : float, Rp : float, Fu : float = 448)-> float:
    Qn = 0.5 * Asa * (fck*Ec)**0.5
    print(f"Qn = 0.5 * Asa * (fck*Ec)**0.5 = {round(0.5 * Asa * (fck*Ec)**0.5,3)}")
    TrashHold = Rg*Rp*Asa*Fu
    if Qn > TrashHold:
        Qn = TrashHold
        print(f"Qn = {round(Qn,3)} > Rg*Rp*Asa*Fu = {round(0.5 * Asa * (fck*Ec)**0.5,3)} ==> Qn = {round(0.5 * Asa * (fck*Ec)**0.5,3)}")
    return round(Qn,3)

def ShearStudCapacity(N : int, Qn : float)-> float:
    """_summary_

    Args:
        N (int): Total shear stud number
        Qn (float): One stud shear capacity

    Returns:
        float: _description_
    """
    return round(N*Qn,3)

def EffectiveSlabWidth(L : float, Lu : float) -> float:
    """Efektif kompozit döşeme genişliği hesabı

    Args:
        L (float): Kiriş uzunluğu birim : m
        Lu (float): Kiriş aralığı birim : m

    Returns:
        b_eff float: efektif döşeme genişliği birim : m
    """
    b1 = L/8
    b2 = Lu/2

    b = 2*min(b1,b2)

    return b

def Calc_tc(hr : float, Ycon : float,IsParallel : bool)-> float:
    if IsParallel:
        tc = Ycon - (hr/2)
    else:
        tc = Ycon - hr

    return tc

def GetRp(Hs : float, hr : float, t_studhead : float = 5,IsPitchParaleltoBeam: bool=False)-> float:
    """Şekil verilmiş döşeme sacı için azaltma katsayısı

    Args:
        IsPitchParaleltoBeam (bool, optional): Döşeme sacı hadveleri kirişlere paralel ise True değilse False. Defaults to False.

    Returns:
        float: Rp değeri
    """
    e_og = Hs - hr/2 - t_studhead
    if IsPitchParaleltoBeam:
        Rp = 0.75
    if IsPitchParaleltoBeam == False:
        if e_og < 50:
            Rp = 0.6
        if e_og >= 50:
            Rp = 0.75
    return Rp

def GetRg(StudsNumberInFlangeWidth : int, wr : float, hr : float, IsPitchParaleltoBeam: bool=False)-> float:
    """Şekil verilmiş döşeme sacı için azaltma katsayısı

    Args:
        StudsNumberInFlangeWidth (int): Kiriş başlık genişliğinde kaynaklanacak kayma çivisi adeti
        wr (float): Hadve genişliği
        hr (float): Hadve yüksekliği
        IsPitchParaleltoBeam (bool, optional): Döşeme sacı hadveleri kirişlere paralel ise True değilse False. Defaults to False.

    Returns:
        float: Rg değeri
    """
    ratio = wr/hr

    if IsPitchParaleltoBeam:
        if ratio < 1.5:
            Rg = 0.85
        else:
            Rg = 1.0
    else:
        if StudsNumberInFlangeWidth == 1:
            Rg = 1.0
        if StudsNumberInFlangeWidth == 2:
            Rg = 0.85
        if StudsNumberInFlangeWidth >= 3:
            Rg = 0.7
    
    return Rg

def Act(Ac : float, n : float)-> float:
    """_summary_

    Args:
        Ac (float): _description_
        n (float): Çelik elastisite modülünün beton elastisite modülüne oranı

    Returns:
        float: _description_
    """
    return Ac/n

def Calc_I_tr(Act : float,n : float,b_eff : float, hr : float, tc : float, hb : float,Ab : float, Ibeam : float)-> float:
    """_summary_

    Args:
        n (float): Çelik elastisite modülünün beton elastisite modülüne oranı
        b_eff (float): Efektif döşeme genişliği
        hr (float): Hadve yüksekliği
        tc (float): Beton döşeme yüksekliği
        hb (float): Kiriş yüksekliği
        Ab (float): Kiriş alanı
        Ibeam (float): Kiriş atalet momenti

    Returns:
        float: Dönüştürülmüş kesitin atalet momenti
    """

    Ict = b_eff * tc**3 / (12 * n)
    print(f"Ict = {Ict}")

    y_beam = tc + hr + hb/2
    y_conc = tc / 2
    print(f"y_beam = {y_beam}, y_conc ={y_conc}")

    TotalAy = Act * y_conc + Ab * y_beam
    TotalA = Act + Ab
    print(f"TotalAy = {TotalAy}, TotalA = {TotalA}")

    Y = TotalAy/TotalA
    print(f"Y ={Y}")

    d_conc = y_conc - Y
    d_beam = y_beam - Y
    print(f"d_conc ={d_conc}, d_beam = {d_beam}")

    IAd2_conc = Ict + (Act * d_conc**2)
    IAd2_beam = Ibeam + (Ab * d_beam**2)
    print(f"IAd2_conc = {IAd2_conc}, IAd2_beam = {IAd2_beam}")

    Itr = IAd2_beam + IAd2_conc

    return Itr

def Calc_Cf(Vbeam : float, Vcon : float):
    return min(Vbeam,Vcon)

def Calc_I_eff(Ibeam : float, TotalQn : float, Cf : float, Itr : float)-> float:
    ratiocomposite = (TotalQn / Cf)

    if ratiocomposite < 0.25:
        print(f"Kompozitlik oranı 0.25 değerinin altında olamaz stud çivisini arttırın veya daha yüksek dayanımlı bir stud çivisi seçin. {round(ratiocomposite,3)} < 0.25")
        return 0.0

    Ieff = Ibeam + ratiocomposite**0.5 * (Itr - Ibeam)

    return Ieff


def PTEInWebMn():
    pass

def PTEInFlangeMn():
    pass

def PTEInSlabMn():
    pass

def CompositeBeamDesignFlexuralCapacity(C_conc : float, T_steel : float, Ycon : float,
                                        BeamAs : float, BeamFy : float, Hbeam : float, t_flange : float, b_flange : float,
                                        Ac : float,hr : float,fck : float, beff : float, tc : float, t_web : float, fi_b : float = 0.9) -> float:

    C = min(C_conc,T_steel)
    a = C / (0.85 * fck * beff)
    print(f"a = {a} mm")
    Y2 = Ycon - (a/2)
    print(f"Y2 = {Y2} mm")

    if C_conc < T_steel : 
        print(f"Kompozit kiriş kısmi etkileşimlidir. Kompozitlik oranı %25'in altına inmemelidir.")
 
        Y1 = round((T_steel - C_conc) / (2*BeamFy*b_flange),2) # çelik kesitte basınç başlıkta kabulü ile basınç derinliği hesabı
        print(f"Basınç bloğu başlıkta kabul edilirse; Y1(veya tf') = {Y1} mm")
        
        if Y1 < t_flange: # çelik kesitte basınç derinliği başlık kalınlığından küçükse PTE başlıktadır.
            print("PTE kiriş başlığındadır.")
            Csflange = BeamFy*b_flange*Y1
            print(f"Csflange = Fy*b_flange*Y1 = {Csflange} N")
            DesignMn = fi_b * ( (C_conc*(Y1+Y2)) + (2*Csflange*Y1/2) + (BeamAs*BeamFy*( (Hbeam/2) - Y1)) )
            print(f"φMn = φ * ((C_conc*(Y1+Y2)) + (2*Csflange*Y1/2) + (BeamAs*BeamFy*( (Hbeam/2) - Y1))) = {fi_b} * {round(C_conc*(Y1+Y2),2)} +  {round( (2*Csflange*Y1/2),2)} + {round((BeamAs*BeamFy*( (Hbeam/2) - Y1)),2)} = {round(DesignMn,3)}"
                  )
        
        if Y1 >= t_flange: # çelik kesitte basınç derinliği başlık kalınlığından büyükse PTE gövdededir ve Y1 gövdedeki basınç ile yeniden hesaplanır.
            print("PTE kiriş gövdesindedir.Çelikteki basınç derinliği(Y1 veya tf') yeniden hesaplanacak...")
            Cflange = b_flange * t_flange * BeamFy
            print(f"Cflange = b_flange * t_flange * Fy = {Cflange} N")
            Y1 = ((T_steel - C_conc - 2*Cflange) / (2*t_web*BeamFy)) + t_flange
            print(f"Y1 = ((T_steel - C_conc - 2*Cflange) / (2*t_web*Fy)) + t_flange = {Y1}mm")
            Cweb    = t_web * BeamFy * (Y1 - t_flange)
            print(f"Cweb = t_web * Fy * (Y1 - t_flange) = {Cweb} N")
            DesignMn = fi_b * (C_conc*(Y1+Y2) + 2*Cflange*(Y1 - 0.5*t_flange) + 2*Cweb*(0.5*(Y1-t_flange)) + T_steel*(0.5*Hbeam-Y1))
            print(f"φMn = φ * (C_conc*(Y1+Y2) + 2*Cflange*(Y1 - 0.5*t_flange) + 2*Cweb*(0.5*(Y1-t_flange)) + T_steel*(0.5*Hbeam-Y1)) = {fi_b} * [{round(C_conc*(Y1+Y2),3)} + {round(2*Cflange*(Y1 - 0.5*t_flange),3)} + {round(2*Cweb*(0.5*(Y1-t_flange)),3)} + {round(T_steel*(0.5*Hbeam-Y1),3)}] = {round(DesignMn,3)} ")

    if C_conc >= T_steel :
        print(f"Kompozit kiriş tam etkileşimlidir. Plastik tarafsız eksen beton döşemenin içindedir.")
        DesignMn = fi_b * min(C_conc,T_steel) * ( 0.5*Hbeam + hr + tc - 0.5*a)
        print(f"φMn = φ * (min(C_conc,T_steel) * ( 0.5*Hbeam + hr + tc - 0.5*a)) \n= {fi_b} * {round(min(C_conc,T_steel),2)} *  {round( ( 0.5*Hbeam + hr + tc - 0.5*a),2)} = {round(DesignMn,3)}")

    return round(DesignMn,2)


def calc_w_cdl(DeadLoad : float, GirdersSpaceLength : float)-> float:
    """Yapım aşamasındaki sabit yük

    Args:
        DeadLoad (float): döşeme artı kiriş ağırlığı
        GirdersSpaceLength (float): Kiriş aralığı

    Returns:
        _type_: _description_
    """
    return DeadLoad * GirdersSpaceLength

def calc_w_sdl(SuperDeadLoad : float, GirdersSpaceLength : float)-> float:
    """Kompozitlik sonrası(yapım sonrası) üst üste eklenmiş çizgisel sabit yük(Kaplama + bölme duvar + mekanik,elektrik yükleri) N/mm or kN/m

    Args:
        SuperDeadLoad (float): üst üste eklenmiş sabit yük(Kaplama + bölme duvar + mekanik,elektrik yükleri) N/mm2 or kN/m2
        GirdersSpaceLength (float): Kiriş aralığı

    Returns:
        _type_: _description_
    """
    return SuperDeadLoad * GirdersSpaceLength

def calc_w_ll(LiveLoad : float, GirdersSpaceLength : float)-> float:
    """_summary_

    Args:
        LiveLoad (float): Hareketli yük
        GirdersSpaceLength (float): Kiriş aralığı

    Returns:
        _type_: _description_
    """
    return LiveLoad * GirdersSpaceLength

def calc_w_tl(w_dl : float, w_ll : float)-> float:
    """Arttırılmış toplam yük

    Args:
        w_dl (float): Ölü yük yapım aşaması için w_cdl veya sonrası için sabit yük girilebilir kN/m or N/mm
        w_ll (float): Hareketli yük yapım aşaması için 1 kN/m^2 veya sonrası için w_ll girilebilir kN/m or N/mm

    Returns:
        float: _description_
    """
    wu1 = 1.4 * w_dl
    wu2 = (1.2 * w_dl + 1.6 * w_ll)
    wu = max(wu1,wu2)
    return wu

def SimpleCompositeBeamDeflection(w : float, Lbeam : float, I : float, Ebeam : float = 2*10**5)-> float:
    """_summary_

    Args:
        w (float): İlgili çizgisel yük
        Lbeam (float): Kiriş uzunluğu
        I (float): İlgili atalet momenti
        Ebeam (float, optional): Çelik kiriş elastisite modülü. Defaults to 2*10**5.

    Returns:
        _type_: _description_
    """
    delta = (5/384) * (w * Lbeam**4) / (Ebeam * I)
    return round(delta,2)

def MainCompositeBeamDeflection(P : float, Lbeam : float, I : float, Ebeam : float = 2*10**5)-> float:
    """_summary_

    Args:
        P (float): İlgili noktasal yük
        Lbeam (float): Kiriş uzunluğu
        I (float): İlgili atalet momenti
        Ebeam (float, optional): Çelik kiriş elastisite modülü. Defaults to 2*10**5.

    Returns:
        _type_: _description_
    """
    delta = (1/28) * (P * Lbeam**3) / (Ebeam * I)
    return delta

def Camber(delta_cdl : float, Lbeam : float, Limit : int = 19)-> float:
    """Ters sehim hesabı, 19mm altı ani sehim veya 7.6m uzunluğundan az kiriş uzunluğu için yapma

    Args:
        delta_cdl (float): _description_
        Lbeam (float): _description_
        Limit (float): _description_

    Returns:
        _type_: _description_
    """
    delta_c = 0.75 * delta_cdl
    if delta_cdl < Limit or Lbeam < 7600:
        print(f"delta_cdl = {delta_cdl}mm < {Limit}mm or Lbeam = {Lbeam} < 7600mm olduğu için ters sehime gerek yoktur.")
        delte_c = 0.0
    return delte_c

def calc_Delta_TL(delta_cdl : float, delta_sdl : float, delta_ll : float, delta_c : float)-> float:
    """_summary_

    Args:
        delta_cdl (float): Yapım aşaması sabit yük nedeniyle düşey yerdeğiştirme
        delta_sdl (float): Super dead load (kaplama+mekanik+sıva+alçı vs.)
        delta_ll (float): Hareketli yük nedeniyle düşey yerdeğiştirme
        delta_c (_type_): Ters sehim miktarı

    Returns:
        _type_: _description_
    """
    delta_cdl_net = delta_cdl - delta_c
    return round(delta_cdl_net + delta_ll + delta_sdl,2)

def DeflectionChecks(delta_tl : float, delta_ll : float, Lbeam : float)-> bool:

    if delta_tl > Lbeam/360 or delta_ll > Lbeam/240:
        return False 
    return True


