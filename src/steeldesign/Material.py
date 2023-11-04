
from dataclasses import asdict, dataclass


@dataclass
class Steel():
    name    : str   = 'B500C'
    density : float = 80.
    f_sy    : float = None
    Ry      : float = None
    Es      : float = None
    
    def __repr__(self) -> str:
        return f'Name : {self.name}, fsy : {self.f_sy},Es : {self.Es} '
    
    def asdict():
        return asdict()