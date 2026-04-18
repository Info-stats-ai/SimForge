"""SimForge CLI — Command-line interface wrapping the SimForge SDK."""

import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Add SDK to path for development
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent / "simforge-sdk"))

from simforge import Scenario, SimForgeClient, ScenarioCompiler, EvaluationEngine

console = Console()

DEFAULT_URL = "http://localhost:8000"


@click.group()
@click.option("--api-url", default=DEFAULT_URL, envvar="SIMFORGE_API_URL", help="Backend API URL")
@click.pass_context
def cli(ctx, api_url: str):
    """SimForge CLI — Warehouse edge-case simulation orchestration."""
    ctx.ensure_object(dict)
    ctx.obj["api_url"] = api_url


# ── Scenario Commands ──────────────────────────────────────────────────────

@cli.group()
def scenario():
    """Manage simulation scenarios."""
    pass


@scenario.command("create")
@click.option("--name", required=True, help="Scenario name")
@click.option("--template", default="warehouse_aisle", help="Environment template")
@click.option("--path-type", default="left_turn_blind_corner", help="Robot path type")
@click.option("--human-prob", default=0.5, type=float, help="Human crossing probability")
@click.option("--obstacle-level", default="medium", help="Dropped obstacle level")
@click.option("--blocked-aisle", is_flag=True, help="Enable blocked aisle")
@click.option("--lighting", default="normal", help="Lighting preset")
@click.option("--camera", default="overhead", help="Camera mode")
@click.option("--variants", default=5, type=int, help="Number of variants")
@click.option("--seed", default=42, type=int, help="Random seed")
@click.pass_context
def scenario_create(ctx, name, template, path_type, human_prob, obstacle_level,
                    blocked_aisle, lighting, camera, variants, seed):
    """Create a new scenario."""
    s = Scenario(
        name=name,
        environment_template=template,
        robot_path_type=path_type,
        human_crossing_probability=human_prob,
        dropped_obstacle_level=obstacle_level,
        blocked_aisle_enabled=blocked_aisle,
        lighting_preset=lighting,
        camera_mode=camera,
        variant_count=variants,
        random_seed=seed,
    )
    try:
        client = SimForgeClient(base_url=ctx.obj["api_url"])
        created = client.create_scenario(s)
        console.print(Panel(f"[green]✓[/green] Scenario created: [bold]{created.id}[/bold]", title="SimForge"))
        console.print(f"  Name: {created.name}")
        console.print(f"  Template: {created.environment_template}")
        console.print(f"  Variants: {created.variant_count}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@scenario.command("compile")
@click.argument("scenario_id")
@click.pass_context
def scenario_compile(ctx, scenario_id: str):
    """Compile a scenario into variants."""
    try:
        client = SimForgeClient(base_url=ctx.obj["api_url"])
        variants = client.compile_scenario(scenario_id)
        table = Table(title=f"Compiled {len(variants)} Variants")
        table.add_column("Index", style="cyan")
        table.add_column("Seed", style="green")
        table.add_column("Human", style="yellow")
        table.add_column("Conflict", style="red")
        for v in variants:
            p = v.variant_parameters
            table.add_row(
                str(v.variant_index),
                str(v.deterministic_seed),
                "✓" if p.get("human_present") else "✗",
                f"{p.get('path_conflict_intensity', 0):.1%}",
            )
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@scenario.command("list")
@click.pass_context
def scenario_list(ctx):
    """List all scenarios."""
    try:
        client = SimForgeClient(base_url=ctx.obj["api_url"])
        scenarios = client.list_scenarios()
        table = Table(title="Scenarios")
        table.add_column("ID", style="dim", max_width=12)
        table.add_column("Name", style="bold")
        table.add_column("Status", style="cyan")
        table.add_column("Variants", style="green")
        for s in scenarios:
            table.add_row(s.id[:12], s.name, s.status, str(s.variant_count))
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


# ── Run Commands ──────────────────────────────────────────────────────────

@cli.group()
def run():
    """Manage simulation runs."""
    pass


@run.command("submit")
@click.argument("scenario_id")
@click.pass_context
def run_submit(ctx, scenario_id: str):
    """Submit a scenario for simulation."""
    try:
        client = SimForgeClient(base_url=ctx.obj["api_url"])
        result = client.submit_scenario(scenario_id)
        console.print(Panel(f"[green]✓[/green] Run submitted: [bold]{result.run_id}[/bold]", title="SimForge"))
        console.print(f"  Jobs: {len(result.job_ids)}")
        console.print(f"  Status: {result.status}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@run.command("status")
@click.argument("job_id")
@click.pass_context
def run_status(ctx, job_id: str):
    """Get run/job status."""
    try:
        client = SimForgeClient(base_url=ctx.obj["api_url"])
        job = client.get_job(job_id)
        console.print(Panel(f"Status: [bold]{job.status}[/bold]", title=f"Job {job_id[:12]}"))
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


# ── Artifacts Commands ────────────────────────────────────────────────────

@cli.group()
def artifacts():
    """Manage output artifacts."""
    pass


@artifacts.command("list")
@click.option("--job-id", default=None, help="Filter by job ID")
@click.pass_context
def artifacts_list(ctx, job_id: Optional[str]):
    """List artifacts."""
    try:
        client = SimForgeClient(base_url=ctx.obj["api_url"])
        arts = client.list_artifacts(job_id=job_id)
        table = Table(title="Artifacts")
        table.add_column("ID", style="dim", max_width=12)
        table.add_column("Type", style="cyan")
        table.add_column("File", style="green")
        for a in arts:
            table.add_row(a.id[:12], a.artifact_type, a.file_path)
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


# ── Evaluation Commands ───────────────────────────────────────────────────

@cli.group()
def evaluation():
    """View evaluation reports."""
    pass


@evaluation.command("show")
@click.argument("job_id")
@click.pass_context
def evaluation_show(ctx, job_id: str):
    """Show evaluation report for a job."""
    try:
        client = SimForgeClient(base_url=ctx.obj["api_url"])
        report = client.get_evaluation(job_id)
        console.print(Panel(report.explanation, title="Evaluation Report"))
        table = Table(title="Scores")
        table.add_column("Metric", style="bold")
        table.add_column("Score", style="cyan")
        table.add_row("Collision Risk", f"{report.collision_risk_score:.1%}")
        table.add_row("Occlusion", f"{report.occlusion_score:.1%}")
        table.add_row("Path Conflict", f"{report.path_conflict_score:.1%}")
        table.add_row("Severity", f"{report.severity_score:.1%}")
        table.add_row("Diversity", f"{report.diversity_score:.1%}")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def main():
    cli()


if __name__ == "__main__":
    main()
