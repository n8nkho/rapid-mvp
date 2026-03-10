"""Engagement autonomy policy engine — Phase 1 + Phase 3."""
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

# ── Phase 3: Tier lock ────────────────────────────────────────────────────────

# Tier hierarchy — index = rank (higher = more capable)
TIER_ORDER: list[str] = ["starter", "professional", "enterprise"]

# Minimum tier required to activate each mode
MODE_TIER_REQUIREMENTS: dict[str, str] = {
    "guided":        "starter",
    "collaborative": "professional",
    "autonomous":    "enterprise",
}

# Medium-risk actions that require enterprise tier regardless of mode label
ENTERPRISE_ONLY_ACTIONS: set[str] = {
    "advance_hitl_low",  # auto-advancing low-confidence HITL
    "confirm_signoff",   # auto-confirming client sign-off
}


def _tier_rank(tier: str) -> int:
    try:
        return TIER_ORDER.index((tier or "starter").lower())
    except ValueError:
        return 0


def check_tier_access(client_tier: str | None, requested_mode: str) -> tuple[bool, str]:
    """Return (allowed, reason). Checks client_tier meets minimum for requested_mode."""
    tier = (client_tier or "starter").lower()
    required = MODE_TIER_REQUIREMENTS.get(requested_mode, "starter")
    if _tier_rank(tier) >= _tier_rank(required):
        return True, ""
    return False, (
        f"Mode '{requested_mode}' requires {required.capitalize()} tier. "
        f"Current tier: {tier.capitalize()}. Upgrade to unlock."
    )


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

    if risk not in allowed:
        return False

    # Tier lock: enterprise-only actions require enterprise tier.
    # Tier is cached in autonomy_config["tier"] when mode is set via PATCH /engagement/{id}/mode.
    if resolved_action in ENTERPRISE_ONLY_ACTIONS:
        cached_tier = config.get("tier", "starter")
        tier_ok, reason = check_tier_access(cached_tier, "autonomous")
        if not tier_ok:
            logger.info("tier_lock blocked: action=%s tier=%s reason=%s", resolved_action, cached_tier, reason)
            return False

    return True


def get_effective_config(engagement: dict) -> dict:
    mode = engagement.get("mode") or "collaborative"
    defaults = DEFAULT_CONFIGS.get(mode, DEFAULT_CONFIGS["collaborative"])
    overrides = engagement.get("autonomy_config") or {}
    return {**defaults, **overrides}
