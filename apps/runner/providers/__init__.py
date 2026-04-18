"""Simulation provider abstraction and implementations."""

from abc import ABC, abstractmethod
from typing import Any


class SimulationProvider(ABC):
    """Abstract simulation provider interface.

    All simulation providers must implement this interface.
    The provider is responsible for preparing, running, and collecting
    outputs from simulation jobs.
    """

    @abstractmethod
    async def prepare_run(self, job_id: str, variant_params: dict[str, Any]) -> dict:
        """Prepare a simulation run. Returns preparation metadata."""
        ...

    @abstractmethod
    async def submit_run(self, job_id: str, preparation: dict) -> dict:
        """Submit a prepared run for execution. Returns submission metadata."""
        ...

    @abstractmethod
    async def get_status(self, job_id: str) -> str:
        """Get the current status of a running job."""
        ...

    @abstractmethod
    async def collect_outputs(self, job_id: str) -> list[dict]:
        """Collect output artifacts from a completed job."""
        ...

    @abstractmethod
    async def cleanup(self, job_id: str) -> None:
        """Clean up resources after job completion."""
        ...
