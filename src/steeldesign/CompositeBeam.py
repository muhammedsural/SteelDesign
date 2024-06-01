# Rib : Hadve
# Camber : Ters sehim
# concrete cover above the top of the headed stud anchors. Hadve Uzerinde Kalan Stud Boyutları Kontrolu

from dataclasses import dataclass
import math


@dataclass
class CompositeBeams:
    # Birimler N,mm
    # Yapım aşaması yükleri
    DeadLoad   : float = 2.5 #kN/m^2
    LiveLoad_c : float = 1 #kN/m^2

    # Kompozit çalışma aşaması yükleri
    SuperDeadLoad : float = 2.0 #kN/m^2
    LiveLoad      : float = 4.0 #kN/m^2
    w_girder      : float = 1.0 #kN/m kiriş ağırlığı

    # Beton bilgisi
    f_ck     : float = 30     #N/mm2
    wc       : float = 2400   #kg/m3

    # Çelik malzeme bilgisi
    Fy       : float = 355        #N/mm2
    Fu_beam  : float = 450        #N/mm2

    # Çelik enkesit özellikleri
    Abeam     : float = 9_880     #mm^2
    Hbeam     : float = 450        #mm
    Hweb      : float = 378.8      #mm
    b_flange  : float = 190        #mm
    t_flange  : float = 14.6        #mm
    t_web     : float = 9.4        #mm
    Ix        : float = 33_740*10**4 #mm^4
    Ycon      : float = 130        #mm Çelik kesit üst başlığından en üst beton lifine olan mesafe

    # Kiriş uzunluk ve aralık bilgisi
    Laralık  : float = 3000  #mm
    Lbeam    : float = 7500  #mm

    # Stud çivisi bilgisi
    D_stud                  : float = 19      #mm
    H_stud                  : float = 100     #mm
    b_studhead              : float = 32      #mm
    t_studhead              : float = 5      #mm
    Fy_stud                 : float = 355     #N/mm2 çelik ankrajın minimum(karakteristik) akma dayanımı
    Fu_stud                 : float = 450     #N/mm2 çelik ankrajın minimum(karakteristik) çekme dayanımı
    CompRatio               : float = 0.25    #Kompozitlik oranı minimum %25 olabilir. %100 tam etkileşimli kompozit demektir.
    Nw                      : float = 2       #Adet Kesit başlığının genişliğinde atılan stud çivisi adeti
    x                       : float = 30       #mm Kesit başlığının genişliğinde atılan stud çivileri arasındaki mesafe
    IsWebAlignmentWelded    : bool  = False   #Stud çivisi kiriş gövdesi izasında mı kaynaklanıyor.

    # Metal sac bilgisi
    hr          : float     = 50    #mm
    wr          : float     = 165   #mm
    t_sac       : float     = 1.2   #mm
    RibsDistance: float     = 330   #mm 2*wr
    IsParallel  : bool      = False

    def Designer(self)->None:
        """Verilmiş bilgilere göre basit mesnetli kompozit kirişin tasarım limit durumlarını kontrol eder henüz hazır değil.

        Returns:
            None
        """
        print("=="*50)
        print("Design Code Requirements\n")
        GeomCheck = self.ConcAvailableStressCheck(f_ck = self.f_ck)
        GeomCheck = self.SteelAvailableStressCheck(Fy = self.Fy)
        GeomCheck = self.MetalDeckCheck(hr = self.hr, wr = self.wr)
        GeomCheck = self.ConcreteCoverAboveTopOfHeadedStudAnchorsChecks(hr = self.hr, t_sac = self.t_sac, h_stud = self.H_stud, Ycon = self.Ycon)
        GeomCheck = self.StudCheck(Ds = self.D_stud, tf = self.t_flange, Hs = self.H_stud, IsWebAlignmentWelded=False)
        if GeomCheck != True:
            print("Geometrik kontroller sağlanmalı hesap yapılmadı!!!\n")
            return None
        # Kiriş enkesit kontrolü
        SectionCheck = self.SectionCheck(Hbeam=self.Hbeam, t_web=self.t_web, Fy=self.Fy)
        if SectionCheck != True:
            print("Kesit değiştirin!!!\n")
            return None
        
        print("=="*50)
        print("Yapım aşaması\n")
        W_G = self.Calc_Load(Load = self.DeadLoad, GirdersSpaceLength = self.Laralık/10**3) + self.w_girder
        W_Q = self.Calc_Load(Load = self.LiveLoad_c, GirdersSpaceLength = self.Laralık/10**3)

        print("Yapım aşaması sabit yüklerinden(döşeme ve çelik kiriş) kaynaklı deplasman\n")
        delta_cdl = self.SimpleCompositeBeamDeflection(w=W_G, Lbeam = self.Lbeam, I = self.Ix)
        self.DeflectionChecks2(delta=delta_cdl, L=self.Lbeam, Ratio=360)

        print("Ters sehim miktarı\n")
        delta_c = self.Camber(delta_cdl = delta_cdl, Lbeam = self.Lbeam)

        delta_yll = self.SimpleCompositeBeamDeflection(w=W_Q, Lbeam = self.Lbeam, I = self.Ix)
        print(f"Yapım aşaması hareketli yüklerinden kaynaklı deplasman {delta_yll}mm\n")

        
        delta_ytl = self.calc_Delta_TL(delta_cdl=delta_cdl, delta_sdl=0., delta_ll=delta_yll,delta_c=delta_c)
        print(f"Yapım aşaması toplam düşey yerdeğiştirme = {delta_ytl}mm, super dead düşey yerdeğiştirmesi yapım öncesi olmadığı için 0.0\n")
        self.DeflectionChecks2(delta=delta_ytl, L=self.Lbeam, Ratio=240)

        print("=="*50)
        print("Verilen kompozitlik oranına göre stud çivisi sayısının hesaplanması\n")
        b_eff       = self.EffectiveSlabWidth(L = self.Lbeam, Lu = self.Laralık) # Effektif döşeme genişliği
        tc          = self.Calc_tc(hr = self.hr,Ycon = self.Ycon, IsParallel = self.IsParallel) # Stud çivisiz beton yüksekliği
        Ac          = self.Calc_Ac(b_eff=b_eff, tc=tc) # Stud çivisiz beton alanı
        Cc          = self.CrushConcCapacity(fck = self.f_ck,Ac=Ac)
        Cs          = self.YieldBeamCapacity(fy = self.Fy, As = self.Abeam)
        Cf          = self.Calc_Cf(Vbeam=Cs, Vcon=Cc)
        Ec          = self.ConcreteYoungModules(fck = self.f_ck, wc=self.wc)
        A_sa        = 3.14 * self.D_stud**2 /4
        Rp          = self.GetRp(Hstud = self.H_stud, hr = self.hr, t_studhead = self.t_studhead, IsPitchParaleltoBeam = self.IsParallel)
        Rg          = self.GetRg(StudsNumberInFlangeWidth=self.Nw, wr = self.wr, hr = self.hr, IsPitchParaleltoBeam = self.IsParallel)
        Qn          = self.OneStudShearCapacity(Asa=A_sa, fck = self.f_ck, Ec=Ec, Rg=Rg, Rp=Rp, Fu = self.Fu_beam)
        # N_stud      = math.ceil((self.CompRatio * Cf) / (Qn)) * self.Nw
        # print(f"%{self.CompRatio*100} kompozitlik oranı için belirlenen stud çivisi sayısı {self.Nw} * {N_stud/self.Nw} = {N_stud}.\n")
        N_stud = self.Calc_StudsNumber(Cf=Cf, CompRatio=self.CompRatio, Qn=Qn, Nw=self.Nw, RibsDistance=self.RibsDistance, L_beam=self.Lbeam, IsParallel=self.IsParallel)
        if N_stud <= 0 :
            return None
        Vstud       = N_stud * Qn
        Vmin        = min(Vstud, Cs, Cc)
        
        print("Dizayn eğilme kapasitesinin hesaplanması \n")
        a           = self.Calc_a(Cf =Vmin, fck = self.f_ck, b_eff = b_eff)
        Y2          = self.Calc_Y2(Ycon = self.Ycon, a = a)
        C_flange    = self.Calc_Cflange(t_flange = self.t_flange, b_flange = self.b_flange, BeamFy = self.Fy)
        Y1          = self.Calc_Y1(T_steel=Cs, C_conc=Vmin, C_flange=C_flange, t_flange = self.t_flange, t_web = self.t_web, BeamFy = self.Fy)
        C_web       = self.Calc_Cweb(Y1=Y1, t_flange = self.t_flange, t_web = self.t_web, BeamFy = self.Fy)
        Mn_web      = self.PTEInWebMn(T_steel=Cs, C_conc=Vmin, Cflange=C_flange, Cweb=C_web, Hbeam = self.Hbeam, t_flange = self.t_flange, Y1=Y1, Y2=Y2)
        Mn_flange   = self.PTEInFlangeMn(C_conc=Vmin, Cflange=C_flange, Hbeam = self.Hbeam, BeamAs = self.Abeam, BeamFy = self.Fy, Y1=Y1, Y2=Y2)
        Mn_slab     = self.PTEInSlabMn(Cf=Cf, Hbeam = self.Hbeam, hr = self.hr, tc=tc, a=a)
        Mn_design   = self.CompositeBeamDesignFlexuralCapacity2(C_conc=Vmin, T_steel=Cs,Mn_web=Mn_web, Mn_slab=Mn_slab, Mn_flange=Mn_flange, Y1=Y1, t_flange = self.t_flange, fi_b=0.9)

        print("Arttırılmış yükler altında basit kirişteki talep eğilme dayanımının hesaplanması \n")
        W_superdeadload = self.Calc_Load(Load = self.SuperDeadLoad, GirdersSpaceLength = self.Laralık/10**3)
        W_G_composite   = W_G + W_superdeadload
        W_Q_composite   = self.Calc_Load(Load = self.LiveLoad, GirdersSpaceLength = self.Laralık/10**3)
        W_TL            = self.calc_w_tl(w_dl=W_G_composite, w_ll=W_Q_composite)
        M_demand        = round(W_TL * self.Lbeam**2 /8, 3)
        print(f"Mdemand = {M_demand/10**6}kNm\n")

        CapacityCheck   = self.CompositeBeamFlexuralCapacityCheck(M_demand=M_demand, Mn_design=Mn_design)
        if CapacityCheck > 1:
            print("Kapasite yetersiz!!!")

        n = self.RatioYoungModules(Ec=Ec)
        Act = self.ChengedConcToSteelArea(n=n, Ac=Ac)
        Itr = self.Calc_I_tr(Act=Act, n=n, b_eff=b_eff, hr = self.hr, tc=tc, hb = self.Hbeam, Ab = self.Abeam, Ibeam = self.Ix) #Tam etkileşimli kompozit kiriş sehim kontrolü için kullanılır
        Ieff = self.Calc_I_eff(Ibeam = self.Ix, TotalQn=Vstud, Cf=Cf, Itr=Itr)
        I_real = self.Calc_I_real(I_eff=Ieff) #Kısmi etkileşimli kompozit kiriş sehim kontrolleri için kullanılır.
        
        delta_cll = self.SimpleCompositeBeamDeflection(w=W_Q_composite, Lbeam=self.Lbeam, I=I_real)
        delta_csdl = self.SimpleCompositeBeamDeflection(w=W_superdeadload, Lbeam=self.Lbeam, I=I_real)
        delta_ctl = delta_cdl + delta_cll + delta_csdl

        self.DeflectionChecks2(delta=delta_cll, L=self.Lbeam, Ratio=360)
        self.DeflectionChecks2(delta=delta_ctl, L=self.Lbeam, Ratio=240)


        # Metal sacın kirişe dik atıldığı durumda, stud çivisi sayısını hadve boşlukları ara mesafesi belirler. örneğin hadveler arası mesafe 305mm ve 9150mm uzunluğunda bir kirişe max 9150/305=30 adet atılabilir. Tam etkileşimli durumda oluyorsa bu durum çift sıraya veya kiriş arttırımına gidilmek zorunluluğu ortaya çıkar.
        if self.Nw > 1:
            self.DistanceBetweenTwoStudsCheck(x=self.x, Ds = self.D_stud)

        self.StudSpaceCheck(Ds = self.D_stud, s=self.RibsDistance, Ycon = self.Ycon)
        pass
    
    def Calc_StudsNumber(self, Cf : float, CompRatio : float, Qn : float, Nw : float, RibsDistance : float, L_beam : float, IsParallel : bool) -> int:
        """Kompozit kirişte belli sınır durumlara göre atılması gereken veya atılabilecek stud çivi sayısını hesaplar

        Args:
            Cf (float): Cconc ve Tsteel kuvvetlerinden minimum olanı
            CompRatio (float): Kompozitlik oranı (ToplamQn / Cf)
            Qn (float): Tek bir stud çivisi kayma dayanımı
            Nw (float): Başlıkta yan yana atılan çivi sayısı
            RibsDistance (float): Hadve aralığı
            L_beam (float): Kiriş uzunluğu
            IsParallel (bool): Hadvelerin kirişe paralellik durumu paralelse True değilse False

        Returns:
            int: Stud çivi sayısı
        """

        N_stud      = math.ceil((CompRatio * Cf) / (Qn)) * Nw
        print(f"%{CompRatio*100} kompozitlik oranı için belirlenen stud çivisi sayısı {Nw} * {N_stud/Nw} = {N_stud}.\n")

        if IsParallel != True:
            n_max = math.floor(L_beam/(RibsDistance*2)) # 2 olukta bir atılması öngörülmüştür.

            if N_stud > n_max and CompRatio == 1:
                if N_stud > n_max*2 and Nw > 1:
                    print("Atılabilecek maksimum stud çivisi sayısından fazla stud çivisi gerekmektedir ve tam etkileşimli kesit olduğu için kiriş kesiti arttırılmalıdır.\n")
                    N_stud = 0.0
                    return N_stud
                print("Başlıkta 2 şerli olacak şekilde atama yapın ==> Nw = 2 yapın...\n")

        return N_stud
    
    def Calc_Ac(self, b_eff : float, tc : float)-> float:
        """Net beton örtüsü

        Args:
            b_eff (float): Efektif döşeme genişliği
            tc (float): Beton örtüsü kalınlığı

        Returns:
            float: Beton örtüsü alanı
        """
        return round(b_eff*tc , 2)

    def SectionCheck(self, Hbeam : float, t_web : float, Fy : float)-> bool:
        """Kesitin süneklilik kontrolü

        Args:
            Hbeam (float): Kesit yüksekliği
            t_web (float): Kesit gövde kalınlığı
            Fy (float): Kesit malzemesinin akma gerilmesi

        Returns:
            bool: Kontrolden geçtiyse True geçemediyse False
        """
        alfa = round(Hbeam /t_web ,2)
        trashold = round(3.76*(2*10**5 / Fy)**0.5 ,2)
        if alfa > trashold:
            print(f"alfa = {alfa} > 3.76*(E/Fy)^0.5 = {trashold} X\n")
            return False
        print(f"alfa = {alfa} ≤ 3.76*(E/Fy)^0.5 = {trashold} √\n")
        return True
    
    def StudCheck(self,Ds : float, tf : float, Hs : float, IsWebAlignmentWelded : bool = False)-> bool:
        """Stud çivisi ile ilgili geometrik kontrolleri yapar.

        Args:
            Ds (float): Stud çivisinin çapı
            tf (float): Kirişin başlık kalınlığı
            Hs (float): Stud çivisi yüksekliği
            IsWebAlignmentWelded (bool, optional): Stud çivisi başlık hizasında kaynaklı ise True değilse False. Defaults to False.

        Returns:
            bool: Geometrik kontrollerden geçtiyse True geçemediyse False
        """

        if Ds > 2.5*tf or Ds > 19:
            print(f"Ds = {Ds}mm > 2.5*tf = {2.5*tf}mm X - TSSDC 12.8.1\n")
            print(f"Ds = {Ds}mm > 19mm X - TSSDC 12.8.1")
            return False
        if Hs < 4*Ds:
            print(f"Hs = {Hs}mm < 4*Ds = {4*Ds}mm X - TSSDC 12.8.2\n")
            return False
        if IsWebAlignmentWelded:
            print("Stud çivisi gövde hizasında bağlandığı için bu kontrollere gerek yoktur.\n")
            return True
        print(f"Ds = {Ds}mm ≤ 2.5*tf = {2.5*tf}mm √ - TSSDC 12.8.1\n")
        print(f"Ds = {Ds}mm ≤ 19mm √ - TSSDC 12.8.1\n")
        print(f"Hs = {Hs}mm ≥ 4*Ds = {4*Ds}mm √ - TSSDC 12.8.2\n")
        return True

    def StudSpaceCheck(self,Ds : float, s : float, Ycon : float) -> bool:
        """Stud çivisi aralık kontrolü

        Args:
            Ds (float): Stud çivisinin çapı
            s (float): Stud çivilerinin kaynaklanma aralığı
            Ycon (float): Toplam döşeme yüksekliği

        Returns:
            bool: _description_
        """

        if s < 6*Ds or s > 8*Ycon or s >914:
            print(f"s = {s}mm < {6*Ds}mm X\n")
            print(f"s = {s}mm > {8*Ycon}mm X\n")
            print(f"s = {s}mm > 914mm X\n")
            return False
        print(f"s = {s}mm ≥ {6*Ds}mm √\n")
        print(f"s = {s}mm ≤ {8*Ycon}mm √\n")
        print(f"s = {s}mm ≤ 914mm √\n")
        return True

    def DistanceBetweenTwoStudsCheck(self,x : float, Ds : float)-> bool:
        """Yan yana atılan stud çivileri aralık kontolü

        Args:
            x (float): Stud çivileri arasındaki mesafe
            Ds (float): Stud çivisi çapı

        Returns:
            bool: Kontrolden geçtiyse True geçemediyse False.
        """
        if x < 4*Ds:
            return False
        return True

    def ConcreteCoverAboveTopOfHeadedStudAnchorsChecks(self,hr : float, t_sac : float, h_stud: float, Ycon : float) -> bool:
        """Stud çivisi üzerinde kalan beton ile ilgili geometrik kontrolleri yapar.

        Args:
            hr (float): Hadve yüksekliği
            h_stud (float): Stud çivisi yüksekliği
            Ycon (float): Çelik kesit üst başlığından en üst beton lifine olan mesafe

        Returns:
            bool: Kontrolden geçtiyse True geçemediyse False.
        """
        if h_stud-hr-t_sac < 38 or Ycon - h_stud < 13 or Ycon - hr < 50:
            print(f"h_stud-hr-t_sac = {h_stud-hr-t_sac}mm < 38mm X - TSSDC 12.4.2.3\n")
            print(f"Ycon - h_stud-t_sac = {Ycon - h_stud-t_sac}mm < 13mm X - TSSDC 12.4.2.3\n")
            print(f"Ycon - hr = {Ycon - hr}mm < 50mm X - TSSDC 12.4.2.3\n")
            return False
        print(f"h_stud-hr-t_sac = {h_stud-hr-t_sac}mm ≥ 38mm √ - TSSDC 12.4.2.3\n")
        print(f"Ycon - h_stud-t_sac = {Ycon - h_stud-t_sac}mm ≥ 13mm √ - TSSDC 12.4.2.3\n")
        print(f"Ycon - hr = {Ycon - hr}mm ≥ 50mm √ - TSSDC 12.4.2.3\n")
        return True

    def MetalDeckCheck(self,hr : float, wr : float)-> bool:
        """Metal sacın geometrik kontrollerini yapar

        Args:
            hr (float): Hadve yüksekliği
            wr (float): Hadve genişliği

        Returns:
            bool: Kontrolden geçtiyse True geçemediyse False.
        """
        if hr > 75 or wr < 50 :
            print(f"hr = {hr}mm > 75mm X - TSSDC 12.4.2.3\n")
            print(f"wr = {wr}mm < 50mm X - TSSDC 12.4.2.3\n")
            return False
        print(f"hr = {hr}mm ≤ 75mm √ - TSSDC 12.4.2.3\n")
        print(f"wr = {wr}mm ≥ 50mm √ - TSSDC 12.4.2.3\n")
        return True

    def ConcAvailableStressCheck(self,f_ck : float) -> bool:
        """Beton karakteristik basınç dayanımının min ve max aralığına göre kontrol eder.

        Args:
            f_ck (float): 28 günlük beton numunesinin karakteristik basınç dayanımı MPa(N/mm^2)

        Returns:
            bool: Kontrolden geçtiyse True geçemediyse False.
        """
        if 20 <= f_ck and f_ck<70:
            print(f"20 N/mm^2 ≤ {f_ck} N/mm^2 < 70 N/mm^2 √ - TSSDC 12.2.3(a)\n")
            return True
        else:
            print(f"20 ≤ {f_ck} < 70 X - TSSDC 12.2.3(a)\n")
            return False

    def SteelAvailableStressCheck(self,Fy : float) -> bool:
        """Çelik akma dayanımının min ve max aralığına göre kontrol eder.

        Args:
            Fy (float): Çelik malzemesinin minimum akma gerilmesi dayanımı MPa(N/mm^2)

        Returns:
            bool: Kontrolden geçtiyse True geçemediyse False.
        """
        if Fy <= 460:
            print(f"{Fy} N/mm^2 ≤ 460 N/mm^2 √ - TSSDC 12.2.3(c)\n")
            return True
        else:
            print(f"Çelik sınıfı yönetmelik şartını sağlamamaktadır => {Fy} > {460} X - TSSDC 12.2.3(c)\n")
            False

    def ConcreteYoungModules(self,fck : float,wc : float = 2320)-> float:
        """Betonun elastisite modülünü hesaplar.

        Args:
            fck (float): 28 günlük beton numunesinin karakteristik basınç dayanımı MPa(N/mm^2)
            wc (float, optional): Beton birim hacim ağırlığı . Defaults to 2320 kg/m^3.

        Returns:
            float: Ec
        """
        Ec = 0.043 * wc **1.5 * fck**0.5
        return Ec

    def RatioYoungModules(self,Ec : float,Es : float = 2*10**5)-> float:
        """Çelik ile beton malzemesinin elastisite oranını hesaplar.

        Args:
            Ec (float):Betonun elastisite modülü MPa
            Es (float, optional): Çeliğin elastisite modülü MPa. Defaults to 2*10**5.
            

        Returns:
            float: n
        """
        return round(Es/Ec,3)

    def ChengedConcToSteelArea(self,n : float, Ac)-> float:
        """Dönüştürülmüş beton alanını hesaplar

        Args:
            n (float): Elastisite oranı çelikle beton malzemesinin
            Ac (_type_): Beton alanı

        Returns:
            float: Dönüştürülmüş beton alanı Act
        """
        return round(Ac/n,3)

    def CrushConcCapacity(self,fck : float, Ac : float)-> float:
        """Beton ezilme dayanımını hesaplar

        Args:
            fck (float): 28 günlük beton numunesinin karakteristik basınç dayanımı MPa(N/mm^2)
            Ac (float): Beton alanı

        Returns:
            float: Beton ezilme dayanımı
        """
        return round(0.85*fck*Ac,3)

    def YieldBeamCapacity(self,fy : float, As : float)-> float:
        """Çelik kiriş akma dayanımını hesaplar.

        Args:
            fy (float): Çelik malzemesinin minimum akma dayanımı N/mm^2
            As (float): Çelik kirişin alanı mm^2

        Returns:
            float: Çelik kiriş akma dayanımı
        """
        return round(fy*As,3)

    def OneStudShearCapacity(self,Asa : float, fck : float, Ec : float, Rg : float, Rp : float, Fu : float = 448)-> float:
        """Tek bir stud çivisin kesme dayanımını hesaplar.

        Args:
            Asa (float): Stud çivisinin alanı
            fck (float): 28 günlük beton numunesinin karakteristik basınç dayanımı MPa(N/mm^2)
            Ec (float): Betonun elastisite modülü MPa
            Rg (float): Çelik sac azaltma katsayısı
            Rp (float): Çelik sac azaltma katsayısı
            Fu (float, optional): Stud çivisi malzemesinin kopma gerilmesi dayanımı. Defaults to 448 MPa.

        Returns:
            float: Tek bir stud çivisin kesme dayanımı Qn
        """
        Qn = round(0.5 * Asa * (fck*Ec)**0.5,3)
        print(f"Qn = 0.5 * Asa * (fck*Ec)**0.5 = {Qn/10**3}kN\n")
        TrashHold = round(Rg*Rp*Asa*Fu ,3)
        if Qn > TrashHold:
            print(f"Qn = {round(Qn,3)/10**3}kN > Rg*Rp*Asa*Fu = {Rg}*{Rp}*{Asa}*{Fu} = {TrashHold/10**3}kN ==> Qn = {TrashHold/10**3}kN\n")
            Qn = TrashHold
        return round(Qn,3)

    def ShearStudCapacity(self,N : int, Qn : float)-> float:
        """Toplam stud çivisin kesme dayanımını hesaplar.

        Args:
            N (int): Stud çivisi sayısı; Total shear stud number 
            Qn (float): Bir adet stud çivisi kesme dayanımı; One stud shear capacity N

        Returns:
            float: Toplam stud çivisin kesme dayanımı
        """
        return round(N*Qn,3)

    def EffectiveSlabWidth(self,L : float, Lu : float) -> float:
        """Efektif kompozit döşeme genişliği hesabı

        Args:
            L (float): Kiriş uzunluğu birim : mm
            Lu (float): Kiriş aralığı birim : mm

        Returns:
            b_eff float: efektif döşeme genişliği birim : mm
        """
        b1 = L/8
        b2 = Lu/2

        b = 2*min(b1,b2)
        print(f"b_eff = {b}mm\n")
        return b

    def Calc_tc(self,hr : float, Ycon : float,IsParallel : bool)-> float:
        """Net beton örtüsü kalınlığını hesaplar

        Args:
            hr (float): Metal sac hadve yüksekliği. mm
            Ycon (float): Toplam döşeme yüksekliği. mm
            IsParallel (bool): Metal sacın kirişlerin boyuna eksen doğrultusuna paralel atılıp atılmama durumu. Paralelse True değilse False

        Returns:
            float: Net beton örtüsü kalınlığı
        """
        if IsParallel:
            tc = Ycon - (hr/2)
        else:
            tc = Ycon - hr
        print(f"tc = {tc}mm")
        return tc

    def GetRp(self,Hstud : float, hr : float, t_studhead : float, IsPitchParaleltoBeam: bool=False)-> float:
        """Şekil verilmiş döşeme sacı için azaltma katsayısı

        Args:
            Hstud (float)       : Stud çivisi yüksekliği. mm
            hr (float)          : Metal sacın hadve yüksekliği. mm
            t_studhead (float)  : Stud çivisi başlık kalınlığı. mm
            IsPitchParaleltoBeam (bool, optional): Döşeme sacı hadveleri kirişlere paralel ise True değilse False. Defaults to False.

        Returns:
            float: Rp değeri
        """
        
        e_og = Hstud - hr/2 - t_studhead
        if IsPitchParaleltoBeam:
            Rp = 0.75
        if IsPitchParaleltoBeam == False:
            if e_og < 50:
                Rp = 0.6
            if e_og >= 50:
                Rp = 0.75
        print(f"Rp = {Rp}\n")
        return Rp

    def GetRg(self,StudsNumberInFlangeWidth : int, wr : float, hr : float, IsPitchParaleltoBeam: bool=False)-> float:
        """Şekil verilmiş döşeme sacı için azaltma katsayısı

        Args:
            StudsNumberInFlangeWidth (int): Kiriş başlık genişliğinde kaynaklanacak kayma çivisi adeti
            wr (float): Metal sacın hadve genişliği mm
            hr (float): Metal sacın hadve yüksekliği mm
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
        print(f"Rg = {Rg}\n")
        return Rg

    def Calc_Cf(self,Vbeam : float, Vcon : float):
        """ Vconc ve Vbeam kuvvetlerinden minimum olanı

        Args:
            Vbeam (float): Çelik kiriş akma dayanımı N
            Vcon (float): Beton ezilme dayanımı N

        Returns:
            _type_:  Cconc ve Tsteel kuvvetlerinden minimum olanı
        """
        return min(Vbeam,Vcon)

    def Calc_I_tr(self,Act : float,n : float,b_eff : float, hr : float, tc : float, hb : float,Ab : float, Ibeam : float)-> float:
        """Dönüştürülmüş kompozir kesitin atalet momentini hesaplar.

        Args:
            n (float): Çelik elastisite modülünün beton elastisite modülüne oranı
            b_eff (float): Efektif döşeme genişliği mm
            hr (float): Hadve yüksekliği mm
            tc (float): Beton döşeme yüksekliği mm
            hb (float): Kiriş yüksekliği mm
            Ab (float): Kiriş alanı mm^2
            Ibeam (float): Kiriş atalet momenti mm^4

        Returns:
            float: Dönüştürülmüş kesitin atalet momenti
        """

        Ict = b_eff * tc**3 / (12 * n)
        # print(f"Ict = {Ict}")

        y_beam = tc + hr + hb/2
        y_conc = tc / 2
        # print(f"y_beam = {y_beam}, y_conc ={y_conc}")

        TotalAy = Act * y_conc + Ab * y_beam
        TotalA = Act + Ab
        # print(f"TotalAy = {TotalAy}, TotalA = {TotalA}")

        Y = TotalAy/TotalA
        # print(f"Y ={Y}")

        d_conc = y_conc - Y
        d_beam = y_beam - Y
        # print(f"d_conc ={d_conc}, d_beam = {d_beam}")

        IAd2_conc = Ict + (Act * d_conc**2)
        IAd2_beam = Ibeam + (Ab * d_beam**2)
        # print(f"IAd2_conc = {IAd2_conc}, IAd2_beam = {IAd2_beam}")

        Itr = IAd2_beam + IAd2_conc

        return Itr

    def Calc_I_eff(self,Ibeam : float, TotalQn : float, Cf : float, Itr : float)-> float:
        """Dönüştürülmüş kesitin efektif atalet momentini hesaplar.

        Args:
            Ibeam (float): Kirişin atalet momenti
            TotalQn (float): Toplam stud çivileri kesme dayanımı
            Cf (float): Vconc ve Vbeam kuvvetlerinden minimum olanı
            Itr (float): Dönüştürülmüş kesit atalet momenti

        Returns:
            float: Dönüştürülmüş kesitin efektif atalet momenti
        """
        ratioselfosite = (TotalQn / Cf)

        if ratioselfosite < 0.25:
            print(f"Kompozitlik oranı 0.25 değerinin altında olamaz stud çivisini arttırın veya daha yüksek dayanımlı bir stud çivisi seçin. {round(ratioselfosite,3)} < 0.25")
            return 0.0

        Ieff = Ibeam + ratioselfosite**0.5 * (Itr - Ibeam)

        return Ieff

    def Calc_I_real(self,I_eff : float)-> float:
        """Dönüştürülmüş kesitin efektif atalet momentinin gerçek olarak kullanılması önerilen atalet momenti. Sehim hesaplarında kullanılabilir.

        Args:
            I_eff (float): Dönüştürülmüş kesitin efektif atalet momenti

        Returns:
            float: Gerçek atalet momenti
        """
        return I_eff * 0.75

    def Calc_a(self,Cf : float, fck : float, b_eff : float)-> float:
        """Beton basınç alanı yüksekliğini hesaplar.

        Args:
            Cf (float): min(selfression_conc,Tension_steel)
            fck (float): Beton karakteristik basınç dayanımı
            b_eff (float): Efektif döşeme genişliği

        Returns:
            float: Beton basınç alanı yüksekliği
        """
        a = round(Cf / (0.85 * fck * b_eff) ,2)
        print(f"a = {a}mm\n")
        return a

    def Calc_Y2(self,Ycon : float, a : float)-> float:
        """Beton basınç kuvvetinin ağırlık merkezi ile çelik enkesit üst kotu arasındaki mesafeyi hesaplar.

        Args:
            Ycon (float): Toplam döşeme yüksekliği
            a (float): Beton basınç alanı yüksekliği

        Returns:
            float: Y2
        """
        Y2 = Ycon - (a/2)
        print(f"Y2 = {Y2}mm\n")
        return Y2

    def Calc_Cflange(self,t_flange:float, b_flange : float, BeamFy:float)-> float:
        """Çelik kesitin başlığındaki basınç kuvvetini hesaplar.

        Args:
            t_flange (float): Çelik kesitin başlık kalınlığı
            b_flange (float): Çelik kesitin başlık genişliği
            BeamFy (float)  : Çelik kesitin malzeme akma dayanımı

        Returns:
            float: Çelik kesitin başlığındaki basınç kuvveti
        """
        Cflange = round(b_flange * t_flange * BeamFy, 3)
        # print(f"Cflange = b_flange * t_flange * Fy = {b_flange} * {t_flange} * {BeamFy} = {Cflange} N")
        return Cflange

    def Calc_Y1(self,T_steel : float, C_conc : float, C_flange, t_flange : float, t_web : float, BeamFy : float)-> float:
        """Plastik tarafsız eksen(PTE) ile çelik enkesitin üst başlık noktası ile arasındaki uzaklığı hesaplar.

        Args:
            T_steel (float): Çelik kesitte çekme kuvveti
            C_conc (float): Betondaki basınç kuvveti
            C_flange (_type_): Başlıktaki basınç kuvveti
            t_flange (float): Çelik kesit başlık kalınlığı
            t_web (float): Çelik kesit gövde kalınlığı
            BeamFy (float): Çelik kesitin malzeme akma dayanımı

        Returns:
            float: Y1
        """
        Y1 = ((T_steel - C_conc - 2*C_flange) / (2*t_web*BeamFy)) + t_flange
        # print(f"Y1 = ((T_steel - C_conc - 2*C_flange) / (2*t_web*Fy)) + t_flange = {Y1}mm")

        if Y1 >= t_flange:
            print(f"Y1 = {Y1} ≥ {t_flange} = t_flange olduğu için PTE çelik kesitin gövdesindedir ve Y1 yeniden hesaplanmalıdır.\n")

            Y1 = ((T_steel - C_conc - 2*C_flange) / (2*t_web*BeamFy)) + t_flange
            print(f"Y1 = ((T_steel - C_conc - 2*Cflange) / (2*t_web*Fy)) + t_flange = {Y1}mm\n")
        if Y1 < 0 :
            print(f"Y1={Y1} < 0 ==> Y1 = 0\n")
            Y1 = 0
            
        return Y1

    def Calc_Cweb(self,Y1 : float, t_flange : float, t_web : float, BeamFy : float)-> float:
        """Çelik kesitin gövdesindeki basınç kuvvetini hesaplar.

        Args:
            Y1 (float): Plastik tarafsız eksen(PTE) ile çelik enkesitin üst başlık noktası ile arasındaki uzaklık
            t_flange (float): Çelik kesit başlık kalınlığı
            t_web (float): Çelik kesit gövde kalınlığı
            BeamFy (float): Çelik kesitin malzeme akma dayanımı

        Returns:
            float: C_web
        """
        Cweb    = t_web * BeamFy * (Y1 - t_flange)
        # print(f"Cweb = t_web * Fy * (Y1 - t_flange) = {Cweb} N")
        return Cweb

    def PTEInWebMn(self,T_steel : float, C_conc : float, Cflange : float, Cweb: float, Hbeam : float, t_flange:float, Y1 : float, Y2 : float) -> float:
        """PTE çelik kesitin gövdesinde olduğu durumdaki moment dayanımını hesaplar.

        Args:
            T_steel (float): Çelik kesitte çekme kuvveti
            C_conc (float): Betondaki basınç kuvveti
            C_flange (_type_): Çelik kesitin başlığında oluşan basınç kuvveti
            Cweb (float): Çelik kesitin gövdesinde oluşan basınç kuvveti
            Hbeam (float): Çelik kesitin yüksekliği
            t_flange (float): Çelik kesitin başlık kalınlığı
            Y1 (float): Plastik tarafsız eksen(PTE) ile çelik enkesitin üst başlık noktası ile arasındaki uzaklık
            Y2 (float): Beton basınç kuvvetinin ağırlık merkezi ile çelik enkesit üst kotu arasındaki mesafe
        Returns:
            float: Mn
        """
        Mn = round(C_conc*(Y1+Y2) + 2*Cflange*(Y1 - 0.5*t_flange) + 2*Cweb*(0.5*(Y1-t_flange)) + T_steel*(0.5*Hbeam-Y1) ,3)
        # print(f"Mn_web = (C_conc*(Y1+Y2) + 2*Cflange*(Y1 - 0.5*t_flange) + 2*Cweb*(0.5*(Y1-t_flange)) + T_steel*(0.5*Hbeam-Y1)) = [{round(C_conc*(Y1+Y2),3)} + {round(2*Cflange*(Y1 - 0.5*t_flange),3)} + {round(2*Cweb*(0.5*(Y1-t_flange)),3)} + {round(T_steel*(0.5*Hbeam-Y1),3)}] = {Mn} ")
        return round(Mn,3)

    def PTEInFlangeMn(self,C_conc : float, Cflange : float, Hbeam : float, BeamAs : float, BeamFy : float, Y1 : float, Y2 : float) -> float:
        """PTE çelik kesitin başlığında olduğu durumdaki moment dayanımını hesaplar.

        Args:
            C_conc (float): Betondaki basınç kuvveti
            Cflange (float): Çelik kesitin başlığında oluşan basınç kuvveti
            Hbeam (float): Çelik kesitin yüksekliği
            BeamAs (float): Çelik kesitinin alanı
            BeamFy (float): Çelik kesitin malzeme akma dayanımı
            Y1 (float): Plastik tarafsız eksen(PTE) ile çelik enkesitin üst başlık noktası ile arasındaki uzaklık
            Y2 (float): Beton basınç kuvvetinin ağırlık merkezi ile çelik enkesit üst kotu arasındaki mesafe
        Returns:
            float: Mn
        """
        Mn = round( ( (C_conc*(Y1+Y2)) + (2*Cflange*Y1/2) + (BeamAs*BeamFy*( (Hbeam/2) - Y1)) ), 3)
        # print(f"Mn_flange = (C_conc*(Y1+Y2)) + (2*Csflange*Y1/2) + (BeamAs*BeamFy*( (Hbeam/2) - Y1)) = {round(C_conc*(Y1+Y2),2)} +  {round( (2*Cflange*Y1/2),2)} + {round((BeamAs*BeamFy*( (Hbeam/2) - Y1)),2)} = {Mn}")
        return round(Mn,3)

    def PTEInSlabMn(self,Cf : float, Hbeam : float, hr : float, tc : float, a : float) -> float:
        """PTE beton döşeme içerisinde olduğu durumdaki moment dayanımını hesaplar.

        Args:
            Cf (float): min(C_conc,T_steel)
            Hbeam (float): Çelik kesitin yüksekliği
            hr (float): Metal sac hadve yüksekliği
            tc (float): Stud çivisiz beton yüksekliği
            a (float): Beton basınç alanı yüksekliği
        Returns:
            float: Mn
        """
        y = round( ( 0.5*Hbeam + hr + tc - 0.5*a), 2)
        Mn = round(Cf * y,3)
        # print(f"Mn_slab = Cf * y = {Cf} * {y} = {Mn}")
        return round(Mn,3)

    def CompositeBeamDesignFlexuralCapacity2(self,C_conc : float, T_steel : float, Mn_web : float, Mn_slab : float, Mn_flange : float, Y1 : float, t_flange: float, fi_b : float = 0.9)-> float:
        """Kompozit kirişin dizayn eğilme dayanımını hesaplar.

        Args:
            C_conc (float): Beton basınç kuvveti
            T_steel (float): Çelik akma kuvveti
            Mn_web (float): PTE kiriş gövdesinde durumu için eğilme dayanımı
            Mn_slab (float): PTE beton döşemede durumu için eğilme dayanımı
            Mn_flange (float): PTE kiriş başlığında durumu için eğilme dayanımı
            Y1 (float): Plastik tarafsız eksen(PTE) ile çelik enkesitin üst başlık noktası ile arasındaki uzaklık
            t_flange (float): Kiriş başlık kalınlığı
            fi_b (float, optional): Limit durum dizayn azaltma katsayısı. Defaults to 0.9.

        Returns:
            float: Kompozit kirişin dizayn eğilme dayanımı
        """
        if C_conc < T_steel : 
            print(f"Kompozit kiriş kısmi etkileşimlidir. Kompozitlik oranı %25'in altına inmemelidir.\n")
            if Y1 < t_flange:
                print("PTE kiriş başlığındadır.\n")
                Mn_design = fi_b * Mn_flange
                print(f"φMn = φ * Mn_flange = {fi_b} * {round(Mn_flange/10**6 ,3)}kNm = {round(Mn_design/10**6 ,3)}kNm\n")
                
            if Y1 >= t_flange:
                print("PTE kiriş gövdesindedir.\n")
                Mn_design = Mn_web * fi_b
                print(f"φMn = φ * Mn_web = {fi_b} * {round(Mn_web/10**6 ,3)}kNm = {round(Mn_design/10**6 ,3)}kNm\n")

        if C_conc >= T_steel :
            print(f"Kompozit kiriş tam etkileşimlidir. Plastik tarafsız eksen beton döşemenin içindedir.\n")
            Mn_design = fi_b * Mn_slab
            print(f"φMn = φ * Mn_slab = {fi_b} * {round(Mn_slab/10**6 ,3)}kNm = {round(Mn_design/10**6 ,3)}kNm\n")

        return Mn_design

    def CompositeBeamFlexuralCapacityCheck(self,M_demand : float, Mn_design : float)-> bool:
        """Eğilme kapasitesi kontrolü

        Args:
            M_demand (float): Talep eğilme dayanımı
            Mn_design (float): Kesitin eğilme dayanımı kapasitesi

        Returns:
            bool: Kontrolü geçtiyse yeterli değilse yetersiz
        """
        ratio = round(M_demand/Mn_design ,2)
        print(f"Talep/Kapasite oranı = {ratio}\n")
        if ratio > 1:
            return False
        else:
            return True

    def CompositeBeamDesignFlexuralCapacity(self,C_conc : float, T_steel : float, Ycon : float,
                                            BeamAs : float, BeamFy : float, Hbeam : float, t_flange : float, b_flange : float,
                                            Ac : float,hr : float,fck : float, beff : float, tc : float, t_web : float, fi_b : float = 0.9) -> float:
        """_summary_

        Args:
            C_conc (float): Beton basınç kuvveti
            T_steel (float): Çelik akma kuvveti
            Ycon (float): Toplam döşeme yüksekliği
            BeamAs (float): Kiriş alanı
            BeamFy (float): Kiriş akma gerilmesi dayanımı
            Hbeam (float): Kiriş yüksekliği
            t_flange (float): Kiriş başlık kalınlığı
            b_flange (float): Kiriş başlık genişliği
            Ac (float): Net beton örtüsü alanı
            hr (float): Metal sac hadve yüksekliği
            fck (float): 28 günlük beton numunesinin karakteristik basınç dayanımı MPa(N/mm^2)
            beff (float): Efektif döşeme genişliği
            tc (float): Net beton örtüsü kalınlığı
            t_web (float): Kiriş gövdesinin kalınlığı
            fi_b (float, optional): Limit durum dizayn azaltma katsayısı. Defaults to 0.9.

        Returns:
            float: Kompozit kiriş tasarım eğilme dayanımı.
        """

        C = min(C_conc,T_steel)
        a = C / (0.85 * fck * beff)
        print(f"a = {a} mm")
        Y2 = Ycon - (a/2)
        print(f"Y2 = {Y2} mm")

        if C_conc < T_steel : 
            print(f"Kompozit kiriş kısmi etkileşimlidir. Kompozitlik oranı %25'in altına inmemelidir.\n")
    
            Y1 = round((T_steel - C_conc) / (2*BeamFy*b_flange),2) # çelik kesitte basınç başlıkta kabulü ile basınç derinliği hesabı
            print(f"Basınç bloğu başlıkta kabul edilirse; Y1(veya tf') = {Y1} mm")
            
            if Y1 < t_flange: # çelik kesitte basınç derinliği başlık kalınlığından küçükse PTE başlıktadır.
                print("PTE kiriş başlığındadır.")
                Csflange = BeamFy*b_flange*Y1
                print(f"Csflange = Fy*b_flange*Y1 = {Csflange} N")
                DesignMn = fi_b * ( (C_conc*(Y1+Y2)) + (2*Csflange*Y1/2) + (BeamAs*BeamFy*( (Hbeam/2) - Y1)) )
                print(f"φMn = φ * ((C_conc*(Y1+Y2)) + (2*Csflange*Y1/2) + (BeamAs*BeamFy*( (Hbeam/2) - Y1))) = {fi_b} * {round(C_conc*(Y1+Y2),2)} +  {round( (2*Csflange*Y1/2),2)} + {round((BeamAs*BeamFy*( (Hbeam/2) - Y1)),2)} = {round(DesignMn,3)}")
            
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

    def Calc_Load(self,Load : float, GirdersSpaceLength : float)-> float:
        """Yapım aşamasındaki sabit yük

        Args:
            Load (float): Yük sınıfı. (döşeme + kiriş ağırlığı =constantdeadload, Kaplama + bölme duvar + mekanik,elektrik vs. yükleri = superdeadload, Hareketli yük = live load) N/mm or kN/m
            GirdersSpaceLength (float): Kiriş aralığı

        Returns:
            _type_: _description_
        """
        return Load * GirdersSpaceLength

    def calc_w_tl(self,w_dl : float, w_ll : float)-> float:
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

    def SimpleCompositeBeamDeflection(self,w : float, Lbeam : float, I : float, Ebeam : float = 2*10**5)-> float:
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

    def MainCompositeBeamDeflection(self,P : float, Lbeam : float, I : float, Ebeam : float = 2*10**5)-> float:
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

    def Camber(self,delta_cdl : float, Lbeam : float, Limit : int = 19) -> float:
        """Ters sehim hesabı, 19mm altı ani sehim veya 7.6m uzunluğundan az kiriş uzunluğu için ters sehim yapmaz

        Args:
            delta_cdl (float): Yapım öncesi sabit yükler altında sehim miktarı
            Lbeam (float): Kiriş uzunluğu
            Limit (float): Ters sehim için minimum deplasman sınırı.

        Returns:
            float: Ters sehim miktarı
        """
        delta_c = 0.75 * delta_cdl
        if delta_cdl < Limit or Lbeam < 7600:
            print(f"delta_cdl = {delta_cdl}mm < {Limit}mm or Lbeam = {Lbeam} < 7600mm olduğu için ters sehime gerek yoktur.\n")
            delte_c = 0.0
        return delta_c

    def calc_Delta_TL(self,delta_cdl : float, delta_sdl : float, delta_ll : float, delta_c : float)-> float:
        """Kesitteki toplam yüklerden oluşan sehimi hesaplar.

        Args:
            delta_cdl (float): Yapım aşaması sabit yük nedeniyle düşey yerdeğiştirme
            delta_sdl (float): Super dead load (kaplama+mekanik+sıva+alçı vs.)
            delta_ll (float): Hareketli yük nedeniyle düşey yerdeğiştirme
            delta_c (_type_): Ters sehim miktarı

        Returns:
            float: Toplam deplasman
        """
        delta_cdl_net = delta_cdl - delta_c
        return round(delta_cdl_net + delta_ll + delta_sdl,2)

    def DeflectionChecks(self, delta : float, L : float, Ratio : int = 360) -> bool:
        """Kesitin sehim kontrolünü yapar

        Args:
            delta (float): Sehim miktarı
            L (float): Kirişin boyu
            Ratio (int, optional): Sehim kontrol oranı. L/ratio, Defaults to 360.

        Returns:
            bool: Kontrolü geçtiyse yeterli değilse yetersiz
        """
        if delta > L/Ratio:
            print(f"{delta} > L/{Ratio} = {round(L/Ratio,2)} X\n")
            return False
        print(f"{delta} ≤ L/{Ratio} = {round(L/Ratio,2)}  √\n")
        return True
    

    
# if __name__ == "__main__":
#     cb = CompositeBeams()
#     cb.Designer()