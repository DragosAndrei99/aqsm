"""HDWM extraction logic."""

from typing import Dict, List, Optional, Sequence

from .carrier_xor_calculator import CarrierXorCalculator
from .extraction_result import ExtractionResult
from .histogram_parameters import HistogramParameters
from .image_matrix_validator import ImageMatrixValidator
from .quantum_block_aggregator import QuantumBlockAggregator
from .quantum_refiner import QuantumRefiner
from .scale_parameters import ScaleParameters
from .types import BitMatrix
from .watermark_reconstructor import WatermarkReconstructor


class HDWMExtractor:
    """Extract an r=1 AQSM/HDWM watermark from a watermarked carrier.

    Inputs:
        Watermarked carrier image, scale parameters, and HDWM histogram parameters.

    Outputs:
        `ExtractionResult` containing extracted AQSM planes, inverse-QBA blocks,
        refined bit planes, and the recovered grayscale watermark.

    Notes:
        This implementation deliberately supports only `r = 1`, because the paper
        explicitly states the three embedded AQSM block sets only for that case.
    """

    def __init__(
        self,
        xor_calculator: Optional[CarrierXorCalculator] = None,
        aggregator: Optional[QuantumBlockAggregator] = None,
        refiner: Optional[QuantumRefiner] = None,
        reconstructor: Optional[WatermarkReconstructor] = None,
    ) -> None:
        self.xor_calculator = xor_calculator or CarrierXorCalculator()
        self.aggregator = aggregator or QuantumBlockAggregator()
        self.refiner = refiner or QuantumRefiner()
        self.reconstructor = reconstructor or WatermarkReconstructor()

    @staticmethod
    def compute_eta(scale_parameters: ScaleParameters) -> int:
        """Compute the xor index `eta` from the scale factor."""

        if scale_parameters.scale_factor == 1:
            return 0
        return scale_parameters.scale_factor % 2

    @staticmethod
    def compute_extracted_bit(
        carrier_lsb_bit: int,
        xor_bit: int,
        tau1: int,
        tau2: Optional[int],
    ) -> int:
        """Compute one recovered AQSM bit using HDWM Table II.

        Args:
            carrier_lsb_bit: Bit read from one watermarked carrier LSB plane.
            xor_bit: Corresponding `V_eta` bit from the watermarked carrier.
            tau1: First HDWM branch selector.
            tau2: Second HDWM branch selector, or `None` when tau1 is `0`.

        Returns:
            The extracted AQSM watermark bit.
        """

        if tau1 == 0:
            return carrier_lsb_bit
        if tau2 == 0:
            return carrier_lsb_bit ^ xor_bit
        return carrier_lsb_bit ^ (1 - xor_bit)

    def extract_plane(
        self,
        watermarked_image: Sequence[Sequence[int]],
        xor_matrix: Sequence[Sequence[int]],
        tau1: int,
        tau2: Optional[int],
        bit_plane_index: int,
    ) -> BitMatrix:
        """Extract one AQSM binary watermark from one carrier LSB plane."""

        ImageMatrixValidator.validate_grayscale(watermarked_image)
        ImageMatrixValidator.validate_binary(xor_matrix)

        extracted: BitMatrix = []
        for row_index, row in enumerate(watermarked_image):
            extracted_row = []
            for column_index, value in enumerate(row):
                carrier_lsb_bit = (value >> bit_plane_index) & 1
                extracted_bit = self.compute_extracted_bit(
                    carrier_lsb_bit=carrier_lsb_bit,
                    xor_bit=xor_matrix[row_index][column_index],
                    tau1=tau1,
                    tau2=tau2,
                )
                extracted_row.append(extracted_bit)
            extracted.append(extracted_row)
        return extracted

    def extract(
        self,
        watermarked_image: Sequence[Sequence[int]],
        histogram_parameters: HistogramParameters,
        scale_parameters: ScaleParameters,
    ) -> ExtractionResult:
        """Extract and reconstruct the watermark for the implemented r=1 path."""

        ImageMatrixValidator.validate_grayscale(watermarked_image)
        if scale_parameters.scale_factor != 1:
            raise NotImplementedError(
                "HDWM extraction is intentionally limited to r=1, because the paper "
                "does not fully specify the general AQSM extraction schedule."
            )

        eta = self.compute_eta(scale_parameters)
        xor_matrix = self.xor_calculator.compute(watermarked_image, eta)
        extracted_aqsm_watermarks: List[BitMatrix] = []

        for bit_plane_index in range(3):
            extracted_aqsm_watermarks.append(
                self.extract_plane(
                    watermarked_image=watermarked_image,
                    xor_matrix=xor_matrix,
                    tau1=histogram_parameters.tau1,
                    tau2=histogram_parameters.tau2,
                    bit_plane_index=bit_plane_index,
                )
            )

        e1_blocks = list(self.aggregator.split_four(extracted_aqsm_watermarks[0]))
        e2_blocks = list(self.aggregator.split_four(extracted_aqsm_watermarks[1]))
        e3_blocks = list(self.aggregator.split_four(extracted_aqsm_watermarks[2]))
        inverse_qba_blocks: Dict[str, List[BitMatrix]] = {
            "E1": e1_blocks,
            "E2": e2_blocks,
            "E3": e3_blocks,
        }

        refined_bit_planes: Dict[str, BitMatrix] = {
            "w1": e1_blocks[0],
            "w2": e1_blocks[1],
            "w3": e1_blocks[2],
            "w4": e1_blocks[3],
            "w5": e2_blocks[0],
            "w6": e3_blocks[0],
            "w7": self.refiner.majority(e2_blocks[1:4]),
            "w8": self.refiner.majority(e3_blocks[1:4]),
        }
        recovered_watermark = self.reconstructor.reconstruct(refined_bit_planes)

        return ExtractionResult(
            xor_matrix=xor_matrix,
            extracted_aqsm_watermarks=extracted_aqsm_watermarks,
            inverse_qba_blocks=inverse_qba_blocks,
            refined_bit_planes=refined_bit_planes,
            recovered_watermark=recovered_watermark,
        )
