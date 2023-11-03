from dataclasses import Field, dataclass
from math import sqrt
from typing import overload
import matplotlib.pyplot as plt
from math import atan2, sin, cos, sqrt, pi, degrees

@dataclass
class MechanicalProperties:
    SectionPoints : list = Field(default_factory=list)
    A             : float = Field(init=False,default_factory=float)
    cx            : float
    cy            : float
    Ixx           : float
    Iyy           : float
    Ixy           : float

    def __post_init__(self):
        self.A = self.area(self.SectionPoints)
        self.cx, self.cy = self.centroid(self.SectionPoints)
        self.Ixx, self.Iyy, self.Ixy = self.inertia(self.SectionPoints)
    
    def area(self,pts):
        'Area of cross-section.'
        
        if pts[0] != pts[-1]:
            pts = pts + pts[:1]
        x = [ c[0] for c in pts ]
        y = [ c[1] for c in pts ]
        s = 0
        for i in range(len(pts) - 1):
            s += x[i]*y[i+1] - x[i+1]*y[i]
        return s/2

    def centroid(self,pts):
        'Location of centroid.'
        
        if pts[0] != pts[-1]:
            pts = pts + pts[:1]
        x = [ c[0] for c in pts ]
        y = [ c[1] for c in pts ]
        sx = sy = 0
        a = self.area(pts)
        for i in range(len(pts) - 1):
            sx += (x[i] + x[i+1])*(x[i]*y[i+1] - x[i+1]*y[i])
            sy += (y[i] + y[i+1])*(x[i]*y[i+1] - x[i+1]*y[i])
        return sx/(6*a), sy/(6*a)

    def inertia(self,pts):
        'Moments and product of inertia about centroid.'
        
        if pts[0] != pts[-1]:
            pts = pts + pts[:1]
        x = [ c[0] for c in pts ]
        y = [ c[1] for c in pts ]
        sxx = syy = sxy = 0
        a = self.area(pts)
        cx, cy = self.centroid(pts)
        for i in range(len(pts) - 1):
            sxx += (y[i]**2 + y[i]*y[i+1] + y[i+1]**2)*(x[i]*y[i+1] - x[i+1]*y[i])
            syy += (x[i]**2 + x[i]*x[i+1] + x[i+1]**2)*(x[i]*y[i+1] - x[i+1]*y[i])
            sxy += (x[i]*y[i+1] + 2*x[i]*y[i] + 2*x[i+1]*y[i+1] + x[i+1]*y[i])*(x[i]*y[i+1] - x[i+1]*y[i])
        return sxx/12 - a*cy**2, syy/12 - a*cx**2, sxy/24 - a*cx*cy

    def principal(self,Ixx, Iyy, Ixy):
        'Principal moments of inertia and orientation.'
        
        avg = (Ixx + Iyy)/2
        diff = (Ixx - Iyy)/2      # signed
        I1 = avg + sqrt(diff**2 + Ixy**2)
        I2 = avg - sqrt(diff**2 + Ixy**2)
        theta = atan2(-Ixy, diff)/2
        return I1, I2, theta

    def summary(self,pts):
        'Text summary of cross-sectional properties.'
        
        a = self.area(pts)
        cx, cy = self.centroid(pts)
        Ixx, Iyy, Ixy = self.inertia(pts)
        I1, I2, theta = self.principal(Ixx, Iyy, Ixy)
        summ = """Area
        A = {}
        Centroid
        cx = {}
        cy = {}
        Moments and product of inertia
        Ixx = {}
        Iyy = {}
        Ixy = {}
        Principal moments of inertia and direction
        I1 = {}
        I2 = {}
        θ︎ = {}°""".format(a, cx, cy, Ixx, Iyy, Ixy, I1, I2, degrees(theta))
        return summ
 
    def outline(self,pts, basename='section', format='pdf', size=(8, 8), dpi=100):
        'Draw an outline of the cross-section with centroid and principal axes.'
        
        if pts[0] != pts[-1]:
            pts = pts + pts[:1]
        x = [ c[0] for c in pts ]
        y = [ c[1] for c in pts ]
        
        # Get the bounds of the cross-section
        minx = min(x)
        maxx = max(x)
        miny = min(y)
        maxy = max(y)
        
        # Whitespace border is 5% of the larger dimension
        b = .05*max(maxx - minx, maxy - miny)
        
        # Get the properties needed for the centroid and principal axes
        cx, cy = self.centroid(pts)
        i = self.inertia(pts)
        p = self.principal(*i)
        
        # Principal axes extend 10% of the minimum dimension from the centroid
        length = min(maxx-minx, maxy-miny)/10
        a1x = [cx - length*cos(p[2]), cx + length*cos(p[2])]
        a1y = [cy - length*sin(p[2]), cy + length*sin(p[2])]
        a2x = [cx - length*cos(p[2] + pi/2), cx + length*cos(p[2] + pi/2)]
        a2y = [cy - length*sin(p[2] + pi/2), cy + length*sin(p[2] + pi/2)]
        
        # Plot and save
        # Axis colors chosen from http://mkweb.bcgsc.ca/colorblind/
        fig, ax = plt.subplots(figsize=size)
        ax.plot(x, y, 'k*-', lw=2)
        ax.plot(a1x, a1y, '-', color='#0072B2', lw=2)     # blue
        ax.plot(a2x, a2y, '-', color='#D55E00')           # vermillion
        ax.plot(cx, cy, 'ko', mec='k')
        ax.set_aspect('equal')
        plt.xlim(xmin=minx-b, xmax=maxx+b)
        plt.ylim(ymin=miny-b, ymax=maxy+b)
        filename = basename + '.' + format
        plt.savefig(filename, format=format, dpi=dpi)
        plt.close()

@dataclass
class IShapeGeometry:
    """
    Arguments
        d       -- Kesit yüksekliği
        h       -- Gövde levhası yüksekliği
        tw      -- Gövde levhası et kalınlığı
        bftop   -- Üst başlık genişliği
        tftop   -- Üst başlık et kalınlığı
        bfbot   -- Alt başlık genişliği
        tfbot   -- Alt başlık kalınlığı
        h0      -- Enkesit basliklarinin agirlik merkezleri arasindaki uzaklik
        Ag      -- En kesit alanı
        x0      -- Kayma merkezinin kesit merkezine x doğrultusundaki uzaklığı
        y0      -- Kayma merkezinin kesit merkezine y doğrultusundaki uzaklığı
    """
    d       : float
    h       : float
    tw      : float
    bftop   : float
    tftop   : float
    bfbot   : float
    tfbot   : float
    h0      : float
    Ag      : float
    x0      : float
    y0      : float

@dataclass
class ISectionPropManager:
    """
    Arguments:
        Iz      -- Z ekseni yönündeki atalet momenti
        Iy      -- Y ekseni yönündeki atalet momenti
        Ip      -- Polar atalet momenti
        iz      -- Z ekseni yönündeki atalet yarıçapı
        iy      -- Y ekseni yönündeki atalet yarıçapı
        ip      -- Polar atalet yarıçapı
        its     -- Etkin atalet yarıçapı
        Jc      -- Burulma sabiti
        Wez     -- Z eksenindeki elastik mukavemet momenti
        Wey     -- Y eksenindeki elastik mukavemet momenti
        Wpx     -- Z eksenindeki elastik mukavemet momenti
        Wpy     -- Y eksenindeki elastik mukavemet momenti
        Cw      -- Warping sabiti
        H       -- Eğilme sabiti

    Returns:
        _type_: _description_
    """
    Geometri : IShapeGeometry = Field(default_factory=IShapeGeometry)
    Iz      : float = Field(init=False)
    Iy      : float = Field(init=False)
    Ip      : float = Field(init=False)
    iz      : float = Field(init=False)
    iy      : float = Field(init=False)
    ip      : float = Field(init=False)
    its     : float = Field(init=False)
    J       : float = Field(init=False)
    Wez     : float = Field(init=False)
    Wey     : float = Field(init=False)
    Wpx     : float = Field(init=False)
    Wpy     : float = Field(init=False)
    Cw      : float = Field(init=False)
    H       : float = Field(init=False)

    def __post_init__(self) -> None:
        self.Iz  = self.Get_Iz()
        self.Iy  = self.Get_Iy()
        self.Ip  = self.Get_Ip()
        self.iz  = self.Get_iz()
        self.iy  = self.Get_iy()
        self.ip  = self.Get_ip()
        self.its = self.Get_its()
        self.J   = self.Get_J()
        self.Wez = self.Get_Wez()
        self.Wey = self.Get_Wey()
        self.Wpx = self.Get_Wpz()
        self.Wpy = self.Get_Wpy()
        self.Cw  = self.Get_Cw()
        self.H   = self.Get_H()
        
    def Get_Iz():
        pass

    def Get_Iy():
        pass

    def Get_Ip():
        pass

    def Get_iy():
        pass

    def Get_iz():
        pass

    def Get_ip():
        pass
    
    def Get_its(self,Iy : float, Cw : float, Sx : float) -> float:
        """
        Etkin atalet yarıçapını hesaplar

        Arguments:
            Iy -- Y eksenindeki atalet
            Cw -- Çarpılma(Warping) sabiti
            Sx -- X ekseni etrafında elastik kesit mukavemet momenti

        Returns:
            Etkin atalet yarıçapı
        """
        i_ts = ((sqrt(Iy*Cw) / Sx))**0.5
        return i_ts
    
    @overload
    def Get_its(self, bf : float, h : float, tw : float, tf : float) -> float:
        """Etkin atalet yarıçapı hesabını yapar. 
        Çift simetri eksenli I kesitlerde güvenli tarafta kalınarak,
        its için enkesit basınç başlığı ve gövdesinin 1/6 sı ile tanımlanan parçasının 
        düşey simetri eksenine göre hesaplanan atalet yarıçapı kullanılır.

        Args:
            bf (float): Basın başlığı genişliği
            h (float) : Kesit gövde levhası yüksekliği
            tw (float): Gövde levhası et kalınlığı
            tf (float): Basınç başlığı et kalınlığı

        Returns:
            float: etkin atalet yarıçapı
        """

        its = bf / (sqrt(12 * (1 + ((1/6) * (h*tw)/(bf*tf)))))
        return round(its,2)

    def Get_J():
        pass

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
    
    def Get_Wez():
        pass
    
    def Get_Wey():
        pass

    def Get_Wpz():
        pass
    
    def Get_Wpy():
        pass

    def Get_r0(x0:float,y0:float,Ix:float,Iy:float,Ag:float) -> float:
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
        first = x0**2 + y0**2
        second = (Ix + Iy)/Ag
        r0 = sqrt(first+second)
        return r0
    
    def Get_H(x0 : float, y0 : float, r0 : float) -> float:
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
        b = sqrt(a)
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
        first = sqrt(a**2 + b)
        Lr = 1.95 * i_ts * (E / (0.7 * Fy)) * sqrt(a + first)
        return round(Lr,2)



@dataclass
class ISection:
    """
    Arguments
        d       -- Kesit yüksekliği
        h       -- Gövde levhası yüksekliği
        tw      -- Gövde levhası et kalınlığı
        bftop   -- Üst başlık genişliği
        tftop   -- Üst başlık et kalınlığı
        bfbot   -- Alt başlık genişliği
        tfbot   -- Alt başlık kalınlığı
        h0      -- Enkesit basliklarinin agirlik merkezleri arasindaki uzaklik
        Ag      -- En kesit alanı
        Iz      -- Z ekseni yönündeki atalet momenti
        Iy      -- Y ekseni yönündeki atalet momenti
        Ip      -- Polar atalet momenti
        iz      -- Z ekseni yönündeki atalet yarıçapı
        iy      -- Y ekseni yönündeki atalet yarıçapı
        ip      -- Polar atalet yarıçapı
        its     -- Etkin atalet yarıçapı
        Jc      -- Burulma sabiti
        Wez     -- Z eksenindeki elastik mukavemet momenti
        Wey     -- Y eksenindeki elastik mukavemet momenti
        Wpx     -- Z eksenindeki elastik mukavemet momenti
        Wpy     -- Y eksenindeki elastik mukavemet momenti
        Cw      -- Warping sabiti
        x0      -- Kayma merkezinin kesit merkezine x doğrultusundaki uzaklığı
        y0      -- Kayma merkezinin kesit merkezine y doğrultusundaki uzaklığı
        r0      -- Kesme merkezindeki polar atalet yarıçapı
        H       -- Eğilme sabiti
        E       -- Elastisite modülü
    """
    d       : float
    h       : float
    tw      : float
    bftop   : float
    tftop   : float
    bfbot   : float
    tfbot   : float
    h0      : float
    Ag      : float
    Iz      : float
    Iy      : float
    Ip      : float
    iz      : float
    iy      : float
    ip      : float
    its     : float
    Jc      : float
    Wez     : float
    Wey     : float
    Wpx     : float
    Wpy     : float
    Cw      : float
    x0      : float
    y0      : float
    r0      : float
    H       : float
    E       : float