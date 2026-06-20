"""Small explicit SI and high-energy unit conversions."""

ELECTRON_VOLT_J = 1.602_176_634e-19
MEV_C2_KG = 1.782_661_921_627_897_5e-30
JULIAN_YEAR_S = 31_557_600.0
MEGAPARSEC_M = 3.085_677_581_491_367e22


def eV_to_J(value: float) -> float:
    return value * ELECTRON_VOLT_J


def J_to_eV(value: float) -> float:
    return value / ELECTRON_VOLT_J


def MeV_to_kg(value: float) -> float:
    return value * MEV_C2_KG


def kg_to_MeV(value: float) -> float:
    return value / MEV_C2_KG


def year_to_second(value: float) -> float:
    return value * JULIAN_YEAR_S


def Mpc_to_meter(value: float) -> float:
    return value * MEGAPARSEC_M


def scale_value(value: float, scale: float) -> float:
    return value * scale
