"""Carrier-side `V_eta` calculator."""

from typing import List, Sequence

from .image_matrix_validator import ImageMatrixValidator
from .types import BitMatrix


class CarrierXorCalculator:
    """Compute the `V_eta` matrix from carrier MSBs.

    Inputs:
        Carrier grayscale image and the xor index `eta`.

    Outputs:
        A binary matrix where each element is the xor of selected carrier MSBs.
    """

    def compute(self, carrier_image: Sequence[Sequence[int]], eta: int) -> BitMatrix:
        """Compute `V_eta` from carrier MSB bit positions.

        Args:
            carrier_image: Square grayscale carrier image.
            eta: `0` for xor of three MSBs, `1` for xor of four MSBs.

        Returns:
            A binary matrix with the same shape as the carrier image.
        """

        ImageMatrixValidator.validate_grayscale(carrier_image)

        if eta == 0:
            bit_positions = (7, 6, 5)
        elif eta == 1:
            bit_positions = (7, 6, 5, 4)
        else:
            raise ValueError("eta must be 0 or 1.")

        xor_matrix: BitMatrix = []
        for row in carrier_image:
            xor_row: List[int] = []
            for value in row:
                xor_value = 0
                for bit_position in bit_positions:
                    xor_value ^= (value >> bit_position) & 1
                xor_row.append(xor_value)
            xor_matrix.append(xor_row)
        return xor_matrix
