"""Tests for SimForge SDK — scenario compilation and evaluation engine."""

import sys
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "simforge-sdk"))

from simforge import Scenario, ScenarioCompiler, EvaluationEngine
from simforge.types import ScenarioVariant


class TestScenarioCompilation:
    """Tests for deterministic scenario compilation."""

    def test_compile_produces_correct_variant_count(self):
        scenario = Scenario(name="test-scenario", variant_count=5, random_seed=42)
        compiler = ScenarioCompiler()
        variants = compiler.compile(scenario)
        assert len(variants) == 5

    def test_compile_is_deterministic(self):
        scenario = Scenario(name="test-deterministic", variant_count=3, random_seed=42)
        compiler = ScenarioCompiler()
        v1 = compiler.compile(scenario)
        v2 = compiler.compile(scenario)
        for a, b in zip(v1, v2):
            assert a.variant_parameters == b.variant_parameters
            assert a.deterministic_seed == b.deterministic_seed

    def test_different_seeds_produce_different_variants(self):
        compiler = ScenarioCompiler()
        s1 = Scenario(name="seed-1", variant_count=3, random_seed=42)
        s2 = Scenario(name="seed-2", variant_count=3, random_seed=99)
        v1 = compiler.compile(s1)
        v2 = compiler.compile(s2)
        assert v1[0].variant_parameters != v2[0].variant_parameters

    def test_variant_indices_are_sequential(self):
        scenario = Scenario(name="test-indices", variant_count=5, random_seed=42)
        compiler = ScenarioCompiler()
        variants = compiler.compile(scenario)
        indices = [v.variant_index for v in variants]
        assert indices == [0, 1, 2, 3, 4]

    def test_variant_parameters_contain_required_keys(self):
        scenario = Scenario(name="test-keys", variant_count=1, random_seed=42)
        compiler = ScenarioCompiler()
        variants = compiler.compile(scenario)
        params = variants[0].variant_parameters
        required_keys = [
            "variant_index", "human_present", "path_conflict_intensity",
            "visibility_modifier", "hazard_severity", "robot_speed_modifier",
        ]
        for key in required_keys:
            assert key in params, f"Missing key: {key}"

    def test_human_crossing_probability_respected(self):
        # With probability 0, no humans should be present
        scenario = Scenario(name="no-humans", variant_count=20, random_seed=42,
                          human_crossing_probability=0.0)
        compiler = ScenarioCompiler()
        variants = compiler.compile(scenario)
        for v in variants:
            assert v.variant_parameters["human_present"] is False

    def test_scenario_validation_warnings(self):
        compiler = ScenarioCompiler()
        scenario = Scenario(
            name="extreme",
            variant_count=60,
            human_crossing_probability=0.95,
            dropped_obstacle_level="extreme",
            blocked_aisle_enabled=True,
            robot_path_type="straight_aisle",
        )
        warnings = compiler.validate_scenario(scenario)
        assert len(warnings) >= 2  # Should flag high count and dense edge cases

    def test_single_variant_compilation(self):
        scenario = Scenario(name="single", variant_count=1, random_seed=1)
        compiler = ScenarioCompiler()
        variants = compiler.compile(scenario)
        assert len(variants) == 1
        assert variants[0].variant_index == 0


class TestEvaluationEngine:
    """Tests for the heuristic evaluation engine."""

    def test_evaluate_produces_valid_scores(self):
        variant = ScenarioVariant(
            scenario_id="test",
            variant_index=0,
            variant_parameters={
                "human_present": True,
                "human_speed": 1.5,
                "aisle_blocked": True,
                "path_conflict_intensity": 0.7,
                "robot_speed_modifier": 1.2,
                "visibility_modifier": 0.8,
                "lighting_variant": "low_light",
                "obstacle_count": 3,
                "hazard_severity": "high",
            },
            deterministic_seed=42,
        )
        engine = EvaluationEngine()
        report = engine.evaluate_variant(variant, "test-job-id")

        assert 0.0 <= report.collision_risk_score <= 1.0
        assert 0.0 <= report.occlusion_score <= 1.0
        assert 0.0 <= report.path_conflict_score <= 1.0
        assert 0.0 <= report.severity_score <= 1.0
        assert 0.0 <= report.diversity_score <= 1.0

    def test_evaluate_produces_risk_factors(self):
        variant = ScenarioVariant(
            scenario_id="test", variant_index=0,
            variant_parameters={"human_present": True, "hazard_severity": "critical"},
            deterministic_seed=42,
        )
        engine = EvaluationEngine()
        report = engine.evaluate_variant(variant, "test-job")
        assert len(report.top_risk_factors) >= 2
        assert len(report.recommended_actions) >= 2

    def test_evaluate_produces_explanation(self):
        variant = ScenarioVariant(
            scenario_id="test", variant_index=0,
            variant_parameters={"human_present": False},
            deterministic_seed=42,
        )
        engine = EvaluationEngine()
        report = engine.evaluate_variant(variant, "test-job")
        assert "severity" in report.explanation.lower()

    def test_higher_risk_params_produce_higher_scores(self):
        engine = EvaluationEngine()
        low_risk = ScenarioVariant(
            scenario_id="test", variant_index=0,
            variant_parameters={
                "human_present": False, "aisle_blocked": False,
                "path_conflict_intensity": 0.1, "robot_speed_modifier": 0.7,
                "visibility_modifier": 1.0, "lighting_variant": "normal",
                "obstacle_count": 0, "hazard_severity": "low",
            },
            deterministic_seed=42,
        )
        high_risk = ScenarioVariant(
            scenario_id="test", variant_index=1,
            variant_parameters={
                "human_present": True, "human_speed": 2.0, "aisle_blocked": True,
                "path_conflict_intensity": 0.9, "robot_speed_modifier": 1.3,
                "visibility_modifier": 0.7, "lighting_variant": "low_light",
                "obstacle_count": 4, "hazard_severity": "critical",
            },
            deterministic_seed=43,
        )
        low_report = engine.evaluate_variant(low_risk, "low")
        high_report = engine.evaluate_variant(high_risk, "high")
        assert high_report.collision_risk_score > low_report.collision_risk_score

    def test_evaluation_is_deterministic(self):
        variant = ScenarioVariant(
            scenario_id="test", variant_index=0,
            variant_parameters={"human_present": True, "hazard_severity": "medium"},
            deterministic_seed=42,
        )
        engine = EvaluationEngine()
        r1 = engine.evaluate_variant(variant, "job-1")
        r2 = engine.evaluate_variant(variant, "job-1")
        assert r1.collision_risk_score == r2.collision_risk_score
        assert r1.severity_score == r2.severity_score


class TestScenarioModel:
    """Tests for the Scenario Pydantic model."""

    def test_scenario_defaults(self):
        s = Scenario(name="test")
        assert s.variant_count == 5
        assert s.random_seed == 42
        assert s.status == "draft"
        assert s.environment_template == "warehouse_aisle"

    def test_scenario_validation(self):
        import pytest
        with pytest.raises(Exception):
            Scenario(name="", variant_count=-1)

    def test_scenario_serialization(self):
        s = Scenario(name="test", human_crossing_probability=0.75)
        data = s.model_dump()
        assert data["name"] == "test"
        assert data["human_crossing_probability"] == 0.75

    def test_scenario_deserialization(self):
        data = {"name": "from-dict", "variant_count": 10, "random_seed": 99}
        s = Scenario(**data)
        assert s.name == "from-dict"
        assert s.variant_count == 10


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
