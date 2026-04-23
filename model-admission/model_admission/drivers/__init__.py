from model_admission.drivers.base import ScanDriver
from model_admission.drivers.modelaudit import ModelAuditDriver
from model_admission.drivers.modelscan import ModelScanDriver

DRIVERS: dict[str, type[ScanDriver]] = {
    "modelscan": ModelScanDriver,
    "modelaudit": ModelAuditDriver,
}


def get_driver(name: str) -> ScanDriver:
    key = name.strip().lower()
    if key not in DRIVERS:
        raise KeyError(f"unknown driver {name!r}; known: {sorted(DRIVERS)}")
    return DRIVERS[key]()
