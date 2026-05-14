"""Watermark reconstruction from recovered bit planes."""

from typing import Dict, Sequence

from .image_matrix_validator import ImageMatrixValidator
from .types import BitMatrix, ImageMatrix


class WatermarkReconstructor:
    """Reconstruct an 8-bit grayscale watermark from `w1`..`w8` bit planes.

    Inputs:
        Eight binary bit-plane matrices where `w1` is the least significant bit.

    Outputs:
        One grayscale image matrix.
    """

    def reconstruct(self, bit_planes: Dict[str, Sequence[Sequence[int]]]) -> ImageMatrix:
        """Reconstruct the grayscale watermark.

        Args:
            bit_planes: Dictionary containing binary matrices named `w1` through `w8`.

        Returns:
            Recovered 8-bit grayscale image.
        """

        required_keys = [f"w{index}" for index in range(1, 9)]
        for key in required_keys:
            if key not in bit_planes:
                raise ValueError(f"Missing bit plane {key}.")
            ImageMatrixValidator.validate_binary(bit_planes[key])

        side = len(bit_planes["w1"])
        if any(len(bit_planes[key]) != side for key in required_keys):
            raise ValueError("All bit planes must have the same side length.")

        recovered: ImageMatrix = []
        for row_index in range(side):
            recovered_row = []
            for column_index in range(side):
                value = 0
                for bit_index in range(8):
                    plane = bit_planes[f"w{bit_index + 1}"]
                    value |= plane[row_index][column_index] << bit_index
                recovered_row.append(value)
            recovered.append(recovered_row)
        return recovered
