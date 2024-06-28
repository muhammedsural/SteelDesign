import math
import pytest

from steeldesign.BaseConnection import BasePlate



# 1kips = 4.45 kN, 1 inç = 2.54cm 1ksi = 6,90N/mm2
P_u  = 2_520_000   #N ,
M_u  = 0.0         #Nmm,
V_u  = 0.0         #N
f_c  = 25          #MPa
d    = 280         #mm
b_f  = 280         #mm
F_y  = 275        #MPa
B    = 440         #mm
N    = 440         #mm
B2   = 490         #mm
N2   = 490         #mm
x    =1.5*2.34      #mm

@pytest.fixture(scope="class")
def BP():
    bp = BasePlate(P_u , M_u, V_u, f_c, d, b_f, F_y, B, N, B2, N2, x)
    return bp

def test_ApproximateBasePlateArea(BP : BasePlate):
    assert math.isclose(BP.ApproximateBasePlateArea(BP.P_u,BP.f_c, 3), 91222.0, rel_tol=1e-2)

def test_FindPlateDimensions(BP : BasePlate):
    A_req = 91222.0
    assert math.isclose(BP.FindPlateDimensions(BP.d,BP.b_f,A_req), 440, rel_tol=1e-2)

def test_GetBasePlateArea(BP : BasePlate):
    assert math.isclose(BP.GetBasePlateArea(BP.B, BP.N), 193600, rel_tol=1e-2)

def test_Get_P_p(BP : BasePlate):
    assert math.isclose(BP.Get_P_p(f_pmax=16.95,A1=193600,f_c=25), 3281520.0, rel_tol=1e-2)

def test_Get_m(BP : BasePlate):
    assert math.isclose(BP.Get_m(N=440, d=d), 87.0, rel_tol=1e-2)

def test_Get_n(BP : BasePlate):
    assert math.isclose(BP.Get_n(B=440, b_f=b_f), 108.0, rel_tol=1e-2)

def test_Get_X(BP : BasePlate):
    assert math.isclose(BP.Get_X(d=d, b_f=b_f, P_u=P_u, P_p=3281520.0), 0.77, rel_tol=1e-2)

def test_Get_lambda(BP : BasePlate):
    assert math.isclose(BP.Get_lambda(X=0.77), 1.0, rel_tol=1e-2)

def test_Get_l(BP : BasePlate):
    assert math.isclose(BP.Get_l(d,b_f,87,108,1.0), 108.0, rel_tol=1e-2)

def test_BasePlateThickness(BP : BasePlate):
    assert math.isclose(BP.BasePlateThickness(P_u,108,440,440,F_y), 35.03, rel_tol=1e-2)

def test_Get_Y(BP : BasePlate):
    assert math.isclose(BP.Get_Y(e = 2.38, e_crit = 51.05, P_u = P_u, N = 440, f = 218.5, q_max = 7458), 435.24, rel_tol=1e-2)

def test_Get_f_p(BP : BasePlate):
    assert math.isclose(BP.Get_f_p(P_u = P_u, B = 440, Y = 435.24), 13.16, rel_tol=1e-2)

def test_ForMomentsBasePlateThickness(BP : BasePlate):
    assert math.isclose(BP.ForMomentsBasePlateThickness(m = 87.0, n = 108.0, f_p = 13.16, Y = 435.24, F_y = F_y), 35.44, rel_tol=1e-2)
    