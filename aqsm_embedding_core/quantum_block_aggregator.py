"""QBA block aggregation logic."""

from typing import Sequence

from .image_matrix_validator import ImageMatrixValidator
from .types import BitMatrix


class QuantumBlockAggregator:
    """Perform the QBA/QBS block merge used by AQSM.

    Inputs:
        Four equally sized binary blocks.

    Outputs:
        One larger binary block with the input blocks placed by quadrant.
    """

    def aggregate_four(
        self,
        top_left: Sequence[Sequence[int]],
        top_right: Sequence[Sequence[int]],
        bottom_left: Sequence[Sequence[int]],
        bottom_right: Sequence[Sequence[int]],
    ) -> BitMatrix:
        """Aggregate four binary blocks into one larger binary block.

        Args:
            top_left: Block placed in the top-left quadrant.
            top_right: Block placed in the top-right quadrant.
            bottom_left: Block placed in the bottom-left quadrant.
            bottom_right: Block placed in the bottom-right quadrant.

        Returns:
            A binary matrix with doubled side length.
        """

        for block in (top_left, top_right, bottom_left, bottom_right):
            ImageMatrixValidator.validate_binary(block)

        block_side = len(top_left)
        if any(len(block) != block_side for block in (top_right, bottom_left, bottom_right)):
            raise ValueError("All blocks must have the same side length.")

        output: BitMatrix = []
        for row_index in range(block_side):
            output.append(list(top_left[row_index]) + list(top_right[row_index]))
        for row_index in range(block_side):
            output.append(list(bottom_left[row_index]) + list(bottom_right[row_index]))
        return output
