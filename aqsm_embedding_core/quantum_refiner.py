"""Quantum refining as classical majority voting."""

from typing import Sequence

from .image_matrix_validator import ImageMatrixValidator
from .types import BitMatrix


class QuantumRefiner:
    """Recover logical bit planes from repeated binary candidates.

    Inputs:
        Odd-length sequences of equally sized binary matrices.

    Outputs:
        One binary matrix whose values are the pixel-wise majority.
    """

    def majority(self, candidates: Sequence[Sequence[Sequence[int]]]) -> BitMatrix:
        """Compute the pixel-wise majority of repeated binary candidates.

        Args:
            candidates: Odd-length sequence of binary matrices.

        Returns:
            A refined binary matrix.
        """

        if not candidates:
            raise ValueError("At least one candidate matrix is required.")
        if len(candidates) % 2 == 0:
            raise ValueError("Quantum refining requires an odd number of candidates.")

        for candidate in candidates:
            ImageMatrixValidator.validate_binary(candidate)

        side = len(candidates[0])
        if any(len(candidate) != side for candidate in candidates):
            raise ValueError("All candidate matrices must have the same side length.")

        threshold = (len(candidates) // 2) + 1
        refined: BitMatrix = []
        for row_index in range(side):
            refined_row = []
            for column_index in range(side):
                bit_sum = sum(candidate[row_index][column_index] for candidate in candidates)
                refined_row.append(1 if bit_sum >= threshold else 0)
            refined.append(refined_row)
        return refined
