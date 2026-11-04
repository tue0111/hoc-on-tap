# Phase 6 long-term evidence admission. No mastery scores.
__version__ = "6.0.0"

from admission.engine import decide_admission
from admission.policy import POLICY_VERSION

__all__ = ["decide_admission", "POLICY_VERSION"]
