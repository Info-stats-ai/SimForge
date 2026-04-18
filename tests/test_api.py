"""Tests for SimForge Backend API."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "simforge-sdk"))

# Use a test database
os.environ["DATABASE_URL"] = "sqlite:///./test_simforge.db"

from app.db.database import init_db
from main import app

# Initialize database for tests
init_db()

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "simforge-api"


class TestScenarioEndpoints:
    def test_list_scenarios(self):
        response = client.get("/api/scenarios")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_scenario(self):
        data = {
            "name": "API Test Scenario",
            "description": "Created from test",
            "environment_template": "warehouse_aisle",
            "robot_path_type": "t_junction",
            "variant_count": 3,
            "random_seed": 100,
        }
        response = client.post("/api/scenarios", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "API Test Scenario"
        assert result["variant_count"] == 3
        return result["id"]

    def test_get_scenario(self):
        # First create one
        scenarios = client.get("/api/scenarios").json()
        if scenarios:
            sid = scenarios[0]["id"]
            response = client.get(f"/api/scenarios/{sid}")
            assert response.status_code == 200
            assert response.json()["id"] == sid

    def test_update_scenario(self):
        scenarios = client.get("/api/scenarios").json()
        if scenarios:
            sid = scenarios[0]["id"]
            response = client.put(f"/api/scenarios/{sid}", json={"notes": "updated"})
            assert response.status_code == 200

    def test_compile_scenario(self):
        scenarios = client.get("/api/scenarios").json()
        if scenarios:
            sid = scenarios[0]["id"]
            response = client.post(f"/api/scenarios/{sid}/compile")
            assert response.status_code == 200
            variants = response.json()
            assert isinstance(variants, list)
            assert len(variants) > 0

    def test_get_variants(self):
        scenarios = client.get("/api/scenarios").json()
        if scenarios:
            sid = scenarios[0]["id"]
            response = client.get(f"/api/scenarios/{sid}/variants")
            assert response.status_code == 200

    def test_delete_scenario(self):
        # Create a scenario to delete
        data = {"name": "To Delete", "variant_count": 1}
        created = client.post("/api/scenarios", json=data).json()
        response = client.delete(f"/api/scenarios/{created['id']}")
        assert response.status_code == 200
        assert response.json()["deleted"] is True

    def test_get_nonexistent_scenario(self):
        response = client.get("/api/scenarios/nonexistent-id")
        assert response.status_code == 404


class TestJobEndpoints:
    def test_list_jobs(self):
        response = client.get("/api/jobs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_nonexistent_job(self):
        response = client.get("/api/jobs/nonexistent-id")
        assert response.status_code == 404


class TestArtifactEndpoints:
    def test_list_artifacts(self):
        response = client.get("/api/artifacts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestEvaluationEndpoints:
    def test_list_evaluations(self):
        response = client.get("/api/evaluations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestActivityEndpoints:
    def test_list_activity(self):
        response = client.get("/api/activity")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestSettingsEndpoints:
    def test_get_settings(self):
        response = client.get("/api/settings")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)


class TestIntegrationFlow:
    """Integration test: scenario -> compile -> run -> check."""

    def test_full_workflow(self):
        # 1. Create scenario
        scenario_data = {
            "name": "Integration Test Scenario",
            "environment_template": "warehouse_aisle",
            "robot_path_type": "left_turn_blind_corner",
            "human_crossing_probability": 0.8,
            "variant_count": 2,
            "random_seed": 42,
        }
        create_resp = client.post("/api/scenarios", json=scenario_data)
        assert create_resp.status_code == 200
        scenario_id = create_resp.json()["id"]

        # 2. Compile variants
        compile_resp = client.post(f"/api/scenarios/{scenario_id}/compile")
        assert compile_resp.status_code == 200
        variants = compile_resp.json()
        assert len(variants) == 2

        # 3. Submit run
        run_resp = client.post(f"/api/scenarios/{scenario_id}/run")
        assert run_resp.status_code == 200
        run_data = run_resp.json()
        assert len(run_data["job_ids"]) == 2
        assert run_data["status"] == "queued"

        # 4. Check jobs exist
        jobs_resp = client.get("/api/jobs")
        assert jobs_resp.status_code == 200

        # 5. Check scenario status updated
        scenario_resp = client.get(f"/api/scenarios/{scenario_id}")
        assert scenario_resp.status_code == 200

        # Cleanup
        client.delete(f"/api/scenarios/{scenario_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
