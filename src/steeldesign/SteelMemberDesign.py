from dataclasses import dataclass, field
from math import sqrt,pi

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
    
    lamda_r_flange = 0.56 * sqrt(E/Fy)
    lamda_r_web = 1.49*sqrt(E/Fy)
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
    lamda_Topflange = TopFlangewidth/2*TopFlangethick
    lamda_Botflange = BotFlangewidth/2*BotFlangethick
    lamda_Web = Webheight/Webthick
    
    lamda_p_flange = 0.38 * sqrt(E/Fy)
    lamda_r_flange = 1.0 * sqrt(E/Fy)

    lamda_p_web = 3.76*sqrt(E/Fy)
    lamda_r_web = 5.70*sqrt(E/Fy)

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
    h   : Kesit yüksekliği
    tw  : Gövde et kalınlığı
    d   : Gövde yüksekliği
    bfc : Basınç başlığı genişliği
    tfc : Basınç başlığı et kalınlığı
    bft : Çekme başlığı genişliği
    tft : Çekme başlığı et kalınlığı
    E   : Elastisite modülü
    Fy  : Beklenen akma gerilmesi

    """
    Vu                   : float
    a                    : float
    h                    : float
    tw                   : float
    d                    : float
    bfc                  : float
    tfc                  : float
    bft                  : float
    tft                  : float
    E                    : float
    Fy                   : float
    Tension_field_action : bool  = False
    kv                   : float = field(init=False)
    Cv1                  : float = field(init=False)
    Cv2                  : float = field(init=False)
    Vn                   : float = field(init=False)


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
                # print(f"gövdede, düşey ara rijitlik levhaları kullanıldığından ve a/h <= 3.0 olduğundan Yönetmelik 10.2.1 uyarınca, \ngövde levhası burkulma katsayısı, kv = 5 + (5/(a/h)) = {kv}\n")
            else:
                kv = 5.34
                # print("gövdede, düşey ara rijitlik levhaları kullanıldığından ve a/h > 3.0 olduğundan Yönetmelik 10.2.1 uyarınca, \ngövde levhası burkulma katsayısı, kv = 5.34\n")
        else:
            # print("Gövdede düşey ara rijitlik levhaları kullanılmadığı durum için, Yönetmelik 10.2.1 uyarınca, Denk.(10.3a) ile \ngövde levhası burkulma katsayısı, kv = 5.34 alınmıştır\n")
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
        chck_point1 = round(2.24* sqrt(E/Fy),2)
        chck_point2 = round(1.10 * sqrt(kv*E/Fy),2)
        #chck_point3 = 1.37 * sqrt(kv*E/Fy)

        if web_slenderness_ratio <= chck_point2 or web_slenderness_ratio <= chck_point1:
            print(f"h/tw = {web_slenderness_ratio} <= {chck_point2} = 1.10 * (kv*E/Fy)^0.5 ==> Cv1 = 1.0\n")
            Cv1 = 1.0 

        if web_slenderness_ratio > chck_point2 :
            Cv1 = round(chck_point2/web_slenderness_ratio,3)
            print(f"h/tw = {web_slenderness_ratio} > {chck_point2} = 1.10 * (kv*E/Fy)^0.5 ==> Cv1 = {Cv1}\n")

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
        chck_point = 1.37 * sqrt(kv*E/Fy)

        if web_slenderness_ratio > chck_point:
            pay = 1.51 * kv * E
            payda = web_slenderness_ratio**2 * Fy
            Cv2 = round(pay/payda,3)
            print(f"Cv2 = {Cv2}")
        else:
            print(f"h/tw={web_slenderness_ratio} < {chck_point} = 1.37*(kv*E/Fy)^0.5 ==> Cv2 kullanılamıyor.\nBu nedenle Cv2 = 0 alındı.\n")
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
        chck_point = round(1.10 * sqrt(kv*E/Fy),2)
        Vgeneral = 0.6 * Fy * Aw

        if a > 0 :
            print("Rijitlik levhaları mevcut ....")
            if a/h <= 3.0 : 
                if Tension_field_action == True :
                    print("Çekme etkisi dikkate alınması için kontrollere başlanıyor...")
                    if web_slenderness_ratio <= chck_point:
                        Vnominal = Vgeneral
                        print(f"h/tw = {web_slenderness_ratio} <= {chck_point} = 1.10 * (kv*E/Fy)^0.5 ==> Vn = 0.6*Fy*Aw = {Vgeneral}\n")

                    if web_slenderness_ratio > chck_point:
                        print(f"h/tw = {web_slenderness_ratio} > {chck_point} = 1.10 * (kv*E/Fy)^0.5 ==> Olduğu için ek kontroller yapılıyor...\n")

                        if (2*Aw/(Afc + Aft)) <= 2.5 and h/bfc <=6 and h/bft <= 6.0:
                            Vnominal = round(Vgeneral * (Cv2 + ((1-Cv2) / (1.15 * sqrt(1 + (a/h)**2)) ) ),3)
                            print(f"(2*Aw/(Afc + Aft)) = {(2*Aw/(Afc + Aft))} <= 2.5 and h/bfc = {h/bfc} <=6 and h/bft = {h/bft} <= 6.0 ==> Vn = 0.6*Fy*Aw * (Cv2 + ((1-Cv2) / (1.15 * (1 + (a/h)**2))^0.5 ) ) = {Vnominal}\n")
                        else:
                            Vnominal = round(Vgeneral * (Cv2 + ((1-Cv2) / (1.15 * ((a/h) + sqrt(1 + (a/h)**2))) ) ),3)
                            print(f"(2*Aw/(Afc + Aft)) = {(2*Aw/(Afc + Aft))} <= 2.5 and h/bfc = {h/bfc} <=6 and h/bft = {h/bft} <= 6.0  şartlarından biri sağlanmadığı için==>\nVn = 0.6*Fy*Aw * (Cv2 + ((1-Cv2) / (1.15 * ((a/h)+ (1+(a/h)**2)^0.5) ) = {Vnominal}\n")

                if Tension_field_action == False:
                    Vnominal = round(Vgeneral* Cv1,3) 
                    print(f"a>0 ; a/h <= 3.0 ama  Tension_field_action = False ==> Vnominal = 0.6 * Fy * Aw * Cv1 = 0.6 * {Fy} * {Aw} * {Cv1} = {Vnominal}\n")

            if a/h > 3.0:
                Vnominal = round(Vgeneral* Cv1,3) 
                print(f"a>0 ama a/h > 3.0 ==> Vnominal = 0.6 * Fy * Aw * Cv1 = 0.6 * {Fy} * {Aw} * {Cv1} = {Vnominal}\n")
        else:
            print("Rijitlik levhaları mevcut değil...\n")
            Vnominal = round(Vgeneral* Cv1,3) 
            print(f"Vnominal = 0.6 * Fy * Aw * Cv1 = 0.6 * {Fy} * {Aw} * {Cv1} = {Vnominal}\n")
        return Vnominal

    def CheckShearCapacity(self,Vu : float,Vn : float,fi_d : float=0.9) -> None:
        Vu = Vu/10**3
        Vn = Vn/10**3

        if Vu > fi_d*Vn:
            print(f"Vu = {Vu}kN >{fi_d}*{Vn} = {round(fi_d*Vn,3)}kN  gövde kesme kapasitesi yetersiz rijitlik levhaları kullanılmalı, \nrijitleştirme levhaları kullanıldı ise çekme alanı etkisi dikkate alınabilir\nbunlara rağmen kurtarmıyorsa rijitlik levhalarının aralıkları azaltılmalı veya kiriş gövde kalınlığı arttırılmalıdır\n")
        else:
            print(f"Vu = {Vu}kN <= {fi_d}*{Vn} = {round(fi_d*Vn,3)}kN gövde kesme kapasitesi yeterlidir. Rijitleştirme levhaları kullanıldıysa bu levhalar kontrol edilmelidir...\n")

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
    Pu      : float
    Lcx     : float
    Lcy     : float
    Lcz     : float
    h0      : float
    Fy      : float
    E       : float
    Ix      : float
    Iy      : float
    ix      : float
    iy      : float
    Ag      : float
    x0      : float
    y0      : float
    J       : float
    G       : float
    Symt    : int   = field(default=2)
    phi_d   : float = field(default=0.9)
    Pn      : float = field(init=False)
    Cw      : float = field(init=False)
    Fcr_e   : float = field(init=False)
    Fcr_ltb : float = field(init=False)
    Fcr     : float = field(init=False)
    Fex     : float = field(init=False)
    Fey     : float = field(init=False)
    Fez     : float = field(init=False)
    r0      : float = field(init=False)
    H       : float = field(init=False)



    def __post_init__(self) -> float:
        self.Cw   = self.get_Cw(self.Iy,self.h0)
        print("X ekseninde elastik eğilme burkulma yükü:")
        self.Fex  = self.GetFlexureBucklingF_e(self.E,self.Lcx,self.ix)
        print("Y ekseninde elastik eğilme burkulma yükü:")
        self.Fey  = self.GetFlexureBucklingF_e(self.E,self.Lcy,self.iy)
        self.r0   = self.Getr0(self.x0,self.y0,self.Ix,self.Iy,self.Ag)
        self.H    = self.GetH(self.x0,self.y0,self.r0)
        self.Fez  = self.GetF_ez(self.E,self.Cw,self.G,self.J,self.Lcz,self.Ag,self.r0)
        
        print("X ekseninde kritik eğilme burkulma yükü:")
        Fcr_ex = self.FlexureBucklingLoadWithoutSlendernessMember(self.Fex, self.Lcx, self.ix, self.Fy, self.E)
        print("Y ekseninde kritik eğilme burkulma yükü:")
        Fcr_ey = self.FlexureBucklingLoadWithoutSlendernessMember(self.Fey, self.Lcy, self.iy, self.Fy, self.E)
        
        print("X ekseninde kritik eğilmeli-burulmalı burkulma yükü:")
        Fcrx_ltb= self.LateralTorsionalBucklingLoadWithoutSlendernessMember(self.Lcx,self.Fy,self.ix,self.E,self.Cw,self.Lcz,self.Ix,self.Iy,self.Fex,self.Fey,self.Fez,self.H,self.Symt)
        print("Y ekseninde kritik eğilmeli-burulmalı burkulma yükü:")
        Fcry_ltb= self.LateralTorsionalBucklingLoadWithoutSlendernessMember(self.Lcy,self.Fy,self.iy,self.E,self.Cw,self.Lcz,self.Ix,self.Iy,self.Fex,self.Fey,self.Fez,self.H,self.Symt)
        
        self.Fcr_e = self.GetMinFcr_e(Fcr_ex,Fcr_ey)
        self.Fcr_ltb = self.GetMinFcr_ltb(Fcrx_ltb,Fcry_ltb)
        self.Fcr = self.GetMinFcr(self.Fcr_e,self.Fcr_ltb)
        
        self.Pn = self.CompressionStrength(self.Fcr,self.Ag)
        self.CheckCompressionStrength(self.Pn,self.Pu,self.phi_d)



    def EulerBurkulmaYükü(self,L : float, I : float,i : float , K:float = 1.0 , E : float = 2*10**5) -> float:
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
        Fcr = pi**2 * E * I / (K*L/i)**2
        return Fcr
    
    
    def Getr0(self,x0:float,y0:float,Ix:float,Iy:float,Ag:float) -> float:
            """
            polar radius of gyration about the shear center

            Arguments:
                x0 -- _description_
                y0 -- _description_
                Ix -- _description_
                Iy -- _description_
                Ag -- _description_

            Returns:
                r0 -- polar radius of gyration about the shear center
            """
            r0 = sqrt((x0**2 + y0**2) + ((Ix + Iy)/Ag))
            return r0
    

    def GetH(self,x0 : float, y0 : float, r0 : float) -> float:
        """
        flexural constant

        Arguments:
            x0 -- x coordinates of the shear center with respect to the centroid
            y0 -- y coordinates of the shear center with respect to the centroid
            r0 -- polar radius of gyration about the shear center

        Returns:
            flexural constant
        """
        H = 1 - (x0**2 + y0**2)/r0**2
        return H
    

    def GetF_ez(self,E:float,Cw:float,G:float,J:float,Lcz:float,Ag:float, r0:float)->float:
        """
        _summary_

        Arguments:
            E -- _description_
            Cw -- _description_
            G -- _description_
            J -- _description_
            Lcz -- effective length for torsional buckling
            Ag -- _description_
            r0 -- _description_

        Returns:
            _description_
        """
        Fez = ((pi**2 * E * Cw/Lcz**2) + (G*J)) * (1 / (Ag * r0**2))
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
 
    def GetFlexureBucklingF_e(self,E:float,Lc:float,i:float) -> float:
        """
        _summary_

        Arguments:
            E -- _description_
            Lc -- _description_
            i -- _description_

        Returns:
            _description_
        """
        Fe = (pi**2 * E)/(Lc/i)**2
        return Fe
    
    
    def GetMinFcr_e(self,Fcr_ex,Fcr_ey) -> float:
        Fcr_e = min(Fcr_ex,Fcr_ey)
        return Fcr_e
    
    
    def GetMinFcr_ltb(self,Fcrx_ltb,Fcry_ltb) -> float:
        Fcr_ltb = min(Fcrx_ltb,Fcry_ltb)
        return Fcr_ltb
    
    
    def GetMinFcr(self,Fcr_e,Fcr_ltb) -> float:
        Fcr = min(Fcr_e,Fcr_ltb)
        return Fcr
   
    
    def LateralTorsionalBucklingLoadWithoutSlendernessMember(self, Lb:float, Fy:float, i:float, E:float, Cw:float, Lcz:float, Ix:float, Iy:float, Fex:float, Fey:float, Fez:float, H:float, Symt:int) -> float:
        """_summary_

        Args:
            Lb (float): _description_
            Fy (float): _description_
            i (float): _description_
            E (float): _description_
            Cw (float): _description_
            Lcz (float): _description_
            Ix (_type_): _description_
            Iy (_type_): _description_
            Fex (float): _description_
            Fey (float): _description_
            Fez (float): _description_
            H (float): _description_
            Symt (int): _description_

        Returns:
            float: _description_
        
        if Symt == 0:
            first = f"(Fe-{round(Fex,3)}) * (Fe-{round(Fey,3)}) * (Fe-{round(Fez,3)})"
            second = f"Fe^2 * (Fe-{round(Fey,3)}) * (x0/r0)^2"
            third = f"Fe^2 * {round(Fex,3)}) * (y0/ro)^2"
            print(f"Kesitin simetrik ekseni yoktur denklem takımı çözülmelidir.\n{first} - {second} - {third}")
        """
       
        Fe = 0.0

        if Symt == 2:
            Fe = (pi**2 * E * Cw/Lcz**2)*(1/(Ix+Iy))
        if Symt == 1:
            Fe = ((Fey + Fez)/(2*H)) * (1 - sqrt(1 - ((4*Fey*Fez*H)/(Fey + Fez)**2)))
        
        Trashold = 4.71*sqrt(E/Fy)
        ratio = (Lb/i)
        if ratio <= Trashold:
            Fcr  = 0.658**(Fy/Fe) * Fy
        if ratio > Trashold:
            Fcr = 0.877 * Fe

        return Fcr

    
    def FlexureBucklingLoadWithoutSlendernessMember(self,Fe : float, L : float, i : float, Fy : float, E : float) -> float:
        """_summary_

        Args:
            Fe (float): _description_
            L (float): _description_
            i (float): _description_
            Fy (float): _description_
            E (float): _description_

        Returns:
            float: _description_
        """
        Trashold = 4.71*sqrt(E/Fy)
        ratio = (L/i)
        if  ratio <= Trashold:
            Fcr  = 0.658**(Fy/Fe) * Fy
        if  ratio > Trashold:
            Fcr = 0.877 * Fe
        return Fcr
    
    
    def CompressionStrength(self,Fcr : float, Ag : float) -> float:
        """
        _summary_

        Arguments:
            Fcr -- Burkulma yükü
            Ag -- Brüt kesit alanı

        Returns:
            Basınç kapasitesi
        """
        Pn = Fcr*Ag
        return Pn

    
    def CheckCompressionStrength(self,Pn:float,Pu:float,phi_d:float) -> None:
        capacity = round(phi_d*Pn,3)
        if Pu > capacity:
            text = f"{Pu/10**3}kN > {capacity/10**3}kN--Basınc kapasitesi yetersizdir..."
        if Pu <= capacity:
            text = f"{Pu/10**3}kN <= {capacity/10**3}kN-- Basınc kapasitesi yeterlidir..."
        return text

#Eğilme kuvveti etkisindeki I profil elemanların tasarımı
#========================================================================================================

#Yerel burkulma durumu kontrol edilmeli
@dataclass
class Flexure:
    Mu       : float
    Lb       : float
    Iy       : float
    h0       : float
    Sx       : float
    Zx       : float
    iy       : float
    Fy       : float
    E        : float
    J        : float
    Mmax     : float
    Ma       : float
    Mb       : float
    Mc       : float
    fi_d     : float = 0.9
    Cw       : float = field(init=False)
    i_ts     : float = field(init=False)
    Lp       : float = field(init=False)
    Lr       : float = field(init=False)
    Cb       : float = field(init=False)
    Fcr      : float = field(init=False)
    Mn_ltb   : float = field(init=False)
    Mp       : float = field(init=False)
    Me       : float = field(init=False)
    

    def __post_init__(self):
        self.Cw     = self.Get_Cw(self.Iy,self.h0)
        self.i_ts   = self.Get_i_ts(self.Iy,self.Cw,self.Sx)
        self.Lp     = self.Get_Lp(self.iy,self.Fy,self.E)
        self.Lr     = self.Get_Lr(self.i_ts,self.J,self.Sx,self.h0,self.Fy,self.E)
        self.Cb     = self.Get_Cb(self.Mmax,self.Ma,self.Mb,self.Mc)
        self.Fcr    = self.Get_ElasticLTB_Fcr(self.Lb,self.i_ts,self.J,self.Sx,self.h0,self.Cb,self.E)
        self.Me     = self.Get_SectionElasticMomentCapacity(self.Fy,self.Sx)
        self.Mp     = self.PlasticFlexureCapacity(self.Fy,self.Zx)
        self.Mn_ltb = self.LateralTorsionalBucklingCapacity(self.Mp, self.Me, self.Lb, self.Lp, self.Lr, self.Fcr, self.Sx, self.Cb)
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
        Etkin atalet yarıçapını hesaplar\nTBDY Denk. 9.8a kullanılmıştır. Dilenirse 9.8b kullanılabilir.

        Arguments:
            Iy -- Y eksenindeki atalet
            Cw -- Çarpılma(Warping) sabiti
            Sx -- X(Z) ekseni etrafında elastik kesit mukavemet momenti

        Returns:
            Etkin atalet yarıçapı
        """
        i_ts = ((sqrt(Iy*Cw) / Sx))**0.5
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
        Lp = 1.76 * i_y * (sqrt(E/Fy))
        return round(Lp,2)

    
    def Get_Lr(self,i_ts : float,J : float,Sx : float,ho : float,Fy:float, c : float = 1.0,E : float = 2*10**5) -> float:
        """Elastik LTB oluşumu için gerekli boy

        Args:
            i_ts (float): Etkin dönme atalet yaricapi
            J (float): Burulma sabiti
            Sx (float): Kesitin x ekseni etrafindaki elastik mukavemet momenti
            ho (float): Enkesit basliklarinin agirlik merkezleri arasindaki uzaklik
            Fy (float): Kesit malzemesinin akma dayanimi
            c (float, optional): Defaults to 1.0
            E (float, optional): Kesit malzemesinin elastisite modulu. Defaults to 2*10**5.

        Returns:
            float: Elastik LTB serbest boy siniri
            # a = (J*c/(Sx*ho))
            # b = (6.76 * (0.7 * Fy / E)**2)
            # first = sqrt(a**2 + b)
            # Lr = 1.95 * i_ts * (E / (0.7 * Fy)) * sqrt(a + first)  
        """
          
        Lr = 1.95 * i_ts * (E / (0.7 * Fy)) * sqrt((J*c/(Sx*ho)) + (sqrt((J*c/(Sx*ho))**2 + (6.76 * (0.7 * Fy / E)**2))))
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
        Cb = (12.5 * Mmax) / (2.5 * Mmax + 3*Ma + 4*Mb + 3*Mc)
        return round(Cb,2)

    
    def Get_ElasticLTB_Fcr(self,Lb : float,i_ts : float,J : float,Sx : float,ho : float ,Cb : float = 1.0 ,E : float = 2*10**5) -> float:
        """
        _summary_

        Arguments:
            Lb -- _description_
            i_ts -- _description_
            J -- _description_
            Sx -- _description_
            ho -- _description_

        Keyword Arguments:
            Cb -- _description_ (default: {1.0})
            E -- _description_ (default: {2*10**5})

        Returns:
            _description_
        """
        Fcr = ((Cb * pi**2 * E) / ((Lb/i_ts)**2)) * (sqrt(1 + (0.078 * (J / (Sx * ho)) * (Lb / i_ts)**2 )))
        return Fcr

    
    def Get_SectionElasticMomentCapacity(self, Fy : float, Sx : float) -> float:
        Me = Fy*Sx
        return Me
    
    
    def PlasticFlexureCapacity(self,Fy : float, Zx : float) -> float:
        """
        _summary_
        Lokal-burkulma-durumu-kompakt-yüksek-sünek-kesit-secildiği-kabulü-ile-kontrol-edilmemiştir-bu-nedenle-plastik-kapasitede-herhangi-bir-azaltma-yapılmamıstır.

        Arguments:
            Fy -- _description_
            Zx -- _description_

        Returns:
            _description_
        """
        Mp = Fy*Zx
        return Mp
    
    
    def LateralTorsionalBucklingCapacity(self,Mp: float, Me : float,Lb : float,Lp : float,Lr : float,Fcr : float,Sx : float,Cb : float = 1.0) -> float:
        """_summary_

        Args:
            Mp (float): _description_
            Me (float): _description_
            Lb (float): _description_
            Lp (float): _description_
            Lr (float): _description_
            Fcr (float): _description_
            Sx (float): _description_
            Cb (float, optional): _description_. Defaults to 1.0.

        Returns:
            float: _description_
        """

        Mn_iltb = Cb * (Mp - (Mp - 0.7*Me) * ((Lb - Lp) / (Lr - Lp)))
        Mn_eltb = Fcr * Sx

        if Lb <= Lp :
            text = "LTB-oluşmaz-Mn-platik-moment-kapasitesine-eşittir."
            Mn = Mp
        
        if Lb > Lp and Lb <= Lr:
            situation = "Inelastik-LTB-olusur"
            Mn = Mn_iltb 
            if Mn > Mp :
                text = "Mn-Plastik-moment-kapasitesinden-fazla-olamaz"
                Mn = Mp
                 
        if Lb > Lr :
            Mn = Mn_eltb
            text = "Elastik-LTB-olusur"
            if Mn > Mp:
                text = "Mn-Plastik-moment-kapasitesinden-fazla-olamaz"
                Mn = Mp
        
        return Mn
    
    
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
        Mn_design = Mn*fi_d
        
        if Mn_design < Mu:
            text = "Mndesign <  Mu --> Eğilme kapasitesi yetersizdir..."
        elif Mn_design >= Mu:
            text = "Mndesign >- Mu --> Eğilme kapasitesi yeterlidir..."

#Burulma kuvvet etkisindeki I profil elemanların tasarımı
#========================================================================================================
@dataclass
class Torsion:

    def PureTorsionCapacity(G : float, J : float, DerivativeTeta : float) -> float:
        """Calculate Pure Torsion Capacity

        Args:
            G (float): Shear modules of elasticity of steel
            J (float): Polar moment of inertia
            DerivativeTeta (float): Torsional curvature, Teta is twist angle

        Returns:
            Ts (float): Pure torsional capacity
        """
        Ts = G * J * DerivativeTeta
        return Ts
    
    def WarpingTorsionalCapacity(E : float, Cw : float, TripleDerivativeTeta : float) -> float:
        """Calculate Warping torsional capacity

        Args:
            E (float): Young modules of steel
            Cw (float): Warping constant. Cw=I_f(h^2/2) note that T and L shapes sections Cw almost zero
            TripleDerivativeTeta (float): thre derivative twist angle. Check design guide 9 

        Returns:
            Tw (float): Warping torsional capacity
        """
        Tw = -1*E*Cw*TripleDerivativeTeta
        return Tw

    def TorsionCapacity(Ts : float, Tw : float) -> float:
        return Ts+Tw

#Bileşik kuvvet etkisindeki I profil elemanların tasarımı
#========================================================================================================
class CombineForce:

    def CheckCombineFlexureAndCompressionSymetricMembers(self,Pr : float, Pc : float, Mrx : float, Mry : float, Mcx : float, Mcy : float) -> None:
        """
        Eğilme ve basınç bileşik etkileri altında olan tek veya çift eksende simetrik olan kesitlerin dayanım kontrolünü yapar. x ekseni kuvvetli eksen, y zayıf eksen için tabir edilmekte

        Arguments:
            Pr -- Gerekli eksenel kuvvet dayanımı
            Pc -- Mevcut eksenel kuvvet dayanımı (fi_d * Pn)
            Mrx -- Kesitin x ekseninde gerekli eğilme momenti dayanımı
            Mry -- Kesitin y ekseninde gerekli eğilme momenti dayanımı
            Mcx -- Kesitin x ekseninde eğilme momenti dayanımı (fi_d * Mn)
            Mcy -- Kesitin y ekseninde eğilme momenti dayanımı (fi_d * Mn)
        """

        if Pr/Pc >= 0.2:
            alfa = (Pr/Pc) + (8/9) * ((Mrx/Mcx) + (Mry/Mcy))
            if alfa <= 1.0 :
                print("Kapasite yeterlidir...")
            else:
                print("Kapasite yetersizdir.")
        
        if Pr/Pc < 0.2:
            alfa = (Pr/(2*Pc)) + (8/9) * ((Mrx/Mcx) + (Mry/Mcy))
            if alfa <= 1.0 :
                print("Kapasite yeterlidir...")
            else:
                print("Kapasite yetersizdir.")
        
    def CheckCombineFlexureAndCompressionNotSymetricMembers(self,f_ra : float, F_ca : float, f_rbw : float, F_cbw : float, f_rbz : float, F_cbz : float) -> None:
        """
        _summary_

        Arguments:
            f_ra -- En büyük eksenel gerilme
            F_ca -- Dikkate alınan noktadaki mevcut eksenel sınır gerilme
            f_rbw -- En büyük eğilme gerilmesi
            F_cbw -- Mevcut eğilme sınır gerilmesi
            f_rbz -- En büyük eğilme gerilmesi
            F_cbz -- Mevcut eğilme sınır gerilmesi (fi_d * Mn / We)
        """
        trashold = abs((f_ra/F_ca) + (f_rbw/F_cbw) + (f_rbz/F_cbz))
        if trashold <= 1.0:
            print("Kapasite yeterli...")
        else:
            print("Kapasite yetersiz...")

    def RoundHssSectionBucklingStress(self,L : float, D : float, t : float, Fy : float, E : float) -> float:
        """
        Boru kesitler için burkulma gerilmesini hesaplar.

        Arguments:
            L -- Eleman uzunluğu
            D -- Boru en kesiti dış çapı
            t -- boru enkesitinin et kalınlığı
            Fy -- Akma gerilmesi
            E -- Elastisite modülü

        Returns:
            Fcr (float) -- Burkulma gerilmesi
        """
        Fcr1 = 1.23*E / (sqrt(L/D) * (D/t)**(5/4))
        Fcr2 = 0.6*E / ((D/t)**(3/2))

        Fcr = max(Fcr1,Fcr2)
        if Fcr > 0.6*Fy:
            Fcr = 0.6*Fy
        return Fcr

    #Burulma + Diğer kuvvetler için
    def GetRoundHssTorsionalConstant(self,D : float, t : float) -> float:
        """
        Boru profiller için güvenli tarafta kalacak şekilde burulma sabitini verir.

        Arguments:
            D -- Boru en kesiti dış çapı
            t -- boru enkesitinin et kalınlığı

        Returns:
            Burulma sabiti
        """
        C = (pi * (D-t)**2 * t )/ 2

    def RectangularHssSectionBucklingStress(self,h : float, t : float, Fy : float, E : float) -> float:
        """
        Kutu kesitler için burkulma gerilmesini hesaplar.

        Arguments:
            h -- Uzun kenar düz kısım genişliği
            t -- Tasarım et kalınlığı
            Fy -- Akma gerilmesi
            E -- Elastisite modülü

        Returns:
            _description_
        """
        Trashold = h/t
        Trashold2 = 2.45 * sqrt(E/Fy)
        Trashold3 = 3.07 * sqrt(E/Fy)

        if Trashold <= Trashold2:
            Fcr = 0.6 * Fy
        if Trashold2 < Trashold and Trashold <= Trashold3:
            Fcr = (0.6 * Fy * (2.45 * sqrt(E/Fy))) / Trashold
        if Trashold3 < Trashold and Trashold <= 260:
            Fcr = (0.458 * pi**2 * E) / Trashold**2
        
        return Fcr

    def GetRectangularHssTorsionalConstant(self,B : float, t : float, H : float) -> float:
        """
        Kutu profiller için güvenli tarafta kalacak şekilde burulma sabitini verir.

        Arguments:
            B -- Kutu en kesit genişliği
            t -- Tasarım et kalınlığı
            H -- Kutu En kesit yüksekliği

        Returns:
            Burulma sabiti
        """

        C = (2* (B-t) * (H-t) * t) - (4.5 * (4-pi) * t**3)

        return C

    def HssSectionDesignTorsionalStrength(self,Fcr : float,C : float, fi_d : float = 0.9):
        """
        Kapalı kesitin tasarım burulma dayanımı

        Arguments:
            Fcr -- Burkulma gerilmesi
            C -- Burulma sabiti

        Keyword Arguments:
            fi_d -- Limit durum azaltma katsayısı (default: {0.9})

        Returns:
            Tasarım burulma dayanımı
        """
        Tn = Fcr * C
        Td = Tn * fi_d
        return Td
        
    def CheckHssSectionCombineTorsionAndOtherForce(self,Pr : float, Pc : float, Mr : float, Mc : float, Vr : float, Vc : float, Tr : float, Tc : float) -> None:
        if Tr <= Tc*0.2:
            self.CheckCombineFlexureAndCompressionSymetricMembers(Pr,Pc,Mr,Mr,Mc,Mc)
        if Tr > Tc*0.2:
            limit = ((Pr/Pc) + (Mr/Mc)) + ((Vr/Vc) + (Tr/Tc))
            if limit <= 1.0 : 
                print("Kesit yeterlidir..")
            else:
                print("kesit yeterli değildir!!!")

    def OtherSectionCombineForceStrength(self, Fy : float,Fcr : float) -> float:
        Fn = min(0.6*Fy, Fcr)
        return Fn

@dataclass
class Concentrated:
    """
    #Tekil kuvvet altında tasarım kontrolleri / Concentrated Force Limit State Check
    #========================================================================================================
    ### 1- Flange local bending
    ### 2- Web local yielding
    ### 3- Web local crippling
    ### 4- Web sidesway buckling
    ### 5- Web compression buckling
    ### 6- Web panel zone shear
    """

    def FlangeLocalBending(self,tf : float, F_yf : float, y : float) -> float:
        """_summary_

        Args:
            tf (float): _description_
            F_yf (float): _description_
            y (float): _description_

        Returns:
            float: _description_
        """
        Rn = 1000000
        if y >= 10*tf:
            Rn = 6.25 * tf**2 * F_yf
        return Rn
    
    def WebLocalYielding(self,lb : float, k : float, Fyw : float, tw : float, y : float, d : float) -> float:
        """_summary_

        Args:
            lb (float): Bearing plate length
            k (float): _description_
            Fyw (float): _description_
            tw (float): _description_
            y (float): _description_
            d (float): _description_

        Returns:
            float: _description_
        """
        if y > d:
            Rn = (5*k + lb) * Fyw * tw
            print(f"y > d ==> Rn = (5*k + lb) * Fyw * tw = (5*{k} + {lb}) * {Fyw} * {tw} = {Rn}N")
        else:
            Rn = (2.5*k + lb) * Fyw * tw
            print(f"y <= d ==> Rn = (2.5*k + lb) * Fyw * tw = (2.5*{k} + {lb}) * {Fyw} * {tw} = {Rn}N")
        
        return Rn
    
    def WebLocalCrippling(self,y : float, d : float, Lb : float, tw : float, tf : float, E : float, Fyw : float) -> float:
        """_summary_

        Args:
            y (float): _description_
            d (float): overall depth of the member
            Lb (float): length of bearing
            tw (float): Web thickness
            tf (float): Flange thickness
            E (float): _description_
            Fyw (float): _description_

        Returns:
            float: _description_
        """
        if y > d:
            Rn = 0.8 * tw**2 * (1 + 3*(Lb/d)*(tw/tf)**1.5) * sqrt((E*Fyw*tf)/tw)
        if y <= d and Lb/d <= 0.2:
            Rn = 0.4 * tw**2 * (1 + 3*(Lb/d)*(tw/tf)**1.5) * sqrt((E*Fyw*tf)/tw)
        if y <= d and Lb/d > 0.2:
            Rn = 0.4 * tw**2 * (1 + 3*((4*Lb/d)-0.2)*(tw/tf)**1.5) * sqrt((E*Fyw*tf)/tw)
        return Rn

    def WebSideswayBuckling(self,h : float, tw : float, Lb : float, bf : float, Cr : float, tf : float, CompFlangeRestrainedRotation : bool) -> float:
        """_summary_

        Args:
            h (float) : _description_
            tw (float): _description_
            Lb (float): Largest laterally unbraced length along either flange at the point of load
            bf (float): _description_
            Cr (float): 6.6x106 MPa for Mu < My at the location of the force
                        3.3x106 MPa for Mu≥ My at the location of the force
            tf (float): _description_
            CompFlangeRestrainedRotation (bool): _description_

        Returns:
            float: _description_
        """
        trashold = (h/tw) / (Lb/bf)

        if CompFlangeRestrainedRotation:
            if trashold <= 2.3:
                Rn = ((Cr * tw**3 * tf)/h**2) * (1 + 0.4 * trashold**3)
            if trashold > 2.3:
                print("Web sidesway buckling doesn't occur")
                Rn = 10000000
        else:
            if trashold <= 1.7:
                Rn = ((Cr * tw**3 * tf)/h**2) * (0.4 * trashold**3)
            if trashold > 1.7:
                print("Web sidesway buckling doesn't occur")
                Rn = 10000000
        
        return Rn
    
    def WebCompressionBuckling(self,y : float, d : float, tw : float, h : float, E : float, Fyw : float) -> float:
        """_summary_

        Args:
            y (float): _description_
            d (float): _description_
            tw (float): _description_
            h (float): _description_
            E (float): _description_
            Fyw (float): _description_

        Returns:
            float: _description_
        """
        if y >= d/2:
            Rn = (24 * tw**3 * sqrt(E*Fyw))/h
        else:
            Rn = (12 * tw**3 * sqrt(E*Fyw))/h
        
        return Rn
    
    def WebPanelZoneShear(self,Pu : float, Py : float, dc : float, tw : float, db : float, bcf : float, tcf : float,Fy :float, PanelZoneConsideredAnalysis : bool) -> float:
        """_summary_

        Args:
            Pu (float): _description_
            Py (float): _description_
            dc (float): _description_
            tw (float): _description_
            db (float): _description_
            bcf (float): _description_
            tcf (float): _description_
            PanelZoneConsideredAnalysis (bool): _description_

        Returns:
            float: _description_
        """
        if PanelZoneConsideredAnalysis == False:
            if Pu <= 0.4*Py:
                Rv = 0.6 * Fy* dc * tw
            else:
                Rv = 0.6 * Fy* dc * tw * (1.4 - (Pu/Py))
        else:
            if Pu <= 0.75*Py:
                Rv = 0.6 * Fy* dc * tw * (1 + ((3*bcf*tcf**2)/(db*dc*tw)))
            else:
                Rv = 0.6 * Fy* dc * tw * (1 + ((3*bcf*tcf**2)/(db*dc*tw))) * (1.9 - (1.2*Pu/Py))
        
        return Rv

    def CheckWebPanelZoneShear(Rv : float, Mu1 : float, Mu2 : float, dm1 : float, dm2 : float, Vu : float, fi_d : float = 0.85) -> None:
        TotalFu = (Mu1/dm1) + (Mu2/dm2) - Vu

        if fi_d*Rv >= TotalFu:
            print("Panel zone safe..")
        else:
            print("Panel zone not safe !!!")

