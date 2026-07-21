"""
Tests package initialization
"""

__version__ = "1.0.0"

from tests.scenarios import (
    ScenarioTest,
    HeatingFailureScenario,
    BenefitReductionScenario,
    MedicationInterruptionScenario,
    SupervisionContinuityScenario,
    run_all_scenarios,
)

__all__ = [
    "ScenarioTest",
    "HeatingFailureScenario",
    "BenefitReductionScenario",
    "MedicationInterruptionScenario",
    "SupervisionContinuityScenario",
    "run_all_scenarios",
]
