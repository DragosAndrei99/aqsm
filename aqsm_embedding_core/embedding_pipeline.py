"""End-to-end embedding pipeline."""

from typing import Optional, Sequence

from .aqsm_watermark_builder import AQSMWatermarkBuilder
from .bit_plane_decomposer import BitPlaneDecomposer
from .embedding_context import EmbeddingContext
from .hdwm_embedder import HDWMEmbedder
from .histogram_analyzer import HistogramAnalyzer
from .neqr_encoder import NEQREncoder
from .scale_parameter_calculator import ScaleParameterCalculator


class EmbeddingPipeline:
    """Run the full embedding-side workflow in the same order as the paper.

    Inputs:
        Watermark image, carrier image, and an optional histogram denominator mode.

    Outputs:
        `EmbeddingContext` containing every major intermediate result.
    """

    def __init__(
        self,
        neqr_encoder: Optional[NEQREncoder] = None,
        scale_calculator: Optional[ScaleParameterCalculator] = None,
        histogram_analyzer: Optional[HistogramAnalyzer] = None,
        bit_plane_decomposer: Optional[BitPlaneDecomposer] = None,
        aqsm_builder: Optional[AQSMWatermarkBuilder] = None,
        embedder: Optional[HDWMEmbedder] = None,
    ) -> None:
        self.neqr_encoder = neqr_encoder or NEQREncoder()
        self.scale_calculator = scale_calculator or ScaleParameterCalculator()
        self.histogram_analyzer = histogram_analyzer or HistogramAnalyzer()
        self.bit_plane_decomposer = bit_plane_decomposer or BitPlaneDecomposer()
        self.aqsm_builder = aqsm_builder or AQSMWatermarkBuilder()
        self.embedder = embedder or HDWMEmbedder()

    def run(
        self,
        watermark_image: Sequence[Sequence[int]],
        carrier_image: Sequence[Sequence[int]],
        histogram_denominator_mode: str = "natural",
    ) -> EmbeddingContext:
        """Run the embedding-side pipeline from NEQR through carrier embedding.

        Args:
            watermark_image: Square watermark image matrix.
            carrier_image: Square carrier image matrix.
            histogram_denominator_mode: `"natural"` or `"paper"`.

        Returns:
            An `EmbeddingContext` with all major intermediate results.
        """

        watermark_neqr = self.neqr_encoder.encode(watermark_image)
        carrier_neqr = self.neqr_encoder.encode(carrier_image)
        scale_parameters = self.scale_calculator.compute(watermark_image, carrier_image)
        histogram_parameters = self.histogram_analyzer.analyze(
            watermark_image=watermark_image,
            scale_parameters=scale_parameters,
            denominator_mode=histogram_denominator_mode,
        )
        bit_planes = self.bit_plane_decomposer.decompose(watermark_image)
        aqsm_result = self.aqsm_builder.build(bit_planes, scale_parameters)
        embedding_result = self.embedder.embed(
            carrier_image=carrier_image,
            aqsm_result=aqsm_result,
            histogram_parameters=histogram_parameters,
            scale_parameters=scale_parameters,
        )

        return EmbeddingContext(
            watermark_neqr=watermark_neqr,
            carrier_neqr=carrier_neqr,
            scale_parameters=scale_parameters,
            histogram_parameters=histogram_parameters,
            bit_planes=bit_planes,
            aqsm_result=aqsm_result,
            embedding_result=embedding_result,
        )
