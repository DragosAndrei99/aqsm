"""Watermark bit-plane decomposition."""

from typing import Dict, Sequence

from .image_matrix_validator import ImageMatrixValidator
from .types import BitMatrix


class BitPlaneDecomposer:
    """Split an 8-bit grayscale image into paper-style bit planes `w1` to `w8`.

    Inputs:
        Grayscale image matrix.

    Outputs:
        A dictionary that maps `w1`..`w8` to binary image matrices.
    """

    def decompose(self, image: Sequence[Sequence[int]]) -> Dict[str, BitMatrix]:
        """Decompose a grayscale image into eight binary bit planes.

        Args:
            image: Square grayscale image matrix.

        Returns:
            A dictionary where `w1` is the LSB plane and `w8` is the MSB plane.
        """

        ImageMatrixValidator.validate_grayscale(image)
        bit_planes: Dict[str, BitMatrix] = {}

        for bit_index in range(8):
            bit_planes[f"w{bit_index + 1}"] = [
                [((value >> bit_index) & 1) for value in row]
                for row in image
            ]

        return bit_planes
