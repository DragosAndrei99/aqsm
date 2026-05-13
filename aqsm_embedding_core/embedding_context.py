"""Data object for the full embedding pipeline context."""

from dataclasses import dataclass
from typing import Dict

from .aqsm_build_result import AQSMBuildResult
from .embedding_result import EmbeddingResult
from .histogram_parameters import HistogramParameters
from .neqr_encoded_image import NEQREncodedImage
from .scale_parameters import ScaleParameters
from .types import BitMatrix


@dataclass(frozen=True)
class EmbeddingContext:
    """Full embedding-side context gathered by the pipeline.

    Inputs:
        watermark_neqr: Conceptual NEQR encoding of the watermark image.
        carrier_neqr: Conceptual NEQR encoding of the carrier image.
        scale_parameters: Scale-related AQSM parameters.
        histogram_parameters: HDWM histogram parameters.
        bit_planes: Watermark bit planes named `w1` to `w8`.
        aqsm_result: AQSM outputs built from the bit planes.
        embedding_result: Final carrier after watermark embedding.

    Outputs:
        One object containing all important intermediate states.
    """

    watermark_neqr: NEQREncodedImage
    carrier_neqr: NEQREncodedImage
    scale_parameters: ScaleParameters
    histogram_parameters: HistogramParameters
    bit_planes: Dict[str, BitMatrix]
    aqsm_result: AQSMBuildResult
    embedding_result: EmbeddingResult
