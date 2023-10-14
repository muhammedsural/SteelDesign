from dataclasses import dataclass, field
import math

# Temel birimler N,mm,kg
# Bütün fonksiyonlarda kesit özellikleri girdi olarak var bunlar bir class içerisinde toplanıp verilebilir. Kod sadeleşir ve bakımı kolaylaşır

def EksenelBasincKesitKontrolü(TopFlangewidth : float, 
                                       TopFlangethick : float, 
                                       BotFlangewidth : float, 
                                       BotFlangethick : float, 
                                       Webheight : float,
                                       Webthick  : float,
                                       Fy: float, 
                                       SectionType : int = 0,
                                       E : float = 2*10**5) -> bool:
    
    kc = 4/(Webheight/Webthick)#0.35 <= kc <= 0.76 
    lamda_Topflange = TopFlangewidth/TopFlangethick
    lamda_Botflange = BotFlangewidth/BotFlangethick
    lamda_Web = Webheight/Webthick
    
    lamda_r_flange = 0.56 * math.sqrt(E/Fy)
    lamda_r_web = 1.49*math.sqrt(E/Fy)
    CompSlenderCheck = False

    if lamda_r_flange<lamda_Topflange:
        print("üst başlık narin...")
        CompSlenderCheck = True
        
    if lamda_r_flange<lamda_Botflange:
        print("alt başlık narin...")
        CompSlenderCheck = True

    if lamda_r_web < lamda_Web:
        print("Kesit gövdesi narindir...")
        CompSlenderCheck = True

    return CompSlenderCheck

def EgilmeKesitKontrolü(TopFlangewidth : float, 
                                       TopFlangethick : float, 
                                       BotFlangewidth : float, 
                                       BotFlangethick : float, 
                                       Webheight : float,
                                       Webthick  : float,
                                       Fy: float, 
                                       SectionType : int = 0,
                                       E : float = 2*10**5) -> bool:
    lamda_Topflange = TopFlangewidth/TopFlangethick
    lamda_Botflange = BotFlangewidth/BotFlangethick
    lamda_Web = Webheight/Webthick
    
    lamda_p_flange = 0.38 * math.sqrt(E/Fy)
    lamda_r_flange = 1.0 * math.sqrt(E/Fy)

    lamda_p_web = 3.76*math.sqrt(E/Fy)
    lamda_r_web = 5.70*math.sqrt(E/Fy)

    FlexCompactCheck = False

    if lamda_p_flange<lamda_Topflange:
        print("Kompakt olmayan üst başlık")
        FlexCompactCheck = True
        if lamda_r_flange<lamda_Topflange:
            print("Kompakt olmayan narin üst başlık...")
            FlexCompactCheck = True
        
    if lamda_p_flange<lamda_Botflange:
        print("Kompakt olmayan alt başlık")
        FlexCompactCheck = True
        if lamda_r_flange<lamda_Botflange:
            print("Kompakt olmayan narin alt başlık...")
            FlexCompactCheck = True

    if lamda_p_web<lamda_Web:
        print("Kompakt olmayan gövde")
        FlexCompactCheck = True
        if lamda_r_web<lamda_Web:
            print("Kompakt olmayan narin gövde...")
            FlexCompactCheck = True

    return FlexCompactCheck

#Eksenel Çekme kuvveti etkisindeki I profil elemanların tasarımı
#========================================================================================================
def NominalÇekmeKapatiesi(Ag : float,Fy : float) -> float:
    return Fy * Ag



#Kesme kuvveti etkisindeki I profil elemanların tasarımı
#========================================================================================================
@dataclass
class Shear:
    """
    Kesme hesaplarının yapıldığı sınıf
    Vu  : Talep kesme kuvveti 
    a   : Varsa rijitleştirme levhaları arası mesafe yoksa 0 girilmeli
    h   : Kesit yüksekliğ
    tw  : Gövde et kalınlığı
    d   : Gövde yüksekliği
    bfc : Basınç başlığı genişliği
    tfc : Basınç başlığı et kalınlığı
    bft : Çekme başlığı genişliği
    tft : Çekme başlığı et kalınlığı
    E   : Elastisite modülü
    Fy  : Beklenen akma gerilmesi

    """
    Vu  : float
    a   : float
    h   : float
    tw  : float
    d   : float
    bfc : float
    tfc : float
    bft : float
    tft : float
    E   : float
    Fy  : float
    Tension_field_action : bool = False
    kv  : float  = field(init=False)
    Cv1 : float = field(init=False)
    Cv2 : float = field(init=False)
    Vn  : float = field(init=False)



    def Get_kv(self,a : float, h : float) -> float:
        """Gövde levhası burkulma katsayısını hesaplar

        Args:
            a (float): Rijitleştirme levhaları arasındaki mesafe
            h (float): Kesit yüksekliği

        Returns:
            kv (float): Gövde levhası burkulma katsayısı
        """
        if a > 0:
            if a/h <= 3.0:
                kv = round(5 + (5/(a/h)**2),3)
                print(f"gövdede, düşey ara rijitlik levhaları kullanıldığından ve a/h <= 3.0 olduğundan Yönetmelik 10.2.1 uyarınca, \ngövde levhası burkulma katsayısı, kv = 5 + (5/(a/h)) = {kv}")
            else:
                kv = 5.34
                print("gövdede, düşey ara rijitlik levhaları kullanıldığından ve a/h > 3.0 olduğundan Yönetmelik 10.2.1 uyarınca, \ngövde levhası burkulma katsayısı, kv = 5.34")
        else:
            print("Gövdede düşey ara rijitlik levhaları kullanılmadığı durum için, Yönetmelik 10.2.1 uyarınca, Denk.(10.3a) ile \ngövde levhası burkulma katsayısı, kv = 5.34 alınmıştır")
            kv = 5.34
        
        return kv

    def Get_Cv1(self,h : float, tw : float, kv : float, E :float, Fy : float) -> float:
        """Gövde kesme kuvveti dayanım katsayısını hesaplar

        Args:
            h (float) : Kesit yüksekliği
            tw (float): Gövde levhası et kalınlığı
            kv (float): Gövde levhası burkulma katsayısı
            E (float) : Kesit malzemesinin elastisite modülü
            Fy (float): Malzemenin beklenen akma dayanımı

        Returns:
            Cv1 (float): Gövde kesme kuvveti dayanım katsayısı
        """
        web_slenderness_ratio = round(h/tw,2)
        chck_point1 = round(2.24* math.sqrt(E/Fy),2)
        chck_point2 = round(1.10 * math.sqrt(kv*E/Fy),2)
        #chck_point3 = 1.37 * math.sqrt(kv*E/Fy)

        if web_slenderness_ratio <= chck_point2 or web_slenderness_ratio <= chck_point1:
            print(f"h/tw = {web_slenderness_ratio} <= {chck_point2} = 1.10 * (kv*E/Fy)^0.5 ==> Cv1 = 1.0")
            Cv1 = 1.0 

        if web_slenderness_ratio > chck_point2 :
            Cv1 = round(chck_point2/web_slenderness_ratio,3)
            print(f"h/tw = {web_slenderness_ratio} > {chck_point2} = 1.10 * (kv*E/Fy)^0.5 ==> Cv1 = {Cv1}")

        return Cv1

    def Get_Cv2(self,h : float, tw : float, kv : float, E :float, Fy : float) -> float:
        """Kayma etkisinde gövde burkulma katsayısını hesaplar

        Args:
            h (float): Kesit yüksekliği
            tw (float): Gövde levhası et kalınlığı
            kv (float): Gövde levhası burkulma katsayısı
            E (float): Elastisite modülü
            Fy (float): Malzemenin beklenen akma dayanımı

        Returns:
            Cv2 (float): Kayma etkisinde gövde plakasının burkulma katsayısı
        """
        web_slenderness_ratio = round(h/tw,2)
        chck_point = 1.37 * math.sqrt(kv*E/Fy)

        if web_slenderness_ratio > chck_point:
            pay = 1.51 * kv * E
            payda = web_slenderness_ratio**2 * Fy
            Cv2 = round(pay/payda,3)
            print(f"Cv2 = {Cv2}")
        else:
            print(f"h/tw={web_slenderness_ratio} < {chck_point} = 1.37*(kv*E/Fy)^0.5 ==> Cv2 kullanılamıyor.\nBu nedenle Cv2 = 0 alındı.")
            Cv2 = 0

        return Cv2

    def Get_NominalShearCapacity(self,tw  : float, 
                               d   : float,
                               h   : float, 
                               Fy  : float,
                               a   : float,
                               bfc : float,
                               tfc : float,
                               bft : float,
                               tft : float,
                               Cv1 : float,
                               Cv2 : float,
                               kv  : float,
                               E   : float,
                               Tension_field_action = False) -> float:
        """Kesme etkisindeki elemanın nominal kesme kapasitesini hesaplar.

        Args:
            tw (float) : Gövde levhası et kalınlığı
            d (float)  : Gövde levhası yüksekliği
            h (float)  : Kesit yüksekliği
            Fy (float) : Beklenen akma dayanımı
            a (float)  : Rijitlik levhaları arasındaki mesafe
            bfc (float): Basınç etkisi altındaki başlık genişliği
            tfc (float): Basınç etkisi altındaki başlıın et kalınlığı
            bft (float): Çekme etkisi altındaki başlık genişliği
            tft (float): Çekme etkisi altındaki başlıın et kalınlığı
            Cv1 (float): Gövde kesme kuvveti dayanım katsayısı
            Cv2 (float): Kayma etkisinde gövde plakasının burkulma katsayısı
            kv  (float): Gövde levhası burkulma katsayısı
            E   (float): Kesit malzemesinin elastisite modülü
            Tension_field_action (bool, optional): Çekme alanı etkisi dikkate alınsın mı? True alır False almaz. Defaults to False.

        Returns:
            Vnominal (float): Kesitin nominal kesme kapasitesi
        """

        #Kesme kuvvetleri gövde kesitinde karşılandığı kabul edilirse kiriş için
        import math
        Aw = tw * d
        Afc = bfc * tfc
        Aft = bft * tft
        web_slenderness_ratio = round(h/tw,2)
        chck_point = round(1.10 * math.sqrt(kv*E/Fy),2)
        Vgeneral = 0.6 * Fy * Aw

        if a > 0 :
            print("Rijitlik levhaları mevcut ....")
            if a/h <= 3.0 : 
                if Tension_field_action == True :
                    print("Çekme etkisi dikkate alınması için kontrollere başlanıyor...")
                    if web_slenderness_ratio <= chck_point:
                        Vnominal = Vgeneral
                        print(f"h/tw = {web_slenderness_ratio} <= {chck_point} = 1.10 * (kv*E/Fy)^0.5 ==> Vn = 0.6*Fy*Aw = {Vgeneral}")

                    if web_slenderness_ratio > chck_point:
                        print(f"h/tw = {web_slenderness_ratio} > {chck_point} = 1.10 * (kv*E/Fy)^0.5 ==> Olduğu için ek kontroller yapılıyor...")

                        if (2*Aw/(Afc + Aft)) <= 2.5 and h/bfc <=6 and h/bft <= 6.0:
                            Vnominal = round(Vgeneral * (Cv2 + ((1-Cv2) / (1.15 * math.sqrt(1 + (a/h)**2)) ) ),3)
                            print(f"(2*Aw/(Afc + Aft)) = {(2*Aw/(Afc + Aft))} <= 2.5 and h/bfc = {h/bfc} <=6 and h/bft = {h/bft} <= 6.0 ==> Vn = 0.6*Fy*Aw * (Cv2 + ((1-Cv2) / (1.15 * (1 + (a/h)**2))^0.5 ) ) = {Vnominal}")
                        else:
                            Vnominal = round(Vgeneral * (Cv2 + ((1-Cv2) / (1.15 * ((a/h) + math.sqrt(1 + (a/h)**2))) ) ),3)
                            print(f"(2*Aw/(Afc + Aft)) = {(2*Aw/(Afc + Aft))} <= 2.5 and h/bfc = {h/bfc} <=6 and h/bft = {h/bft} <= 6.0  şartlarından biri sağlanmadığı için==>\nVn = 0.6*Fy*Aw * (Cv2 + ((1-Cv2) / (1.15 * ((a/h)+ (1+(a/h)**2)^0.5) ) = {Vnominal}")

                if Tension_field_action == False:
                    Vnominal = round(Vgeneral* Cv1,3) 
                    print(f"a>0 ; a/h <= 3.0 ama  Tension_field_action = False ==> Vnominal = 0.6 * Fy * Aw * Cv1 = 0.6 * {Fy} * {Aw} * {Cv1} = {Vnominal}")

            if a/h > 3.0:
                Vnominal = round(Vgeneral* Cv1,3) 
                print(f"a>0 ama a/h > 3.0 ==> Vnominal = 0.6 * Fy * Aw * Cv1 = 0.6 * {Fy} * {Aw} * {Cv1} = {Vnominal}")
        else:
            print("Rijitlik levhaları mevcut değil...")
            Vnominal = round(Vgeneral* Cv1,3) 
            print(f"Vnominal = 0.6 * Fy * Aw * Cv1 = 0.6 * {Fy} * {Aw} * {Cv1} = {Vnominal}")
        return Vnominal

    def CheckShearCapacity(self,Vu : float,Vn : float,fi_d : float=0.9) -> None:
        Vu = Vu/10**3
        Vn = Vn/10**3

        if Vu > fi_d*Vn:
            print(f"Vu = {Vu}kN >{fi_d}*{Vn} = {round(fi_d*Vn,3)}kN  gövde kesme kapasitesi yetersiz rijitlik levhaları kullanılmalı, \nrijitleştirme levhaları kullanıldı ise çekme alanı etkisi dikkate alınabilir\nbunlara rağmen kurtarmıyorsa rijitlik levhalarının aralıkları azaltılmalı veya kiriş gövde kalınlığı arttırılmalıdır")
        else:
            print(f"Vu = {Vu}kN <= {fi_d}*{Vn} = {round(fi_d*Vn,3)}kN gövde kesme kapasitesi yeterlidir. Rijitleştirme levhaları kullanıldıysa bu levhalar kontrol edilmelidir...")

    def __post_init__(self):
        self.kv  = self.Get_kv(self.a,self.h)
        self.Cv1 = self.Get_Cv1(self.h,self.tw,self.kv,self.E,self.Fy)
        self.Cv2 = self.Get_Cv2(self.h,self.tw,self.kv,self.E,self.Fy)
        self.Vn  = self.Get_NominalShearCapacity(self.tw, 
                               self.d  ,
                               self.h  , 
                               self.Fy ,
                               self.a  ,
                               self.bfc,
                               self.tfc,
                               self.bft,
                               self.tft,
                               self.Cv1,
                               self.Cv2,
                               self.kv ,
                               self.E  ,
                               self.Tension_field_action) 
        self.CheckShearCapacity(self.Vu,self.Vn)

#Eksenel Basınç kuvveti etkisindeki I profil elemanların tasarımı
#========================================================================================================

@dataclass
class Compression:


    def EulerBucklingLoad(L : float, I : float,i : float , K:float = 1.0 , E : float = 2*10**5) -> float:
        """
        Euler burkulma yükünü hesaplar
        L : float, 
        I : float,
        i : float , 
        K:float = 1.0 , 
        E : float = 2*10**5
        Returns:
            Fcr (float) -> Euler burkulma yükü
        """
        Fcr = math.pi**2 * E * I / (K*L/i)**2
        return Fcr
    
    def GetF_ex(E:float,Lcx:float,ix:float) -> float:
        """
        _summary_

        Arguments:
            E -- _description_
            Lcx -- _description_
            ix -- _description_

        Returns:
            _description_
        """
        return (math.pi**2 * E)/(Lcx/ix)**2
    
    def GetF_ey(E:float,Lcy:float,iy:float) -> float:
        """
        _summary_

        Arguments:
            E -- _description_
            Lcy -- _description_
            iy -- _description_

        Returns:
            _description_
        """
        return (math.pi**2 * E)/(Lcy/iy)**2
    
    def Getr0(x0:float,y0:float,Ix:float,Iy:float,Ag:float) -> float:
        """
        _summary_

        Arguments:
            x0 -- _description_
            y0 -- _description_
            Ix -- _description_
            Iy -- _description_
            Ag -- _description_

        Returns:
            _description_
        """
        first = x0**2 + y0**2
        second = (Ix + Iy)/Ag
        r0 = math.sqrt(first+second)
        return r0

    def GetH(x0 : float, y0 : float, r0 : float) -> float:
        """
        _summary_

        Arguments:
            x0 -- _description_
            y0 -- _description_
            r0 -- _description_

        Returns:
            _description_
        """
        H = 1 - (x0**2 + y0**2)/r0**2
        return H

    def GetF_ez(E:float,Cw:float,G:float,J:float,Lcz:float,Ag:float, r0:float)->float:
        """
        _summary_

        Arguments:
            E -- _description_
            Cw -- _description_
            G -- _description_
            J -- _description_
            Lcz -- _description_
            Ag -- _description_
            r0 -- _description_

        Returns:
            _description_
        """
        first = (math.pi**2 * E * Cw/Lcz**2) + (G*J)
        second = 1 / (Ag * r0**2)
        Fez = first*second
        return Fez
   
    def get_Cw(self,Iy : float, h0 : float) -> float:
        """
        Warping katsayısını hesaplar I tipi kesitler için
            Cw = (Iy * h0**2) / 4 ==> I kesit

        Arguments:
            Iy -- Y eksenindeki atalet
            h0 -- Başlık merkezleri arasındaki mesafe

        Returns:
            Warping katsayısı - float
        """
        Cw = (Iy * h0**2) / 4
        return Cw
    
    def LateralTorsionalBucklingLoadWithoutSlendernessMember(Lb:float,
                                                       Fy:float,
                                                       i:float,
                                                       E:float,
                                                       Cw:float,
                                                       Lcz:float,
                                                       Ix,Iy,
                                                       Fex:float,
                                                       Fey:float,
                                                       Fez:float,
                                                       H:float,
                                                       Symt:int) -> float:
       
        Fe = 0.0
        if Symt == 2:
            Fe = (math.pi**2 * E * Cw/Lcz**2)*(1/(Ix+Iy))
            print(f"Çift eksende simetrik kesit ==>\nFe = (pi**2 * E * Cw/Lcz**2)*(1/(Ix+Iy)) = {Fe} ")
        if Symt == 1:
            indis = (4*Fey*Fez*H)/(Fey + Fez)**2
            Fe = ((Fey + Fez)/(2*H)) * (1 - math.sqrt(1 - indis))
            print(f"Tek eksende simetrik kesit ==>\nFe = ((Fey + Fez)/(2*H)) * (1 - (1 - (4*Fey*Fez*H)/(Fey + Fez)**2)**0.5)) = {Fe} ")
        if Symt == 0:
            first = f"(Fe-{round(Fex,3)}) * (Fe-{round(Fey,3)}) * (Fe-{round(Fez,3)})"
            second = f"Fe^2 * (Fe-{round(Fey,3)}) * (x0/r0)^2"
            third = f"Fe^2 * {round(Fex,3)}) * (y0/ro)^2"
            print(f"Kesitin simetrik ekseni yoktur denklem takımı çözülmelidir.\n{first} - {second} - {third}")
        
        Trashold = 4.71*math.sqrt(E/Fy)
        if (Lb/i) <= Trashold:
            Fcr  = 0.658**(Fy/Fe) * Fy
        else:
            Fcr = 0.877 * Fe

        return Fcr

    def FlexureBucklingLoadWithoutSlendernessMember(L : float, i : float, Fy : float, E : float) -> float:
        """
        _summary_

        Returns:
            _description_
        """
        Fe = math.pi**2 * E /(L/i)**2
        Trashold = 4.71*math.sqrt(E/Fy)
        if (L/i) <= Trashold:
            Fcr  = 0.658**(Fy/Fe) * Fy
        else:
            Fcr = 0.877 * Fe
        return Fcr
    
    def CompressionStrength(Fcr_e : float, Fcr_ebb:float, Ag : float) -> float:
        """
        _summary_

        Arguments:
            Fcr_e -- Eğilme burkulması yükü
            Fcr_ebb -- Eğilmeli burulmalı burkulma yükü
            Ag -- Brüt kesit alanı

        Returns:
            Basınç kapasitesi
        """
        Fcr = min(Fcr_e,Fcr_ebb)
        return Fcr*Ag

    def CheckCompressionStrength(Pn:float,Pu:float,fi_d:float) -> None:

        if Pu>fi_d*Pn:
            print(f"Pu = {Pu} > {fi_d*Pn}= fi_d*Pn Basınç kapasitesi yetersizdir...")
        else:
            (f"Pu = {Pu} <= {fi_d*Pn}= fi_d*Pn Basınç kapasitesi yeterlidir...")



#Eğilme kuvveti etkisindeki I profil elemanların tasarımı
#========================================================================================================

#Yerel burkulma durumu kontrol edilmeli
@dataclass
class Flexure:
    Mu   : float
    Lb   : float
    Iy   : float
    h0   : float
    Sx   : float
    Zx   : float
    iy   : float
    Fy   : float
    E    : float
    Jc   : float
    Mmax : float
    Ma   : float
    Mb   : float
    Mc   : float
    fi_d : float = 0.9
    Cw   : float = field(init=False)
    i_ts : float = field(init=False)
    Lp   : float = field(init=False)
    Lr   : float = field(init=False)
    Cb   : float = field(init=False)
    Fcr  : float = field(init=False)
    Mn_ltb   : float = field(init=False)
    Mp       : float = field(init=False)
    

    def __post_init__(self):
        self.Cw     = self.Get_Cw(self.Iy,self.h0)
        self.i_ts   = self.Get_i_ts(self.Iy,self.Cw,self.Sx)
        self.Lp     = self.Get_Lp(self.iy,self.Fy,self.E)
        self.Lr     = self.Get_Lr(self.i_ts,self.Jc,self.Sx,self.h0,self.Fy,self.E)
        self.Cb     = self.Get_Cb(self.Mmax,self.Ma,self.Mb,self.Mc)
        self.Fcr    = self.Get_ElasticLTB_Fcr(self.Lb,self.i_ts,self.Jc,self.Sx,self.h0,self.Cb,self.E)
        self.Mn_ltb = self.LateralTorsionalBucklingCapacity(self.Lb,
                                                            self.Lp,
                                                            self.Lr,
                                                            self.Fcr,
                                                            self.Sx,
                                                            self.Zx,
                                                            self.Fy,
                                                            self.Cb)
        self.Mp = self.PlasticFlexureCapacity(self.Fy,self.Zx)
        self.FlexureCapacityCheck(self.Mu,self.Mn_ltb,self.Mp,self.fi_d)

    def Get_Cw(self,Iy : float, h0 : float) -> float:
        """
        Warping katsayısını hesaplar I tipi kesitler için
            Cw = (Iy * h0**2) / 4 ==> I kesit

        Arguments:
            Iy -- Y eksenindeki atalet
            h0 -- Başlık merkezleri arasındaki mesafe

        Returns:
            Warping katsayısı - float
        """
        Cw = (Iy * h0**2) / 4
        return Cw
    
    def Get_i_ts(self,Iy : float, Cw : float, Sx : float) -> float:
        """
        Etkin atalet yarıçapını hesaplar

        Arguments:
            Iy -- Y eksenindeki atalet
            Cw -- Çarpılma(Warping) sabiti
            Sx -- X ekseni etrafında elastik kesit mukavemet momenti

        Returns:
            Etkin atalet yarıçapı
        """
        i_ts = ((math.sqrt(Iy*Cw) / Sx))**0.5
        return i_ts

    def Get_Lp(self,i_y : float,Fy:float, E : float = 2*10**5) -> float:
        """LTB(Yanal burulmali burkulma) olmayacak uzunluğu verir

        Args:
            i_y (float): Kesitin y eksenine göre atalet yaricapi
            Fy (float): Kesit malzemesinin akma dayanimi MPa
            E (float, optional): Kesit malzemesinin elastisite modulu. Defaults to 2*10**5.

        Returns:
            float: LTB olusmayan serbest boy siniri
        """
        a = E/Fy
        b = math.sqrt(a)
        Lp = 1.76 * i_y * b
        return round(Lp,2)

    def Get_Lr(self,i_ts : float,Jc : float,Sx : float,ho : float,Fy:float, E : float = 2*10**5) -> float:
        """Elastik LTB oluşumu için gerekli boy

        Args:
            i_ts (float): Etkin dönme atalet yaricapi
            Jc (float): Burulma sabiti
            Sx (float): Kesitin x ekseni etrafindaki elastik mukavemet momenti
            ho (float): Enkesit basliklarinin agirlik merkezleri arasindaki uzaklik
            Fy (float): Kesit malzemesinin akma dayanimi
            E (float, optional): Kesit malzemesinin elastisite modulu. Defaults to 2*10**5.

        Returns:
            float: Elastik LTB serbest boy siniri
        """
        a = Jc/(Sx*ho)
        b = 6.76 * (0.7 * Fy / E)**2
        first = math.sqrt(a**2 + b)
        Lr = 1.95 * i_ts * (E / (0.7 * Fy)) * math.sqrt(a + first)
        return round(Lr,2)

    def Get_Cb(self,Mmax : float, Ma : float, Mb : float, Mc : float) -> float:
        """
        _summary_

        Arguments:
            Mmax -- _description_
            Ma -- _description_
            Mb -- _description_
            Mc -- _description_

        Returns:
            _description_
        """
        Cb = 12.5 * Mmax / (2.5 * Mmax + 3*Ma + 4*Mb + 3*Mc)
        print(f"Cb = 12.5 * Mmax / (2.5 * Mmax + 3*Ma + 4*Mb + 3*Mc) = 12.5 * {Mmax} / (2.5 * {Mmax} + 3*{Ma} + 4*{Mb} + 3*{Mc}) = {round(Cb,2)}\n")
        return round(Cb,2)

    def Get_ElasticLTB_Fcr(self,Lb : float,i_ts : float,Jc : float,Sx : float,ho : float ,Cb : float = 1.0 ,E : float = 2*10**5) -> float:
        """
        _summary_

        Arguments:
            Lb -- _description_
            i_ts -- _description_
            Jc -- _description_
            Sx -- _description_
            ho -- _description_

        Keyword Arguments:
            Cb -- _description_ (default: {1.0})
            E -- _description_ (default: {2*10**5})

        Returns:
            _description_
        """

        a = (Cb * math.pi**2 * E) / ((Lb/i_ts)**2)
        b = math.sqrt(1 + (0.078 * (Jc / (Sx * ho)) * (Lb / i_ts)**2 ))
        Fcr = a * b
        return Fcr

    def LateralTorsionalBucklingCapacity(self,
                                            Lb : float, 
                                            Lp : float, 
                                            Lr : float, 
                                            Fcr : float, 
                                            Sx : float, 
                                            Zx : float, 
                                            Fy : float, 
                                            Cb : float = 1.0) -> float:
        """
        _summary_

        Arguments:
            Lb -- _description_
            Lp -- _description_
            Lr -- _description_
            Fcr -- _description_
            Sx -- _description_
            Zx -- _description_
            Fy -- _description_

        Keyword Arguments:
            Cb -- _description_ (default: {1.0})

        Returns:
            _description_
        """

        Mp = Fy*Zx # plastik mukavemet momenti
        Me = Fy*Sx # elastik mukavemet momenti
        print(f"Mp = Fy*Zx = {Fy}*{Zx} = {Mp/10**6}kNm\nMp = Fy*Sx = {Fy}*{Sx} = {Me/10**6}kNm\n")

        if Lb <= Lp :
            print(f"L_ltb ={Lb} <= {Lp}=Lp LTB oluşmaz Mn platik moment kapasitesine eşittir\n")
            Mn = Mp
        
        if Lb > Lp and Lb <= Lr:
            Mn = Cb * (Mp - (Mp - 0.7*Me) * ((Lb - Lp) / (Lr - Lp)))
            print(f"Lp={Lp} < L_ltb = {Lb} <= {Lr}=Lr inelastik LTB oluşur ==> \nMn = Cb * (Mp - (Mp - 0.7*Me) * ((Lb - Lp) / (Lr - Lp))) ==> Mn = {Cb} * ({Mp} - ({Mp} - 0.7*{Me}) * (({Lb} - {Lp}) / ({Lr} - {Lp}))) = {Mn}\n")
            if Mn > Mp :
                print(f"Mn = {Mn} > {Mp} = Mp ==> Mn = Mp alındı\n")
                Mn = Mp
                
            
        if Lb > Lr :
            Mn = Fcr * Sx
            print(f"L_ltb={Lb} > Lr={Lr} elastik LTB oluşur Mn = Fcr * Sx ==> Mn = {Fcr} * {Sx} = {Mn}\n")
            if Mn > Mp:
                print(f"Plastik moment kapasitesinden fazla olamaz {Mn} > {Mp}\n")
                Mn = Mp
        return Mn

    def PlasticFlexureCapacity(self,Fy : float, Zx : float):
        """
        _summary_

        Arguments:
            Fy -- _description_
            Zx -- _description_

        Returns:
            _description_
        """
        print("Lokal burkulma durumu kompakt yüksek sünek kesit seçildiği kabulü ile kontrol edilmemiştir bu nedenle plastik kapasitede herhangi bir azaltma yapılmamıştır. ==> Mn=Mp=Fy*Zx\n")
        return Fy*Zx
    
    def FlexureCapacityCheck(self,Mu : float, Mn_ltb : float, Mn_plastic : float, fi_d : float ) -> None:
        """
        _summary_

        Arguments:
            Mu -- _description_
            Mn_ltb -- _description_
            Mn_plastic -- _description_
            fi_d -- _description_
        """
        
        Mn = min(Mn_plastic,Mn_ltb)
        
        if Mn*fi_d < Mu:
            print(f"Mn*fi_d = {Mn*fi_d} < Mu = {Mu} ==> Eğilme kapasitesi yetersizdir...\n")
        else:
            print(f"Mn*fi_d = {Mn*fi_d} >=  Mu = {Mu} ==> Eğilme kapasitesi yeterlidir...\n")

#Burulma kuvvet etkisindeki I profil elemanların tasarımı
#========================================================================================================


#Bileşik kuvvet etkisindeki I profil elemanların tasarımı
#========================================================================================================


# TEST
#========================================================================================================
if __name__ == "__main__":

    d              = 440 #mm
    h              = 344 #mm
    tw             = 11.5 #mm
    bf_compression = 300 #mm
    bf_tension     = 300 #mm
    tf_comp        = 21 #mm
    tf_tension     = 21 #mm
    Vu             = 1370*10**3 #N
    a_stiffner     = 1500 #mm
    h0             = 281#mm
    iy             = 72.9#mm
    Jc             = 243.8*10**4#mm^4
    Sx             = 2896*10**3    #mm^3
    Zx             = 3216*10**3   #mm^3
    Iy             = 8563 *10**4  #mm^4
    Lb_ltb         = 8000     #mm
    Fy             = 355 #N/mm^2
    E              = 2*10**5 #
    Vu             = 1220 * 10**3 #N
    Mu             = 960 * 10**6 #Nmm
    Mmax           =1 #Nmm
    Ma             =0.438 #Nmm 
    Mb             =0.751 #Nmm 
    Mc             =0.938 #Nmm  

    # print("==========KESME HESABI==========")
    # Vn = Shear(Vu,a_stiffner,h,tw,d,bf_compression,tf_comp,bf_tension,tf_tension,E,Fy,Tension_field_action=False)
    print("==========EĞİLME HESABI==========")
    M_ltb = Flexure(Mu , 
                    Lb_ltb  ,
                    Iy  ,
                    h0 , 
                    Sx , 
                    Zx , 
                    iy , 
                    Fy , 
                    E ,  
                    Jc , 
                    Mmax,
                    Ma,  
                    Mb,  
                    Mc  )
    #print(f"Lr = {M_ltb.Lr}, Lp = {M_ltb.Lp}")

    