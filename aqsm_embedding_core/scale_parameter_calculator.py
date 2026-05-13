"""AQSM scale parameter calculator."""

from typing import Sequence

from .image_matrix_validator import ImageMatrixValidator
from .scale_parameters import ScaleParameters


class ScaleParameterCalculator:
    """Compute the AQSM scale parameters from watermark and carrier sizes.

    Inputs:
        Watermark and carrier grayscale image matrices.

    Outputs:
        A `ScaleParameters` instance following the paper formulas.
    """

    def compute(
        self,
        watermark_image: Sequence[Sequence[int]],
        carrier_image: Sequence[Sequence[int]],
    ) -> ScaleParameters:
        """Compute `m`, `n`, `r`, `beta`, `alpha`, `d`, and `q`.

        Args:
            watermark_image: Square watermark image matrix.
            carrier_image: Square carrier image matrix.

        Returns:
            The scale parameters required by AQSM and embedding.
        """

        ImageMatrixValidator.validate_grayscale(watermark_image)
        ImageMatrixValidator.validate_grayscale(carrier_image)

        m = ImageMatrixValidator.validate_square_power_of_two(watermark_image)
        n = ImageMatrixValidator.validate_square_power_of_two(carrier_image)

        if n < m:
            raise ValueError("Carrier image must be at least as large as the watermark image.")

        r = n - m
        beta = 2 if r == 1 else r
        alpha = (2 ** (2 * beta - 3)) - 1
        aggregation_level = 1 if r == 1 else r
        q_outputs = 4 if r == 1 else 4 ** (r - aggregation_level)

        return ScaleParameters(
            watermark_side_exponent=m,
            carrier_side_exponent=n,
            scale_factor=r,
            beta=beta,
            alpha=alpha,
            aggregation_level=aggregation_level,
            q_outputs=q_outputs,
        )
