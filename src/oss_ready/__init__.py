"""Repository readiness checks for open-source projects."""

from .models import CheckResult, ScanReport
from .scanner import scan_repository

__all__ = ["CheckResult", "ScanReport", "scan_repository"]
__version__ = "0.1.0"

