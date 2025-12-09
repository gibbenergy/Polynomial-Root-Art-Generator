import numpy as np
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class DomainSpec(BaseModel):
    """A schema for defining a sampling domain for a complex variable."""
    domain_type: Literal['unit_circle', 'annulus', 'line', 'uniform_disk']
    n_samples: int
    seed: Optional[int] = None

class UnitCircleSpec(DomainSpec):
    domain_type: Literal['unit_circle'] = 'unit_circle'

class AnnulusSpec(DomainSpec):
    domain_type: Literal['annulus'] = 'annulus'
    min_radius: float = 0.0
    max_radius: float = 1.0

class LineSpec(DomainSpec):
    domain_type: Literal['line'] = 'line'
    start: List[float] = Field(..., min_items=2, max_items=2)  # [real, imag]
    end: List[float] = Field(..., min_items=2, max_items=2)    # [real, imag]

class UniformDiskSpec(DomainSpec):
    domain_type: Literal['uniform_disk'] = 'uniform_disk'
    max_radius: float = 1.0


# --- Sampler Implementations ---

def get_sampler(spec: dict):
    """Factory function to get the correct sampler class from a spec dictionary."""
    domain_type = spec.get('domain_type')
    if domain_type == 'unit_circle':
        return UnitCircleSampler(UnitCircleSpec(**spec))
    elif domain_type == 'annulus':
        return AnnulusSampler(AnnulusSpec(**spec))
    elif domain_type == 'line':
        return LineSampler(LineSpec(**spec))
    elif domain_type == 'uniform_disk':
        return UniformDiskSampler(UniformDiskSpec(**spec))
    else:
        raise ValueError(f"Unknown domain type: {domain_type}")

class BaseSampler:
    def __init__(self, spec: DomainSpec):
        self.spec = spec
        self.rng = np.random.default_rng(spec.seed)

    def sample(self) -> np.ndarray:
        raise NotImplementedError

class UnitCircleSampler(BaseSampler):
    def sample(self) -> np.ndarray:
        angles = self.rng.uniform(0, 2 * np.pi, self.spec.n_samples)
        return np.exp(1j * angles)

class AnnulusSampler(BaseSampler):
    def sample(self) -> np.ndarray:
        angles = self.rng.uniform(0, 2 * np.pi, self.spec.n_samples)
        # To ensure uniform area sampling, we sample radius^2, then take the sqrt
        r_squared = self.rng.uniform(self.spec.min_radius**2, self.spec.max_radius**2, self.spec.n_samples)
        radii = np.sqrt(r_squared)
        return radii * np.exp(1j * angles)

class LineSampler(BaseSampler):
    def sample(self) -> np.ndarray:
        start_complex = self.spec.start[0] + 1j * self.spec.start[1]
        end_complex = self.spec.end[0] + 1j * self.spec.end[1]
        t = self.rng.uniform(0, 1, self.spec.n_samples)
        return start_complex + t * (end_complex - start_complex)

class UniformDiskSampler(BaseSampler):
    def sample(self) -> np.ndarray:
        # Sample using r = sqrt(U) to ensure uniform spatial distribution
        angles = self.rng.uniform(0, 2 * np.pi, self.spec.n_samples)
        radii_squared = self.rng.uniform(0, self.spec.max_radius**2, self.spec.n_samples)
        radii = np.sqrt(radii_squared)
        return radii * np.exp(1j * angles)
