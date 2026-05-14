"""Data object for watermark extraction outputs."""

from dataclasses import dataclass
from typing import Dict, List

from .types import BitMatrix, ImageMatrix


@dataclass(frozen=True)
class ExtractionResult:
    """Complete output of the implemented r=1 extraction path.

    Inputs:
        xor_matrix: `V_eta` matrix recomputed from the watermarked carrier.
        extracted_aqsm_watermarks: Binary AQSM watermarks extracted from carrier LSBs.
        inverse_qba_blocks: Quadrant blocks recovered by inverse QBA.
        refined_bit_planes: Recovered watermark bit planes `w1` through `w8`.
        recovered_watermark: Final reconstructed grayscale watermark.

    Outputs:
        One reusable snapshot of the extraction process.
    """

    xor_matrix: BitMatrix
    extracted_aqsm_watermarks: List[BitMatrix]
    inverse_qba_blocks: Dict[str, List[BitMatrix]]
    refined_bit_planes: Dict[str, BitMatrix]
    recovered_watermark: ImageMatrix
