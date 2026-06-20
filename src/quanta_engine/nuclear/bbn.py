"""Minimal primordial light-element availability summary."""

from .stability import NuclearReport


def light_element_inventory(report: NuclearReport) -> dict[str, bool]:
    return {
        "hydrogen": report.hydrogen_available,
        "deuterium": report.deuteron_stable,
        "helium4": report.helium_available,
    }
