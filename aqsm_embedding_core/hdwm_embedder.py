"""HDWM embedding logic."""

from typing import Dict, Optional, Sequence

from .aqsm_build_result import AQSMBuildResult
from .carrier_xor_calculator import CarrierXorCalculator
from .embedding_result import EmbeddingResult
from .histogram_parameters import HistogramParameters
from .image_matrix_validator import ImageMatrixValidator
from .scale_parameters import ScaleParameters
from .types import ImageMatrix


class HDWMEmbedder:
    """Embed AQSM watermark images into carrier LSB planes using HDWM rules.

    Inputs:
        Carrier image, AQSM watermark images, scale parameters, and histogram parameters.

    Outputs:
        `EmbeddingResult` with the xor matrix, step-by-step carrier snapshots, and the final carrier.
    """

    def __init__(self, xor_calculator: Optional[CarrierXorCalculator] = None) -> None:
        self.xor_calculator = xor_calculator or CarrierXorCalculator()

    @staticmethod
    def compute_eta(scale_parameters: ScaleParameters) -> int:
        """Compute the xor index `eta` from the scale factor.

        Args:
            scale_parameters: AQSM scale parameters.

        Returns:
            `0` for `r=1`, otherwise `r mod 2`.
        """

        if scale_parameters.scale_factor == 1:
            return 0
        return scale_parameters.scale_factor % 2

    @staticmethod
    def compute_embedded_bit(
        watermark_bit: int,
        xor_bit: int,
        tau1: int,
        tau2: Optional[int],
    ) -> int:
        """Compute one embedded carrier bit using the HDWM rules.

        Args:
            watermark_bit: One binary AQSM watermark value.
            xor_bit: Corresponding `V_eta` bit from the carrier.
            tau1: First HDWM branch selector.
            tau2: Second HDWM branch selector, or `None` when tau1 is `0`.

        Returns:
            The target bit that should be written into the carrier LSB plane.
        """

        if tau1 == 0:
            return watermark_bit
        if tau2 == 0:
            return watermark_bit ^ xor_bit
        return watermark_bit ^ (1 - xor_bit)

    def embed_plane(
        self,
        carrier_image: Sequence[Sequence[int]],
        watermark_bits: Sequence[Sequence[int]],
        xor_matrix: Sequence[Sequence[int]],
        tau1: int,
        tau2: Optional[int],
        bit_plane_index: int,
    ) -> ImageMatrix:
        """Embed one binary watermark image into one carrier bit plane.

        Args:
            carrier_image: Current grayscale carrier image.
            watermark_bits: Binary AQSM watermark image.
            xor_matrix: Precomputed `V_eta` matrix.
            tau1: First HDWM branch selector.
            tau2: Second HDWM branch selector, or `None`.
            bit_plane_index: Target carrier bit-plane index, where `0` is the first LSB.

        Returns:
            A new carrier image with the selected bit plane overwritten.
        """

        ImageMatrixValidator.validate_grayscale(carrier_image)
        ImageMatrixValidator.validate_binary(watermark_bits)
        ImageMatrixValidator.validate_binary(xor_matrix)

        if len(carrier_image) != len(watermark_bits):
            raise ValueError("Watermark and carrier image sizes must match for embedding.")

        updated = ImageMatrixValidator.clone(carrier_image)
        for row_index, row in enumerate(updated):
            for column_index, value in enumerate(row):
                target_bit = self.compute_embedded_bit(
                    watermark_bit=watermark_bits[row_index][column_index],
                    xor_bit=xor_matrix[row_index][column_index],
                    tau1=tau1,
                    tau2=tau2,
                )
                row[column_index] = (value & ~(1 << bit_plane_index)) | (
                    target_bit << bit_plane_index
                )
        return updated

    def embed(
        self,
        carrier_image: Sequence[Sequence[int]],
        aqsm_result: AQSMBuildResult,
        histogram_parameters: HistogramParameters,
        scale_parameters: ScaleParameters,
    ) -> EmbeddingResult:
        """Embed all AQSM watermark images into the carrier.

        Args:
            carrier_image: Original grayscale carrier image.
            aqsm_result: AQSM watermark images that should be embedded.
            histogram_parameters: HDWM histogram parameters.
            scale_parameters: AQSM scale parameters used to compute `eta`.

        Returns:
            An `EmbeddingResult` with the intermediate and final images.
        """

        ImageMatrixValidator.validate_grayscale(carrier_image)

        current_image = ImageMatrixValidator.clone(carrier_image)
        eta = self.compute_eta(scale_parameters)
        xor_matrix = self.xor_calculator.compute(current_image, eta)
        intermediate_images: Dict[str, ImageMatrix] = {}

        for plane_index, watermark_bits in enumerate(aqsm_result.embedded_watermarks):
            current_image = self.embed_plane(
                carrier_image=current_image,
                watermark_bits=watermark_bits,
                xor_matrix=xor_matrix,
                tau1=histogram_parameters.tau1,
                tau2=histogram_parameters.tau2,
                bit_plane_index=plane_index,
            )
            intermediate_images[f"after_bit{plane_index}"] = ImageMatrixValidator.clone(
                current_image
            )

        return EmbeddingResult(
            xor_matrix=xor_matrix,
            intermediate_images=intermediate_images,
            final_image=current_image,
        )
