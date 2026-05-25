"""Heuristic practice detectors (catalog rules PR2, PR8, B1, …)."""

from insight_proto.detectors.b1 import detect_b1_routing
from insight_proto.detectors.pr2 import detect_pr2_logging
from insight_proto.detectors.pr8 import detect_pr8_validation

__all__ = ["detect_b1_routing", "detect_pr2_logging", "detect_pr8_validation"]
