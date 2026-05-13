"""Validation helpers for image matrices."""

from typing import Sequence

from .types import ImageMatrix


class ImageMatrixValidator:
    """Validate and clone image matrices used across the implementation.

    Inputs:
        Square grayscale or binary image matrices represented as nested lists.

    Outputs:
        Validated image metadata or defensive deep copies of the input.
    """

    @staticmethod
    def clone(image: Sequence[Sequence[int]]) -> ImageMatrix:
        """Create a deep copy of an image matrix.

        Args:
            image: Nested list-like image matrix.

        Returns:
            A plain Python list-of-lists copy of the image.
        """

        return [list(row) for row in image]

    @staticmethod
    def validate_square_power_of_two(image: Sequence[Sequence[int]]) -> int:
        """Validate that an image is square and its side length is a power of two.

        Args:
            image: Nested list-like image matrix.

        Returns:
            The side exponent `s` for an image of size `2^s x 2^s`.
        """

        if not image:
            raise ValueError("Image must not be empty.")

        side = len(image)
        if any(len(row) != side for row in image):
            raise ValueError("Image must be square.")

        if side & (side - 1):
            raise ValueError("Image side length must be a power of two.")

        return side.bit_length() - 1

    @staticmethod
    def validate_grayscale(image: Sequence[Sequence[int]]) -> None:
        """Validate that an image contains 8-bit grayscale pixels.

        Args:
            image: Image matrix with integer pixel values.

        Returns:
            None. Raises `ValueError` if the image is invalid.
        """

        ImageMatrixValidator.validate_square_power_of_two(image)
        for row in image:
            for value in row:
                if not isinstance(value, int) or not (0 <= value <= 255):
                    raise ValueError("Grayscale pixels must be integers in [0, 255].")

    @staticmethod
    def validate_binary(image: Sequence[Sequence[int]]) -> None:
        """Validate that an image contains only binary pixels.

        Args:
            image: Image matrix with binary pixel values.

        Returns:
            None. Raises `ValueError` if the image is invalid.
        """

        ImageMatrixValidator.validate_square_power_of_two(image)
        for row in image:
            for value in row:
                if value not in (0, 1):
                    raise ValueError("Binary images must contain only 0 or 1.")
