"""Heuristic evaluation engine for simulation results."""

from __future__ import annotations

import random
from typing import Any

from simforge.types import EvaluationReport, ScenarioVariant


class EvaluationEngine:
    """Lightweight heuristic evaluator for warehouse edge-case simulation results.

    Computes normalized scores for collision risk, occlusion, path conflict,
    severity, diversity, and coverage. Designed to be modular and replaceable
    with ML-based evaluators in production.
    """

    RISK_FACTORS = [
        "Human detected in robot blind spot",
        "Obstacle occluding sensor field of view",
        "Path conflict at intersection timing window",
        "Low visibility reducing reaction margin",
        "Blocked aisle forcing path replanning",
        "Late human crossing into robot trajectory",
        "Multiple hazards co-occurring in same frame",
        "Robot speed exceeding safe threshold for environment",
        "Dropped object in narrow aisle passage",
        "Timing conflict between AMR and crossing agent",
    ]

    RECOMMENDED_ACTIONS = [
        "Review blind-corner detection algorithm thresholds",
        "Add safety margin for low-light conditions",
        "Increase sensor coverage at T-junctions",
        "Implement predictive human trajectory modeling",
        "Add dynamic speed reduction near intersections",
        "Test with higher obstacle density scenarios",
        "Validate emergency stop response times",
        "Consider adding proximity warning signals",
    ]

    def evaluate_variant(
        self, variant: ScenarioVariant, job_id: str
    ) -> EvaluationReport:
        """Evaluate a single variant's simulation results."""
        params = variant.variant_parameters
        rng = random.Random(variant.deterministic_seed)

        collision_risk = self._compute_collision_risk(params, rng)
        occlusion = self._compute_occlusion_score(params, rng)
        path_conflict = self._compute_path_conflict(params, rng)
        severity = self._compute_severity(params, collision_risk, occlusion, path_conflict)
        diversity = rng.uniform(0.3, 0.95)

        top_risks = self._select_risk_factors(params, rng)
        actions = self._select_actions(params, rng)

        coverage = {
            "lighting_conditions_tested": params.get("lighting_variant", "normal"),
            "obstacle_levels_tested": params.get("dropped_obstacle_level", "none"),
            "human_scenarios_covered": params.get("human_present", False),
            "path_types_tested": params.get("robot_path_type", "unknown"),
            "hazard_severity": params.get("hazard_severity", "low"),
        }

        explanation = self._generate_explanation(
            collision_risk, occlusion, path_conflict, severity, top_risks
        )

        return EvaluationReport(
            job_id=job_id,
            collision_risk_score=round(collision_risk, 3),
            occlusion_score=round(occlusion, 3),
            path_conflict_score=round(path_conflict, 3),
            severity_score=round(severity, 3),
            diversity_score=round(diversity, 3),
            coverage_summary=coverage,
            explanation=explanation,
            top_risk_factors=top_risks,
            recommended_actions=actions,
        )

    def _compute_collision_risk(self, params: dict, rng: random.Random) -> float:
        base = 0.2
        if params.get("human_present"):
            base += 0.25
            base += params.get("human_speed", 1.0) * 0.05
        if params.get("aisle_blocked"):
            base += 0.15
        base += params.get("path_conflict_intensity", 0.5) * 0.2
        speed_mod = params.get("robot_speed_modifier", 1.0)
        if speed_mod > 1.1:
            base += (speed_mod - 1.0) * 0.3
        return min(1.0, base + rng.uniform(-0.05, 0.05))

    def _compute_occlusion_score(self, params: dict, rng: random.Random) -> float:
        base = 0.15
        vis = params.get("visibility_modifier", 1.0)
        if vis < 0.9:
            base += (1.0 - vis) * 0.5
        lighting = params.get("lighting_variant", "normal")
        if lighting in ("low_light", "flickering"):
            base += 0.2
        if params.get("obstacle_count", 0) > 2:
            base += 0.15
        return min(1.0, base + rng.uniform(-0.05, 0.05))

    def _compute_path_conflict(self, params: dict, rng: random.Random) -> float:
        return min(1.0, params.get("path_conflict_intensity", 0.5) + rng.uniform(-0.1, 0.1))

    def _compute_severity(
        self, params: dict, collision: float, occlusion: float, conflict: float
    ) -> float:
        weighted = collision * 0.4 + occlusion * 0.25 + conflict * 0.35
        hazard = params.get("hazard_severity", "low")
        multipliers = {"low": 0.8, "medium": 1.0, "high": 1.2, "critical": 1.4}
        return min(1.0, weighted * multipliers.get(hazard, 1.0))

    def _select_risk_factors(self, params: dict, rng: random.Random) -> list[str]:
        count = rng.randint(2, 5)
        factors = rng.sample(self.RISK_FACTORS, min(count, len(self.RISK_FACTORS)))
        return factors

    def _select_actions(self, params: dict, rng: random.Random) -> list[str]:
        count = rng.randint(2, 4)
        return rng.sample(self.RECOMMENDED_ACTIONS, min(count, len(self.RECOMMENDED_ACTIONS)))

    def _generate_explanation(
        self, collision: float, occlusion: float, conflict: float,
        severity: float, risks: list[str],
    ) -> str:
        level = "LOW" if severity < 0.3 else "MODERATE" if severity < 0.6 else "HIGH" if severity < 0.8 else "CRITICAL"
        lines = [
            f"Overall severity: {level} ({severity:.1%})",
            f"Collision risk: {collision:.1%} | Occlusion: {occlusion:.1%} | Path conflict: {conflict:.1%}",
            "",
            "Top risk factors:",
        ]
        for r in risks:
            lines.append(f"  • {r}")
        return "\n".join(lines)
