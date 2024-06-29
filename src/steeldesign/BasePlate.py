
from dataclasses import dataclass, field

from steeldesign.Material import Steel,S235


@dataclass
class Plate:
    B  : float
    N  : float
    B2 : float
    N2 : float
    m  : float
    n  : float
    t  : float
    Mat : Steel = field(default_factory=Steel)

    def __init__(self, B : int, N : int, B2 : int, N2 : int, m : float, n : float, t : float, Mat : Steel) -> None:
        self.B = B
        self.N = N
        self.B2 = B2
        self.N2 = N2
        self.m = m
        self.n = n
        self.t = t
        self.Mat = Mat

        self.A1 = self.GetBasePlateArea()
        self.A2 = self.GetGroutArea()
        self.Case = self.DefineCase()

    def GetBasePlateArea(self) -> float:
        A1 = self.B * self.N
        return round(A1,2)
    
    def GetGroutArea(self) -> float:
        A2 = self.B2 * self.N2
        return round(A2,2)
    
    def DefineCase(self)-> int:
        if self.A1 == self.A2:
            Case = 1
        if self.A2 >= 4*self.A1:
            Case = 2
        if self.A1 < self.A2 and self.A2 < 4*self.A1:
            Case = 3
        return Case

# class Plate:

#     def __init__(self, B : int, N : int, B2 : int, N2 : int, m : float, n : float, t : float, Mat : Steel) -> None:
#         self.B = B
#         self.N = N
#         self.B2 = B2
#         self.N2 = N2
#         self.m = m
#         self.n = n
#         self.t_p = t
#         self.Mat = Mat

#         self.A1 = self.B * self.N
#         self.A2 = self.B2 * self.N2
#         self.Case = self.DefineCase()

#     def __repr__(self) -> str:
#         return f" B = {self.B}\n N = {self.N}\n B2 = {self.B2}\n N2 = {self.N2}\n m = {self.m}\n n = {self.n}\n t_p = {self.t_p}\n Mat = {self.Mat}\n A1 = {self.A1}\n A2 = {self.A2}\n Case = {self.Case}\n"
    
#     def DefineCase(self)-> int:
#         if self.A1 == self.A2:
#             Case = 1
#         if self.A2 >= 4*self.A1:
#             Case = 2
#         if self.A1 < self.A2 and self.A2 < 4*self.A1:
#             Case = 3
#         return Case


# if __name__=="__main__":
#     s1 = S235()
#     p1 = Plate(100,100,110,110,10,10,10,s1)
#     print(p1)
#     print(p1.Case)