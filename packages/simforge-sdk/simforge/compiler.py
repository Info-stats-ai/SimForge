"""Deterministic scenario compiler — generates variants from a scenario definition."""

from __future__ import annotations

import random
from typing import Any

from simforge.types import (
    CameraMode,
    LightingPreset,
    ObstacleLevel,
    Scenario,
    ScenarioVariant,
)


class ScenarioCompiler:
    """Compiles a Scenario into deterministic ScenarioVariants."""

    TIMING_OFFSET_RANGE = (-2.0, 5.0)
    OBSTACLE_OFFSET_RANGE = (-1.5, 1.5)
    PATH_CONFLICT_RANGE = (0.1, 1.0)
    VISIBILITY_MODIFIERS = [0.7, 0.8, 0.9, 1.0, 1.1]
    CAMERA_ADJUSTMENTS = {
        "pan_offset": (-15.0, 15.0),
        "tilt_offset": (-10.0, 10.0),
        "zoom_factor": (0.8, 1.3),
    }
    HAZARD_SEVERITY_WEIGHTS = ["low", "medium", "high", "critical"]
    LIGHTING_VARIANTS = list(LightingPreset)
    OBSTACLE_VARIANTS = list(ObstacleLevel)

    def compile(self, scenario: Scenario) -> list[ScenarioVariant]:
        variants = []
        base_seed = scenario.random_seed
        for i in range(scenario.variant_count):
            variant_seed = base_seed + i * 1000 + 7
            rng = random.Random(variant_seed)
            params = self._gen_params(scenario, rng, i)
            variant = ScenarioVariant(
                scenario_id=scenario.id,
                variant_index=i,
                variant_parameters=params,
                deterministic_seed=variant_seed,
            )
            variants.append(variant)
        return variants

    def _gen_params(self, s: Scenario, rng: random.Random, idx: int) -> dict[str, Any]:
        human_present = rng.random() < s.human_crossing_probability
        path_conflict = rng.uniform(*self.PATH_CONFLICT_RANGE)
        if s.human_crossing_probability > 0.6:
            path_conflict = min(1.0, path_conflict * 1.3)
        lighting = s.lighting_preset
        if rng.random() < 0.3:
            lv = rng.choice(self.LIGHTING_VARIANTS)
            lighting = lv if isinstance(lv, str) else lv.value
        return {
            "variant_index": idx,
            "actor_timing_offset": round(rng.uniform(*self.TIMING_OFFSET_RANGE), 3),
            "human_present": human_present,
            "human_delay": round(rng.uniform(0, 3), 3) if human_present else 0.0,
            "human_speed": round(rng.uniform(0.8, 2.0), 3) if human_present else 0.0,
            "human_entry_angle": round(rng.uniform(-45, 45), 2) if human_present else 0.0,
            "obstacle_x_offset": round(rng.uniform(*self.OBSTACLE_OFFSET_RANGE), 3),
            "obstacle_y_offset": round(rng.uniform(*self.OBSTACLE_OFFSET_RANGE), 3),
            "obstacle_count": max(0, int(rng.gauss(2, 1))) if s.dropped_obstacle_level != "none" else 0,
            "path_conflict_intensity": round(path_conflict, 3),
            "visibility_modifier": rng.choice(self.VISIBILITY_MODIFIERS),
            "lighting_variant": lighting if isinstance(lighting, str) else lighting,
            "camera_pan_offset": round(rng.uniform(-15, 15), 2),
            "camera_tilt_offset": round(rng.uniform(-10, 10), 2),
            "camera_zoom_factor": round(rng.uniform(0.8, 1.3), 3),
            "hazard_severity": rng.choice(self.HAZARD_SEVERITY_WEIGHTS),
            "robot_speed_modifier": round(rng.uniform(0.7, 1.3), 3),
            "aisle_blocked": s.blocked_aisle_enabled and rng.random() < 0.6,
            "dropped_obstacle_level": s.dropped_obstacle_level if isinstance(s.dropped_obstacle_level, str) else s.dropped_obstacle_level,
            "environment_template": s.environment_template if isinstance(s.environment_template, str) else s.environment_template,
            "robot_path_type": s.robot_path_type if isinstance(s.robot_path_type, str) else s.robot_path_type,
            "camera_mode": s.camera_mode if isinstance(s.camera_mode, str) else s.camera_mode,
        }

    def validate_scenario(self, scenario: Scenario) -> list[str]:
        warnings = []
        if scenario.variant_count > 50:
            warnings.append("High variant count (>50) may result in long compilation times.")
        if scenario.human_crossing_probability > 0.9 and scenario.dropped_obstacle_level in ("high", "extreme"):
            warnings.append("High human crossing + high obstacles creates very dense edge cases.")
        if scenario.blocked_aisle_enabled and scenario.robot_path_type in ("straight_aisle", "u_turn"):
            warnings.append("Blocked aisle with straight/U-turn path may create unsolvable scenarios.")
        return warnings
