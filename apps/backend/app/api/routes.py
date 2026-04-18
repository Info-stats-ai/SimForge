"""API routes for SimForge backend."""

import sys
import uuid
import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    Scenario, ScenarioVariant, SimulationJob, OutputArtifact,
    EvaluationReport, ActivityLog, SystemSetting,
)

# Add SDK to path
SDK_PATH = str(Path(__file__).parent.parent.parent.parent / "packages" / "simforge-sdk")
if SDK_PATH not in sys.path:
    sys.path.insert(0, SDK_PATH)

from simforge.compiler import ScenarioCompiler
from simforge.evaluation import EvaluationEngine
from simforge.types import Scenario as SDKScenario, ScenarioVariant as SDKVariant

router = APIRouter()
compiler = ScenarioCompiler()
evaluator = EvaluationEngine()


def _uid():
    return str(uuid.uuid4())


def _log_activity(db: Session, event_type: str, entity_type: str, entity_id: str, message: str):
    db.add(ActivityLog(
        id=_uid(), event_type=event_type,
        related_entity_type=entity_type, related_entity_id=entity_id,
        message=message,
    ))
    db.commit()


def _scenario_to_dict(s: Scenario) -> dict:
    return {
        "id": s.id, "name": s.name, "description": s.description,
        "environment_template": s.environment_template, "robot_path_type": s.robot_path_type,
        "human_crossing_probability": s.human_crossing_probability,
        "dropped_obstacle_level": s.dropped_obstacle_level,
        "blocked_aisle_enabled": s.blocked_aisle_enabled, "lighting_preset": s.lighting_preset,
        "camera_mode": s.camera_mode, "variant_count": s.variant_count,
        "random_seed": s.random_seed, "notes": s.notes, "status": s.status,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def _variant_to_dict(v: ScenarioVariant) -> dict:
    return {
        "id": v.id, "scenario_id": v.scenario_id, "variant_index": v.variant_index,
        "variant_parameters": v.variant_parameters_json, "deterministic_seed": v.deterministic_seed,
        "status": v.status, "created_at": v.created_at.isoformat() if v.created_at else None,
    }


def _job_to_dict(j: SimulationJob) -> dict:
    return {
        "id": j.id, "scenario_id": j.scenario_id, "variant_id": j.variant_id,
        "provider_type": j.provider_type, "mode": j.mode, "status": j.status,
        "submitted_at": j.submitted_at.isoformat() if j.submitted_at else None,
        "started_at": j.started_at.isoformat() if j.started_at else None,
        "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        "duration_seconds": j.duration_seconds, "log_path": j.log_path,
        "error_message": j.error_message,
    }


def _artifact_to_dict(a: OutputArtifact) -> dict:
    return {
        "id": a.id, "job_id": a.job_id, "artifact_type": a.artifact_type,
        "file_path": a.file_path, "preview_path": a.preview_path,
        "metadata": a.metadata_json, "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _eval_to_dict(e: EvaluationReport) -> dict:
    return {
        "id": e.id, "job_id": e.job_id,
        "collision_risk_score": e.collision_risk_score, "occlusion_score": e.occlusion_score,
        "path_conflict_score": e.path_conflict_score, "severity_score": e.severity_score,
        "diversity_score": e.diversity_score, "coverage_summary": e.coverage_summary_json,
        "explanation": e.explanation, "top_risk_factors": e.top_risk_factors,
        "recommended_actions": e.recommended_actions,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


# ── Health ────────────────────────────────────────────────────────────────

@router.get("/health")
def health():
    return {"status": "ok", "service": "simforge-api", "version": "0.1.0"}


# ── Scenarios ─────────────────────────────────────────────────────────────

@router.post("/scenarios")
def create_scenario(data: dict, db: Session = Depends(get_db)):
    s = Scenario(id=data.get("id", _uid()), **{k: v for k, v in data.items() if k != "id" and hasattr(Scenario, k)})
    db.add(s)
    db.commit()
    db.refresh(s)
    _log_activity(db, "scenario_created", "scenario", s.id, f"Scenario '{s.name}' created")
    return _scenario_to_dict(s)


@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(Scenario.created_at.desc()).all()
    return [_scenario_to_dict(s) for s in scenarios]


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(404, "Scenario not found")
    return _scenario_to_dict(s)


@router.put("/scenarios/{scenario_id}")
def update_scenario(scenario_id: str, data: dict, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(404, "Scenario not found")
    for key, value in data.items():
        if hasattr(s, key) and key not in ("id", "created_at"):
            setattr(s, key, value)
    s.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(s)
    return _scenario_to_dict(s)


@router.delete("/scenarios/{scenario_id}")
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(404, "Scenario not found")
    db.delete(s)
    db.commit()
    return {"deleted": True, "id": scenario_id}


@router.post("/scenarios/{scenario_id}/compile")
def compile_scenario(scenario_id: str, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(404, "Scenario not found")

    # Delete existing variants
    db.query(ScenarioVariant).filter(ScenarioVariant.scenario_id == scenario_id).delete()

    # Compile using SDK
    sdk_scenario = SDKScenario(
        id=s.id, name=s.name, description=s.description,
        environment_template=s.environment_template, robot_path_type=s.robot_path_type,
        human_crossing_probability=s.human_crossing_probability,
        dropped_obstacle_level=s.dropped_obstacle_level,
        blocked_aisle_enabled=s.blocked_aisle_enabled, lighting_preset=s.lighting_preset,
        camera_mode=s.camera_mode, variant_count=s.variant_count, random_seed=s.random_seed,
    )
    sdk_variants = compiler.compile(sdk_scenario)

    db_variants = []
    for v in sdk_variants:
        dbv = ScenarioVariant(
            id=v.id, scenario_id=scenario_id, variant_index=v.variant_index,
            variant_parameters_json=v.variant_parameters,
            deterministic_seed=v.deterministic_seed,
        )
        db.add(dbv)
        db_variants.append(dbv)

    s.status = "compiled"
    s.updated_at = datetime.utcnow()
    db.commit()

    _log_activity(db, "scenario_compiled", "scenario", scenario_id,
                  f"Compiled {len(db_variants)} variants")
    return [_variant_to_dict(v) for v in db_variants]


@router.get("/scenarios/{scenario_id}/variants")
def list_variants(scenario_id: str, db: Session = Depends(get_db)):
    variants = db.query(ScenarioVariant).filter(
        ScenarioVariant.scenario_id == scenario_id
    ).order_by(ScenarioVariant.variant_index).all()
    return [_variant_to_dict(v) for v in variants]


# ── Runs / Jobs ───────────────────────────────────────────────────────────

async def _run_mock_simulation(job_id: str):
    """Background task: simulate job execution through state machine."""
    await asyncio.sleep(1)
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        job = db.query(SimulationJob).filter(SimulationJob.id == job_id).first()
        if not job:
            return

        # preparing
        job.status = "preparing"
        job.started_at = datetime.utcnow()
        db.commit()
        await asyncio.sleep(2)

        # running
        job.status = "running"
        db.commit()
        await asyncio.sleep(3)

        # rendering
        job.status = "rendering"
        db.commit()
        await asyncio.sleep(2)

        # completed
        rng = random.Random(hash(job_id))
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
        db.commit()

        # Generate artifacts
        for atype, fname in [
            ("preview_image", f"preview_{job_id[:8]}.png"),
            ("manifest_json", f"manifest_{job_id[:8]}.json"),
            ("labels_json", f"labels_{job_id[:8]}.json"),
            ("evaluation_json", f"eval_{job_id[:8]}.json"),
            ("log_file", f"log_{job_id[:8]}.txt"),
        ]:
            db.add(OutputArtifact(
                id=_uid(), job_id=job_id, artifact_type=atype,
                file_path=f"/storage/artifacts/{fname}",
                metadata_json={"generated": "mock", "provider": "mock"},
            ))
        db.commit()

        # Generate evaluation
        variant = db.query(ScenarioVariant).filter(ScenarioVariant.id == job.variant_id).first()
        if variant:
            sdk_variant = SDKVariant(
                id=variant.id, scenario_id=variant.scenario_id,
                variant_index=variant.variant_index,
                variant_parameters=variant.variant_parameters_json or {},
                deterministic_seed=variant.deterministic_seed,
            )
            report = evaluator.evaluate_variant(sdk_variant, job_id)
            db.add(EvaluationReport(
                id=report.id, job_id=job_id,
                collision_risk_score=report.collision_risk_score,
                occlusion_score=report.occlusion_score,
                path_conflict_score=report.path_conflict_score,
                severity_score=report.severity_score,
                diversity_score=report.diversity_score,
                coverage_summary_json=report.coverage_summary,
                explanation=report.explanation,
                top_risk_factors=report.top_risk_factors,
                recommended_actions=report.recommended_actions,
            ))
            variant.status = "completed"
            db.commit()

        db.add(ActivityLog(
            id=_uid(), event_type="job_completed",
            related_entity_type="job", related_entity_id=job_id,
            message=f"Job completed in {job.duration_seconds:.1f}s",
        ))
        db.commit()
    except Exception as e:
        job = db.query(SimulationJob).filter(SimulationJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/scenarios/{scenario_id}/run")
async def submit_run(scenario_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(404, "Scenario not found")

    variants = db.query(ScenarioVariant).filter(ScenarioVariant.scenario_id == scenario_id).all()
    if not variants:
        raise HTTPException(400, "Scenario has no compiled variants. Compile first.")

    run_id = _uid()
    job_ids = []
    for v in variants:
        job_id = _uid()
        job = SimulationJob(
            id=job_id, scenario_id=scenario_id, variant_id=v.id,
            provider_type="mock", mode="mock", status="queued",
        )
        db.add(job)
        job_ids.append(job_id)
        background_tasks.add_task(_run_mock_simulation, job_id)

    s.status = "running"
    s.updated_at = datetime.utcnow()
    db.commit()

    _log_activity(db, "run_submitted", "scenario", scenario_id,
                  f"Run submitted with {len(job_ids)} jobs")

    return {
        "run_id": run_id, "scenario_id": scenario_id,
        "job_ids": job_ids, "variant_count": len(variants),
        "status": "queued", "message": f"Submitted {len(job_ids)} simulation jobs",
    }


@router.get("/jobs")
def list_jobs(
    status: Optional[str] = Query(None),
    scenario_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(SimulationJob)
    if status:
        q = q.filter(SimulationJob.status == status)
    if scenario_id:
        q = q.filter(SimulationJob.scenario_id == scenario_id)
    jobs = q.order_by(SimulationJob.submitted_at.desc()).all()
    return [_job_to_dict(j) for j in jobs]


@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    j = db.query(SimulationJob).filter(SimulationJob.id == job_id).first()
    if not j:
        raise HTTPException(404, "Job not found")
    return _job_to_dict(j)


@router.post("/jobs/{job_id}/retry")
async def retry_job(job_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    j = db.query(SimulationJob).filter(SimulationJob.id == job_id).first()
    if not j:
        raise HTTPException(404, "Job not found")
    if j.status != "failed":
        raise HTTPException(400, "Only failed jobs can be retried")
    j.status = "queued"
    j.error_message = None
    j.started_at = None
    j.completed_at = None
    j.duration_seconds = None
    db.commit()
    background_tasks.add_task(_run_mock_simulation, job_id)
    _log_activity(db, "job_retried", "job", job_id, "Job retried")
    return _job_to_dict(j)


# ── Artifacts ─────────────────────────────────────────────────────────────

@router.get("/artifacts")
def list_artifacts(db: Session = Depends(get_db)):
    arts = db.query(OutputArtifact).order_by(OutputArtifact.created_at.desc()).all()
    return [_artifact_to_dict(a) for a in arts]


@router.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    a = db.query(OutputArtifact).filter(OutputArtifact.id == artifact_id).first()
    if not a:
        raise HTTPException(404, "Artifact not found")
    return _artifact_to_dict(a)


@router.get("/jobs/{job_id}/artifacts")
def list_job_artifacts(job_id: str, db: Session = Depends(get_db)):
    arts = db.query(OutputArtifact).filter(OutputArtifact.job_id == job_id).all()
    return [_artifact_to_dict(a) for a in arts]


# ── Evaluations ───────────────────────────────────────────────────────────

@router.get("/evaluations")
def list_evaluations(db: Session = Depends(get_db)):
    evals = db.query(EvaluationReport).order_by(EvaluationReport.created_at.desc()).all()
    return [_eval_to_dict(e) for e in evals]


@router.get("/jobs/{job_id}/evaluation")
def get_job_evaluation(job_id: str, db: Session = Depends(get_db)):
    e = db.query(EvaluationReport).filter(EvaluationReport.job_id == job_id).first()
    if not e:
        raise HTTPException(404, "Evaluation not found")
    return _eval_to_dict(e)


# ── Activity ──────────────────────────────────────────────────────────────

@router.get("/activity")
def list_activity(limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
    return [{
        "id": l.id, "event_type": l.event_type,
        "related_entity_type": l.related_entity_type,
        "related_entity_id": l.related_entity_id,
        "message": l.message, "metadata": l.metadata_json,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    } for l in logs]


# ── Settings ──────────────────────────────────────────────────────────────

@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(SystemSetting).all()
    return {s.key: s.value for s in settings}


@router.put("/settings")
def update_settings(data: dict, db: Session = Depends(get_db)):
    for key, value in data.items():
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.utcnow()
        else:
            db.add(SystemSetting(id=_uid(), key=key, value=str(value)))
    db.commit()
    return get_settings(db)
