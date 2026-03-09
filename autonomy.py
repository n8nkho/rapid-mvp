"""Engagement autonomy policy engine — Phase 1."""
import logging
from datetime import datetime, timezone

logger = logging.getLogger("rapid")

RISK_LEVELS: dict[str, str] = {
    "run_fitgap":           "low",
    "generate_ricefw":      "low",
    "advance_hitl_high":    "low",
    "advance_hitl_low":     "medium",
    "send_portal_update":   "low",
    "confirm_signoff":      "medium",
    "change_phase":         "high",
    "mark_golive_ready":    "high",
}

MODE_AUTO_EXECUTE: dict[str, set] = {
    "guided":        set(),
    "collaborative": {"low"},
    "autonomous":    {"low", "medium"},
}

DEFAULT_CONFIGS: dict[str, dict] = {
    "guided":        {"hitl_confidence_threshold": 95, "auto_fitgap": False, "auto_ricefw": False},
    "collaborative": {"hitl_confidence_threshold": 85, "auto_fitgap": True, "auto_ricefw": True},
    "autonomous":    {"hitl_confidence_threshold": 70, "auto_fitgap": True, "auto_ricefw": True},
}


def should_auto_execute(engagement: dict, action_type: str, confidence: float | None = None) -> bool:
    mode = engagement.get("mode") or "collaborative"
    config = engagement.get("autonomy_config") or {}
    defaults = DEFAULT_CONFIGS.get(mode, DEFAULT_CONFIGS["collaborative"])

    resolved_action = action_type
    if action_type in ("advance_hitl_high", "advance_hitl_low") and confidence is not None:
        threshold = config.get("hitl_confidence_threshold", defaults["hitl_confidence_threshold"])
        resolved_action = "advance_hitl_high" if confidence >= threshold else "advance_hitl_low"

    risk = RISK_LEVELS.get(resolved_action, "high")
    allowed = MODE_AUTO_EXECUTE.get(mode, set())
    return risk in allowed


def get_effective_config(engagement: dict) -> dict:
    mode = engagement.get("mode") or "collaborative"
    defaults = DEFAULT_CONFIGS.get(mode, DEFAULT_CONFIGS["collaborative"])
    overrides = engagement.get("autonomy_config") or {}
    return {**defaults, **overrides}
