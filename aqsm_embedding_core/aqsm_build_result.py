"""Data object for AQSM watermark build outputs."""

from dataclasses import dataclass
from typing import List

from .types import BitMatrix


@dataclass(frozen=True)
class AQSMBuildResult:
    """AQSM watermark images built from bit planes.

    Inputs:
        embedded_watermarks: Binary images actually embedded into the carrier.
        declared_output_count: Number of AQSM outputs stated by the paper.

    Outputs:
        The binary watermark images produced for embedding.
    """

    embedded_watermarks: List[BitMatrix]
    declared_output_count: int
