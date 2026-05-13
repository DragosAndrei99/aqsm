"""Data object for watermark embedding outputs."""

from dataclasses import dataclass
from typing import Dict

from .types import BitMatrix, ImageMatrix


@dataclass(frozen=True)
class EmbeddingResult:
    """Final watermark embedding result.

    Inputs:
        xor_matrix: `V_eta` matrix derived from the carrier MSBs.
        intermediate_images: Carrier images after each LSB-plane embedding step.
        final_image: Final watermarked carrier image.

    Outputs:
        A reusable snapshot of the embedding process.
    """

    xor_matrix: BitMatrix
    intermediate_images: Dict[str, ImageMatrix]
    final_image: ImageMatrix
