"""AQSM watermark construction from bit planes."""

from typing import Dict, Optional

from .aqsm_build_result import AQSMBuildResult
from .quantum_block_aggregator import QuantumBlockAggregator
from .scale_parameters import ScaleParameters
from .types import BitMatrix


class AQSMWatermarkBuilder:
    """Build AQSM binary watermark images from bit planes.

    Inputs:
        Bit-plane dictionary `w1`..`w8` and the current `ScaleParameters`.

    Outputs:
        `AQSMBuildResult` containing the binary watermark images to embed.

    Notes:
        This implementation deliberately supports only `r = 1`, because that is
        the only case where the paper explicitly states the three embedded AQSM
        watermark block sets.
    """

    def __init__(self, aggregator: Optional[QuantumBlockAggregator] = None) -> None:
        self.aggregator = aggregator or QuantumBlockAggregator()

    def build(
        self,
        bit_planes: Dict[str, BitMatrix],
        scale_parameters: ScaleParameters,
    ) -> AQSMBuildResult:
        """Build AQSM watermark images from the bit planes.

        Args:
            bit_planes: Dictionary mapping `w1`..`w8` to binary matrices.
            scale_parameters: AQSM scale parameters for the current images.

        Returns:
            An `AQSMBuildResult` containing the embedded AQSM outputs.
        """

        if scale_parameters.scale_factor != 1:
            raise NotImplementedError(
                "AQSM watermark construction is intentionally limited to r=1, "
                "because the paper does not fully specify the general AQSM "
                "customization schedule for larger scales."
            )

        required_keys = [f"w{i}" for i in range(1, 9)]
        for key in required_keys:
            if key not in bit_planes:
                raise ValueError(f"Missing bit plane {key}.")

        watermark_1 = self.aggregator.aggregate_four(
            bit_planes["w1"],
            bit_planes["w2"],
            bit_planes["w3"],
            bit_planes["w4"],
        )
        watermark_2 = self.aggregator.aggregate_four(
            bit_planes["w5"],
            bit_planes["w7"],
            bit_planes["w7"],
            bit_planes["w7"],
        )
        watermark_3 = self.aggregator.aggregate_four(
            bit_planes["w6"],
            bit_planes["w8"],
            bit_planes["w8"],
            bit_planes["w8"],
        )

        return AQSMBuildResult(
            embedded_watermarks=[watermark_1, watermark_2, watermark_3],
            declared_output_count=scale_parameters.q_outputs,
        )
