"""NEQR encoder implementation."""

from typing import List, Sequence

from .image_matrix_validator import ImageMatrixValidator
from .neqr_encoded_image import NEQREncodedImage
from .neqr_pixel_term import NEQRPixelTerm


class NEQREncoder:
    """Build a simple, inspectable NEQR encoding from a grayscale image.

    Inputs:
        Grayscale image matrix represented as nested Python lists.

    Outputs:
        `NEQREncodedImage` containing the shared amplitude and row-major terms.
    """

    def encode(self, image: Sequence[Sequence[int]]) -> NEQREncodedImage:
        """Encode a grayscale image using the conceptual NEQR structure.

        Args:
            image: Square power-of-two grayscale image.

        Returns:
            A `NEQREncodedImage` describing the NEQR basis terms.
        """

        ImageMatrixValidator.validate_grayscale(image)
        side_exponent = ImageMatrixValidator.validate_square_power_of_two(image)
        coordinate_width = side_exponent
        terms: List[NEQRPixelTerm] = []

        for y, row in enumerate(image):
            for x, value in enumerate(row):
                terms.append(
                    NEQRPixelTerm(
                        grayscale_bits=f"{value:08b}",
                        y_bits=f"{y:0{coordinate_width}b}",
                        x_bits=f"{x:0{coordinate_width}b}",
                    )
                )

        return NEQREncodedImage(
            side_exponent=side_exponent,
            amplitude=1 / (2 ** side_exponent),
            terms=terms,
        )
