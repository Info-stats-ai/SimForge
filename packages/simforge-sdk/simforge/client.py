"""SimForge API client for programmatic access to the orchestration backend."""

from __future__ import annotations

from typing import Any, Optional

import httpx

from simforge.types import (
    Artifact,
    EvaluationReport,
    Scenario,
    ScenarioVariant,
    SimulationRun,
    SubmitRunResponse,
)


class SimForgeClient:
    """HTTP client for interacting with the SimForge orchestration API.

    Example usage:
        client = SimForgeClient(base_url="http://localhost:8000")
        scenario = Scenario(name="blind-corner-test", ...)
        created = client.create_scenario(scenario)
        run = client.submit_scenario(created.id)
        status = client.get_run_status(run.run_id)
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ── Health ──────────────────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        r = self._client.get("/api/health")
        r.raise_for_status()
        return r.json()

    # ── Scenarios ───────────────────────────────────────────────────────

    def create_scenario(self, scenario: Scenario) -> Scenario:
        r = self._client.post("/api/scenarios", json=scenario.model_dump(mode="json"))
        r.raise_for_status()
        return Scenario(**r.json())

    def list_scenarios(self) -> list[Scenario]:
        r = self._client.get("/api/scenarios")
        r.raise_for_status()
        return [Scenario(**s) for s in r.json()]

    def get_scenario(self, scenario_id: str) -> Scenario:
        r = self._client.get(f"/api/scenarios/{scenario_id}")
        r.raise_for_status()
        return Scenario(**r.json())

    def update_scenario(self, scenario_id: str, data: dict[str, Any]) -> Scenario:
        r = self._client.put(f"/api/scenarios/{scenario_id}", json=data)
        r.raise_for_status()
        return Scenario(**r.json())

    def delete_scenario(self, scenario_id: str) -> dict:
        r = self._client.delete(f"/api/scenarios/{scenario_id}")
        r.raise_for_status()
        return r.json()

    # ── Compilation ─────────────────────────────────────────────────────

    def compile_scenario(self, scenario_id: str) -> list[ScenarioVariant]:
        r = self._client.post(f"/api/scenarios/{scenario_id}/compile")
        r.raise_for_status()
        return [ScenarioVariant(**v) for v in r.json()]

    def list_variants(self, scenario_id: str) -> list[ScenarioVariant]:
        r = self._client.get(f"/api/scenarios/{scenario_id}/variants")
        r.raise_for_status()
        return [ScenarioVariant(**v) for v in r.json()]

    # ── Runs / Jobs ─────────────────────────────────────────────────────

    def submit_scenario(self, scenario_id: str) -> SubmitRunResponse:
        r = self._client.post(f"/api/scenarios/{scenario_id}/run")
        r.raise_for_status()
        return SubmitRunResponse(**r.json())

    def list_jobs(self, status: Optional[str] = None, scenario_id: Optional[str] = None) -> list[SimulationRun]:
        params: dict[str, str] = {}
        if status:
            params["status"] = status
        if scenario_id:
            params["scenario_id"] = scenario_id
        r = self._client.get("/api/jobs", params=params)
        r.raise_for_status()
        return [SimulationRun(**j) for j in r.json()]

    def get_job(self, job_id: str) -> SimulationRun:
        r = self._client.get(f"/api/jobs/{job_id}")
        r.raise_for_status()
        return SimulationRun(**r.json())

    def get_run_status(self, job_id: str) -> str:
        job = self.get_job(job_id)
        return job.status

    def retry_job(self, job_id: str) -> SimulationRun:
        r = self._client.post(f"/api/jobs/{job_id}/retry")
        r.raise_for_status()
        return SimulationRun(**r.json())

    # ── Artifacts ───────────────────────────────────────────────────────

    def list_artifacts(self, job_id: Optional[str] = None) -> list[Artifact]:
        if job_id:
            r = self._client.get(f"/api/jobs/{job_id}/artifacts")
        else:
            r = self._client.get("/api/artifacts")
        r.raise_for_status()
        return [Artifact(**a) for a in r.json()]

    def get_artifact(self, artifact_id: str) -> Artifact:
        r = self._client.get(f"/api/artifacts/{artifact_id}")
        r.raise_for_status()
        return Artifact(**r.json())

    # ── Evaluation ──────────────────────────────────────────────────────

    def get_evaluation(self, job_id: str) -> EvaluationReport:
        r = self._client.get(f"/api/jobs/{job_id}/evaluation")
        r.raise_for_status()
        return EvaluationReport(**r.json())

    def list_evaluations(self) -> list[EvaluationReport]:
        r = self._client.get("/api/evaluations")
        r.raise_for_status()
        return [EvaluationReport(**e) for e in r.json()]
