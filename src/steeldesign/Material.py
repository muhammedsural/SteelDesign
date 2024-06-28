from dataclasses import asdict, dataclass


@dataclass
class Steel:
    Name    : str   = None
    F_y     : float = None
    F_u     : float = None
    Ry      : float = None
    Density : float = 80.
    Es      : float = 2*10**5
        
    def asdict():
        return asdict()
    
class S235(Steel):
    def __init__(self)->None:
        super().__init__(Name='S235',F_y=235,F_u=360,Ry=round(360/235,2))

class S275(Steel):
    def __init__(self)->None:
        super().__init__(Name='S275',F_y=275,F_u=360,Ry=round(430/275,2))

class S355(Steel):
    def __init__(self)->None:
        super().__init__(Name='S355',F_y=510,F_u=360,Ry=round(510/355,2))

class S440(Steel):
    def __init__(self)->None:
        super().__init__(Name='S450',F_y=440,F_u=550,Ry=round(550/440,2))


@dataclass
class Concrete:
    Name   : str
    F_ck   : float
    F_ctk  : float
    E_c    : float 
    Density: float = 24

    def asdict():
        return asdict()
    
class C16(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C16',F_ck=16,F_ctk=1.4,E_c=27_000)

class C18(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C18',F_ck=18,F_ctk=1.5,E_c=27_500)

class C20(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C20',F_ck=20,F_ctk=1.6,E_c=28_000)

class C25(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C25',F_ck=25,F_ctk=1.8,E_c=30_000)

class C30(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C30',F_ck=30,F_ctk=1.9,E_c=32_000)

class C35(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C35',F_ck=35,F_ctk=2.1,E_c=33_000)

class C40(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C40',F_ck=40,F_ctk=2.2,E_c=34_000)

class C45(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C45',F_ck=45,F_ctk=2.3,E_c=36_000)

class C50(Concrete):
    def __init__(self)->None:
        super().__init__(Name='C50',F_ck=50,F_ctk=2.5,E_c=37_000)

# if __name__ == "__main__":
#     s1 = S355()
#     c1 = C25()
#     print(s1)
#     print(c1)